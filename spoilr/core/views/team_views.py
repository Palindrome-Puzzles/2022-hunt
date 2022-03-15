from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.core.api.decorators import inject_team
from spoilr.core.api.team import impersonate, end_impersonate, get_team_by_username
from spoilr.core.models import Team

@xframe_options_sameorigin
@inject_team(require_admin=True)
def impersonate_view(request, team_username):
    try:
        team = get_team_by_username(team_username)
        impersonate(request, team)
    except Team.DoesNotExist:
        return HttpResponseBadRequest('Team does not exist')

    next_url = request.POST.get('next')
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
        next_url = None
    return redirect(next_url or reverse('index'))

@xframe_options_sameorigin
@inject_team(require_admin=True)
def end_impersonate_view(request):
    end_impersonate(request)
    return redirect(reverse('hq'))
