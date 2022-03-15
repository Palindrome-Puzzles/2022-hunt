from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import model_to_dict
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_POST

from spoilr.core.api.decorators import inject_team
from spoilr.core.models import Puzzle
from spoilr.events.models import EventParticipant, Event, EventStatus

from hunt.app.core.cache import cache_page_by_team
from hunt.app.core.hosts import use_site_2_if_unlocked
from hunt.deploy.util import require_hunt_launch
from .common import get_shared_context, verify_team_accessible

EVENT_DIXIT_URL = 'cryptic-dixit'
EVENT_DIXIT_CATEGORIES = ['animals', 'units', 'emotions', 'colors', 'directions']

EVENT_SESSION_MESSAGE_KEY = 'hunt:event:message'

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
def events_view(request):
    events = (Event.objects
        .prefetch_related(
            models.Prefetch(
                'participants',
                queryset=EventParticipant.objects.filter(team=request.team)
            ))
        .exclude(status=EventStatus.UNAVAILABLE)
        .order_by('expected_start_time'))

    context = get_shared_context(request.team)
    context['events'] = [
        {
            **model_to_dict(event),
            'puzzle_url': event.puzzle.url,
            'ordinal': i + 1,
            'participant_count': event.participants.all().count(),
            'dixit_categories': [
                EVENT_DIXIT_CATEGORIES[p.dixit_category]
                if p.dixit_category != None and 0 <= p.dixit_category < len(EVENT_DIXIT_CATEGORIES)
                else None
                for p in event.participants.all()
            ]
        } for i, event in enumerate(events)
    ]

    return render(request, 'top/events/all.tmpl', context)

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
def events_register_view(request, event_url):
    event = (Event.objects
        .filter(url=event_url)
        .prefetch_related(
            models.Prefetch(
                'participants',
                queryset=EventParticipant.objects.filter(team=request.team)
            ))
        .exclude(status=EventStatus.UNAVAILABLE)
        .first())
    if not event:
        return redirect(reverse('events'))

    dixit_category_counts = {}
    if event_url == EVENT_DIXIT_URL:
        dixit_category_counts = {
            summary['dixit_category']: summary['count']
            for summary in (EventParticipant.objects
                .filter(event__url=EVENT_DIXIT_URL)
                .values('dixit_category')
                .annotate(count=models.Count('dixit_category'))
                .order_by())
        }

    participants = event.participants.order_by('create_time')

    context = get_shared_context(request.team)
    context['event'] = event
    context['puzzle_url'] = event.puzzle.url
    context['name'] = []
    context['email'] = []
    context['pronouns'] = []
    context['message'] = ''
    context['error'] = ''
    context['dixit_category'] = []
    context['participant_count'] = len(participants)

    if request.session.get(EVENT_SESSION_MESSAGE_KEY):
        context['message'] = request.session[EVENT_SESSION_MESSAGE_KEY]
        del request.session[EVENT_SESSION_MESSAGE_KEY]
        request.session.save()

    if event.status == EventStatus.OPEN and request.POST:
        valid = True
        for i in range(event.max_participants):
            if i < len(participants) and not request.POST.get(f'name{i}'):
                context['error'] = f'Please enter a name for participant {i + 1}'
                valid = False
            if not request.POST.get(f'name{i}'):
                break
            if not request.POST.get(f'email{i}'):
                context['error'] = f'Please enter an email for participant {i + 1}'
                valid = False
            try:
                validate_email(request.POST.get(f'email{i}'))
            except ValidationError:
                context['error'] = f'Please enter a valid email for participant {i + 1}'
                valid = False

            context['name'].append(request.POST.get(f'name{i}', ''))
            context['email'].append(request.POST.get(f'email{i}', ''))
            context['pronouns'].append(request.POST.get(f'pronouns{i}', ''))

        if valid:
            for i in range(len(context['name'])):
                if i < len(participants.all()):
                    context['dixit_category'].append(participants[i].dixit_category)

                    participants[i].name = context['name'][i]
                    participants[i].email = context['email'][i]
                    participants[i].pronouns = context['pronouns'][i]
                    participants[i].save()
                else:
                    dixit_category = None
                    if event_url == EVENT_DIXIT_URL:
                        dixit_category = min(
                            range(len(EVENT_DIXIT_CATEGORIES)),
                            key=lambda i: dixit_category_counts.get(i, 0))
                        dixit_category_counts[i] = dixit_category_counts.get(i, 0) + 1

                    context['dixit_category'].append(dixit_category)

                    EventParticipant.objects.create(
                        event=event, team=request.team,
                        name=context['name'][i], email=context['email'][i],
                        pronouns=context['pronouns'][i],
                        dixit_category=dixit_category)

            # Avoid annoying POST refresh issue, but still show a message.
            if len(participants):
                request.session[EVENT_SESSION_MESSAGE_KEY] = 'Registration updated!'
            else:
                request.session[EVENT_SESSION_MESSAGE_KEY] = 'Registered!'
            request.session.save()
            return redirect(reverse('events_register', args=(event_url,)))

    else:
        for participant in participants:
            context['name'].append(participant.name)
            context['email'].append(participant.email)
            context['pronouns'].append(participant.pronouns)
            context['dixit_category'].append(participant.dixit_category)

    context['dixit_category'] = [
        EVENT_DIXIT_CATEGORIES[i]
        if i != None and 0 <= i < len(EVENT_DIXIT_CATEGORIES)
        else None
        for i in context['dixit_category']
    ]

    return render(request, 'top/events/register.tmpl', context)

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
def events_unregister_view(request, event_url):
    event = (Event.objects
        .filter(url=event_url)
        .prefetch_related(
            models.Prefetch(
                'participants',
                queryset=EventParticipant.objects.filter(team=request.team)
            ))
        .exclude(status=EventStatus.UNAVAILABLE)
        .first())
    if not event:
        return redirect(reverse('events'))

    if event.status == EventStatus.OPEN:
        participants = event.participants.all()
        raw_index = request.GET.get('index', '')
        index = int(raw_index) if raw_index.isdigit() else len(participants)
        if index < len(participants):
            participants[index].delete()
    return redirect(reverse('events_register', args=(event_url,)))
