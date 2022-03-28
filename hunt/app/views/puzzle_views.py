import logging, json, random

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, reverse, redirect
from django.template import Template, Context

from spoilr.core.models import PuzzleAccess
from spoilr.hints.models import HintSubmission

from hunt.app.core.assets.refs import get_round_static_path, get_puzzle_static_path
from hunt.app.core.constants import ROUND_RD0_URL, PUZZLE_ENDGAME_URL, SESSION_BOOK_DISCOVERED
from hunt.app.models import InteractionType
from hunt.data_loader.puzzle import get_puzzle_data_text
from hunt.data_loader.round import get_round_data_text
from hunt.deploy.util import require_rd0_launch

from hunt.app.core.assets.resolvers import create_puzzle_url_resolver, create_round_url_resolver
from hunt.app.core.assets.rewriter import rewrite_relative_paths
from .common import require_puzzle_access, get_puzzle_context, get_round_accesses, get_puzzle_accesses, puzzle_access_to_puzzle_obj, puzzle_to_puzzle_obj, should_show_solutions, use_noop_puzzle_submission, get_puzzle_variant, is_posthunt_enabled
from .responses import XHttpResponse

logger = logging.getLogger(__name__)

@require_puzzle_access(allow_rd0_access=True)
def puzzle_view(request):
    """View for a puzzle's content."""
    if request.puzzle.url == PUZZLE_ENDGAME_URL and not request.path.startswith(reverse('endgame_puzzle')):
        return redirect(reverse('endgame_puzzle'))

    maybe_team = request.team
    puzzle = request.puzzle
    noop_submission = use_noop_puzzle_submission(request)

    # Show posthunt version of puzzle if it exists and the hunt is complete.
    is_public_team = maybe_team and maybe_team.is_public
    variant = get_puzzle_variant(puzzle.url, is_public_team)
    posthunt_enabled = is_posthunt_enabled(puzzle.url, is_public_team)
    if variant == 'puzzle':
        html = get_puzzle_data_text(puzzle.url, 'index.html')
        style = get_puzzle_data_text(puzzle.url, 'style.css')
    else:
        html = get_puzzle_data_text(puzzle.url, 'posthunt', 'index.html')
        style = get_puzzle_data_text(puzzle.url, 'posthunt', 'style.css')

    common_style = get_round_data_text(puzzle.round.url, 'round_common.css')
    if html == None:
        return XHttpResponse('Unknown puzzle "%s"' % (puzzle.url))

    context = get_puzzle_context(maybe_team, puzzle)
    context['rd_root'] = get_round_static_path(puzzle.round.url, variant='round')

    context['hint_submission_exists'] = (
        not context['puzzle_info']['solved'] and
        HintSubmission.objects
            .filter(team=request.team, puzzle=request.puzzle)
            .exists())

    if puzzle.url == PUZZLE_ENDGAME_URL:
        context['is_book_discovery'] = request.session.get(SESSION_BOOK_DISCOVERED, False)
        if context['is_book_discovery']:
            del request.session[SESSION_BOOK_DISCOVERED]
            request.session.save()

    puzzle_url_resolver = create_puzzle_url_resolver(puzzle.url, variant, can_access_posthunt=posthunt_enabled)
    round_url_resolver = create_round_url_resolver(puzzle.round.url, 'round')

    context_obj = Context(context)
    context['no_puzzle_actions'] = noop_submission or puzzle.round.url == ROUND_RD0_URL or (request.team and request.team.is_public)
    context['posthunt_enabled'] = posthunt_enabled
    context['puzzle_html'] = rewrite_relative_paths(
        Template(html).render(context_obj), puzzle_url_resolver)
    context['puzzle_style'] = rewrite_relative_paths(
        Template(style).render(context_obj), puzzle_url_resolver) if style else None
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    return render(request, 'round_files/%s/puzzle.tmpl' % (puzzle.round.url), context)

