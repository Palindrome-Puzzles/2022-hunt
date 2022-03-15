import collections

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from hunt.app.models import InteractionType, FreeUnlockStatus, FreeUnlockRequest
from hunt.app.core.rewards import get_manuscrip_info

from spoilr.core.api.answer import submit_puzzle_answer
from spoilr.core.api.hunt import accomplish_interaction, release_interaction
from spoilr.core.models import InteractionAccess, Interaction, Team
from spoilr.email.models import IncomingMessage, OutgoingMessage
from spoilr.hq.models import Task, TaskStatus, HqLog
from spoilr.hq.util.decorators import hq
from spoilr.hq.util.redirect import redirect_with_message
from spoilr.interaction.models import InteractionAccessTask

HQ_EMAIL_PREFIX = 'HQ Update: '

@hq()
def dashboard_view(request):
    accesses = (InteractionAccess.objects
        .select_related('interaction__interactiondata')
        .filter(interactionaccesstask__tasks__isnull=False)
        .exclude(interactionaccesstask__tasks__status=TaskStatus.IGNORED)
        .order_by('create_time'))

    available_by_interaction = collections.defaultdict(int)
    accomplished_by_interaction = collections.defaultdict(int)
    for access in accesses:
        if access.accomplished:
            accomplished_by_interaction[access.interaction_id] += 1
        else:
            available_by_interaction[access.interaction_id] += 1

    interactions = Interaction.objects.order_by('order')
    interaction_infos = [
        {
            'interaction': interaction,
            'available_count': available_by_interaction[interaction.id],
            'accomplished_count': accomplished_by_interaction[interaction.id],
        } for interaction in interactions
    ]
    interaction_infos.sort(
        key=lambda interaction_info: (-interaction_info['available_count'], interaction_info['interaction'].order))
    return render(request, 'spoilr/interaction/dashboard.tmpl', {
        'interaction_infos': interaction_infos,
    })

@hq()
def interaction_view(request, interaction_url):
    interaction = get_object_or_404(Interaction, url=interaction_url)
    accesses = (InteractionAccess.objects
        .select_related('interaction__interactiondata')
        .prefetch_related('interactionaccesstask__tasks')
        .filter(
            interaction=interaction,
            interactionaccesstask__tasks__isnull=False,
            interactionaccesstask__tasks__status__in=(TaskStatus.PENDING, TaskStatus.SNOOZED)))

    teams_ready = []
    teams_claimed = []
    teams_snoozed = []
    for access in accesses:
        task = access.interactionaccesstask.tasks.first()
        if task.status == TaskStatus.SNOOZED:
            teams_snoozed.append({
                'team': access.team,
                'task': task,
                'create_time': access.create_time,
            })
        elif task.handler and task.handler != request.handler:
            teams_claimed.append({
                'team': access.team,
                'task': task,
                'create_time': access.create_time,
            })
        else:
            teams_ready.append({
                'team': access.team,
                'task': task,
                'create_time': access.create_time,
            })

    teams_snoozed.sort(key=lambda x: x['create_time'])
    teams_ready.sort(key=lambda x: x['create_time'])
    teams_claimed.sort(key=lambda x: x['create_time'])
    teams_accomplished = []
    for access in (InteractionAccess.objects
        .select_related('team')
        .prefetch_related('interactionaccesstask__tasks')
        .filter(interaction=interaction, accomplished=True)
        .order_by('-accomplished_time')):
        teams_accomplished.append({
            'team': access.team,
            'task': access.interactionaccesstask.tasks.first(),
            'create_time': access.create_time,
            'accomplished_time': access.accomplished_time,
        })

    teams_accomplished.reverse()

    used_team_ids = (
        [t['team'].id for t in teams_ready] +
        [t['team'].id for t in teams_snoozed] +
        [t['team'].id for t in teams_accomplished])
    teams_not_ready = Team.objects.exclude(id__in=used_team_ids)

    return render(request, 'spoilr/interaction/interaction.tmpl', {
        'interaction': interaction,
        'teams_ready': teams_ready,
        'teams_snoozed': teams_snoozed,
        'teams_claimed': teams_claimed,
        'teams_accomplished': teams_accomplished,
        'teams_not_ready': teams_not_ready,
    })

@hq()
def details_view(request, interaction_url, team_username):
    interaction = get_object_or_404(Interaction.objects.select_related('interactiondata'), url=interaction_url)
    team = get_object_or_404(Team, username=team_username)
    access = (InteractionAccess.objects
        .select_related('interaction__interactiondata')
        .prefetch_related('interactionaccesstask__tasks')
        .filter(interaction=interaction, team=team)
        .first())

    task = None
    try:
        task = access and access.interactionaccesstask and access.interactionaccesstask.tasks.first()
    except InteractionAccessTask.DoesNotExist:
        pass

    if access and task and task.status == TaskStatus.DONE:
        status = 'accomplished'
    elif access and task and task.status == TaskStatus.SNOOZED:
        status = 'snoozed'
    elif access and task and task.handler and task.handler != request.handler:
        status = 'claimed'
    elif access and task and task.handler:
        status = 'ready'
    elif access and task:
        status = 'unclaimed'
    else:
        status = 'not_ready'

    extra_context = {}
    if interaction.interactiondata.type == InteractionType.STORY:
        if request.method == 'POST':
            extra_context, response = handle_story_email(request, interaction, team, access)
            if response:
                return response
        else:
            extra_context = {
                'subject': HQ_EMAIL_PREFIX,
                'body': '',
            }
    elif interaction.interactiondata.type == InteractionType.ANSWER:
        extra_context = {
            'manuscrip_info': get_manuscrip_info(team),
        }

    incoming_emails = (IncomingMessage.objects
        .select_related('team', 'interaction')
        .filter(team=team, interaction=interaction)
        .prefetch_related('outgoingmessage_set', 'outgoingmessage_set__handler')
        .order_by('-received_time'))
    outgoing_emails = (OutgoingMessage.objects
        .filter(team=team, interaction=interaction)
        .filter(reply_to__isnull=True, automated=False)
        .order_by('-sent_time'))
    emails = (
        [{'type': 'in', 'email': email} for email in incoming_emails] +
        [{'type': 'out', 'email': email} for email in outgoing_emails]
    )

    return render(request, 'spoilr/interaction/details.tmpl', {
        'interaction': interaction,
        'team': team,
        'interaction_access': access,
        'task': task,
        'status': status,
        'emails': emails,
        'allow_danger': request.GET.get('danger') == '1',
        **extra_context,
    })

