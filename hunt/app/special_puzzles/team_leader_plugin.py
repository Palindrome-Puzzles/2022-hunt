import logging, time, threading

from django.db import transaction, models

from spoilr.core.models import Team

from hunt.app.core.plugins import Plugin

logger = logging.getLogger(__name__)

# Time to allow the leader to respond to a ping before usurping leadership.
VERIFY_LEADER_TIME_S = 1.0

class TeamLeaderModelBase(models.Model):
    """The partial base model for a team puzzle with a leader."""
    # The WebSocket channel name for the consumer belonging to the session leader.
    leader = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True

class TeamLeaderPlugin(Plugin):
    """
    Plugin for a TeamConsumer that elects a leader and re-elects a leader when
    the current leader changes.

    It guarantees that there is at most one leader, and if there are consumers
    using this plugin, one shall be elected as a leader soon.

    It sends messages to the client that are a dict with the following keys:
     - `type`: 'hunt.team.leader.has_leader'
     - `value`: Whether a leader is currently elected for the team

    It exposes an additional hook:
     - `claimed_leader`: Handler for when this consumer becomes leader.

    The leader can be a backend concept only, to function as a lock so that only
    one consumer makes calls to singleton actions (like perform a broadcast, or
    re-generate puzzle content).

    Or it can be broadcast to the frontend if a puzzle needs to have a leader.

    Any session data should be stored in a model that is a subclass of
    `TeamLeaderModelBase`.
    """

    # Retry interval for claiming leadership in seconds.
    LEADER_RETRY_INTERVAL_S = 0.1
    is_leader = False
    plugin_name = 'leader'
    _usurp_leader_timer = None

    def verify_plugin(self):
        self.parent.assert_has_plugin('session')
        self.get_sibling_plugin('session').assert_has_subclass(TeamLeaderModelBase)

    def joined(self):
        self._maybe_claim_leader(verify_leader=True)

    def disconnected(self, was_authed, close_code):
        if was_authed:
            # This works even after we're disconnected because you can send
            # messages to a channel group without being a member of that group.
            self._maybe_abandon_leader()

    def _maybe_claim_leader(self, verify_leader):
        """
        Claim leadership of the session if one doesn't exist, and updates
        whether the consumer is now the leader.

        If `verify_leader` is `True`, it also waits until the leader responds to
        a ping, and otherwise usurps it.
        """
        leader_channel_name = self._claim_leader(lambda session: bool(session.leader))

        if self.is_leader or not verify_leader:
            self._mark_leader_elected(True)
        else:
            # Ping the leader's channel. If it doesn't exist, then claim leadership
            # instead. This may occur if the server restarted, and the leader's
            # client needs to reconnect with a new channel name.
            self.parent.notify_consumer(leader_channel_name, {
                'type': 'hunt.team.leader.ping',
                'sender': self.parent.channel_name,
            })
            self._usurp_leader_timer = threading.Timer(
                VERIFY_LEADER_TIME_S, self._usurp_leader, args=[leader_channel_name])
            self._usurp_leader_timer.start()

    def _usurp_leader(self, old_leader_channel_name):
        self._claim_leader(lambda session: session.leader != old_leader_channel_name)
        self._mark_leader_elected(True)

        # Defensively tell the old leader they were usurped just in case.
        if self.is_leader:
            self.parent.notify_consumer(old_leader_channel_name, {
                'type': 'hunt.team.leader.usurped',
            })

    def _claim_leader(self, abandon_claim_predicate):
        while True:
            with transaction.atomic():
                session = self.get_sibling_plugin('session').get()
                if abandon_claim_predicate(session):
                    break
                session.leader = self.parent.channel_name
                session.save()
            time.sleep(self.LEADER_RETRY_INTERVAL_S)

        self.is_leader = (session.leader == self.parent.channel_name)

        if self.is_leader:
            self.parent.dispatch_to_plugins('claimed_leader')

        return session.leader

    def _maybe_abandon_leader(self):
        """Abandon being leader if this consumer is currently the leader."""
        if not self.is_leader:
            return

        session = self.get_sibling_plugin('session').get()
        session.leader = None
        session.save()

        self.parent.notify_team({
            'type': 'hunt.team.repick_leader',
            'sender': self.parent.channel_name,
        })

    def hunt_team_repick_leader(self, event):
        """Handler for the channel layer message to repick the leader."""
        self._mark_leader_elected(False)

        # First wait for the leader abandoment to propagate.
        while self.get_sibling_plugin('session').get().leader == event['sender']:
            time.sleep(self.LEADER_RETRY_INTERVAL_S)

        # Then race to try claim leadership.
        self._maybe_claim_leader(verify_leader=False)

    def hunt_team_leader_ping(self, event):
        self.parent.notify_consumer(event['sender'], {
            'type': 'hunt.team.leader.pong',
        })

    def hunt_team_leader_pong(self, event):
        if self._usurp_leader_timer:
            self._usurp_leader_timer.cancel()
            self._usurp_leader_timer = None
        self._mark_leader_elected(True)

    def hunt_team_leader_usurped(self, event):
        # Should never happen because we should have ponged to prevent this. But
        # if it does, run the claim process to reset whether we're leader or not.
        # Otherwise, there may be two leaders and that's probably bad.
        self._maybe_claim_leader(verify_leader=False)
        logger.warn(f'Team leadership was usurped')

    def _mark_leader_elected(self, is_leader_elected):
        self.parent.send_json({
            'type': 'hunt.team.leader.has_leader',
            'value': is_leader_elected,
        })

