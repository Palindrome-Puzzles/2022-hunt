import logging

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from spoilr.core.api.decorators import inject_team
from spoilr.core.api.answer import submit_puzzle_answer
from spoilr.core.api.hunt import release_interaction
from spoilr.core.models import Puzzle, Interaction

from hunt.app.core.constants import INTERACTION_MANUSCRIP
from hunt.app.core.rewards import get_manuscrip_info
from hunt.app.models import FreeUnlockRequest, FreeUnlockStatus
from hunt.deploy.util import require_hunt_launch, is_autopilot

from .common import verify_team_accessible

logger = logging.getLogger(__name__)

@require_POST
@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def spend_view(request):
    puzzle = get_object_or_404(Puzzle, url=request.POST.get('puzzle'))
    if not puzzle.puzzleaccess_set.filter(team=request.team, solved=False).exists():
        logger.warning(f'Tried to spend manuscrip on inaccessible or solved puzzle {request.team}: {puzzle}')
        return redirect(reverse('rewards_drawer'))

    manuscrip_info = get_manuscrip_info(request.team)
    if not manuscrip_info['can_unlock']:
        logger.warning(f'Tried to spend manuscrip when unavailable puzzle {request.team}: {puzzle}')
        return redirect(reverse('rewards_drawer'))

    unlock, _ = FreeUnlockRequest.objects.update_or_create(
        team=request.team, puzzle=puzzle, defaults={'status': FreeUnlockStatus.NEW})

    if is_autopilot():
        unlock.status = FreeUnlockStatus.APPROVED
        unlock.save()

        submit_puzzle_answer(request.team, puzzle, puzzle.answer)

    else:
        interaction = get_object_or_404(Interaction, url=INTERACTION_MANUSCRIP)
        release_interaction(request.team, interaction, reopen=True)

    return redirect(reverse('rewards_drawer'))
