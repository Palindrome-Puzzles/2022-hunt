import logging, time
from enum import Enum

from django.db import models, transaction, DatabaseError, ProgrammingError
from django.forms.models import model_to_dict
from django.utils.timezone import now

from spoilr.core.models import Team

from hunt.app.core.plugins import Plugin

logger = logging.getLogger(__name__)

class LockStatus(str, Enum):
    Continue = 'continue'
    FutureUpdate = 'future-update'
    PastUpdate = 'past-update'
    Restarted = 'restarted'

class TeamStateModelBase(models.Model):
    """
    The partial base model for shared state instances in a team puzzle.

    It can optionally be scoped, which can be used for things like multiple save
    states in a game.

    When restarted, the state can be abandoned and a new one will be created for
    the next game.

    Note: this is generally used for data that should be shared, modified by,
    and synchronized across team member clients. Use `TeamSessionPlugin` to
    store backend-only data like who the leader is or whether the team has
    solved the puzzle.
    """
    scope = models.CharField(max_length=200, blank=True, null=True)
    seq = models.IntegerField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    abandoned_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = [
            ['scope', 'abandoned_time'],
        ]

class TeamStateClientAdaptor:
    """
    Adaptor for puzzle-specific state instance management behavior.

    It separates the concept of the state model, and an in-memory version of the
    state. This is so each consumer can keep track in a distributed way without
    hitting the database.
    """

    def state_defaults(self):
        """Returns default values for a new puzzle state model."""
        return {}

    def initialize_state(self, state):
        """Perform side-effects that should occur when the state is first created."""
        pass

    def prefetch_related(self):
        """
        Returns an optional list of args to pass to prefetch_related, when
        loading the puzzle state model.
        """
        return []

    def to_in_memory_state(self, state):
        """Converts the puzzle state model to an in-memory version."""
        return model_to_dict(state)

    def validate_updates(self, consumer, state, updates):
        """
        Verifies the consumer is allowed to perform this update. If not, the
        update is rejected.
        """
        return True

    def apply_updates(self, state, updates):
        """
        Transforms a state model by applying the update descriptor.

        The update descriptor is supplied by the client in a `state.update`
        message.

        It can return a (serializable) "server updates" descriptor that is passed
        to in_memory_updates so that you can track things like randomly
        generated values.
        """
        for key, value in updates.items():
            setattr(state, key, value)

    def apply_in_memory_updates(self, in_memory_state, updates, server_updates):
        """
        Transforms the in-memory state by applying the update descriptor.

        The update descriptor is supplied by the client in a `state.update`
        message. The server_updates descriptor is the result of applying
        `apply_updates`.

        Returns a boolean indicating whether the state was changed. If it was
        not changed, we can skip sending it to the client.
        """
        changed = False
        for key, value in updates.items():
            if in_memory_state.get(key) != value:
                changed = True
            in_memory_state[key] = value
        return changed

    def project_for_client(self, consumer, in_memory_state, updates=None):
        """
        Transforms the in-memory state into what should be sent to the client.

        `consumer` is a reference to the consumer, in case other state variables
        affect what gets projected (i.e. the user's role controls which subset
        of info they receive).

        `updates` is the update descriptor if we were applying partial updates,
        or None if this was a refresh. You can use this to reduce what fields are
        sent to the client.

        This must return a dict to be sent directly to the client.
        """
        return in_memory_state

