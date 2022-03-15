from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from spoilr.core.api.events import dispatch, HuntEvent
from spoilr.core.models import Puzzle, Round, Team
from spoilr.email.models import OutgoingMessage
from spoilr.contact.models import ContactRequest
from spoilr.hq.models import Task, TaskStatus, HqLog
from spoilr.hq.util.decorators import hq
from spoilr.hq.util.redirect import redirect_with_message

MAX_CONTACT_REQUEST_LIMIT = 200

@hq()
def dashboard_view(request):
    contact_requests = (ContactRequest.objects
        .filter(tasks__isnull=False)
        .select_related('team')
        .prefetch_related('tasks')
        .order_by('-update_time'))

    team = None
    if request.GET.get('team'):
        team = get_object_or_404(Team, username=request.GET['team'])
        contact_requests = contact_requests.filter(team=team)

    open_only = False
    if request.GET.get('open') == '1':
        open_only = True
        contact_requests = contact_requests.filter(resolved_time__isnull=True, tasks__status=TaskStatus.PENDING)

    limit = 10
    if request.GET.get('limit'):
        limit = min([int(request.GET['limit']), MAX_CONTACT_REQUEST_LIMIT])
        contact_requests = contact_requests[:limit]

    teams = Team.objects.values_list('username', flat=True).order_by('username')

    return render(request, 'spoilr/contact/dashboard.tmpl', {
        'contact_requests': [
            {
                'contact_request': contact_request,
                'task': contact_request.tasks.first(),
            } for contact_request in contact_requests
        ],
        'limit': limit,
        'open_only': open_only,
        'team': team.username if team else None,
        'teams': teams,
    })

@require_POST
@hq(require_handler=True)
def respond_view(request):
    confirm = request.POST.get('confirm')
    response = request.POST.get('response', '').strip()
    if confirm.lower() != 'respond':
        return redirect_with_message(request, 'spoilr.contact:dashboard', 'Contact response was not confirmed.')

    contact_request_id = int(request.POST.get('id'))
    contact_request = ContactRequest.objects.select_related('team').get(id=contact_request_id) if contact_request_id else None
    if not contact_request or not response:
        return HttpResponseBadRequest('Missing or invalid fields')

    task = contact_request.tasks.first()
    if not task or task.handler != request.handler:
        return redirect_with_message(
            request, 'spoilr.contact:dashboard', f'You are no longer handling this contact request.')
    if task.status == TaskStatus.DONE:
        return redirect_with_message(request, 'spoilr.contact:dashboard', 'Contact request is already done.')

    contact_request.result = response
    contact_request.resolved_time = now()
    contact_request.save()

    task.status = TaskStatus.DONE
    task.snooze_time = None
    task.snooze_until = None
    task.save()

    HqLog.objects.create(
        handler=request.handler, event_type='contact-request-resolved',
        object_id=contact_request.team.username, message=f'Resolve contact request {contact_request}')

    dispatch(
        HuntEvent.CONTACT_REQUEST_RESOLVED, team=contact_request.team, contact_request=contact_request,
        object_id=contact_request.team.username,
        message=f'Resolved contact request for {contact_request.team.name}')

    if settings.SPOILR_HQ_DEFAULT_FROM_EMAIL:
        subject = f'Response from HQ'
        full_response = response + '\n---\n\n' + 'Your original contact request is below.' + '\n--\n\n' + contact_request.comment
        send_mail(
            subject, full_response, settings.SPOILR_HINTS_FROM_EMAIL,
            [contact_request.email])
        OutgoingMessage.objects.create(
            subject=subject, body_text=full_response,
            sender=settings.SPOILR_HQ_DEFAULT_FROM_EMAIL,
            recipient=contact_request.email,
            team=contact_request.team,
            automated=True, handler=request.handler)

    return redirect_with_message(request, 'spoilr.contact:dashboard', 'Contact request resolved.')
