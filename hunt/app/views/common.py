import datetime, functools, random

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import reverse, redirect
from django.template import Context
from django.utils.http import urlencode
from django.utils.timezone import now

from spoilr.core.api.decorators import inject_team, inject_round, inject_puzzle, get_inaccessible_puzzle_response, get_inaccessible_round_response
from spoilr.core.api.shortcuts import get_shortcuts
from spoilr.core.models import InteractionAccess, Puzzle

from hunt.app.core.assets.refs import get_puzzle_static_path
from hunt.app.core.constants import ROUND_RD0_URL, ROUND_ENDGAME_URL, PUZZLE_ENDGAME_URL, ROUND_EVENTS_URL, ROUND_SAMPLE_URL, SITE_1_ROUND_URLS, ROUND_RD2_URL, ROUND_RD3_URLS, ROUND_RD1_URL, ROUND_RD3_META_URL, USE_POSTHUNT_ON_HUNT_COMPLETE, USE_POSTHUNT_ON_PUBLIC_AND_HUNT_COMPLETE
from hunt.app.core.cache import cache_page_by_puzzle, cache_shared_context, cache_page_by_round
from hunt.app.core.hosts import use_site_1, use_site_2_if_unlocked
from hunt.app.core.rewards import get_reward
from hunt.data_loader.puzzle import get_puzzle_data_text
from hunt.deploy.util import require_rd0_launch, require_hunt_launch, is_it_hunt, is_autopilot, is_hunt_complete

NOOP_DECORATOR = lambda view_func: view_func

def require_puzzle_access(allow_rd0_access, skip_cache=False, require_access=False, any_host=False, require_admin=False):
    def decorator(view_func):
        cache_decorator = NOOP_DECORATOR if skip_cache else cache_page_by_puzzle

        @require_rd0_launch
        @inject_team(redirect_if_missing=require_access or require_admin, require_admin=require_admin)
        @verify_team_accessible()
        @inject_puzzle(error_if_inaccessible=False)
        @cache_decorator
        def wrapped(request, *args, **kwargs):
            # Because of the prologue, we need special rules for checking puzzle
            # access.
            # Note: we may create puzzle and round access entities before launching
            # the hunt, so that teams are ready to go as soon as hunt starts.
            has_access = (
                (request.puzzle_access and is_it_hunt()) or
                (request.user.is_staff and not request.impersonating and not require_access) or
                (allow_rd0_access and request.puzzle.round.url == ROUND_RD0_URL))

            inaccessible_to_locked_teams = request.puzzle.round.url != ROUND_RD0_URL
            if has_access and inaccessible_to_locked_teams and request.team and request.team.teamdata.missing_documents:
                return redirect(reverse('missing_documents'))

            should_use_site_1 = request.puzzle.round.url in SITE_1_ROUND_URLS
            decorator = NOOP_DECORATOR
            if not any_host:
                decorator = use_site_1 if should_use_site_1 else use_site_2_if_unlocked

            if has_access:
                return decorator(view_func)(request, *args, **kwargs)
            elif not request.team:
                return redirect_to_login(request.get_full_path())
            else:
                return get_inaccessible_puzzle_response(request.puzzle.url)
        return wrapped
    return decorator

def require_round_access(skip_cache=False, any_host=False):
    def decorator(view_func):
        cache_decorator = NOOP_DECORATOR if skip_cache else cache_page_by_round

        @require_hunt_launch()
        @inject_team()
        @verify_team_accessible()
        @inject_round()
        @cache_decorator
        def wrapped(request, *args, **kwargs):
            inaccessible_to_locked_teams = request.round.url != ROUND_RD0_URL
            if inaccessible_to_locked_teams and request.team and request.team.teamdata.missing_documents:
                return redirect(reverse('missing_documents'))

            should_use_site_1 = request.round.url in SITE_1_ROUND_URLS
            decorator = NOOP_DECORATOR
            if not any_host:
                decorator = use_site_1 if should_use_site_1 else use_site_2_if_unlocked
            return decorator(view_func)(request, *args, **kwargs)
        return wrapped
    return decorator

