import collections
from functools import cmp_to_key

from django.db import models
from django.db.models import Prefetch
from django.shortcuts import render
from django.utils.timezone import now

from hunt.app.models import InteractionType
from hunt.app.core.constants import ROUND_SAMPLE_URL, ROUND_RD0_URL
from spoilr.core.models import PuzzleAccess, TeamType, Round, Puzzle, Interaction, InteractionAccess, Team, SystemLog, Minipuzzle
from spoilr.contact.models import ContactRequest
from spoilr.hq.util.decorators import hq

@hq()
def teams_view(request):
    # TODO(sahil): Also display progress in the fantasy minipuzzles, and the amount of
    # manuscrip available to each team.
    all_teams = list(Team.objects.exclude(type=TeamType.INTERNAL))
    latest_log_ids_by_team = SystemLog.objects.filter(team__isnull=False).values('team_id').annotate(max_log_id=models.Max('id')).values_list('max_log_id', flat=True)
    latest_logs_by_team = {
        log.team_id: log for log in SystemLog.objects.filter(id__in=latest_log_ids_by_team)
    }

    all_rounds = Round.objects.exclude(url=ROUND_SAMPLE_URL).order_by('order')
    all_puzzles = Puzzle.objects.exclude(round__url=ROUND_SAMPLE_URL).order_by('is_meta', 'order')
    all_interactions = Interaction.objects.all().order_by('order')

    all_puzzles_by_round = collections.defaultdict(list)
    for puzzle in all_puzzles:
        all_puzzles_by_round[puzzle.round_id].append(puzzle)

    puzzles_solved_by_team = collections.defaultdict(set)
    puzzles_accessible_by_team = collections.defaultdict(set)
    for puzzle_access in PuzzleAccess.objects.exclude(team__type=TeamType.INTERNAL).exclude(puzzle__round__url=ROUND_RD0_URL):
        team_id = puzzle_access.team_id
        puzzle_id = puzzle_access.puzzle_id

        puzzles_accessible_by_team[team_id].add(puzzle_id)
        if puzzle_access.solved:
            puzzles_solved_by_team[team_id].add(puzzle_id)

    interactions_accessible_by_team = collections.defaultdict(set)
    interactions_solved_by_team = collections.defaultdict(set)
    for interaction_access in InteractionAccess.objects.exclude(team__type=TeamType.INTERNAL):
        team_id = interaction_access.team_id
        interaction_id = interaction_access.interaction_id

        interactions_accessible_by_team[team_id].add(interaction_id)
        if interaction_access.accomplished:
            interactions_solved_by_team[team_id].add(interaction_id)

    contact_info = ContactRequest.objects.exclude(resolved_time__isnull=False, team__type=TeamType.INTERNAL).values('team_id').annotate(count=models.Count('id'))
    contact_count_by_team = {
        result['team_id']: result['count']
        for result in contact_info
    }

    teams = []
    for team in all_teams:
        p_released = len(puzzles_accessible_by_team[team.id])
        p_solved = len(puzzles_solved_by_team[team.id])
        rounds = []
        for round in all_rounds:
            puzzles = []
            for puzzle in all_puzzles_by_round[round.id]:
                puzzles.append(get_encoded_puzzle(
                    puzzle,
                    accessible=(puzzle.id in puzzles_accessible_by_team[team.id]),
                    solved=(puzzle.id in puzzles_solved_by_team[team.id])))
            num_released = len(list(puzzle for puzzle in all_puzzles_by_round[round.id] if puzzle.id in puzzles_accessible_by_team[team.id]))
            num_solved = len(list(puzzle for puzzle in all_puzzles_by_round[round.id] if puzzle.id in puzzles_solved_by_team[team.id]))
            if num_released > 0:
                rounds.append({
                    'round': round,
                    'puzzles': puzzles,
                    'released': any((puzzle.id in puzzles_accessible_by_team[team.id]) for puzzle in all_puzzles_by_round[round.id]),
                    'solved': (
                        sum(puzzle.is_meta for puzzle in all_puzzles_by_round[round.id]) and
                        all(
                            puzzle.id in puzzles_solved_by_team[team.id]
                            for puzzle in all_puzzles_by_round[round.id]
                            if puzzle.is_meta)),
                    'num_released': num_released,
                    'num_solved': num_solved,
                })

        i_released = len(interactions_accessible_by_team[team.id])
        i_solved = sum(interactions_solved_by_team[team.id])
        interactions = []
        for interaction in all_interactions:
            interactions.append(get_encoded_interaction(
                interaction,
                accessible=(interaction.id in interactions_accessible_by_team[team.id]),
                solved=(interaction.id in interactions_solved_by_team[team.id])))

        teams.append({
            'team': team,
            'rounds': rounds,
            'interactions': interactions,
            'log1': latest_logs_by_team.get(team.id),
            'r_released': sum(round['released'] for round in rounds),
            'r_solved': sum(round['solved'] for round in rounds),
            'p_released': p_released,
            'p_solved': p_solved,
            'p_open': p_released - p_solved,
            'q_submissions': contact_count_by_team.get(team.id, 0),
            'i_released': i_released,
            'i_solved': i_solved,
            'i_open': i_released - i_solved,
        })

    teams.sort(key=lambda x: (-x['r_solved'], -x['p_solved']))
    context = {
        'teams': teams,
        'r_total': len(all_rounds),
        'p_total': len(all_puzzles),
        'i_pending': sum(team['i_open'] for team in teams),
        'i_teams': len(list(team for team in teams if team['i_open'] > 0)),
        'i_total': len(all_interactions),
        'all_interactions': all_interactions,
        'all_puzzles': all_puzzles,
    }
    return render(request, 'spoilr/progress/teams.tmpl', context)

