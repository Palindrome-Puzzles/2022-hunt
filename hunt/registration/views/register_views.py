from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_sameorigin

from ..forms.register_team_form import RegisterTeamForm
from ..forms.register_solver_form import RegisterSolverForm

from hunt.app.core.teams import generate_team_auth
from hunt.app.models import TeamData
from hunt.deploy.util import require_registration_launch

from spoilr.core.api.decorators import inject_team
from spoilr.core.api.events import HuntEvent, dispatch
from spoilr.core.api.team import get_shared_account_username
from spoilr.core.models import Team, UserTeamRole

from .auth_views import login_redirect

COMMON_FORM_ATTRS = {
    'label_suffix': '',
    'use_required_attribute': True,
}

@require_registration_launch
@xframe_options_sameorigin
def register_team_view(request):
    if request.user and request.user.is_authenticated:
        return redirect(reverse('update_registration') + '?status=existing')

    if request.method == 'POST':
        form = RegisterTeamForm(request.POST, **COMMON_FORM_ATTRS)
        if form.is_valid():
            return register_new_team(request, form, add_sso_token=bool(request.GET.get('auth')))

    else:
        form = RegisterTeamForm(**COMMON_FORM_ATTRS)

    return _render_registration_view(request, form, create=True)

@require_registration_launch
@xframe_options_sameorigin
@inject_team(login_url='registration_login')
def update_registration_view(request):
    team = request.team
    shared_user = team.user_set.get(team_role=UserTeamRole.SHARED_ACCOUNT)
    if request.method == 'POST':
        # `initial` is ignored when data is bound, so we need to merge the
        # team_username into the data ourselves.
        data = request.POST.copy()
        data['team_username'] = team.username
        form = RegisterTeamForm(
            data, instance=team.teamregistrationinfo, **COMMON_FORM_ATTRS)
        form.for_update()
        if request.team.teamregistrationinfo.locked:
            form.for_locked()

        if form.is_valid():
            return update_existing_team(request, team, shared_user, form)
    else:
        initial = {
            'team_name': team.name,
            'team_username': team.username,
            'captain_name': shared_user.first_name,
            'captain_email': shared_user.email,
        }
        form = RegisterTeamForm(
            instance=team.teamregistrationinfo, initial=initial, **COMMON_FORM_ATTRS)
        form.for_update()

        if request.team.teamregistrationinfo.locked:
            form.for_locked()

    return _render_registration_view(request, form, create=False)

@require_POST
@require_registration_launch
@xframe_options_sameorigin
@inject_team(login_url='registration_login')
def registration_lock_view(request):
    team = request.team
    team.teamregistrationinfo.locked = True
    team.teamregistrationinfo.save()

    next_url = request.POST.get('next')
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
        next_url = None
    return redirect(next_url or reverse('update_registration'))

@require_registration_launch
@xframe_options_sameorigin
def register_solver_view(request):
    if request.method == 'POST':
        assert not settings.HUNT_REGISTRATION_CLOSED

        form = RegisterSolverForm(request.POST, **COMMON_FORM_ATTRS)
        if form.is_valid():
            form.save()
            return redirect(reverse('registration_index') + '?status=registered-solver')

    else:
        form = RegisterSolverForm(**COMMON_FORM_ATTRS)

    return _render_solver_view(request, form)

def register_new_team(request, form, *, add_sso_token):
    assert not settings.HUNT_REGISTRATION_CLOSED

    username = form.cleaned_data['team_username']
    team = Team.objects.create(
        username=username,
        name=form.cleaned_data['team_name'])

    team_data = TeamData.objects.create(
        team=team,
        auth=generate_team_auth(username=username, password=form.cleaned_data['team_password2'])
    )

    registration_info = form.save(commit=False)
    registration_info.team = team
    registration_info.save()

    UserModel = get_user_model()
    shared_user = UserModel.objects.create_user(
        get_shared_account_username(username),
        form.cleaned_data['captain_email'],
        form.cleaned_data['team_password2'],
        first_name=form.cleaned_data['captain_name'],
        team=team,
        team_role=UserTeamRole.SHARED_ACCOUNT)

    # Feature: if we register auto log you in.
    login(request, shared_user)

    dispatch(
        HuntEvent.TEAM_REGISTERED, team=team, object_id=team.id,
        message=f'Registered team {team.name}')

    next_url = request.POST.get('next')
    return login_redirect(next_url, shared_user, add_sso_token=add_sso_token, require_https=request.is_secure())

