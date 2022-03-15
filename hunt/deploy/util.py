import logging
from functools import wraps

from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import redirect

from spoilr.core.api.decorators import require_launch
from spoilr.core.api.hunt import is_site_launched

logger = logging.getLogger(__name__)

# TODO(sahil): Build a dashboard for toggling these stages into spoilr. If we
# do that, it may make sense to associate each stage with an ordering constant,
# so that spoilr can show them in the right order. It should be technically
# possible to use the Django admin panel, but it's very broken for the
# `HuntSetting` model in at least Django 3.2, and doesn't handle "exactly 1
# non-null field".

# The hunt website goes through certain stages as hunt approaches, is in progress,
# and completes. Each stage is documented below. The stages are enabled using
# `spoilr.core.api.hunt.launch_site` or the Django `launch` command. The stages
# should be launched in the order documented below, or there may be unpredictable
# site behavior.
#
# Note: for stage 6-8, calling them "sites" is a little misleading, so maybe the
# utility methods should be renamed?
#
# Orthogonally, you may want to tweak the following settings and constants:
# - `settings.HUNT_LOGIN_ALLOWED`: To control whether (non-internal) teams can
#   still log in and track their progress.
# - `hunt.app.core.USE_POSTHUNT_ON_HUNT_COMPLETE`: To control which puzzles use
#   their posthunt version, when the hunt has been marked complete.

# Stage 1: Release the registration site publicly, and allow teams to register.
HUNT_REGISTRATION_SITE_REF = 'registration'
# Stage 2: Release the round 0 star rats website, and make it public. Also enable
# access to round 0 puzzles.
HUNT_RD0_REF = 'rd0'
# Stage 3: Update the registration site to show that round 0 is released. This
# adds links to the star rats website, relevant updates, zappy, etc. It's
# separate from Stage 2 so that star rats could be internally tested.
HUNT_RD0_RELEASED_REF = 'rd0-released'
# Stage 4: Release puzzles to each team, but without allowing teams access to the
# hunt website. This is necessary because releasing each puzzle to each team takes
# time (up to a few seconds per team), so we need to perform it in advance for
# fairness.
HUNT_PRELAUNCH_REF = 'site-prelaunch'
# Stage 5: Release the hunt website publicly, and allow teams to see puzzles.
HUNT_REF = 'hunt'
# Stage 6: Release hints unconditionally for each puzzle. This should only be
# done after the first team has found the coin.
HUNT_HINTS_RELEASED = 'hints-released'
# Stage 7: Auto-resolve actions that would normally require HQ, such as spending
# scrip, resolving interactions. This also indicates that we're not checking
# contact requests or hint requests with the same SLA.
HUNT_AUTOPILOT = 'autopilot'
# Stage 8: Indicate the hunt is complete and release solutions. Disable actions
# such as contact requests and hint requests.
HUNT_COMPLETE = 'complete'

ACCESS_TOKEN = 'hunt:access-token'

def is_it_hunt():
    return is_site_launched(HUNT_REF)

def are_hunt_hints_released():
    return is_site_launched(HUNT_HINTS_RELEASED)

def is_autopilot():
    return is_site_launched(HUNT_AUTOPILOT)

def is_hunt_complete():
    return is_site_launched(HUNT_COMPLETE)

def require_site_access(view_func):
    """
    Decorator that verifies the user has access to the view. This implements a
    very coarse authentication where a magic GET param needs to exist or
    otherwise, a 404 is shown. If the GET param exists, then future
    requests don't need to provide it thanks to sessions!

    This is useful for gating access to the staging websites, without colliding
    with the Django authentication system.
    """
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        if settings.HUNT_WEBSITE_ACCESS_TOKEN:
            token = request.COOKIES.get(ACCESS_TOKEN)
            authenticated = token == settings.HUNT_WEBSITE_ACCESS_TOKEN
        else:
            authenticated = True

        if not authenticated:
            logger.warn(f'Someone tried to access the website without a token {request}')
            return HttpResponseNotFound('Not found')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def require_registration_launch(view_func):
    # Note: for registration, this launches first and so teams can't already be
    # logged in to prove they are internal. So just don't worry about internal
    # team access, and rely on the staging version for testing.
    return require_site_access(
        require_launch(HUNT_REGISTRATION_SITE_REF, allow_admin=False)(view_func))

def require_rd0_launch(view_func):
    """Requires that round 0 is publicly accessible or the user is an admin."""
    return require_site_access(require_launch(HUNT_RD0_REF)(view_func))

def require_hunt_launch(allow_admin=True, redirect_target=None):
    """
    Decorator which requires the hunt to have been publicly launched before
    granting access.

    If allow_admin is True, then admin teams have access still.

    If redirect_target is None, a 404 error is shown to teams without
    access. Otherwise, they are redirected to the value returned by calling
    redirect_target with the `team` or `None` as an argument.

    If not launched, it will show a 404 error.
    """
    return require_launch(HUNT_REF, allow_admin, redirect_target)
