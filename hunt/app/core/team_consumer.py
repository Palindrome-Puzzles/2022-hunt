from abc import ABC, abstractmethod
import json, logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from spoilr.core.models import Team

from .plugins import MixinPlugins

logger = logging.getLogger(__name__)

# The 'type' field within a message sent from a WebSocket client when trying to
# authenticate.
AUTH_MESSAGE_TYPE = 'AUTH'

# The 'type' field within a message sent from the channel layer to indicate
# broadcasting the message data to all authenticated WebSocket clients.
HUNT_TEAM_BROADCAST_TYPE = 'hunt.team.broadcast'

def get_channel_layer_group_name(team, group_type):
    """Returns the channel layer group name to use for a specific team and group type."""
    return f'hunt.{group_type}.{team.id}'

class TeamConsumer(MixinPlugins, ABC, JsonWebsocketConsumer):
    """
    Basic consumer that authenticates that the user has access to a team before
    receiving messages intended for the team, or being allowed to send messages
    to the team.

    All messages sent and received must be valid JSON.

    *Important*: Each subclass must implement a `group_type` property. This is
    accessed after authentication, and is used to determine the group type under
    which to group messages. For example, for a teamwork puzzle, it should be
    deterministic and contain some puzzle ID so that all team members viewing
    the puzzle join the same group type.

    Subclasses can add strategy plugins. Plugins can optionally expose the
    following methods to hook into certain behaviour:
     - `authenticate`: Perform further authentication before being allowed to
       join the team room. If unauthenticated, the method should raise an exception.
       Arguments: the `team` and the raw `auth_message`.
     - `joined`: Handler for when the user has successfully joined themself to the
        team's group.
     - `disconnected`: Handler for when the user disconnected from the team's group.
       Arguments: a boolean was_authed, and the socket close code.
     - `received_json`: Handler for when a message was received from an authenticated user.
       Arguments: the raw message from the client.

    They can also handle hooks from other plugins.

    They can also handle messages from other consumers by adding the appropriate
    method. This will only work if the notification is prefixed with
    'hunt.team.'.

    If creating a model to store data, use `self.team` as a foreign key, and
    use that to query for the model. `self.team` will be initialized before
    `joined`, `disconnected`, or `received_json` is called.

    *Warning*: Every user session gets a short-lived instance of this object in
    the backend server to manage WebSocket sutff. It should be assumed to die
    shortly after the user disconnects, and any internal state is only available
    to that one user session. Any important stuff should be persisted to the
    database.
    """

    def __init__(self):
        super().__init__()

        # The team that this consumer is connected to, or None if the user is
        # not connected or not authenticated yet.
        self.team = None

        # The channel layer group name this consumer is connected to, or None if
        # the user is not connected, authenticated or joined yet.
        self.group_name = None

    def __getattr__(self, name):
        # Dispatch messages from other consumers to the plugin that it is
        # intended for.
        if name.startswith('hunt_team_'):
            def proxy(*args, **kwargs):
                for plugin in self.plugins.values():
                    if hasattr(plugin, name) and callable(getattr(plugin, name)):
                        getattr(plugin, name)(*args, **kwargs)
            return proxy
        raise AttributeError()

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
            self.dispatch_to_plugins('disconnected', was_authed=True, close_code=close_code)
        else:
            self.dispatch_to_plugins('disconnected', was_authed=False, close_code=close_code)

    def receive_json(self, content):
        action = content['type']
        # Intercept AUTH messages, and join the group if possible.
        if action == AUTH_MESSAGE_TYPE:
            # Ensure the team is authenticated.
            team = authenticate_team(content)
            self.dispatch_to_plugins('authenticate', team, content)

            if not team.is_internal and not team.is_public and not settings.HUNT_LOGIN_ALLOWED:
                raise Exception(
                    f'Someone has attempted to authenticate when hunt login is, '
                    f'disabled -- nothing happened for consumer {self.__class__.__name__} '
                    f'and team {team}')

            # TODO(sahil): We can't disable this unless we find another solution for puzzles
            # like the endgame.
            # if team.is_public:
            #     logger.info(
            #         f'Someone has attempted to authenticate as public user for '
            #         f'{self.__class__.__name__} -- nothing happened')
            #     return

            self.team = team

            # Join the session for the team.
            self.join_channel_layer_group()

            self.dispatch_to_plugins('joined')
        elif self.group_name:
            try:
                self.dispatch_to_plugins('received_json', content)
            except:
                self.send_json({'type': 'error'})
                raise
        else:
            logger.info(
                f'Someone has attempted to send to group consumer '
                f'{self.__class__.__name__} without authenticating')

    def join_channel_layer_group(self):
        group_name = get_channel_layer_group_name(self.team, self.group_type)
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)
        self.group_name = group_name

    def notify_team_clients(self, data):
        """
        Helper to broadcast to every authenticated user's client in the group.

        *Warning*: This data is sent to every other authenticated team member
        without any processing. In particular, if this contains content that is
        shown in the document, escape it to avoid XSS!
        """
        self.notify_team({
            'type': HUNT_TEAM_BROADCAST_TYPE,
            'data': data,
        })

    def notify_team(self, message):
        """
        Helper to broadcast to every authenticated user's consumer in the group.

        *Warning*: This data is sent to every other authenticated team member
        without any processing. In particular, if this contains content that is
        shown in the document, escape it to avoid XSS!
        """
        assert message['type'].startswith('hunt.team.')

        if self.group_name:
            async_to_sync(self.channel_layer.group_send)(self.group_name, message)
        else:
            logger.info(
                f'Someone has attempted to broadcast to group consumers '
                f'{self.__class__.__name__} without authenticating')
            raise AccessDeniedException()

    def notify_consumer(self, target_channel_name, message):
        """Helper to broadcast to a specific consumer by channel name."""
        async_to_sync(self.channel_layer.send)(target_channel_name, message)

    def hunt_team_broadcast(self, event):
        """Handler for the channel layer message with type `HUNT_TEAM_BROADCAST_TYPE`."""
        self.send_json(event['data'])

    @property
    @abstractmethod
    def group_type(self):
        """
        Accesses the group type for the team's messages and this consumer.

        The group type should be at most 100 characters. It should only contain
        letters, numbers, hyphens, or periods.

        Will only be called after authentication.
        """
        pass

class AccessDeniedException(Exception):
    pass

def authenticate_team(auth_message):
    """
    Helper to authenticate a team given the client-sent auth message, that returns
    the team if authenticated, or raises otherwise.
    """
    try:
        return Team.objects.get(teamdata__auth=auth_message['data'])

    except Team.DoesNotExist as e:
        logger.info(
            f'Someone has attempted to access teamwork puzzle '
            f'with invalid token {auth_message["data"]}.')
        raise

    except Exception as e:
        logger.warn(
            f'Auth data {json.dumps(auth_message)} resulted in unexpected error {str(e)}.')
        raise
