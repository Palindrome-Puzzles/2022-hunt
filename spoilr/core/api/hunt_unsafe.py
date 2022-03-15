"""
Business logic for unsafe operations on the hunt state.

*Warning*: This module should only be called by commands, or by admin team members.
"""

from django.conf import settings
from django.core.cache import caches

from spoilr.core.models import HuntSetting, SystemLog, PuzzleAccess, RoundAccess, InteractionAccess, PuzzleSubmission
from spoilr.hints.models import HintSubmission

from .events import dispatch, HuntEvent

def reset_hunt_activity():
    """Resets the hunt and clears all team activity."""
    HuntSetting.objects.filter(name__startswith='spoilr.').delete()
    caches[settings.SPOILR_CACHE_NAME].clear()

    PuzzleAccess.objects.all().delete()
    RoundAccess.objects.all().delete()
    InteractionAccess.objects.all().delete()

    PuzzleSubmission.objects.all().delete()
    HintSubmission.objects.all().delete()

    dispatch(HuntEvent.HUNT_ACTIVITY_RESET, message=f'Reset hunt activity')

def reset_hunt_log():
    """Resets the hunt system log."""
    SystemLog.objects.all().delete()
