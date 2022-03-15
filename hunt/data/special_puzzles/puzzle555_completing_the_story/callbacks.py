from hunt.app.core.constants import PUZZLE_ENDGAME_URL

from spoilr.core.api.events import register, HuntEvent

def on_minipuzzle_attempted(team, puzzle, minipuzzle_ref, is_correct, **kwargs):
    if is_correct and puzzle.url == PUZZLE_ENDGAME_URL:
        from .progress import P555CTSProgressModel
        from hunt.app.special_puzzles.team_progress_plugin import team_puzzle_progressed

        team_puzzle_progressed(P555CTSProgressModel, team, puzzle)

register(HuntEvent.MINIPUZZLE_ATTEMPTED, on_minipuzzle_attempted)
