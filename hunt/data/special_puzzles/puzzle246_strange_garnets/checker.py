"""
Minipuzzle answer checker for the puzzle "Strange Garnets".
"""
from hunt.app.views.puzzle_submit_views import minipuzzle_answers_view_factory

from .common import MINIPUZZLE_ANSWERS

answers_view = minipuzzle_answers_view_factory(MINIPUZZLE_ANSWERS)