def get_encoded_puzzle(puzzle, *, accessible, solved):
    ret = 'p'
    ret += 'r' if puzzle.is_meta else 'p'
    ret += 's' if solved else 'r' if accessible else 'u'
    return ret + str(puzzle.id)

def get_encoded_interaction(interaction, *, accessible, solved):
    ret = 'ip'
    ret += 's' if solved else 'f' if accessible else 'u'
    return ret + str(interaction.id)

@hq()
def puzzles_view(request):
    all_rounds = Round.objects.order_by('order')
    all_puzzles = Puzzle.objects.all().order_by('is_meta', 'order')
    all_interactions = Interaction.objects.all().order_by('order')

    solved_by_puzzle_and_team = collections.defaultdict(dict)
    first_release_by_puzzle = dict()
    for puzzle_access in PuzzleAccess.objects.exclude(team__type=TeamType.INTERNAL).order_by('timestamp'):
        solved_by_puzzle_and_team[puzzle_access.puzzle_id][puzzle_access.team_id] = puzzle_access.solved
        first_release_by_puzzle.setdefault(puzzle_access.puzzle_id, puzzle_access.timestamp)

    t_total = Team.objects.exclude(type=TeamType.INTERNAL).count()
    p_total = len(all_puzzles)
    m_total = 0
    p_released = 0
    p_solved = 0

    rounds_lookup = {}
    for round in all_rounds:
        rounds_lookup[round.id] = {
            'round': round,
            'puzzles': [],
        }
    for puzzle in all_puzzles:
        released = len(solved_by_puzzle_and_team[puzzle.id])
        solved = sum(solved_by_puzzle_and_team[puzzle.id].values())
        if released > 0: p_released += 1
        if solved > 0: p_solved += 1
        if puzzle.is_meta: m_total += 1
        rounds_lookup[puzzle.round_id]['puzzles'].append({
            'puzzle': puzzle,
            'first': first_release_by_puzzle.get(puzzle.id, None),
            'released': released,
            'releasedp': percent(released, t_total),
            'solved': solved,
            'solvedp': percent(solved, released),
        })

    context = {
        'rounds': rounds_lookup.values(),
        't_total': t_total,
        'p_total': p_total,
        'm_total': m_total,
        'p_released': p_released,
        'p_releasedp': percent(p_released, p_total),
        'p_solved': p_solved,
        'p_solvedp': percent(p_solved, p_released),
    }
    return render(request, 'spoilr/progress/puzzles.tmpl', context)

