from django.conf import settings

from spoilr.core.api.cache import memoized_cache, delete_memoized_cache_entry
from spoilr.core.api.events import register, HuntEvent
from spoilr.core.models import Team, User

IMPERSONATE_SESSION_KEY = 'impersonated-team'
TEAM_CACHE_USERNAME_BUCKET = 'spoilr:team_username'
TEAM_CACHE_ID_BUCKET = 'spoilr:team_id'
PUBLIC_USER_BUCKET = 'spoilr:public_user'

def get_shared_account_username(team_username):
    return f'{team_username}__shared'

def impersonate(request, team):
    request.session[IMPERSONATE_SESSION_KEY] = team.username
    request.session.save()

def end_impersonate(request):
    del request.session[IMPERSONATE_SESSION_KEY]
    request.session.save()

def get_impersonated_team(request):
    if IMPERSONATE_SESSION_KEY in request.session:
        return get_team_by_username(request.session[IMPERSONATE_SESSION_KEY])
    return None

@memoized_cache(TEAM_CACHE_USERNAME_BUCKET)
def get_team_by_username(team_username):
    # Optimization: Make sure we select_related the users when we fetch
    # the team, so `shared_account` is cheap.
    return Team.objects.prefetch_related('user_set').filter(username=team_username).first()

@memoized_cache(TEAM_CACHE_ID_BUCKET)
def get_team_by_id(team_id):
    # Optimization: Make sure we select_related the users when we fetch
    # the team, so `shared_account` is cheap.
    return Team.objects.prefetch_related('user_set').filter(id=team_id).first()

def _on_team_changed(team, **kwargs):
    delete_memoized_cache_entry(TEAM_CACHE_USERNAME_BUCKET, team.username)
    delete_memoized_cache_entry(TEAM_CACHE_ID_BUCKET, team.id)

@memoized_cache(PUBLIC_USER_BUCKET)
def get_public_user():
    assert settings.HUNT_PUBLIC_TEAM_NAME
    return User.objects.prefetch_related('team').get(username=get_shared_account_username(settings.HUNT_PUBLIC_TEAM_NAME))

register(HuntEvent.TEAM_UPDATED, _on_team_changed)
register(HuntEvent.TEAM_REGISTERED, _on_team_changed)
