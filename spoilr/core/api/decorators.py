"""
Decorators for authenticating that a team has access to views based on their
hunt progress.
"""

import logging
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme

from spoilr.core.models import Interaction, InteractionAccess, Puzzle, PuzzleAccess, Round, RoundAccess, Team
from .hunt import is_site_launched
from .team import get_impersonated_team, get_team_by_id

logger = logging.getLogger(__name__)

def inject_team(*, require_admin=False, require_internal=False, redirect_if_missing=True, login_url=None):
    """
    Decorator which injects the team associated with the current user into the
    request as a `team` attribute.

    If `require_admin` or `require_internal` are `True`, then the user needs to
    also be an admin or associated with an internal account respectively.

    If `redirect_if_missing` is `True`, then when the user is not logged in,
    somehow the logged in user is not associated with a team, or they fail the
    `require_admin` or `require_internal` tests (if enabled), then they will be
    redirected to `settings.LOGIN_URL`. Otherwise, they will receive a 403
    Forbidden error.
    """
    if require_admin or require_internal:
        assert redirect_if_missing, 'redirect_if_missing should be True if we require admin or internal accounts'

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user if request.user.is_authenticated else None
            team = get_team_by_id(user.team_id) if user else None

            if user and user.is_staff:
                impersonated_team = get_impersonated_team(request)
                request.team = impersonated_team or team
                request.impersonating = request.team != team
            else:
                # TODO(sahil): Check this doesn't just throw an error if the user is
                # authenticated but has no team.
                request.team = team
                request.impersonating = False

            if user and not request.team:
                logger.error(f'Cannot find team for user {user}')

            valid = bool(request.team)
            if require_admin and not (user and user.is_staff):
                valid = False
            if require_internal and not (request.team and request.team.is_internal):
                valid = False

            if not valid and redirect_if_missing:
                return redirect_to_login(request.get_full_path(), login_url=login_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def inject_puzzle(*, allow_admin=True, error_if_inaccessible=True):
    """
    Decorator which injects the puzzle associated with the current request into
    the request as a `puzzle` attribute. It also injects the puzzle access
    object into the request as a `puzzle_access` attribute if the current team
    has access to the puzzle.

    If the request does not contain a `puzzle` kwarg with the puzzle URL, or if
    the `puzzle` kwarg can not be resolved to a puzzle URL, then a generic error
    is shown.

    If `error_if_inaccessible` is `True` and the current team does not have
    access to the puzzle, then the same generic error is shown. Otherwise, the
    request is served but `puzzle_access` will be `None`.

    If `allow_admin` is `True`, admin teams can override the puzzle access check
    and still access the view without an error being thrown.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            team = getattr(request, 'team', None)

            try:
                puzzle_url = kwargs['puzzle']
                request.puzzle = Puzzle.objects.select_related('round').get(url=puzzle_url)
                del kwargs['puzzle']
            except Puzzle.DoesNotExist:
                logger.warning('Cannot find puzzle %s', puzzle_url)
                return get_inaccessible_puzzle_response(puzzle_url)

            request.puzzle_access = None
            if team:
                request.puzzle_access = PuzzleAccess.objects.filter(team=team, puzzle=request.puzzle).first()

            if not request.puzzle_access:
                if error_if_inaccessible and not (allow_admin and request.user.is_staff):
                    logger.warning(
                        'Team %s does not have access to puzzle %s', team, request.puzzle)
                    return get_inaccessible_puzzle_response(puzzle_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def inject_round(*, allow_admin=True, error_if_inaccessible=True):
    """
    Decorator which injects the round associated with the current request into
    the request as a `round` attribute. It also injects the round access
    object into the request as a `round_access` attribute if the current team
    has access to the round.

    If the request does not contain a `round` kwarg with the round URL, or if
    the `round` kwarg can not be resolved to a round URL, then a generic error
    is shown.

    If `error_if_inaccessible` is `True` and the current team does not have
    access to the round, then the same generic error is shown. Otherwise, the
    request is served but `round_access` will be `None`.

    If `allow_admin` is `True`, admin teams can override the round access check
    and still access the view without an error being thrown.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            team = getattr(request, 'team', None)

            try:
                round_url = kwargs['round']
                request.round = Round.objects.get(url=round_url)
                del kwargs['round']
            except Round.DoesNotExist:
                logger.warning('Cannot find round %s', round_url)
                return get_inaccessible_round_response(round_url)

            request.round_access = None
            if team:
                request.round_access = RoundAccess.objects.filter(team=team, round=request.round).first()

            if not request.round_access:
                if error_if_inaccessible and not (allow_admin and request.user.is_staff):
                    logger.warning(
                        'Team %s does not have access to round %s', team, request.round)
                    return get_inaccessible_round_response(round_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def inject_interaction(*, allow_admin=True, error_if_inaccessible=True):
    """
    Decorator which injects the interaction associated with the current request into
    the request as a `interaction` attribute. It also injects the interaction access
    object into the request as a `interaction_access` attribute if the current team
    has access to the interaction.

    If the request does not contain a `interaction` kwarg with the interaction URL, or if
    the `interaction` kwarg can not be resolved to a interaction URL, then a generic error
    is shown.

    If `error_if_inaccessible` is `True` and the current team does not have
    access to the interaction, then the same generic error is shown. Otherwise, the
    request is served but `interaction_access` will be `None`.

    If `allow_admin` is `True`, admin teams can override the interaction access check
    and still access the view without an error being thrown.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            team = getattr(request, 'team', None)

            try:
                interaction_url = kwargs['interaction']
                request.interaction = Interaction.objects.get(url=interaction_url)
                del kwargs['interaction']
            except Interaction.DoesNotExist:
                logger.warning('Cannot find interaction %s', interaction_url)
                return get_inaccessible_interaction_response(interaction_url)

            request.interaction_access = None
            if team:
                request.interaction_access = InteractionAccess.objects.filter(
                    team=team, interaction=request.interaction).first()

            if not request.interaction_access:
                if error_if_inaccessible and not (allow_admin and request.user.is_staff):
                    logger.warning(
                        'Team %s does not have access to interaction %s',
                        team, request.interaction)
                    return get_inaccessible_interaction_response(interaction_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def require_launch(site_ref, allow_admin=True, redirect_target=None):
    """
    Decorator which requires a website to have been publicly launched before
    granting access.

    If allow_admin is True, then admin teams have access still.

    If redirect_target is None, a 404 error is shown to teams without
    access. Otherwise, they are redirected to the value returned by calling
    redirect_target with the `team` or `None` as an argument.

    If not launched, it will show a 404 error.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if is_site_launched(site_ref) or (allow_admin and request.user.is_staff):
                return view_func(request, *args, **kwargs)

            maybe_team = getattr(request, 'team', None)
            target = redirect_target and redirect_target(maybe_team)
            if target:
                return redirect(target)
            else:
                return get_inaccessible_site_response()
        return wrapped
    return decorator

def require_safe_referrer(view_func):
    """Verifies the referrer is from a safe domain, so that we can redirect to it as part of the view."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        next_url = request.META.get('HTTP_REFERER')
        if next_url and not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
            return HttpResponseForbidden('Referrer not allowed')
        return view_func(request, *args, **kwargs)
    return wrapped

def get_inaccessible_puzzle_response(puzzle_url):
    return HttpResponseBadRequest('Cannot find puzzle ' + escape(puzzle_url))

def get_inaccessible_round_response(round_url):
    return HttpResponseBadRequest('Cannot find round ' + escape(round_url))

def get_inaccessible_interaction_response():
    return HttpResponseNotFound('Not found')

def get_inaccessible_site_response():
    return HttpResponseNotFound('Not found')
