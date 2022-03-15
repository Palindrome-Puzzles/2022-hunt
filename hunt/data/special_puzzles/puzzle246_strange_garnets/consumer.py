"""
Puzzle progress for the puzzle "Strange Garnets".

It has minipuzzle answer checkers, plus a couple of minipuzzles that the team
needs to win before an answer is available
"""
from hunt.app.core.team_consumer import TeamConsumer

from hunt.app.special_puzzles.team_minipuzzle_plugin import TeamMinipuzzlePlugin
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_progress_plugin import TeamProgressPlugin

from .common import P246StrangeGarnetsProgressModel, MINIPUZZLE_ANSWERS
from .open_pass_progress import project_progress as project_open_pass_progress, maybe_initialize_progress as maybe_initialize_open_pass_progress

class P246StrangeGarnetsConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        self.add_plugin(TeamPuzzlePlugin(246))
        self.add_plugin(TeamMinipuzzlePlugin(MINIPUZZLE_ANSWERS))
        self.add_plugin(TeamProgressPlugin(
            P246StrangeGarnetsProgressModel,
            project_progress=project_progress,
            maybe_initialize_progress=maybe_initialize_progress))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

def project_progress(progress):
    return {
        'game6': project_open_pass_progress(progress),
    }

def maybe_initialize_progress(progress):
    maybe_initialize_open_pass_progress(progress)