class TeamStatePlugin(Plugin):
    """
    Plugin for a TeamConsumer that has shared state instance for a team, where
    the state instance should automatically be synchronized with all team members.

    The data can optionally be scoped. If it is, then the plugin only listens
    for updates to the shared state with the specified scope. (Consumers can
    listen for the list of scopes using `TeamStateScopesPlugin`.)

    The data can be abandoned when the game is restarted.

    Any shared state should be stored in a model that is a subclass of
    `TeamStateModelBase`. It should also have a foreign key reference to the
    model used for the team session in `TeamSessionPlugin`.

    The client can send messages with the following `type`:
     - `state.refresh`: Refetch all state for this client only.
     - `state.update`: Apply the update descriptor in the `updates` key to the
       state, and synchronize to all clients.
     - `state.abandon`: Abandon the current state, and create a new one to use
       instead, and synchronize to all clients. This has no effect if the state
       is already new, unless a `force` key has value `true`.

    If the client includes an `expectedSeq` key when performing state updates,
    it will perform optimistic locking to ensure data integrity.

    If the client includes a `scope` key, it will only affect that scoped
    instance.

    The client will receive messages with type 'state'. The message will also
    contain a `refresh` key, a `seq` key, a `scope` key, and a `state` key. The
    `state` key will contain the update as projected by the client adaptor.

    The client may also receive messages with type 'state.update.rollback'. The
    message will contain all fields in the original `state.update` message that
    is being rolled back (except the `type` being changed).

    When authenticating, if the auth message include a valid `scope` key, then
    joining will send the appropriately scoped state instance. Likewise, if data is
    unscoped, joining will send the state instance. (Otherwise, `TeamStateScopesPlugin`
    will send the list of scopes.)

    Puzzle-specific logic is part of the `client_adaptor` argument.
    """
    last_state_id = None
    last_seq = None
    in_memory_state = None

    def __init__(self, ModelClass, *, session_foreign_key_field, client_adaptor, plugin_scope=None):
        super().__init__()

        assert issubclass(ModelClass, TeamStateModelBase)
        assert isinstance(client_adaptor, TeamStateClientAdaptor)

        self.ModelClass = ModelClass
        self.session_foreign_key_field = session_foreign_key_field
        self.client_adaptor = client_adaptor
        self.plugin_scope = plugin_scope

    @property
    def plugin_name(self):
        return f'state:{self.plugin_scope}' if self.plugin_scope else 'state'

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
        self.refresh_client()

    def should_send_to_client(self):
        return (not self.plugin_scope or
            self.get_sibling_plugin('state_list').scope == self.plugin_scope)

    def received_json(self, message):
        if message.get('scope') != self.plugin_scope:
            return
        if not self.in_memory_state:
            logger.warn(f'Ignoring message received before initializing state {message}')
            return

        if message['type'] == 'state.refresh':
            self.refresh_client()
        elif message['type'] == 'state.update':
            try:
                self.handle_update(message)
            except DatabaseError as e:
                logger.exception('Database error while updating state')
                self.parent.send_json({
                    **message,
                    'type': 'state.update.rollback',
                })
        elif message['type'] == 'state.abandon':
            self.handle_abandon(message)

    def handle_update(self, message):
        updates = message['updates']

        proceed = False
        committed = False
        original_seq = None
        with transaction.atomic():
            state = self.get_or_create_latest_state()
            lock_status = check_lock_status(state_id=state.id, seq=state.seq, update_state_id=self.last_state_id, update_seq=message.get('expectedSeq'))

            proceed = lock_status == LockStatus.Continue
            if proceed:
                original_seq = state.seq
                if not self.client_adaptor.validate_updates(self.parent, state, updates):
                    logger.error(
                        f'Tried to send an invalid update, should not happen: {state} {updates}')
                    raise ProgrammingError('Attempted to commit a logically invalid update')
                server_updates = self.client_adaptor.apply_updates(state, updates)
                state.seq += 1
                state.save()
                committed = True

            # Note: we could raise an error to trigger a rollback, but no
            # need. The only side-effect was maybe creating an initial state,
            # so no big deal.
            if lock_status == LockStatus.FutureUpdate:
                logger.error(
                    f'Tried to send an update with a future seq, should not happen: {lock_status} {message}')
            elif lock_status in (LockStatus.PastUpdate, LockStatus.Restarted):
                logger.warn(
                    f'Received an update for stale data, silently ignoring {message}')

        if committed:
            self.parent.notify_team({
                'type': 'hunt.team.state.updated',
                'updates': updates,
                'server_updates': server_updates,
                # Send old sequence so each consumer can replay the sequence
                # increment on their in-memory state.
                'seq': original_seq,
                'state_id': state.id,
            })
        elif proceed:
            logger.error(f'Commit unexpectedly failed: {message}')

    def handle_abandon(self, message):
        proceed = False
        committed = False
        with transaction.atomic():
            state = self.get_or_create_latest_state()
            # Dont both abandoning if this is new, unless the client forces it.
            proceed = state.seq > 0 or message.get('force') == True
            if proceed:
                state.abandoned_time = now()
                state.save()

                # Recreate state to avoid consumers racing to do so.
                _ = self.get_or_create_latest_state()
                committed = True

        if committed:
            self.parent.notify_team({
                'type': 'hunt.team.state.refreshed',
            })
        elif proceed:
            logger.error(f'Commit unexpectedly failed: {message}')

    def refresh_client(self):
        state = self.get_or_create_latest_state()

        self.in_memory_state = self.client_adaptor.to_in_memory_state(state)
        self.last_state_id = state.id
        self.last_seq = state.seq
        self.maybe_notify_scope_updated()

        # Skip refresh if the client is looking at some other scope.
        if self.should_send_to_client():
            self.parent.send_json({
                'type': 'state',
                'refresh': True,
                'seq': state.seq,
                'scope': state.scope,
                'state': self.client_adaptor.project_for_client(self.parent, self.in_memory_state),
            })

    def hunt_team_state_updated(self, event):
        if not self.in_memory_state:
            logger.warn(f'Ignoring updated event received before initializing state {event}')
            return

        updates = event['updates']
        server_updates = event['server_updates']
        seq = event['seq']
        state_id = event['state_id']

        lock_status = check_lock_status(state_id=self.last_state_id, seq=self.last_seq, update_state_id=state_id, update_seq=seq)
        if lock_status == LockStatus.Continue:
            was_updated = self.client_adaptor.apply_in_memory_updates(self.in_memory_state, updates, server_updates)
            assert was_updated != None, 'Make sure apply_updates returns a boolean indicating if there were changes'
            self.last_seq = seq + 1

            if was_updated:
                self.maybe_notify_scope_updated()
                # Skip update if the client is looking at some other scope.
                if self.should_send_to_client():
                    self.parent.send_json({
                        'type': 'state',
                        'refresh': False,
                        'seq': self.last_seq,
                        'scope': self.plugin_scope,
                        'state': self.client_adaptor.project_for_client(
                            self.parent, self.in_memory_state, updates),
                    })
        elif lock_status in (LockStatus.FutureUpdate, LockStatus.Restarted):
            self.refresh_client()
        else:
            logger.warn(
                f'We received an update that has already been processed: {lock_status}. '
                f'This can occur when messages are out of order and so we '
                f'processed a later update by refreshing {event}')

    def hunt_team_state_refreshed(self, event):
        self.refresh_client()

    def get_or_create_latest_state(self):
        session = self.get_sibling_plugin('session').get()
        defaults = {
            'seq': 0,
            **self.client_adaptor.state_defaults(),
        }
        session_kwarg = {
            self.session_foreign_key_field: session
        }
        model, created = (self.ModelClass.objects
            .prefetch_related(*self.client_adaptor.prefetch_related())
            .get_or_create(
                scope=self.plugin_scope,
                abandoned_time=None,
                **session_kwarg,
                defaults=defaults))
        if created:
            self.client_adaptor.initialize_state(model)
        return model

    def in_memory_scope_updated(self, scope):
        if self.plugin_scope == scope:
            self.refresh_client()

    def maybe_notify_scope_updated(self):
        if self.plugin_scope:
            self.parent.dispatch_to_plugins('scope_updated', self.plugin_scope)

def check_lock_status(*, state_id, seq, update_seq, update_state_id):
    if state_id != update_state_id:
        return LockStatus.Restarted

    if update_seq == None or update_seq == seq:
        return LockStatus.Continue

    if update_seq < seq:
        # Can happen if due to out-of-order messages, we process a future
        # update by refreshing.
        return LockStatus.PastUpdate

    # Can happen if our in memory state is stale.
    return LockStatus.FutureUpdate
