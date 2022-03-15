import urllib.parse

from django.contrib.auth import logout
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .cache import cache_intermediate_by_team
from .constants import ROUND_RD2_URL

TEAM_SYNC_TOKEN = 'ts'

SITE_1_PREFIX = None
SITE_2_PREFIX = None

# To workaround circular import issues.
def lazy_init_site_prefixes():
    from django_hosts.resolvers import reverse as hosts_reverse

    global SITE_1_PREFIX, SITE_2_PREFIX
    SITE_1_PREFIX = hosts_reverse('host_resolve_root', host='site-1')
    SITE_2_PREFIX = hosts_reverse('host_resolve_root', host='site-2')

def use_site_1(view_func):
    '''Redirects a view to site 1 unconditionally.'''
    @verify_team_sync
    def wrapped(request, *args, **kwargs):
        lazy_init_site_prefixes()
        team = getattr(request, 'team', None)
        response = redirect_to_host(request, SITE_1_PREFIX, SITE_2_PREFIX, team=team)
        return response or view_func(request, *args, **kwargs)
    return wrapped

def use_site_2_if_unlocked(view_func):
    '''Redirects a view to site 2 unconditionally.'''
    @verify_team_sync
    def wrapped(request, *args, **kwargs):
        lazy_init_site_prefixes()

        team = getattr(request, 'team', None)

        response = None
        if is_site_2_accessible(team):
            response = redirect_to_host(request, SITE_2_PREFIX, SITE_1_PREFIX, team)
        elif not team:
            response = redirect_to_login(request.get_full_path())
        else:
            response = redirect_to_host(request, SITE_1_PREFIX, SITE_2_PREFIX, team)

        return response or view_func(request, *args, **kwargs)
    return wrapped

def verify_team_sync(view_func):
    def wrapped(request, *args, **kwargs):
        team = getattr(request, 'team', None)
        raw_team_sync_token = request.GET.get(TEAM_SYNC_TOKEN, '')
        team_sync_token = int(raw_team_sync_token) if raw_team_sync_token.isdigit() else None

        if team_sync_token != None:
            actual_team_sync_token = team.id if team else -1
            if team_sync_token != actual_team_sync_token:
                logout(request)

            parsed = urllib.parse.urlparse(request.get_full_path())
            qs = urllib.parse.parse_qs(parsed.query)
            del qs[TEAM_SYNC_TOKEN]
            updated = parsed._replace(query=urllib.parse.urlencode(qs, doseq=True))
            return redirect(urllib.parse.urlunparse(updated))
        return view_func(request, *args, **kwargs)
    return wrapped

@cache_intermediate_by_team
def is_site_2_accessible(team):
    return team and team.roundaccess_set.filter(round__url=ROUND_RD2_URL).exists()

def redirect_to_host(request, desired_host_prefix, other_host_prefix, team):
    if request.method != 'GET':
        return None

    # Avoid redirect loops.
    if desired_host_prefix == other_host_prefix:
        return None

    parsed_other_host_prefix = urllib.parse.urlparse(other_host_prefix)
    if (request.get_host() == parsed_other_host_prefix.netloc and
        request.path.startswith(parsed_other_host_prefix.path)):
        relative_path = request.path[len(parsed_other_host_prefix.path):]

        target = urllib.parse.urljoin(desired_host_prefix, relative_path)
        return redirect_and_sync_logins(request, target, team)
    return None

# TODO(sahil): Multiple domains breaks team impersonation. The impersonation status
# isn't synced across domains, and the forced logout below forgets which team is
# impersonated. If future teams use this code for multiple domains, then impersonation
# needs to be rewritten so the source of truth is in the registration website, and
# it's passed along with auth tokens.
#
# (This is also a more general problem with storing stuff in the session at all
# while using multiple domains.)
#
# Workaround: impersonate in HQ from the same domain as where you want to
# impersonate a team.
def redirect_and_sync_logins(request, target, team):
    # Log out on this site in case we're out of sync. That way, in redirect loops,
    # both will end up unauthenticated, and we force a sync from the registration
    # website.
    logout(request)
    team_sync_token = team.id if team else -1
    team_sync_suffix = ('&' if '?' in target else '?') + f'{TEAM_SYNC_TOKEN}={team_sync_token}'
    return redirect(target + team_sync_suffix)
