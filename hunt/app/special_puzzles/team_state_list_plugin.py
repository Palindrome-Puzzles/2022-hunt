import logging, time
from enum import Enum

from django.db import models, transaction
from django.forms.models import model_to_dict
from django.utils.timezone import now

from spoilr.core.models import Team

from hunt.app.core.plugins import Plugin

logger = logging.getLogger(__name__)

class TeamStateListPlugin(Plugin):
    """
    Plugin for a TeamConsumer that has a list of shared state instances for a
    team, and where each state instance should automatically be synchronized
    with all team members.

    This plugin is responsible for sending the list of state instances to the
    client, and selecting which state the client is viewing. It does this with a
    fixed list of scopes, from which the client can select.

    The client can send messages with the following `type`:
     - `state.scope.select`: Select a scope based on the nullable `scope` key
       in the message.

    The client will receive messages with the following `type`s:
     - `state.scopes`: List of all scopes with display info, or updates to a
       specific scope in the `state` key.
     - `state.scope`: The newly selected scope in the `scope` key.

    Users can subclass this and implement the `project_state` method to change
    what information is sent to the client. If you set `watch_state_changes=True`,
    then `project_state` will be called whenever any state changes, and if changed,
    will be synchronized to clients.
    """
    plugin_name = 'state_list'
    in_memory_state_list = None
    scope = None

    def __init__(self, scopes, *, watch_state_changes=False):
        # A fixed list of scopes for state. Each should be a short string.
        self.scopes = scopes
        # Whether we should re-project states as they change. This is useful when
        # the state list contains a live summary of the state.
        self.watch_state_changes = watch_state_changes

    def project_state(self, scope):
        """
        Returns the current state of the specified `scope` as it should be sent
        to the client.

        The implementation may use `self.get_scoped_plugin(scope).in_memory_state`
        and similar to access room data to assemble what should be sent.

        This must return a dict to be sent directly to the client. The dict must
        contain a key `scope` with the scope.
        """
        return {'scope': scope}

    def verify_plugin(self):
        self.parent.assert_has_plugin('session')

        assert len(self.scopes)
        for scope in self.scopes:
            self.parent.assert_has_plugin(f'state:{scope}')

    def is_scope_valid(self, scope):
        return scope in self.scopes

    def authenticate(self, team, auth_message):
        if 'scope' in auth_message and auth_message['scope']:
            assert self.is_scope_valid(auth_message['scope'])
            self.scope = auth_message['scope']

    def joined(self):
        # If we're focusing on a scope, no need to watch the scope list.
        if self.scope:
            return
        self.send_scope_list()

    def send_scope_list(self):
        self.in_memory_state_list = [self.project_state(scope) for scope in self.scopes]
        self.parent.send_json({
            'type': 'state.scopes',
            'state': self.in_memory_state_list,
        })

    def scope_updated(self, scope):
        if not self.watch_state_changes or not self.in_memory_state_list:
            return

        state = self.project_state(scope)
        matching_state = next(
            in_memory_state
            for in_memory_state in self.in_memory_state_list
            if in_memory_state.scope == state.scope)

        # Only bother sending the state update if it's actually changed.
        if state != matching_state:
            self.parent.send_json({
                'type': 'state.scopes',
                'state': state,
            })
            self.in_memory_state_list = [
                state if in_memory_state.scope == state.scope else in_memory_state
                for in_memory_state in self.in_memory_state_list
            ]

    def received_json(self, message):
        if message['type'] == 'state.scope.select':
            self.handle_select_scope(message)

    def handle_select_scope(self, message):
        assert not message['scope'] or self.is_scope_valid(message['scope'])
        self.scope = message['scope']

        self.parent.send_json({
            'type': 'state.scope',
            'scope': self.scope,
        })

        if self.scope:
            self.parent.dispatch_to_plugins('in_memory_scope_updated', self.scope)
        else:
            self.send_scope_list()

    def get_scoped_plugin(self, scope):
        return self.get_sibling_plugin(f'state:{scope}')
