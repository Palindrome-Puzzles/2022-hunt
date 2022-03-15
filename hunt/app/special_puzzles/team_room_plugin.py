import datetime, logging, random, threading
from enum import Enum, auto

from django.db import models, IntegrityError
from django.forms.models import model_to_dict
from django.utils.timezone import now

from hunt.app.core.plugins import Plugin

logger = logging.getLogger(__name__)

PING_1_TIMEOUT_S = 1.0
PING_ALL_TIMEOUT_S = 1.0
LIVENESS_PRUNE_INTERVAL_S = 20.0

class TeamRoomJoinStatus(Enum):
    """States a consumer can be in as it joins a team room."""
    # The consumer has just joined the team room and is still confirming whether
    # it's "alive". It may not be alive because of non-persistence of channel
    # names, or unclean websocket disconnects.
    New = auto()

    # The consumer has joined the team room, and has an up-to-date list of
    # participants. It is not a participant yet.
    Entered = auto()

    # The consumer is a participant in the team room.
    Participating = auto()

class TeamParticipantModelBase(models.Model):
    """
    The partial base model for participants in a scrum puzzle.

    It can optionally be scoped, which can be used for things like multiple save
    states in a game. This scope should match `TeamStateListPlugin`.
    """
    scope = models.CharField(max_length=200, blank=True, null=True)
    channel_name = models.CharField(max_length=100, blank=True, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class TeamRoomPlugin(Plugin):
    """
    Plugin for a TeamConsumer where clients need to know who else is present, and
    this information should be synchonized. It performs liveness checking when
    joining to protect against cases where the server restarted, or where there
    were unclean disconnects, and so participant tracking breaks.

    The data can optionally be scoped. If it is, then the plugin only listens
    for room members in the room with the specified scope. (Consumers can
    listen for the list of scopes using `TeamStateScopesPlugin`.)

    Participant info should be stored in a model that is a subclass of
    `TeamParticipantModelBase`. It should also have a foreign key reference to
    the model used for the team session in `TeamSessionPlugin`. If members should
    have specific roles (say 'Player 1', 'Player 2', ...), then set that up as a
    database constraint.

    When the websocket connects (and is authenticated), it performs liveness
    checking, and sends a list of participating members of the room to the client.
    Once this initial liveness check is complete, clients are able to join as
    participants.

    The client can send messages with the following `type` once they've entered:
     - `room.join`: to join as a participant, or to update their join info. It
       can include an optional `scope`, and a `defaults` field for other model
       fields

    When they enter, or when the room participants change, the client will
    receive messages with type `room`. It will include an optional `scope`, and
    a `participants` key with the list of participants as dicts. Exactly one
    participant will contain a `me` field set to `True`.

    They may receive a message with `type` `room.join.error` if they try to take
    a participant role that is already claimed.
    """
    in_memory_participants = None
    join_status = None
    participant_info = None
    dont_prune_channel_names = set()
    ping_1_timer = None
    ping_all_timer = None
    ping_all_time = None
    liveness_timer = None
    last_ping_all_received = None

    def __init__(self, ModelClass, *, session_foreign_key_field, plugin_scope=None):
        super().__init__()

        assert issubclass(ModelClass, TeamParticipantModelBase)

        self.ModelClass = ModelClass
        self.session_foreign_key_field = session_foreign_key_field
        self.plugin_scope = plugin_scope

    @property
    def plugin_name(self):
        return f'room:{self.plugin_scope}' if self.plugin_scope else 'room'

    def verify_plugin(self):
        self.parent.assert_has_plugin('session')
        # TODO(sahil): Is there a way to verify the ModelClass has a foreign key
        # to the session model correctly? Otherwise, runtime errors will have to
        # do.

        if self.plugin_scope:
            self.parent.assert_has_plugin('state_list')
            is_scope_valid = self.get_sibling_plugin('state_list').is_scope_valid
            assert is_scope_valid(self.plugin_scope)

    def joined(self):
        self._debug('joined')
        self.load_participants()

        if len(self.in_memory_participants):
            self._debug('there are other participants', len(self.in_memory_participants))
            self.join_status = TeamRoomJoinStatus.New
            self.participant_info = None
            # Ping a random participant's channel, to check if the room is valid.
            # It may not be if the server restarted, and channel names are
            # obsolete. Or if everyone has disconnected uncleanly, and the keep-alive
            # signals aren't up-to-date yet. We mostly care about the first case
            # for now though.
            participants_list = list(self.in_memory_participants.values())
            other = random.choice(participants_list)
            self._debug('ping1', other['channel_name'])
            self.parent.notify_consumer(other['channel_name'], {
                'type': 'hunt.team.room.ping',
                'sender': self.parent.channel_name,
                'reason': 'ping_1',
            })
            self.ping_1_timer = threading.Timer(
                PING_1_TIMEOUT_S, self.handle_ping_1_timeout)
            self.ping_1_timer.start()

        else:
            self._debug('there are no other participants, enter')
            # We're the first participant, we can just join safely.
            self.enter()

    def handle_ping_1_timeout(self):
        self.ping_1_timeout = None

        self._debug('other participant did not respond, pinging all')
        self.ping_all_and_prune()

    def ping_all_and_prune(self):
        # Ping the whole room before we give up completely. This will be super-rare,
        # but we're about to prune everyone so okay to stall a little bit more.
        self._debug('beginning prune all')
        self.dont_prune_channel_names = set([self.parent.channel_name])
        self.ping_all_time = now()
        self.parent.notify_team({
            'type': 'hunt.team.room.ping',
            'sender': self.parent.channel_name,
            'reason': 'pingAll',
        })
        self.ping_all_timer = threading.Timer(
            PING_ALL_TIMEOUT_S, self.handle_ping_all_timeout)
        self.ping_all_timer.start()

    def hunt_team_room_ping(self, message):
        if self.join_status in (TeamRoomJoinStatus.Entered, TeamRoomJoinStatus.Participating):
            self._debug('received ping from', message['sender'], 'we are', self.join_status)
            self.parent.notify_consumer(message['sender'], {
                'type': 'hunt.team.room.pong',
                'sender': self.parent.channel_name,
                'reason': message['reason'],
            })

        # If multiple clients are running a pingAll check, defer to the one with
        # an earlier channel name. This prevents n^2 prunes needing to be handled
        # (the thundering herd problem).
        if message['reason'] == 'pingAll' and message['sender'] < self.parent.channel_name:
            self._debug('received pingAll from', message['sender'])
            if self.ping_all_timer:
                self._debug('cancelling my pingAll')
                self.ping_all_timer.cancel()
                self.ping_all_timer = None
            self.last_ping_all_received = now()

    def hunt_team_room_pong(self, message):
        self._debug('received pong from', message['sender'], message['reason'])
        if message['reason'] == 'ping_1' and self.ping_1_timer:
            self._debug('received pong from', message['sender'], 'entering')
            self.ping_1_timer.cancel()
            self.ping_1_timer = None
            self.enter()

        elif message['reason'] == 'pingAll' and self.ping_all_timer:
            self._debug('received pongAll from', message['sender'], 'not pruning')
            self.dont_prune_channel_names.add(message['sender'])

    def handle_ping_all_timeout(self):
        self.ping_all_timer = None

        # Prune everyone who didn't respond.
        self._debug('finished pingAll, pruning all except', len(self.dont_prune_channel_names))
        filters = {
            'scope': self.plugin_scope,
            'create_time__lte': self.ping_all_time,
            self.session_foreign_key_field: self.get_sibling_plugin('session').get(),
        }
        deleted, _ = (self.ModelClass.objects
            .filter(**filters)
            .exclude(channel_name__in=self.dont_prune_channel_names)
            .delete())
        self.dont_prune_channel_names = set()
        self.ping_all_time = None

        self._debug('pruning removed', deleted)
        if deleted:
            self.parent.notify_team({
                'type': 'hunt.team.room.pruned',
                'sender': self.parent.channel_name,
            })

    def hunt_team_room_pruned(self, message):
        self._debug('someone pruned room, refetching', message['sender'])
        self.clear_timers_if_needed()
        self.load_participants()

        if self.join_status == TeamRoomJoinStatus.New:
            self.enter()
        else:
            self.update_client()

    def schedule_liveness_check(self):
        if self.liveness_timer:
            return

        self.liveness_timer = threading.Timer(
            LIVENESS_PRUNE_INTERVAL_S, self.perform_liveness_check)
        self.liveness_timer.start()

    def perform_liveness_check(self):
        if self.join_status != TeamRoomJoinStatus.New and not self.ping_all_timer:
            # There's a failure mode where due to unclean disconnects, a channel
            # thinks they're in the group alone. They send pingAlls and get no
            # response so they nuke real channels that are in the group. So for
            # ping alls that aren't on first entry, re-join the group just in
            # case.
            self.parent.join_channel_layer_group()
            too_old = (
                not self.last_ping_all_received or
                (now() - self.last_ping_all_received) >
                    datetime.timedelta(seconds=LIVENESS_PRUNE_INTERVAL_S * 1.5))
            lowest_channel_name = self.in_memory_participants and min(self.in_memory_participants.keys(), default=None)
            if too_old or lowest_channel_name == self.parent.channel_name:
                self.ping_all_and_prune()

        self.liveness_timer = None
        self.schedule_liveness_check()

    def load_participants(self):
        filters = {
            'scope': self.plugin_scope,
            self.session_foreign_key_field: self.get_sibling_plugin('session').get(),
        }
        self.in_memory_participants = {
            p.channel_name: model_to_dict(p)
            for p in self.ModelClass.objects.filter(**filters)
        }
        self._debug('reloading participants', len(self.in_memory_participants))
        self.maybe_notify_scope_updated()

    def enter(self):
        self._debug('entered room')
        self.join_status = TeamRoomJoinStatus.Entered
        self.update_client()
        self.schedule_liveness_check()

    def update_client(self):
        # Skip refresh if the client is looking at some other scope.
        should_send_to_client = (not self.plugin_scope or
            self.get_sibling_plugin('state_list').scope == self.plugin_scope)
        if should_send_to_client:
            self._debug('sending update to client')
            self.parent.send_json({
                'type': 'room',
                'scope': self.plugin_scope,
                'participants': list(
                    {
                        **p,
                        'me': p['channel_name'] == self.parent.channel_name,
                    } for p in self.in_memory_participants.values()
                )
            })

    def received_json(self, message):
        if message.get('scope') != self.plugin_scope:
            return

        if message['type'] != 'room.join':
            return

        if self.join_status == TeamRoomJoinStatus.New:
            logger.warn(f'Ignoring message received before entering room {message}')
            return

        self._debug('received join message', message)
        filters = {
            'scope': self.plugin_scope,
            self.session_foreign_key_field: self.get_sibling_plugin('session').get(),
        }
        try:
            participant, _ = self.ModelClass.objects.update_or_create(
                channel_name=self.parent.channel_name, **filters,
                defaults=message.get('defaults'))
            self.participant_info = participant
            self.join_status = TeamRoomJoinStatus.Participating
            self.parent.dispatch_to_plugins('room_participant_changed', self.plugin_scope)
            self.parent.notify_team({
                'type': 'hunt.team.room.updated',
                'channel_name': participant.channel_name,
                'participant': model_to_dict(participant),
            })
        except IntegrityError:
            self.parent.send_json({
                'type': 'room.join.error',
            })

    def disconnected(self, was_authed, close_code):
        if not was_authed:
            return

        self._debug('disconnected, leaving room')
        self.clear_timers_if_needed()

        filters = {
            'channel_name': self.parent.channel_name,
            'scope': self.plugin_scope,
            self.session_foreign_key_field: self.get_sibling_plugin('session').get(),
        }
        self.ModelClass.objects.filter(**filters).delete()
        self.join_status = TeamRoomJoinStatus.New
        self.participant_info = None

        self.parent.notify_team({
            'type': 'hunt.team.room.left',
            'channel_name': self.parent.channel_name,
        })

    def hunt_team_room_updated(self, message):
        self._debug('someone updated the hunt room', message['participant']['channel_name'])
        self.in_memory_participants[message['channel_name']] = message['participant']
        self.update_client()

    def hunt_team_room_left(self, message):
        self._debug('someone left the hunt room', message['channel_name'])
        if message['channel_name'] in self.in_memory_participants:
            del self.in_memory_participants[message['channel_name']]
            self.update_client()

    def in_memory_scope_updated(self, scope):
        if self.plugin_scope == scope and self.join_status != TeamRoomJoinStatus.New:
            self.update_client()

    def maybe_notify_scope_updated(self):
        if self.plugin_scope:
            self.parent.dispatch_to_plugins('scope_updated', self.plugin_scope)

    def clear_timers_if_needed(self):
        if self.ping_1_timer:
            self.ping_1_timer.cancel()
            self.ping_1_timer = None
        if self.ping_all_timer:
            self.ping_all_timer.cancel()
            self.ping_all_timer = None
        if self.liveness_timer:
            self.liveness_timer.cancel()
            self.liveness_timer = None

    def _debug(self, *message):
        # print(self.parent.channel_name, *message)
        pass