@require_puzzle_access(allow_rd0_access=False)
def solution_view(request):
    """View for a puzzle's solution."""
    team = request.team
    puzzle = request.puzzle

    if not should_show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')

    html = get_puzzle_data_text(puzzle.url, 'solution', 'index.html')
    style = get_puzzle_data_text(puzzle.url, 'solution', 'style.css')
    common_style = get_round_data_text(puzzle.round.url, 'round_common.css')
    metadata = get_metadata(puzzle.url)
    if html == None or not metadata:
        return XHttpResponse('Unknown puzzle "%s"' % (puzzle.url))

    context = get_puzzle_context(team, puzzle)
    context['credits'] = [metadata['credits']]
    additional_authors = metadata.get('additional_authors','')
    if additional_authors:
      context['credits'].append(additional_authors)

    # Process other_credits (Art, Tech, etc.)
    TYPE_TO_STRING = {'ART': 'Art by', 'TCH': 'Tech by',
                      'OTH': 'Additional support:'}
    try:
      other_credits = metadata.get('other_credits', {})
      for type in TYPE_TO_STRING.keys():
        if type in other_credits:
          team_members, write_in = other_credits[type]
          if write_in:
            people = write_in
          else:
            people = team_members
          if people:
            context['credits'].append(f'{TYPE_TO_STRING[type]} {people}')
    except Exception as err:
      logger.error(f'Exception while processing `other_credits`: {err}')

    context['rd_root'] = get_round_static_path(puzzle.round.url, variant='round')

    puzzle_url_resolver = create_puzzle_url_resolver(puzzle.url, 'solution', can_access_posthunt=True)
    round_url_resolver = create_round_url_resolver(puzzle.round.url, 'round')

    context_obj = Context(context)
    context['puzzle_solution_html'] = rewrite_relative_paths(
        Template(html).render(context_obj), puzzle_url_resolver)
    context['puzzle_solution_style'] = rewrite_relative_paths(
        Template(style).render(context_obj), puzzle_url_resolver) if style else None
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    return render(request, 'round_files/%s/puzzle_solution.tmpl' % (puzzle.round.url), context)

@require_puzzle_access(allow_rd0_access=False)
def puzzle_subview(request, subview, variant, require_solved):
    maybe_team = request.team
    puzzle = request.puzzle

    if variant == 'posthunt' and not should_show_solutions(maybe_team):
        return HttpResponseNotFound('Not found')
    if variant == 'solution' and not should_show_solutions(maybe_team):
        return HttpResponseNotFound('Not found')
    if require_solved and not ((request.puzzle_access and request.puzzle_access.solved) or should_show_solutions(maybe_team)):
        return HttpResponseNotFound('Not found')

    is_public_team = maybe_team and maybe_team.is_public
    posthunt_enabled = is_posthunt_enabled(puzzle.url, is_public_team)

    common_style = get_round_data_text(puzzle.round.url, 'round_common.css')

    context = get_puzzle_context(maybe_team, puzzle)
    context['puzz_root'] = get_puzzle_static_path(puzzle.url, variant='puzzle')
    context['rd_root'] = get_round_static_path(puzzle.round.url, variant='round')
    context['posthunt_enabled'] = posthunt_enabled
    if variant == 'posthunt' or variant == 'solution':
        context['spuzz_root'] = get_puzzle_static_path(puzzle.url, variant='solution')

    round_url_resolver = create_round_url_resolver(puzzle.round.url, 'round')

    context_obj = Context(context)
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    path = ['puzzle_files', puzzle.url] + ([] if variant == 'puzzle' else [variant]) + [f'{subview}.tmpl']
    return render(request, '/'.join(path), context)

def get_metadata(puzzle_url):
    """Returns puzzle metadata."""
    metadata = get_puzzle_data_text(puzzle_url, 'metadata.json')
    if metadata:
        return json.loads(metadata)
    return None
