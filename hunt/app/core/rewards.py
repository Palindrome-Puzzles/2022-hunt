import re
from more_itertools import partition

from django.shortcuts import reverse
from django.template import loader

from hunt.app.core.assets.refs import get_round_static_path
from hunt.app.core.constants import ROUND_RD0_URL, PUZZLES_WITH_REWARDS, ROUND_URLS_WITH_BONUS_CONTENT, EVENT_PUZZLE_MANUSCRIP, ROUND_SAMPLE_URL, ROUND_EVENTS_URL, PUZZLE_ENDGAME_URL

from spoilr.core.api.events import HuntEvent

def get_rewards(rounds_summary):
    rewards = {}
    for round_summary in rounds_summary:
        reward = get_reward(round_summary)
        if reward:
            slug = re.sub(r'\-','', round_summary['round'].url)
            rewards[slug] = reward
    return rewards

def get_reward(round_summary):
    for round_puzzle in PUZZLES_WITH_REWARDS:
        if round_summary['round'].url == round_puzzle[0]:
            puzzle = next((puzzle_info for puzzle_info in round_summary['puzzles'] if puzzle_info['puzzle'].external_id == round_puzzle[1]), None)
            if puzzle and puzzle['solved']:
                return {
                    'rd_root': get_round_static_path(round_summary['round'].url, variant='round'),
                }
    return None

def get_reward_info(event_type, puzzle, team):
    from spoilr.core.models import InteractionAccess
    from hunt.deploy.util import is_autopilot

    if not puzzle or not team or team.is_public: return

    if (puzzle.round.url, puzzle.external_id) in PUZZLES_WITH_REWARDS:
        solved = puzzle.puzzleaccess_set.filter(team=team, solved=True).exists()
        if solved:
            context = {
                'reward': {
                  'rd_root': get_round_static_path(puzzle.round.url, variant='round'),
                },
                'completed_interactions':
                    InteractionAccess.objects.filter(team=team, accomplished=True),
                'showing_all': False,
                'is_autopilot': is_autopilot(),
            }
            html = loader.render_to_string(f'round_files/{puzzle.round.url}/reward.tmpl', context, request=None)
            url = reverse('puzzle_view', args=(puzzle.url,))
            if puzzle.url == PUZZLE_ENDGAME_URL:
                url = reverse('endgame_puzzle')
            return {
                'html': html,
                'url': url,
            }
    return None

def get_manuscrip_info(team):
    from hunt.app.models import FreeUnlockRequest, FreeUnlockStatus
    from spoilr.core.models import Puzzle, PuzzleAccess

    solved_events = PuzzleAccess.objects.select_related('puzzle').filter(team=team, puzzle__external_id__in=EVENT_PUZZLE_MANUSCRIP.keys(), solved=True).values_list('puzzle__external_id', flat=True)
    manuscrip = sum(EVENT_PUZZLE_MANUSCRIP[puzzle_id] for puzzle_id in solved_events)
    unlocks = FreeUnlockRequest.objects.select_related('puzzle').order_by('status').filter(team=team)
    pending_unlocks = list(unlock for unlock in unlocks if unlock.status == FreeUnlockStatus.NEW)
    unlocked = list(unlock for unlock in unlocks if unlock.status == FreeUnlockStatus.APPROVED)

    return {
        'manuscrip': manuscrip,
        'net_manuscrip': max(manuscrip - len(unlocked) - len(pending_unlocks), 0),
        'pending_unlock': pending_unlocks[0] if len(pending_unlocks) else None,
        'unlocked': unlocked,
        'all_unlocks': unlocks,
        'can_unlock': manuscrip - len(unlocked) - len(pending_unlocks) >= 1 and len(pending_unlocks) == 0,
        # There are puzzles we can't use manuscrip on.
        'available_puzzles': Puzzle.objects
            .filter(
                puzzleaccess__team=team, puzzleaccess__solved=False,
                puzzledata__unlock_order__isnull=False)
            .exclude(round__url__in=(ROUND_SAMPLE_URL, ROUND_EVENTS_URL, ROUND_RD0_URL)),
    }

def get_bonus_content(puzzle, team):
    if not puzzle.is_meta and puzzle.round.url in ROUND_URLS_WITH_BONUS_CONTENT:
        is_solved = (
            puzzle.puzzleaccess_set.filter(team=team, solved=True).exists() or
            team.is_public)
        if is_solved:
            context = {
                'puzzle_info': {
                    'puzzle': puzzle,
                    'solved': True
                },
                'team': team,
                'rd_root': get_round_static_path(puzzle.round.url, variant='round')
            }
            html = loader.render_to_string(f'round_files/{puzzle.round.url}/submissions.tmpl', context, request=None)
            return {
                'html': html,
                'url': reverse('puzzle_view', args=(puzzle.url,))
            }
