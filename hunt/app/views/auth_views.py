import datetime, urllib.parse

from django.contrib.auth import login, logout
from django.conf import settings
from django.http import QueryDict, HttpResponseForbidden, HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import now
from django.shortcuts import redirect, reverse

from django_hosts.resolvers import reverse as hosts_reverse

from spoilr.core.api.team import get_public_user
from spoilr.core.models import User

from hunt.deploy.util import require_rd0_launch, require_site_access
from hunt.registration.models import UserAuth
from hunt.registration.views.auth_views import SSO_AUTH_NORMAL, SSO_AUTH_REAUTH, PUBLIC_LOGIN_AUTH_TOKEN

AUTH_TOKEN_EXPIRY = datetime.timedelta(minutes=2)

# NOTE(sahil): We should probably make at least logout be a same-origin iframe
# only, but will ignore to make the in-iframe solving experience work.

# Note: Let you login (and authorize) without checking if the site is launched,
# as you may log in as an admin team that has access anyway.
@require_site_access
def login_view(request):
    auth_flow = SSO_AUTH_NORMAL
    next_url = request.GET.get('next', None)
    # If the user is logged in but got redirected to the login page, then they
    # tried to access a page they don't have access to. Let the registration site
    # know, so it doesn't auto-redirect the user to next_url immediately and cause
    # a redirect loop.
    if next_url and request.user.is_authenticated:
        auth_flow = SSO_AUTH_REAUTH

    # Daisy chain registration login -> authorize in this site -> next URL.
    next_url = next_url or reverse('index')

    parsed_authorize_url = urllib.parse.urlparse(
        request.build_absolute_uri(reverse('authorize')))
    authorize_query = QueryDict(mutable=True)
    authorize_query['next'] = next_url
    parsed_authorize_url = parsed_authorize_url._replace(query=authorize_query.urlencode(safe='/'))
    authorize_url = urllib.parse.urlunparse(parsed_authorize_url)

    parsed_registration_login_url = urllib.parse.urlparse(
        hosts_reverse('registration_login', host='registration'))
    registration_login_query = QueryDict(mutable=True)
    registration_login_query['next'] = authorize_url
    registration_login_query['auth'] = auth_flow
    parsed_registration_login_url = parsed_registration_login_url._replace(query=registration_login_query.urlencode(safe='/'))
    registration_login_url = urllib.parse.urlunparse(parsed_registration_login_url)

    return redirect(registration_login_url)

# TODO(sahil): Make it so logging out of one site will log you out of all of them.
# Not sure exactly how to do that though. Like maybe disable sessions that used the
# same auth code?

# Note: Let you authorize (and login) without checking if the site is launched,
# as you may log in as an admin team that has access anyway.
@require_site_access
def authorize_view(request):
    # TODO(sahil): Move this to an authentication backend, and use authenticate() instead.
    token = request.GET.get('token')
    next_url = request.GET.get('next')
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
        next_url = None

    if token == PUBLIC_LOGIN_AUTH_TOKEN and settings.HUNT_PUBLIC_TEAM_NAME:
        user = get_public_user()
    else:
        user_auth = (UserAuth.objects
            .prefetch_related('user')
            .filter(token=token, create_time__gt=now() - AUTH_TOKEN_EXPIRY,
                    delete_time__isnull=True)
            .first())

        if not user_auth:
            return redirect(next_url or reverse('index'))

        user_auth.delete_time = now()
        user_auth.save()

        user = user_auth.user

    login(request, user)
    return redirect(next_url or reverse('index'))

@require_rd0_launch
def update_registration_view(request):
    next_url = request.build_absolute_uri(request.GET.get('next') or hosts_reverse('index', host='site-1'))

    parsed_registration_update_url = urllib.parse.urlparse(
        hosts_reverse('update_registration', host='registration'))
    registration_update_query = QueryDict(mutable=True)
    registration_update_query['next'] = next_url
    parsed_registration_update_url = parsed_registration_update_url._replace(query=registration_update_query.urlencode(safe='/'))
    registration_update_url = urllib.parse.urlunparse(parsed_registration_update_url)

    return redirect(registration_update_url)

@require_rd0_launch
def logout_view(request):
    logout(request)

    next_url = request.build_absolute_uri(request.GET.get('next') or hosts_reverse('index', host='site-1'))

    parsed_registration_logout_url = urllib.parse.urlparse(
        hosts_reverse('registration_logout', host='registration'))
    registration_logout_query = QueryDict(mutable=True)
    registration_logout_query['next'] = next_url
    parsed_registration_logout_url = parsed_registration_logout_url._replace(query=registration_logout_query.urlencode(safe='/'))
    registration_logout_url = urllib.parse.urlunparse(parsed_registration_logout_url)

    return redirect(registration_logout_url)
