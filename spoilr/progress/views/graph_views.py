import collections, colorsys, random

from django.http import JsonResponse
from django.shortcuts import render

from spoilr.core.models import Puzzle, PuzzleAccess, TeamType, Team
from spoilr.hq.util.decorators import hq

from hunt.app.core.constants import ROUND_RD0_URL, ROUND_SAMPLE_URL
from hunt.deploy.util import is_it_hunt

@hq()
def solve_graph_view(request):
    team_names_by_id = {
        team.id: truncate(team.name, 40)
        for team in Team.objects.exclude(type=TeamType.INTERNAL)
    }
    puzzle_names_by_id = {
        puzzle.id: puzzle.name
        for puzzle in Puzzle.objects.all()
    }

    solve_counts_by_team = collections.defaultdict(int)
    solve_counts_time_series_by_team = collections.defaultdict(list)
    puzzle_accesses = (
        PuzzleAccess.objects
            .exclude(team__type=TeamType.INTERNAL)
            .filter(solved=True, solved_time__isnull=False)
            .values_list('team_id', 'puzzle_id', 'solved_time')
            .order_by('solved_time')
    )

    show_prologue = request.GET.get('prologue') == '1'
    if is_it_hunt():
        if show_prologue:
            puzzle_accesses = puzzle_accesses.filter(puzzle__round__url=ROUND_RD0_URL)
        else:
            puzzle_accesses = puzzle_accesses.exclude(puzzle__round__url=ROUND_RD0_URL)

    for team_id, puzzle_id, solved_time in puzzle_accesses:
        solve_counts_by_team[team_id] += 1
        solved_time_as_unix = solved_time.timestamp() * 1000
        solve_counts_time_series_by_team[team_id].append(
            (solved_time_as_unix, solve_counts_by_team[team_id], puzzle_id))

    return render(request, 'spoilr/progress/solves.tmpl', {
        'is_it_hunt': is_it_hunt(),
        'show_prologue': show_prologue,
        'solve_counts_for_chartjs': {
            'datasets': [
                {
                    'label': team_names_by_id[team_id],
                    'data': [
                        {
                            'x': solve_count[0],
                            'y': solve_count[1],
                        } for solve_count in solve_counts
                    ],
                    'borderColor': team_id_to_line_color(team_id),
                    'fill': False,
                }
                for team_id, solve_counts in solve_counts_time_series_by_team.items()
            ],
            'pointLabels': [
                [
                    f'{team_names_by_id[team_id]} solved {puzzle_names_by_id[solve_count[2]]}, '
                    f'{solve_count[1]} {"puzzle" if solve_count[1] == 1 else "puzzles"} solved'
                    for solve_count in solve_counts
                ]
                for team_id, solve_counts in solve_counts_time_series_by_team.items()
            ],
        },
    })

# Access raw data via JSON so that we can experiment with different uses
# more flexibly.
@hq()
def solve_data_json_view(request):
    team_names_by_id = {
        team.id: truncate(team.name, 40)
        for team in Team.objects.exclude(type=TeamType.INTERNAL)
    }
    puzzle_names_by_id = {
        puzzle.id: puzzle.name
        for puzzle in Puzzle.objects.all()
    }

    solve_counts_by_team = collections.defaultdict(int)
    solve_counts_time_series_by_team = collections.defaultdict(list)
    puzzle_accesses = (
        PuzzleAccess.objects
            .exclude(team__type=TeamType.INTERNAL)
            .filter(solved=True, solved_time__isnull=False)
            .values_list('team_id', 'puzzle_id', 'solved_time')
            .order_by('solved_time')
            .exclude(puzzle__round__url=ROUND_RD0_URL)
    )

    for team_id, puzzle_id, solved_time in puzzle_accesses:
        solve_counts_by_team[team_id] += 1
        solved_time_as_unix = solved_time.timestamp() * 1000
        solve_counts_time_series_by_team[team_id].append(
            (solved_time_as_unix, solve_counts_by_team[team_id], puzzle_id))

    return JsonResponse({
      "data":
        [
          {
            "team": team_names_by_id[team_id],
            "solves": [
              {
                "puzzle": puzzle_names_by_id[solve_count[2]],
                "timestamp": solve_count[0],
                "solve_number": solve_count[1],
              }
              for solve_count in solve_counts],
          }
          for team_id, solve_counts in solve_counts_time_series_by_team.items()
        ]
      })

def team_id_to_line_color(team_id):
    old_seed = random.random()
    random.seed(team_id)
    r, g, b = colorsys.hls_to_rgb(random.random(), random.random() * 0.5 + 0.25, random.random() * 0.5 + 0.3)
    random.seed(old_seed)

    return f'rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, 1)'

def truncate(name, length):
    if len(name) > length - 3:
        return name[:length-3] + '...'
    return name