@hq()
def puzzle_view(request, puzzle_id):
    puzzle = Puzzle.objects.get(external_id=puzzle_id)
    all_teams = Team.objects.prefetch_related(
        Prefetch(
            'puzzleaccess_set',
            queryset=PuzzleAccess.objects.filter(puzzle_id=puzzle.id)
        )).exclude(type=TeamType.INTERNAL)

    teams_data = []
    for team in all_teams:
        access = team.puzzleaccess_set.first()
        solve_duration = None
        if access and access.solved:
            solve_duration = access.solved_time - access.timestamp
        released_duration = None
        if access and access.timestamp:
            released_duration = now() - access.timestamp
        teams_data.append({
            'access': access,
            'team': team,
            'solve_duration': solve_duration,
            'released_duration': released_duration
        })
    def sort_team_data(team1, team2):
        access1 = team1.get('access')
        access2 = team2.get('access')
        if access1 and access1.solved:
            if access2 and access2.solved:
                return (team2['solve_duration'] - team1['solve_duration']).total_seconds()
            return 1
        elif access1:
            if access2 and access2.solved:
                return -1
            elif access2:
                return (access1.timestamp - access2.timestamp).total_seconds()
            return 1
        if access2:
            return -1
        return 0
    teams_data.sort(key=cmp_to_key(sort_team_data), reverse=True)
    context = {
        'puzzle': puzzle,
        'teams': teams_data
    }
    return render(request, 'spoilr/progress/puzzle.tmpl', context)

@hq()
def interactions_view(request):
    all_interactions = Interaction.objects.all().order_by('order')

    solved_by_interaction_and_team = collections.defaultdict(dict)
    for interaction_access in InteractionAccess.objects.exclude(team__type=TeamType.INTERNAL).order_by('create_time'):
        solved_by_interaction_and_team[interaction_access.interaction_id][interaction_access.team_id] = interaction_access.accomplished

    t_total = Team.objects.exclude(type=TeamType.INTERNAL).count()

    interactions = []
    for interaction in all_interactions:
        released = len(solved_by_interaction_and_team[interaction.id])
        solved = sum(solved_by_interaction_and_team[interaction.id].values())
        interactions.append({
            'interaction': interaction,
            'released': released,
            'releasedp': percent(released, t_total),
            'solved': solved,
            'solvedp': percent(solved, released),
        })

    context = {
        'interactions': interactions,
        't_total': t_total,
        'i_total': len(all_interactions),
    }
    return render(request, 'spoilr/progress/interactions.tmpl', context)

def percent(n, d):
    return f'{n*100//d}%' if d else '-'

@hq()
def team_view(request, team_username):
    all_rounds = Round.objects.order_by('order')
    all_puzzles = Puzzle.objects.select_related('round').order_by('round__order', 'order')
    all_interactions = Interaction.objects.all().order_by('order')

    team = (Team.objects
        .select_related('teamregistrationinfo')
        .prefetch_related('user_set', 'roundaccess_set', 'puzzleaccess_set', 'interactionaccess_set', 'hintsubmission_set')
        .get(username=team_username))
    all_round_accesses = {x.round_id: x for x in team.roundaccess_set.all()}
    all_puzzle_accesses = {x.puzzle_id: x for x in team.puzzleaccess_set.all()}
    all_interaction_accesses = {x.interaction_id: x for x in team.interactionaccess_set.all()}

    hint_info = team.hintsubmission_set.values('puzzle_id').annotate(count=models.Count('id'))
    hint_count_by_puzzle = {
        result['puzzle_id']: result['count']
        for result in hint_info
    }

    rounds = []
    for round in all_rounds:
        rounds.append({
            'round': round,
            'access': all_round_accesses.get(round.id, None),
        })

    puzzles = []
    for puzzle in all_puzzles:
        access = all_puzzle_accesses.get(puzzle.id, None)
        solve_time = None
        if access and access.solved:
            solve_time = access.solved_time - access.timestamp
        puzzles.append({
            'puzzle': puzzle,
            'access': access,
            'hints': hint_count_by_puzzle.get(puzzle.id, 0),
            'solve_time': solve_time,
        })

    interactions = []
    for interaction in all_interactions:
        interactions.append({
            'interaction': interaction,
            'access': all_interaction_accesses.get(interaction.id, None),
        })

    context = {
        'team': team,
        'rounds': rounds,
        'puzzles': puzzles,
        'interactions': interactions,
        'hints': sum(hint_count_by_puzzle.values()),
    }
    return render(request, 'spoilr/progress/team.tmpl', context)
