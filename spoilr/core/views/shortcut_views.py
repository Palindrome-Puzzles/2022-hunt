import urllib.parse

from django.shortcuts import redirect, reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from spoilr.core.api.shortcuts import Shortcuts
from spoilr.core.api.decorators import inject_team, require_safe_referrer
from spoilr.core.api.events import HuntEvent, dispatch
from spoilr.core.models import Puzzle

@require_POST
@xframe_options_sameorigin
@require_safe_referrer
@inject_team(require_admin=True)
def shortcuts_view(request):
    callback = getattr(Shortcuts, request.POST.get('action'))
    puzzle = Puzzle.objects.get(url=request.POST.get('puzzle'))
    callback(puzzle, request.team)

    dispatch(
        HuntEvent.HUNT_PUZZLE_SHORTCUT, team=request.team, puzzle=puzzle, object_id=puzzle.url,
        message=f'Used shortcut {request.POST.get("action")}')

    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url or reverse('index'))
