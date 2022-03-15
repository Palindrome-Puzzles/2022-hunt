from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.generic.websocket import JsonWebsocketConsumer
from django.urls import reverse

from spoilr.core.models import HuntSetting, Team, TeamType
from hunt.deploy.util import is_it_hunt

from .team_consumer import TeamConsumer, HUNT_TEAM_BROADCAST_TYPE, get_channel_layer_group_name

TEAM_NOTIFICATIONS_GROUP_TYPE = 'notifications'

class TeamNotificationsConsumer(TeamConsumer):
    """Consumer for receiving notifications sent to the entire team."""
    @property
    def group_type(self):
        return TEAM_NOTIFICATIONS_GROUP_TYPE

def notify_team_log(team, event_type, message, theme=None, link=None, puzzle_url=None, sound_url=None, reward_info=None, bonus_content=None):
    """Callback for spoilr signal that the team's hunt status has changed."""
    should_team_receive_notification = (is_it_hunt() or team.is_internal) and not team.is_public
    if _are_notifications_enabled() and should_team_receive_notification:
        async_to_sync(get_channel_layer().group_send)(
            _get_group_name(team),
            {
                'type': HUNT_TEAM_BROADCAST_TYPE,
                'data': {
                    'special': theme,
                    'message': message,
                    'link': link,
                    'puzzleUrl': puzzle_url,
                    'soundUrl': sound_url,
                    'rewardInfo': reward_info,
                    'bonusContent': bonus_content,
                },
            })

def notify_hq_update(update):
    """Callback for spoilr signal that a new HQ update was published."""
    iih = is_it_hunt()
    if _are_notifications_enabled():
        for team in Team.objects.exclude(type=TeamType.PUBLIC):
            if iih or team.is_internal:
                async_to_sync(get_channel_layer().group_send)(
                    _get_group_name(team),
                    {
                        'type': HUNT_TEAM_BROADCAST_TYPE,
                        'data': {
                            'special': 'announcement',
                            'message': '<em>HQ Update</em> %s' % update.subject,
                            'link': reverse('updates'),
                        },
                    })

def notify_hunt_launched():
    """Callback for when the hunt is launched for a specific team."""
    if _are_notifications_enabled():
        for team in Team.objects.exclude(type=TeamType.PUBLIC):
            async_to_sync(get_channel_layer().group_send)(
                _get_group_name(team),
                {
                    'type': HUNT_TEAM_BROADCAST_TYPE,
                    'data': {
                        'special': 'announcement',
                        'message': 'MITMH2022 Available',
                        'link': reverse('index'),
                    },
                })

def _are_notifications_enabled():
    try:
        HuntSetting.objects.get(name='hunt.disable_notifications')
    except HuntSetting.DoesNotExist:
        return True

def _get_group_name(team):
    """Returns the name used by the channel layer for team notifications."""
    return get_channel_layer_group_name(team, TEAM_NOTIFICATIONS_GROUP_TYPE)

