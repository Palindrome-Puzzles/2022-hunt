"""
Minipuzzle answer checker for the puzzle "Fruit Around".
"""
from hunt.app.views.puzzle_submit_views import minipuzzle_answers_view_factory

MINIPUZZLE_ANSWERS = {
    'zoo': 'OFF',
    'lamb': 'LEVEL',
    'color': 'NUMBERTHEORY',
    'motion': 'HANDSEWN',
    'nonsense': 'EDICT',
}

answers_view = minipuzzle_answers_view_factory(MINIPUZZLE_ANSWERS)