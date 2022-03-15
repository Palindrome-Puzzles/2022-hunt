from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from spoilr.core.models import Team
from spoilr.hq.util.decorators import hq

@hq()
def nuke_cache_view(request):
    from hunt.app.core.cache import nuke_cache
    nuke_cache()
    return HttpResponse('OK')

@hq()
def unlock_puzzles_view(request):
    from hunt.app.core.puzzles import unlock_available_puzzles
    from hunt.app.core.cache import nuke_cache
    team = None
    if request.GET.get('team'):
        team = get_object_or_404(Team, username=request.GET.get('team'))
    unlock_available_puzzles(team)
    nuke_cache()
    return HttpResponse('OK')