@require_POST
def handle_story_email(request, interaction, team, interaction_access):
    confirm = request.POST.get('confirm')
    subject = request.POST.get('subject', '')
    body_text = request.POST.get('body', '')
    allow_resend = request.POST.get('danger-resend', '') == '1'

    error = None
    if not subject or not body_text:
        error = 'Missing fields'
    elif confirm.lower() != 'send':
        error = 'Did not confirm sending the email'
    elif not allow_resend and interaction_access.interactionaccesstask.replied:
        error = 'Someone has already replied - maybe from clicking refresh?'
    elif subject.strip() == HQ_EMAIL_PREFIX.strip():
        error = 'Make sure you enter a subject'

    if error:
        return {
            'subject': subject,
            'body': body_text,
            'error': error,
        }, None

    assert settings.SPOILR_HQ_DEFAULT_FROM_EMAIL, 'No HQ email configured'

    sender = settings.SPOILR_HQ_DEFAULT_FROM_EMAIL
    send_mail(subject, body_text, sender, [team.team_email])

    message = OutgoingMessage.objects.create(
        subject=subject, body_text=body_text, sender=sender, recipient=team.team_email,
        team=team, interaction=interaction, automated=False, handler=request.handler)

    interaction_access.interactionaccesstask.replied = True
    interaction_access.interactionaccesstask.save()

    HqLog.objects.create(
        handler=request.handler, event_type='story-send', object_id=interaction.url,
        message=f'Sent story email to {team.username}: {message}')

    return None, redirect_with_message(
        request, 'spoilr.interaction:details', 'Story email sent.',
        default_path_args=(interaction.url, team.username))

@require_POST
@hq(require_handler=True)
def resolve_answer_view(request):
    unlock_id = int(request.POST.get('unlock_id'))
    task_id = int(request.POST.get('task_id'))
    action = request.POST.get('action')
    if not unlock_id or action not in ('solve', 'cancel'):
        return HttpResponseBadRequest('Missing or invalid fields')

    confirm = request.POST.get('confirm')
    if confirm.lower() != action:
        return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Interaction was not resolved.')

    unlock = get_object_or_404(FreeUnlockRequest, id=unlock_id)
    task = get_object_or_404(Task, id=task_id)

    if unlock.status != FreeUnlockStatus.NEW:
        return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Answer unlock request is no longer new.')

    # Update the unlock first, so that it doesn't get reset by the puzzle solve listener.
    unlock.status = FreeUnlockStatus.APPROVED if action == 'solve' else FreeUnlockStatus.CANCELLED
    unlock.save()

    if action == 'solve':
        submit_puzzle_answer(unlock.team, unlock.puzzle, unlock.puzzle.answer)

    resolve_task(request, task)

    return redirect_with_message(
        request, 'spoilr.interaction:dashboard',
        'Manuscrip request approved.' if action == 'solve' else 'Manuscrip request cancelled.')

@require_POST
@hq(require_handler=True)
def resolve_view(request):
    confirm = request.POST.get('confirm')
    if confirm.lower() != 'resolve':
        return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Interaction was not resolved.')

    task_id = int(request.POST.get('task_id'))
    task = Task.objects.get(id=task_id) if task_id else None
    if not task:
        return HttpResponseBadRequest('Missing or invalid fields')

    resolve_task(request, task)

    return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Interaction resolved.')

@require_POST
@hq(require_handler=True)
def danger_release_view(request):
    confirm = request.POST.get('confirm')
    if confirm.lower() != 'release':
        return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Interaction was not released.')

    interaction_id = int(request.POST.get('interaction_id'))
    interaction = get_object_or_404(Interaction, id=interaction_id)
    team_id = int(request.POST.get('team_id'))
    team = get_object_or_404(Team, id=team_id)

    release_interaction(team, interaction)

    HqLog.objects.create(
        handler=request.handler, event_type='interaction-released-danger',
        object_id=interaction.url, message=f'Release interaction {interaction} for team {team}')

    return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Interaction released.')

def resolve_task(request, task):
    if task.handler != request.handler:
        return redirect_with_message(
            request, 'spoilr.interaction:dashboard', f'You are no longer handling this task.')
    if task.status == TaskStatus.DONE:
        return redirect_with_message(request, 'spoilr.interaction:dashboard', 'Task is already done.')

    if task.content_type != ContentType.objects.get_for_model(InteractionAccessTask):
        return HttpResponseBadRequest('Invalid task type')

    interaction_access = task.content_object.interaction_access
    accomplish_interaction(interaction_access=interaction_access)

    task.status = TaskStatus.DONE
    task.snooze_time = None
    task.snooze_until = None
    task.save()

    HqLog.objects.create(
        handler=request.handler, event_type='interaction-resolved',
        object_id=interaction_access.interaction.url, message=f'Resolve interaction {interaction_access.interaction} for team {interaction_access.team}')
