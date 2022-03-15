from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from hunt.deploy.util import HUNT_REF, HUNT_PRELAUNCH_REF

from spoilr.core.api.hunt import is_site_launched
from spoilr.core.models import Team, Interaction, UserTeamRole
from spoilr.email.models import IncomingMessage, OutgoingMessage
from spoilr.hq.models import Task, TaskStatus
from spoilr.hq.util.decorators import hq

MAX_EMAIL_LIMIT = 200

@hq()
def dashboard_view(request):
    emails = (IncomingMessage.objects
        .select_related('interaction', 'team')
        .prefetch_related('tasks')
        .filter(tasks__isnull=False, tasks__status__in=(TaskStatus.PENDING, TaskStatus.SNOOZED))
        .order_by('-received_time'))
    hidden = not (request.GET.get('hidden') and request.GET['hidden'] == '0')
    if hidden:
        emails = emails.filter(hidden=False)

    return render(request, 'spoilr/email/dashboard.tmpl', {
        'emails': [
            {
                'email': email,
                'task': email.tasks.first(),
            } for email in emails
        ],
        'hidden': hidden,
        'is_active': is_site_launched(HUNT_REF) or is_site_launched(HUNT_PRELAUNCH_REF),
    })

@hq()
def archive_view(request):
    incoming_emails = (IncomingMessage.objects
        .select_related('team', 'interaction')
        .prefetch_related('outgoingmessage_set', 'outgoingmessage_set__handler')
        .order_by('-received_time'))
    outgoing_emails = (OutgoingMessage.objects
        .filter(reply_to__isnull=True, automated=False)
        .order_by('-sent_time'))

    interaction = None
    if request.GET.get('interaction'):
        interaction = get_object_or_404(Interaction, url=request.GET['interaction'])
        incoming_emails = incoming_emails.filter(interaction=interaction)
        outgoing_emails = outgoing_emails.filter(interaction=interaction)

    team = None
    if request.GET.get('team'):
        team = get_object_or_404(Team, username=request.GET['team'])
        captain_email = team.user_set.get(team_role=UserTeamRole.SHARED_ACCOUNT).email
        team_email = team.teamregistrationinfo.team_email

        team_query = Q(team=team)
        email_query = Q(sender__icontains=captain_email) | Q(recipient__icontains=captain_email)
        if captain_email:
            email_query |= Q(sender__icontains=captain_email) | Q(recipient__icontains=captain_email)

        incoming_emails = incoming_emails.filter(team_query | email_query)
        outgoing_emails = outgoing_emails.filter(team_query | email_query)

    email = None
    if request.GET.get('email'):
        email = request.GET['email']
        incoming_emails = incoming_emails.filter(Q(sender__icontains=email) | Q(recipient__icontains=email))
        outgoing_emails = outgoing_emails.filter(Q(sender__icontains=email) | Q(recipient__icontains=email))

    # Note: Could totally use the postgres full-text search magic when we know we're
    # running against postgres.
    search = None
    if request.GET.get('search'):
        search = request.GET['search']
        incoming_emails = incoming_emails.filter(Q(subject__icontains=search) | Q(body_text__icontains=search) | Q(body_html__icontains=search))
        outgoing_emails = outgoing_emails.filter(Q(subject__icontains=search) | Q(body_text__icontains=search))

    hidden = not (request.GET.get('hidden') and request.GET['hidden'] == '0')
    if hidden:
        incoming_emails = incoming_emails.filter(hidden=False)
        outgoing_emails = outgoing_emails.filter(hidden=False)

    limit = 10
    if request.GET.get('limit'):
        limit = min([int(request.GET['limit']), MAX_EMAIL_LIMIT])
        incoming_emails = incoming_emails[:limit]
        outgoing_emails = outgoing_emails[:limit]

    emails = (
        [{'type': 'in', 'email': email} for email in incoming_emails] +
        [{'type': 'out', 'email': email} for email in outgoing_emails]
    )
    emails.sort(
        key=lambda email_ref: email_ref['email'].sent_time if email_ref['type'] == 'out' else email_ref['email'].received_time,
        reverse=True)

    teams = Team.objects.values_list('username', flat=True).order_by('username')
    interactions = Interaction.objects.values_list('url', flat=True).order_by('url')

    return render(request, 'spoilr/email/archive.tmpl', {
        'limit': limit,
        'hidden': hidden,
        'interaction': interaction.url if interaction else None,
        'team': team.username if team else None,
        'email': email or '',
        'search': search or '',
        'emails': emails,
        'teams': teams,
        'interactions': interactions,
    })