def verify_team_accessible():
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            team = getattr(request, 'team', None)
            impersonating = getattr(request, 'impersonating', False)
            if team and not impersonating and not (team.is_internal or team.is_public) and not settings.HUNT_LOGIN_ALLOWED:
                next_url = request.build_absolute_uri()
                logout_url = reverse('logout') + '?' + urlencode({'next': next_url})
                return redirect(logout_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def xframe_sameorigin_if_post(view_func):
    def wrapped(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if request.method == 'POST' and response.get('X-Frame-Options') is None:
            response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    return functools.wraps(view_func)(wrapped)

def use_noop_puzzle_submission(request):
    """
    Whether a request for a view that is guarded by `require_puzzle_access(..)`
    should use noop submissions.

    This will only ever return `True` if the view was guarded by
    `require_puzzle_access(allow_rd0_access=True)`, as otherwise, both `team`
    and `puzzle_access` will be populated.
    """
    return not request.team or not request.puzzle_access or request.team.is_public

def should_show_solutions(maybe_team):
    """Whether to show solutions to the specified team."""
    return (maybe_team and maybe_team.is_admin) or is_hunt_complete()

@cache_shared_context
def get_shared_context(maybe_team):
    status = (
        'complete' if is_hunt_complete()
        else 'launch' if is_it_hunt()
        else 'prelaunch')

    available_interactions = []
    completed_interactions = []
    if maybe_team:
        available_interactions = InteractionAccess.objects.filter(
            team=maybe_team, accomplished=False)
        completed_interactions = InteractionAccess.objects.filter(
            team=maybe_team, accomplished=True)

    rounds = get_rounds_summary(maybe_team)
    is_endgame_unlocked = any(round_info['round'].url == ROUND_ENDGAME_URL for round_info in rounds)
    endgame_books_discovered = set()
    if maybe_team and is_endgame_unlocked:
        from hunt.app.special_puzzles.team_progress_plugin import get_team_puzzle_progress
        from hunt.data.special_puzzles.puzzle555_completing_the_story.progress import P555CTSProgressModel

        endgame_round = next(round_info for round_info in rounds if round_info['round'].url == ROUND_ENDGAME_URL)
        endgame_puzzle_info = next(iter(endgame_round['puzzles']), None)
        if endgame_puzzle_info:
            progress = get_team_puzzle_progress(P555CTSProgressModel, maybe_team, endgame_puzzle_info['puzzle'])
            endgame_books_discovered |= set(book.book for book in progress.books.all())

    acts_unlocked = {
        'act2': any(round['round'].url == ROUND_RD2_URL for round in rounds),
        'act3': any(round['round'].url == ROUND_RD3_URLS[0] for round in rounds),
        'act3_rounds': [round_info['round'] for round_info in rounds if round_info['round'].url in ROUND_RD3_URLS],
        'plot_device': any(round['round'].url == ROUND_RD3_META_URL for round in rounds),
        'act4': any(round['round'].url == ROUND_ENDGAME_URL for round in rounds),
    }

    return {
        'status': status,
        'acts_unlocked': acts_unlocked,
        'act': None,
        'team': maybe_team,
        'show_solutions': should_show_solutions(maybe_team),
        'rounds': rounds,
        'auth': maybe_team.teamdata.auth if maybe_team else '',
        'available_interactions': available_interactions,
        'completed_interactions': completed_interactions,
        'endgame_available': is_endgame_unlocked,
        'endgame_books_discovered': endgame_books_discovered,
        'is_autopilot': is_autopilot(),
        'is_login_allowed': settings.HUNT_LOGIN_ALLOWED,
        'has_posthunt_team_banner': status == 'complete' and maybe_team and not maybe_team.is_public,
        'shortcuts': get_shortcuts(),
    }

def get_puzzle_context(maybe_team, puzzle):
    context = get_shared_context(maybe_team)

    puzzle_access = (
        get_puzzle_accesses(maybe_team).filter(puzzle=puzzle).first()
        if maybe_team else None)
    context['puzzle_info'] = (
        puzzle_access_to_puzzle_obj(puzzle_access) if puzzle_access
        else puzzle_to_puzzle_obj(puzzle))
    context['round_info'] = get_round_summary(maybe_team, puzzle.round)
    context['round_reward'] = get_reward(context['round_info'])
    context['is_breakglass_access'] = not (puzzle_access and is_it_hunt()) and puzzle.round.url != ROUND_RD0_URL
    context['act'] = get_act_for_round(puzzle.round)

    return context

def get_rounds_summary(maybe_team):
    """Collates rounds and puzzles accessible to the team for templates."""
    if not maybe_team:
        return []

    puzzle_accesses = get_puzzle_accesses(maybe_team).order_by('puzzle__order')
    puzzle_objs = list(map(puzzle_access_to_puzzle_obj, puzzle_accesses))

    round_accesses = get_round_accesses(maybe_team).exclude(round__url__in=(ROUND_SAMPLE_URL, ROUND_EVENTS_URL)).order_by('round__order')
    round_objs = list(map(
        lambda round_access: to_round_obj(round_access.round, puzzle_objs),
        round_accesses))
    return round_objs

def get_round_summary(maybe_team, round, breakglass_access=None):
    """Collate round info and puzzles accessible to the team for the specified round for templates."""
    if breakglass_access:
        # Get the first N unlocked puzzles, and put special puzzles (no unlock order)
        # at the end. Then sort by presentation order.
        puzzles = list(
            Puzzle.objects
                .filter(round=round, is_meta=False, puzzledata__unlock_order__isnull=False)
                .order_by('puzzledata__unlock_order')[:breakglass_access['puzzle_count']])
        if len(puzzles) < breakglass_access['puzzle_count']:
            remaining = breakglass_access['puzzle_count'] - len(puzzles)
            puzzles.extend(
                Puzzle.objects
                    .filter(round=round, is_meta=False, puzzledata__unlock_order__isnull=True)
                    .order_by('puzzledata__unlock_order')[:remaining])
        puzzles.sort(key=lambda puzzle: puzzle.order)

        puzzles.extend(
            Puzzle.objects
                .filter(round=round, is_meta=True)
                .order_by('order')[:breakglass_access['meta_count']])
        puzzle_objs = list(map(puzzle_to_puzzle_obj, puzzles))
        if breakglass_access['solved']:
            for puzzle_obj in puzzle_objs:
                puzzle_obj['solved'] = True
                puzzle_obj['solved_time'] = now()
    else:
        if maybe_team:
            puzzle_accesses = (get_puzzle_accesses(maybe_team)
                .filter(puzzle__round=round)
                .order_by('puzzle__order'))
        else:
            puzzle_accesses = []
        puzzle_objs = list(map(puzzle_access_to_puzzle_obj, puzzle_accesses))

    return to_round_obj(round, puzzle_objs)

def get_puzzle_accesses(team):
    """Returns the list of puzzles accessible to the team, with useful data filled in."""
    return team.puzzleaccess_set.select_related('team', 'puzzle', 'team__teamdata', 'puzzle__puzzledata')

def get_round_accesses(team):
    """Returns the list of rounds accessible to the team, with useful data filled in."""
    return team.roundaccess_set.select_related('team', 'round', 'round__rounddata')

def puzzle_access_to_puzzle_obj(puzzle_access):
    """Transforms a puzzle access model to a dictionary for templates."""
    return {
        'puzzle': puzzle_access.puzzle,
        'full_path': reverse('puzzle_view', args=(puzzle_access.puzzle.url,)),
        'unlock_time': puzzle_access.timestamp,
        'solved': puzzle_access.solved,
        'solved_time': puzzle_access.solved_time,
        'static_directory': get_puzzle_static_path(puzzle_access.puzzle.url, 'puzzle'),
        'posthunt_static_directory': get_puzzle_static_path(puzzle_access.puzzle.url, 'posthunt'),
    }

def puzzle_to_puzzle_obj(puzzle):
    """Transforms a puzzle model to a dictionary for templates."""
    return {
        'puzzle': puzzle,
        'full_path': reverse('puzzle_view', args=(puzzle.url,)),
        # Choose an arbitrary unlock time.
        'unlock_time': now() - datetime.timedelta(minutes=60),
        'solved': False,
        'solved_time': None,
        'static_directory': get_puzzle_static_path(puzzle.url, 'puzzle'),
        'posthunt_static_directory': get_puzzle_static_path(puzzle.url, 'posthunt'),
    }

def is_posthunt_enabled(puzzle_url, is_public_team):
    complete = is_hunt_complete()
    posthunt_on_complete = puzzle_url in USE_POSTHUNT_ON_HUNT_COMPLETE
    posthunt_on_complete_public_only = is_public_team and puzzle_url in USE_POSTHUNT_ON_PUBLIC_AND_HUNT_COMPLETE
    return complete and (posthunt_on_complete or posthunt_on_complete_public_only)

def get_puzzle_variant(puzzle_url, is_public_team):
    posthunt_html = get_puzzle_data_text(puzzle_url, 'posthunt', 'index.html')
    if is_posthunt_enabled(puzzle_url, is_public_team) and posthunt_html:
        return 'posthunt'
    return 'puzzle'

def to_round_obj(round, puzzle_objs):
    """Transforms a round access model to a dictionary for templates."""
    return {
        'round': round,
        'solved': any(po['puzzle'].is_meta and po['solved'] for po in puzzle_objs),
        'puzzles': list(filter(
            lambda po: po['puzzle'].round_id == round.id,
            puzzle_objs))
    }

def get_act_for_round(round):
    if round.url == ROUND_RD0_URL:
        return 'act0'
    if round.url in (ROUND_RD1_URL, ROUND_SAMPLE_URL):
        return 'act1'
    if round.url == ROUND_RD2_URL:
        return 'act2'
    if round.url in ROUND_RD3_URLS or round.url == ROUND_RD3_META_URL:
        return 'act3'
    if round.url == ROUND_ENDGAME_URL:
        return 'act4'
    if round.url in (ROUND_SAMPLE_URL, ROUND_EVENTS_URL):
        return None

    logger.error(f'Unexpected round URL {round}')
    return None
