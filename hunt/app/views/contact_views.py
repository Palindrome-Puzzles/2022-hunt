import datetime, json

from django.conf import settings
from django.shortcuts import render, redirect

from spoilr.core.api.events import dispatch, HuntEvent
from spoilr.core.api.decorators import inject_team
from spoilr.contact.models import ContactRequest

from .common import get_shared_context, xframe_sameorigin_if_post, verify_team_accessible
from hunt.app.core.hosts import use_site_2_if_unlocked
from hunt.deploy.util import require_hunt_launch, is_hunt_complete

HUNT_OPEN_CONTACT_QUOTA = 2

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@xframe_sameorigin_if_post
def contact_view(request):
    open_contacts_count = ContactRequest.objects.filter(team=request.team, resolved_time__isnull=True).count()
    if open_contacts_count >= HUNT_OPEN_CONTACT_QUOTA:
        at_quota = True

    at_quota = False

    if request.method == 'POST':
        return contact_post_view(request, request.team)

    contact_requests = ContactRequest.objects.filter(team=request.team)
    context = get_shared_context(request.team)
    context['contact_requests'] = contact_requests
    context['email'] = request.team.team_email
    context['at_quota'] = at_quota

    return render(request, 'top/contact.tmpl', context)

def contact_post_view(request, team):
    assert not is_hunt_complete(), 'Can no longer submit contact requests'

    comment = request.POST['comment'].strip()
    email = request.POST['email']

    if len(comment):
        contact_request, created = (ContactRequest.objects
            .update_or_create(team=team, comment__iexact=comment, defaults={
                'comment': comment,
                'email': email,
            }))
        if created:
            dispatch(
                HuntEvent.CONTACT_REQUESTED, team=team, contact_request=contact_request,
                object_id=team.username,
                message=f'{team.name} asked “{comment}”')
    return redirect(request.get_full_path())
