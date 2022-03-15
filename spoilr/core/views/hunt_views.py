from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.core.api.decorators import inject_team
from spoilr.core.api.events import HuntEvent, dispatch

from spoilr.core.models import HuntSetting

@xframe_options_sameorigin
@inject_team(require_admin=True)
def tick_view(request):
    """
    Global tick view to advance hunt state.

    This view should be visited by HQ during the hunt regularly, so that puzzles
    and interactions that are time-based can proceed.
    """
    tick = now()

    tick_setting, _ = HuntSetting.objects.get_or_create(name='spoilr.last_tick')
    last_tick = tick_setting.date_value if tick_setting.date_value else None

    tick_setting.date_value = tick
    tick_setting.save()

    dispatch(HuntEvent.HUNT_TICK, message='Tick', tick=tick, last_tick=last_tick)

    return JsonResponse({'success': True, 'time': tick})
