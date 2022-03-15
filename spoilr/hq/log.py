from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from spoilr.core.models import *
from spoilr.hints.models import HintSubmission
from spoilr.hq.util.decorators import hq

@hq()
def system_log_view(request):
    entries = SystemLog.objects.select_related('team').order_by('-id')

    team = None
    if request.GET.get('team'):
        team = get_object_or_404(Team, username=request.GET['team'])
        entries = entries.filter(team=team)

    puzzle = None
    if request.GET.get('puzzle'):
        puzzle = get_object_or_404(Puzzle, url=request.GET['puzzle'])
        entries = entries.filter(object_id=puzzle.url)

    search = None
    if request.GET.get('search'):
        search = request.GET['search']
        entries = entries.filter(Q(message__icontains=search) | Q(object_id__icontains=search) | Q(event_type__icontains=search))

    limit = 200
    if request.GET.get('limit'):
        limit = min([int(request.GET['limit']), 5000])
    entries = entries[:int(limit)]

    teams = Team.objects.values_list('username', flat=True).order_by('username')
    puzzles = Puzzle.objects.values_list('url', flat=True).order_by('url')

    return HttpResponse(render(request, 'hq/log.html', {
        'limit': limit,
        'team': team.username if team else None,
        'puzzle': puzzle.url if puzzle else None,
        'search': search or '',
        'entries': entries,
        'teams': teams,
        'puzzles': puzzles,
    }))

@hq()
def hint_log_view(request, limit):
    entries = HintSubmission.objects.select_related('team', 'puzzle').prefetch_related('tasks').order_by('-id')
    if limit: entries = entries[:int(limit)]
    else: entries = entries[:int(1000)]
    entries = [
        {
            'entry': entry,
            'task': entry.tasks.first(),
        } for entry in entries
    ]
    return HttpResponse(render(request, 'hq/hint-log.html', {
        'limit': limit,
        'entries': entries,
    }))
