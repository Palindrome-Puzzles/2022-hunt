import json

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from spoilr.core.api.events import dispatch, HuntEvent
from spoilr.core.api.decorators import inject_puzzle
from spoilr.core.models import Puzzle, Round, Team
from spoilr.email.models import OutgoingMessage
from spoilr.hints.models import HintSubmission
from spoilr.hq.models import Task, TaskStatus, HqLog
from spoilr.hq.util.decorators import hq
from spoilr.hq.util.redirect import redirect_with_message

from hunt.data_loader.puzzle import get_puzzle_data_text

MAX_HINT_LIMIT = 200

@hq()
def dashboard_view(request):
    hints = (HintSubmission.objects
        .filter(tasks__isnull=False)
        .select_related('puzzle', 'team')
        .prefetch_related('tasks')
        .order_by('-update_time'))

    team = None
    puzzle = None
    open_only = False
    limit = 10
    hint_id = None

    if request.GET.get('hint'):
        hints = hints.filter(id=request.GET['hint'])
    else:
        if request.GET.get('team'):
            team = get_object_or_404(Team, username=request.GET['team'])
            hints = hints.filter(team=team)

        if request.GET.get('puzzle'):
            puzzle = get_object_or_404(Puzzle, url=request.GET['puzzle'])
            hints = hints.filter(puzzle=puzzle)

        if request.GET.get('open') == '1':
            open_only = True
            hints = hints.filter(resolved_time__isnull=True, tasks__status=TaskStatus.PENDING)

        if request.GET.get('limit'):
            limit = min([int(request.GET['limit']), MAX_HINT_LIMIT])
            hints = hints[:limit]

    teams = Team.objects.values_list('username', flat=True).order_by('username')
    puzzles = Puzzle.objects.values_list('url', flat=True).order_by('url')

    return render(request, 'spoilr/hints/dashboard.tmpl', {
        'hints': [
            {
                'hint': hint,
                'task': hint.tasks.first(),
                'total_team_puzzle_hints' : len((HintSubmission.objects.filter(team=hint.team, puzzle=hint.puzzle)))
            } for hint in hints
        ],
        'limit': limit,
        'open_only': open_only,
        'team': team.username if team else None,
        'puzzle': puzzle.url if puzzle else None,
        'teams': teams,
        'puzzles': puzzles,
    })

@require_POST
@hq(require_handler=True)
def respond_view(request):
    confirm = request.POST.get('confirm')
    response = request.POST.get('response', '').strip()
    if confirm.lower() != 'respond':
        return redirect_with_message(request, 'spoilr.hints:dashboard', 'Hint response was not confirmed.')

    hint_id = int(request.POST.get('id'))
    hint = HintSubmission.objects.select_related('team', 'puzzle').get(id=hint_id) if hint_id else None
    if not hint or not response:
        return HttpResponseBadRequest('Missing or invalid fields')

    task = hint.tasks.first()
    if not task or task.handler != request.handler:
        return redirect_with_message(
            request, 'spoilr.hints:dashboard', f'You are no longer handling this hint.')
    if task.status == TaskStatus.DONE:
        return redirect_with_message(request, 'spoilr.hints:dashboard', 'Hint is already done.')

    hint.result = response
    hint.resolved_time = now()
    hint.save()

    task.status = TaskStatus.DONE
    task.snooze_time = None
    task.snooze_until = None
    task.save()

    HqLog.objects.create(
        handler=request.handler, event_type='hint-resolved',
        object_id=hint.puzzle.id, message=f'Resolve hint {hint}')

    dispatch(
        HuntEvent.HINT_RESOLVED, team=hint.team, puzzle=hint.puzzle, hint=hint, object_id=hint.puzzle.url,
        message=f'Resolved hint for {hint.team.name} about {hint.puzzle}')

    if settings.SPOILR_HINTS_FROM_EMAIL and hint.email:
        subject = f'Hint Response for {hint.puzzle.name}'
        full_response = response + '\n---\n\n' + 'Your original hint request is below.' + '\n--\n\n' + hint.question
        send_mail(
            subject, full_response, settings.SPOILR_HINTS_FROM_EMAIL,
            [hint.email])
        OutgoingMessage.objects.create(
            subject=subject, body_text=full_response,
            sender=settings.SPOILR_HINTS_FROM_EMAIL,
            recipient=hint.email, team=hint.team,
            automated=True, handler=request.handler)

    return redirect_with_message(request, 'spoilr.hints:dashboard', 'Hint resolved.')

@hq()
@inject_puzzle(error_if_inaccessible=True)
def canned_hints_view(request):
    '''View for canned hints available to team.'''
    puzzle = request.puzzle

    context = {}
    context['puzzle'] = puzzle
    context['canned_hints'] = get_canned_hints(puzzle.url)

    return render(request, 'spoilr/hints/canned.tmpl', context)

# TODO(sahil): Load hints into the database so we're not depending on hunt-specific
# data loaders.
def get_canned_hints(puzzle_url):
    '''Returns canned hints from puzzle data.'''
    hints = get_puzzle_data_text(puzzle_url, 'hints.json')
    if hints:
        return json.loads(hints)
    return []
