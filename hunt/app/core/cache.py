# Caching is hard. This module centralizes logic for how we cache hunt pages.
#
# There are a few levels of caching we can use:
# - server-side intermediate result caching
# - server-side view caching
# - browser caching
# - conditional HTTP responses
#
# Ideally we use server-side view caching and conditional HTTP responses. This
# is the best of both worlds because we can tell browsers to not use cached pages
# without revalidation, and we can calculate page etags + share them across team
# members easily with server-side caching.
#
# However, these are broken if pages vary by user such as if there are CSRF cookies.
# So instead we choose from these strategies:
# 1) for pages that do not contain CSRF cookies (or any Vary header, just in case),
#    cache by one of:
#     a) team
#     b) team and puzzle
# 2) for pages with CSRF cookies, prevent caching altogether. (We do cache some
#    intermediate results though!)
# 3) for HQ pages, use server-side view caching and browser caching because it
#    doesn't matter as much if we serve stale data
#
# There are a lot of pages with team info (such as all the top pages, plus round
# pages), and so caching each separately is wasteful.
#
# And there are pages with CSRF cookies that compute expensive stuff but that we
# can't cache. So we also use intermediate result caching for some common
# stuff like the shared context.
#
# For any changes to a team puzzle's state, we clear cache keys prefixed with the
# team and puzzle. This includes answers, hints, etc. For some like solves, we nuke
# the whole round, so that the round map updates.
#
# For any other changes to a team's state such as puzzle unlocks, round answers,
# interaction changes, updating registration, etc, we nuke the whole team cache.
#
# For other changes such as teams registering or HQ updates, we take a bespoke
# approach. Pages that show those have their own caching rules entirely.

import datetime, hashlib, random, string
from functools import wraps

from django.conf import settings
from django.core.cache import caches
from django.utils.cache import patch_cache_control
from django.views.decorators.http import condition

from .constants import PUZZLES_SKIP_CACHE_URLS

from spoilr.core.models import Team, Puzzle, Round

TEAMS_LIST_CATEGORY = 'teams_list'
SERVER_CACHE_TIMEOUT_S = 60 * 60;

cache = caches[settings.HUNT_CACHE_NAME]

def by_team_key(maybe_team, page_category=None):
    return f't{maybe_team.id if maybe_team else -1}{":" + page_category if page_category else ""}'
by_puzzle_key = lambda maybe_team, puzzle: f'{by_team_key(maybe_team)}:r{puzzle.round.url}:p{puzzle.external_id}'
by_round_key = lambda maybe_team, round: f'{by_team_key(maybe_team)}:r{round.url}'

