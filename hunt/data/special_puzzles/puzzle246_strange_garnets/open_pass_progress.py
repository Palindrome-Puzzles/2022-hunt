"""
Puzzle progress tracking for the Open, Pass minipuzzle in "Genius Game".
"""

from django.db import models

from spoilr.core.api.answer import mark_minipuzzle_solved

from hunt.app.special_puzzles.team_progress_plugin import team_puzzle_progressed, get_team_puzzle_progress
from .common import P246StrangeGarnetsProgressModel, OPEN_PASS_TARGETS, OPEN_PASS_MINIPUZZLE_REF

FIRST_LEVEL = min(OPEN_PASS_TARGETS.keys())
LAST_LEVEL = max(OPEN_PASS_TARGETS.keys())

class P246StrangeGarnetsOpenPassProgressModel(models.Model):
    progress = models.ForeignKey(P246StrangeGarnetsProgressModel, on_delete=models.CASCADE, related_name='open_pass_levels')
    level = models.PositiveSmallIntegerField()
    won = models.BooleanField()

    class Meta:
        unique_together = [['progress', 'level']]

def maybe_initialize_progress(progress):
    P246StrangeGarnetsOpenPassProgressModel.objects.get_or_create(
        progress=progress,
        level=1,
        defaults={'won': False})

def project_progress(progress):
    return {
        'levels': [
            {
                'level': level_info.level,
                'target': OPEN_PASS_TARGETS[level_info.level],
                'won': level_info.won,
            } for level_info in progress.open_pass_levels.all()
        ],
    }

def has_access_to_level(team, puzzle, level):
    return P246StrangeGarnetsOpenPassProgressModel.objects.filter(
        progress__team=team,
        progress__puzzle=puzzle,
        level=level
    ).exists()

def mark_level_as_won(team, puzzle, level):
    progress = get_team_puzzle_progress(
        P246StrangeGarnetsProgressModel, team, puzzle)
    P246StrangeGarnetsOpenPassProgressModel.objects.update_or_create(
        progress=progress,
        level=level,
        defaults={'won': True})

    if level == LAST_LEVEL:
        mark_minipuzzle_solved(team, puzzle, OPEN_PASS_MINIPUZZLE_REF)

    else:
        P246StrangeGarnetsOpenPassProgressModel.objects.get_or_create(
            progress=progress,
            level=level + 1,
            defaults={'won': False})

    team_puzzle_progressed(P246StrangeGarnetsProgressModel, team, puzzle)
