import secrets

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django_hosts.resolvers import reverse as hosts_reverse
from django.shortcuts import render, redirect, reverse
from django.utils.http import url_has_allowed_host_and_scheme

from spoilr.core.api.team import get_public_user, get_shared_account_username
from spoilr.core.models import User

from hunt.deploy.util import require_registration_launch, is_hunt_complete
from hunt.registration.models import UserAuth

SSO_AUTH_NORMAL = '1'
SSO_AUTH_REAUTH = '2'
PUBLIC_LOGIN_AUTH_TOKEN = 'public'

TOKEN_BYTES = 32

# NOTE(sahil): We should probably make at least logout be a same-origin iframe
# only, but will ignore to make the in-iframe solving experience work.

@require_registration_launch
def login_view(request):
    # If we're performing a normal SSO flow, then auto-login.
    should_auto_login = request.GET.get('next') and request.GET.get('auth') == SSO_AUTH_NORMAL
    if should_auto_login:
        if request.user.is_authenticated:
            return login_redirect(request.GET['next'], request.user, add_sso_token=True, require_https=request.is_secure())

        # Automatically log in with public access.
        if not settings.HUNT_LOGIN_ALLOWED and settings.HUNT_PUBLIC_TEAM_NAME:
            user = get_public_user()
            login(request, user)
            return login_redirect(request.GET['next'], user, add_sso_token=True, require_https=request.is_secure())

    if request.method == "POST":
        return login_post_view(request)

    return render(
        request,
        'registration/login.tmpl',
        {
            'public_enabled': bool(settings.HUNT_PUBLIC_TEAM_NAME) and is_hunt_complete(),
            'next': request.GET.get('next'),
            'sso': bool(request.GET.get('auth')),
            'error': None,
        })

def login_post_view(request):
    is_public_login = 'public' in request.POST and is_hunt_complete()
    public_team_name = settings.HUNT_PUBLIC_TEAM_NAME
    if is_public_login and public_team_name:
        user = get_public_user()
    else:
        team_username = request.POST.get('username', None)
        username = get_shared_account_username(team_username)
        password = request.POST.get('password', None)
        user = authenticate(request, username=username, password=password)

    next_url = request.POST.get('next', None)
    add_sso_token = request.POST.get('sso', False)

    error = None
    if user is None:
        error = 'no-user'
    elif not user.is_active:
        error = 'inactive'
    elif not settings.HUNT_LOGIN_ALLOWED and not (user.team.is_internal or user.team.is_public):
        error = 'disabled'

    if error:
        return render(
            request, 'registration/login.tmpl',
            {
                'public_enabled': bool(settings.HUNT_PUBLIC_TEAM_NAME),
                'next': next_url,
                'sso': add_sso_token,
                'error': error,
            })

    login(request, user)
    return login_redirect(next_url, user, add_sso_token=add_sso_token, require_https=request.is_secure())

def login_redirect(next_url, user, *, add_sso_token, require_https):
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, require_https):
        next_url = None

    suffix = ''
    if next_url and add_sso_token:
        # Use a constant token for public logins, to save a database check.
        if user.team.is_public:
            auth = UserAuth(user=user, token=PUBLIC_LOGIN_AUTH_TOKEN)
        else:
            auth = UserAuth.objects.create(
                user=user,
                token=secrets.token_hex(TOKEN_BYTES))
        suffix = ('' if '?' in next_url else '?') + f'&token={auth.token}'
        next_url += suffix
    # TODO(sahil): Go to the profile page instead?
    return redirect(next_url or hosts_reverse('index', host='site-1'))

@require_registration_launch
def logout_view(request):
    logout(request)

    next_url = request.GET.get('next')
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
        next_url = None

    return redirect(next_url or (reverse('registration_index') + '?status=logged-out'))