def cache_page_by_team(page_category=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            assert hasattr(request, 'team'), 'should be used after @inject_team'
            key_prefix = by_team_key(request.team, page_category)
            return _cacheable_page_view(view_func, key_prefix, request, *args, **kwargs)
        return wrapped
    return decorator

def cache_page_by_puzzle(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        assert hasattr(request, 'team'), 'should be used after @inject_team'
        assert hasattr(request, 'puzzle'), 'should be used after @inject_puzzle'
        # Some puzzle pages are not cacheable as they change over time, or due to
        # actions in other rounds.
        # For the public, they can be cached though.
        if request.puzzle.url in PUZZLES_SKIP_CACHE_URLS and (request.team and not request.team.is_public):
            return view_func(request, *args, **kwargs)
        key_prefix = by_puzzle_key(request.team, request.puzzle)
        return _cacheable_page_view(view_func, key_prefix, request, *args, **kwargs)
    return wrapped

def cache_page_by_round(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        assert hasattr(request, 'team'), 'should be used after @inject_team'
        assert hasattr(request, 'round'), 'should be used after @inject_round'
        key_prefix = by_round_key(request.team, request.round)
        return _cacheable_page_view(view_func, key_prefix, request, *args, **kwargs)
    return wrapped

def _cacheable_page_view(view_func, key_prefix, request, *args, **kwargs):
    # We have two types of "caching":
    #  1) a server-side cache to avoid recomputing views.
    #  2) conditional GETs so we don't need to transmit a response if the user
    #     already has it. This performs validation so we can always ensure users
    #     see fresh content.
    #
    # These act as two layers that would normally be done with decorators.
    # However, they can both use the same cache key, so as a minor optimization,
    # I've smushed them together.
    #
    # We can't cache pages (either server-side or with a conditional GET) if they
    # have a Vary header. However, sometimes, the Vary header is set in
    # middleware... Thankfully, I know all the middleware running, and we can
    # just check whether the CSRF middleware is going to set the Vary header. In
    # Django 3.2, that can be checked using the CSRF_COOKIE_USED. (NB: It's been
    # renamed in Django 4.)

    if settings.HUNT_ENABLE_CACHING and request.method == 'GET':
        url_hash = hashlib.sha256(request.build_absolute_uri().encode('utf-8')).hexdigest()
        cache_key = f'{key_prefix}:u:{url_hash}'

        etag = _generate_etag()
        etag_func = lambda *args, **kwargs: cache.get(f'{cache_key}:etag', etag)
        last_modified = datetime.datetime.now()
        last_modified_func = lambda *args, **kwargs: cache.get(f'{cache_key}:last_modified', last_modified)

        decorated = (
            condition(etag_func, last_modified_func)(
                _server_cached_view(request, cache_key, etag, last_modified)(
                    view_func)))
        return decorated(request, *args, **kwargs)
    else:
        return view_func(request, *args, **kwargs)

def _server_cached_view(request, cache_key, etag, last_modified):
    def decorator(view_func):
        def wrapped(*args, **kwargs):
            response = cache.get(cache_key)
            if response is not None:
                return response

            # NB: CSRF_COOKIE_USED is only set after running view_func!
            response = view_func(*args, **kwargs)
            if request.META.get('CSRF_COOKIE_USED') or response.has_header('Vary'):
                # Prevent any caching. Otherwise, browsers will apply some default
                # cache time, which prevents us from showing changes to solvers
                # as soon as possible.
                patch_cache_control(response, private=True, no_store=True, max_age=0)
            else:
                # Force cache re-validation every time.
                patch_cache_control(response, private=True, no_cache=True)
                cache.set(cache_key, response, SERVER_CACHE_TIMEOUT_S)
                cache.set(f'{cache_key}:etag', etag, SERVER_CACHE_TIMEOUT_S)
                cache.set(f'{cache_key}:last_modified', last_modified, SERVER_CACHE_TIMEOUT_S)
            return response
        return wrapped
    return decorator

def cache_shared_context(context_factory):
    @wraps(context_factory)
    def wrapped(*args, **kwargs):
        assert len(args) == 1
        assert isinstance(args[0], Team) or args[0] == None
        key = f'{by_team_key(args[0])}:context'
        return _memoized_cache(context_factory, key, *args, **kwargs)
    return wrapped

def memoized_cache(bucket):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args):
            hasher = hashlib.sha256()
            for arg in args:
                hasher.update(arg.encode('utf-8'))
            key = f'memoized:{bucket}:{hasher.hexdigest()}'
            return _memoized_cache(view_func, key, *args)
        return wrapped
    return decorator

def _memoized_cache(result_factory, key, *args, **kwargs):
    result = cache.get(key)
    if not settings.HUNT_ENABLE_CACHING or not result:
        result = result_factory(*args, **kwargs)
        cache.set(key, result, timeout=SERVER_CACHE_TIMEOUT_S)
    return result

def cache_intermediate_by_team(fn):
    def wrapped(team, *args, **kwargs):
        key = f'{by_team_key(team)}:intermediate'
        return _memoized_cache(fn, key, team, *args, **kwargs)
    return wrapped

def team_puzzle_updated(team, puzzle):
    _clear_cache_by_prefixes(by_puzzle_key(team, puzzle))

def team_round_updated(team, round):
    _clear_cache_by_prefixes(by_round_key(team, round))

def team_updated(team):
    _clear_cache_by_prefixes(by_team_key(team))

def nuke_page_category(page_category):
    for team in Team.objects.all():
        _clear_cache_by_prefixes(by_team_key(team, page_category))

def nuke_cache():
    cache.clear()

def _clear_cache_by_prefixes(*prefixes):
    # If available, use a redis extension for deleting globs.
    # https://github.com/jazzband/django-redis#scan--delete-keys-in-bulk
    if hasattr(cache, 'delete_pattern'):
        for prefix in prefixes:
            cache.delete_pattern(prefix + '*')
    else:
        cache.clear()

def _generate_etag():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))