def update_existing_team(request, team, shared_user, form):
    assert not team.is_public, 'Can\'t edit public teams'
    team.name = form.cleaned_data['team_name']
    team.save()

    team_data = TeamData.objects.get_or_create(
        team=team,
        defaults={
            'auth': generate_team_auth(username=team.username, password=form.cleaned_data['team_password2'])
        })

    form.save()

    UserModel = get_user_model()
    shared_user.email = form.cleaned_data['captain_email']
    shared_user.first_name = form.cleaned_data['captain_name']
    if form.cleaned_data['team_password2']:
        shared_user.set_password(form.cleaned_data['team_password2'])
    shared_user.save()

    dispatch(
        HuntEvent.TEAM_UPDATED, team=team, object_id=team.id,
        message=f'Updated team {team.name}')

    next_url = request.POST.get('next')
    if not url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_REDIRECTS, request.is_secure()):
        next_url = None
    return redirect(next_url or (reverse('registration_index') + '?status=updated'))

def _render_registration_view(request, form, *, create):
    fields = {field: form[field] for field in form.fields}
    team_fields = tuple(fields[f] for f in ('team_name', 'team_email', 'team_emoji', 'team_username', 'team_password1', 'team_password2'))
    captain_fields = tuple(fields[f] for f in ('captain_name', 'captain_pronouns', 'captain_email', 'captain_phone'))
    bg_fields = tuple(fields[f] for f in ('bg_bio', 'bg_style', 'bg_win', 'bg_first_year', 'bg_started', 'bg_location', 'bg_comm'))
    size_fields = tuple(fields[f] for f in ('size_total', 'size_last_year', 'size_undergrads', 'size_grads', 'size_alumni', 'size_faculty', 'size_minors'))
    other_fields = tuple(fields[f] for f in ('other_unattached', 'other_workshop', 'other_puzzle_club', 'other_how'))

    return render(request, 'registration/register_team.tmpl', {
        'form': form,
        'create': create,
        'status': request.GET.get('status'),
        'next': request.GET.get('next'),
        'locked': hasattr(request, 'team') and (request.team.teamregistrationinfo.locked or request.team.is_public),
        'fieldsets': [
            {'label': 'Team Name', 'fields': team_fields, 'classes': ''},
            {'label': 'Team Captain', 'fields': captain_fields, 'classes': ''},
            {'label': 'Background Information', 'fields': bg_fields, 'classes': 'multiline'},
            {'label': 'Team Size', 'fields': size_fields, 'classes': 'multiline'},
            {'label': 'Other Information', 'fields': other_fields, 'classes': 'multiline'},
        ],
        'registration_closed': settings.HUNT_REGISTRATION_CLOSED,
    })

def _render_solver_view(request, form):
    fields = {field: form[field] for field in form.fields}
    solver_fields = tuple(fields[f] for f in ('first_name', 'last_name', 'pronouns', 'email'))
    bg_fields = tuple(fields[f] for f in ('bg_mitmh', 'bg_puzzles', 'bg_style', 'bg_prefs', 'bg_age', 'bg_mit'))

    return render(request, 'registration/register_solver.tmpl', {
        'form': form,
        'status': request.GET.get('status'),
        'fieldsets': [
            {'label': 'Contact Information', 'fields': solver_fields, 'classes': ''},
            {'label': 'Background Information', 'fields': bg_fields, 'classes': 'multiline'},
        ],
        'registration_closed': settings.HUNT_REGISTRATION_CLOSED,
    })
