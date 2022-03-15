import datetime

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template import Template, Context
from django.utils.timezone import now

from spoilr.core.api.cache import memoized_cache
from spoilr.core.api.events import dispatch, HuntEvent
from spoilr.hints.models import HintSubmission
from spoilr.core.models import PuzzleAccess, HuntSetting

from hunt.app.core.assets.resolvers import create_round_url_resolver
from hunt.app.core.assets.rewriter import rewrite_relative_paths
from hunt.app.core.constants import ROUND_RD0_URL
from hunt.data_loader.round import get_round_data_text
from hunt.deploy.util import is_it_hunt, are_hunt_hints_released, is_hunt_complete

from .common import should_show_solutions, require_puzzle_access, get_puzzle_context, xframe_sameorigin_if_post

@require_puzzle_access(allow_rd0_access=False, require_access=True, skip_cache=True)
@xframe_sameorigin_if_post
def hints_view(request, embed):
    hints_unlocked = are_hints_available_for_puzzle(request.puzzle)
    time_left = None
    at_quota = False
    if hints_unlocked:
        time_left, at_quota = are_hints_available_for_team(request.team, request.puzzle, request.puzzle_access)

    hints_available = hints_unlocked and not time_left and not at_quota

    if request.method == 'POST':
        if not hints_available:
            return redirect(request.get_full_path())
        return hints_post_view(request, request.team, request.puzzle)

    round_url_resolver = create_round_url_resolver(request.puzzle.round.url, 'round')
    common_style = get_round_data_text(request.puzzle.round.url, 'round_common.css')

    hints = HintSubmission.objects.filter(team=request.team, puzzle=request.puzzle)
    context = get_puzzle_context(request.team, request.puzzle)
    context['hints'] = hints
    context['solved'] = request.puzzle_access.solved
    context['email'] = request.team.team_email
    context['hints_available'] = hints_available
    context['time_left'] = time_left
    context['at_quota'] = at_quota

    context_obj = Context(context)
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    return render(request, 'puzzle/hints_embed.tmpl' if embed else 'puzzle/hints.tmpl', context)

def hints_post_view(request, team, puzzle):
    assert not is_hunt_complete(), 'Can no longer submit hint requests'

    question = request.POST['question'].strip()
    email = request.POST['email']

    if len(question):
        hint, created = (HintSubmission.objects
            .update_or_create(team=team, puzzle=puzzle, question__iexact=question, defaults={
                'question': question,
                'email': email,
            }))
        if created:
            dispatch(
                HuntEvent.HINT_REQUESTED, team=team, puzzle=puzzle, hint=hint, object_id=puzzle.url,
                message=f'{team.name} asked “{question}” about {puzzle}')
    return redirect(request.get_full_path())

def are_hints_available_for_puzzle(puzzle):
    if not is_it_hunt():
        return False
    if puzzle.round.url == ROUND_RD0_URL:
        return False
    if are_hunt_hints_released() or puzzle.puzzledata.hints_force_released:
        return True
    return puzzle.puzzledata.hints_release_delay != None

def are_hints_available_for_team(team, puzzle, puzzle_access):
    at_quota = False
    time_left = None
    solved_puzzle_ids = PuzzleAccess.objects.filter(team=team, solved=True).values_list('puzzle_id', flat=True)
    open_hints_count = HintSubmission.objects.filter(team=team, resolved_time__isnull=True).exclude(puzzle__in=solved_puzzle_ids).count()
    quota = settings.HUNT_OPEN_HINTS_EXPANDED_QUOTA if are_hunt_hints_released() else settings.HUNT_OPEN_HINTS_QUOTA
    if open_hints_count >= quota:
        at_quota = True

    if not are_hunt_hints_released():
        available_time = now() - puzzle_access.timestamp
        if puzzle.puzzledata.hints_release_delay and puzzle.puzzledata.hints_release_delay > available_time:
            time_left = puzzle.puzzledata.hints_release_delay - available_time
    return time_left, at_quota
