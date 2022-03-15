import datetime

from django import template
from django.utils.timezone import now
from hunt.deploy.util import is_autopilot

register = template.Library()

@register.filter
def has_been_available_for_minutes(puzzle, duration):
    """
    Returns whether the puzzle has been available for at least the specified
    duration in minutes.
    """
    if is_autopilot():
        return True

    desired_time = puzzle['unlock_time'] + datetime.timedelta(minutes=duration)
    return now() >= desired_time

@register.filter
def until_available_for_minutes(puzzle, duration):
    """
    Returns how many minutes remain until the puzzle has been available for at
    least the specified duration in minutes
    """
    if is_autopilot():
        return 0

    desired_time = puzzle['unlock_time'] + datetime.timedelta(minutes=duration)
    remaining_time = desired_time - now()

    remaining_time = datetime.timedelta(minutes=duration) + puzzle['unlock_time'] - now()
    return max(remaining_time // datetime.timedelta(minutes=1), 0)

@register.filter
def is_puzzle_solved(puzzle_infos, puzzle_external_id):
    puzzle_info = next(
        (puzzle_info for puzzle_info in puzzle_infos if puzzle_info['puzzle'].external_id == puzzle_external_id),
        None)
    return bool(puzzle_info and puzzle_info['solved'])

@register.filter
def is_puzzle_available(puzzle_infos, puzzle_external_id):
    puzzle_info = next(
        (puzzle_info for puzzle_info in puzzle_infos if puzzle_info['puzzle'].external_id == puzzle_external_id),
        None)
    return bool(puzzle_info)

@register.filter
def has_interaction(ias, interaction_url):
    ia = next(
        (ia for ia in ias if ia.interaction.url == interaction_url),
        None)
    return bool(ia and ia.accomplished)

@register.filter
def solve_count(puzzles):
    feeders_solved = len(list(puzzle for puzzle in puzzles if puzzle['solved']))
    return feeders_solved
