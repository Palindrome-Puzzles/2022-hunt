from django.conf import settings
from django.shortcuts import render

from hunt.app.core.cache import cache_page_by_team, TEAMS_LIST_CATEGORY
from hunt.app.core.constants import PUZZLE_THIS_IS_NOW_A_PUZZLE_ID
from hunt.deploy.util import require_registration_launch, HUNT_RD0_RELEASED_REF, is_hunt_complete

from spoilr.core.api.decorators import inject_team
from spoilr.core.api.hunt import is_site_launched
from spoilr.core.models import PuzzleAccess, Team

@require_registration_launch
@inject_team(redirect_if_missing=False)
@cache_page_by_team(page_category=TEAMS_LIST_CATEGORY)
def index_view(request):
    teams = (Team.objects
        .filter(type__isnull=True)
        .prefetch_related('teamregistrationinfo')
        .order_by('name'))

    has_this_is_now_a_puzzle_access = False
    if request.team:
        has_this_is_now_a_puzzle_access = (
            PuzzleAccess.objects
                .filter(team=request.team, puzzle__external_id=PUZZLE_THIS_IS_NOW_A_PUZZLE_ID)
                .exists())

    return render(request, 'registration/index.tmpl',
        {
            'teams': teams,
            'status': request.GET.get('status'),
            'rd0_released': is_site_launched(HUNT_RD0_RELEASED_REF),
            'static_url': settings.STATIC_URL,
            'has_this_is_now_a_puzzle_access': has_this_is_now_a_puzzle_access,
            'is_hunt_complete': is_hunt_complete(),
            'is_public': request.team and request.team.is_public,
            'is_archive': settings.HUNT_ARCHIVE_MODE,
        })
