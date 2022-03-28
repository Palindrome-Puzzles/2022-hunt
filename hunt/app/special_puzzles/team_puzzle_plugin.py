import logging

from spoilr.core.models import PuzzleAccess, Puzzle

from hunt.app.core.team_consumer import AccessDeniedException, get_channel_layer_group_name
from hunt.app.core.plugins import Plugin

logger = logging.getLogger(__name__)

class TeamPuzzlePlugin(Plugin):
    """
    Plugin for a TeamConsumer that authenticates that the team has access to a
    specified puzzle before allowing team communication.

    Only one of these plugins may be added to a consumer.

    The consumer must pass a `puzzle_external_id` argument when creating the plugin, to
    indicate which puzzle this consumer is managing teamwork for.
    """
    plugin_name = 'puzzle'

    # The current puzzle object for this consumer, or None if the user is
    # not connected or not authenticated yet.
    puzzle = None

    def __init__(self, puzzle_external_id):
        self.puzzle_external_id = puzzle_external_id

    @property
    def team_puzzle_group_type(self):
        return _team_puzzle_group_type(self.puzzle_external_id)

    def authenticate(self, team, auth_message):
        puzzle = Puzzle.objects.get(external_id=self.puzzle_external_id)
        has_puzzle_access = PuzzleAccess.objects.filter(team=team, puzzle=puzzle).exists()
        if not team.is_admin and not has_puzzle_access:
            logger.info(f'{team.username} attempted to access {puzzle.name} without unlocking it.')
            raise AccessDeniedException()

        self.puzzle = puzzle
        self.has_puzzle_access = has_puzzle_access

def get_team_puzzle_group_name(team, puzzle_external_id):
    """Returns the name used by the channel layer for team puzzle notifications."""
    return get_channel_layer_group_name(team, _team_puzzle_group_type(puzzle_external_id))

def _team_puzzle_group_type(puzzle_external_id):
    return f'puzzle.{puzzle_external_id}'
