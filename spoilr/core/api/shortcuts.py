from spoilr.core.api.answer import submit_puzzle_answer
from spoilr.core.api.hunt import release_puzzle, release_round
from spoilr.core.api.progress import clear_all_progress
from spoilr.core.models import Minipuzzle, MinipuzzleSubmission

def get_shortcuts():
    shortcuts = []
    for action, callback in Shortcuts.__dict__.items():
        if action.startswith('__'):
            continue
        shortcuts.append({'action': action, 'name': callback.__doc__})
    return shortcuts

class Shortcuts:
    def solve(puzzle, team):
        'Solve this puzzle'
        release_round(team, puzzle.round)
        release_puzzle(team, puzzle)
        submit_puzzle_answer(team, puzzle, puzzle.answer)

    def unsolve(puzzle, team):
        'Clear puzzle progress'
        team.puzzlesubmission_set.filter(puzzle=puzzle).delete()
        team.puzzleaccess_set.filter(puzzle=puzzle).update(solved=False)
        team.interactionaccess_set.filter(interaction__interactiondata__puzzle_trigger=puzzle).delete()

        Minipuzzle.objects.filter(team=team, puzzle=puzzle).delete()
        MinipuzzleSubmission.objects.filter(
            minipuzzle__team=team, minipuzzle__puzzle=puzzle).delete()

        clear_all_progress(team, puzzle)

    def toggle_access(puzzle, team):
        'Toggle access to puzzle'
        puzzle_access = team.puzzleaccess_set.filter(puzzle=puzzle).first()
        if puzzle_access:
            puzzle_access.delete()
        else:
            release_round(team, puzzle.round)
            release_puzzle(team, puzzle)

    def unanswered_hint(puzzle, team):
        'Request hint'
        team.hintsubmission_set.update_or_create(
            puzzle=puzzle, question__iexact='Halp',
            defaults={'question': 'Halp', 'resolved__time': None, 'result': None})

    def answered_hint(puzzle, team):
        'Answered hint'
        team.hintsubmission_set.update_or_create(
            puzzle=puzzle, question__iexact='Halp',
            defaults={'question': 'Halp', 'resolved__time': None, 'result': 'Ok'})

    def delete_hints(puzzle, team):
        'Clear hints'
        team.hintsubmission_set.filter(puzzle=puzzle).delete()
