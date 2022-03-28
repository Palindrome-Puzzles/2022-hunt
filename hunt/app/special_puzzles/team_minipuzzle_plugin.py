import logging, time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models, transaction
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.forms.models import model_to_dict

from spoilr.core.api.answer import canonicalize_puzzle_answer_display, maybe_initialize_minipuzzle
from spoilr.core.api.events import HuntEvent, register
from spoilr.core.models import Minipuzzle, MinipuzzleSubmission, Team

from hunt.app.core.helpers import omit
from hunt.app.core.plugins import Plugin

from .team_puzzle_plugin import get_team_puzzle_group_name

logger = logging.getLogger(__name__)

class TeamMinipuzzlePlugin(Plugin):
    """
    Plugin for a TeamConsumer that tracks minipuzzles within a puzzle and
    synchronizes the state across the team.

    It will send messages to the client with the following keys:
     - `type`: 'minipuzzle'.
     - `updates`: A list of dict with the following keys:
         - `ref`: The minipuzzle ref
         - `solved`: A boolean
         - `answer`: A string that will be present if solved, or `null`
         - `submissions`: A list of dicts with the following keys:
             - `create_time`
             - `answer`
             - `correct`

            Only updated minipuzzles will be included in the list.

            (If the minipuzzle answer is granted to solvers through say winning
            a minigame, then `submissions` will always be empty.)
    """
    plugin_name = 'minipuzzle'

    def __init__(self, answers_by_ref):
        super().__init__()
        self.answers_by_ref = answers_by_ref

    def verify_plugin(self):
        self.parent.assert_has_plugin('puzzle')

    def joined(self):
        for ref in self.answers_by_ref.keys():
            maybe_initialize_minipuzzle(
                self.parent.team, self.get_sibling_plugin('puzzle').puzzle, ref)

        self.send_minipuzzles()

    def hunt_team_minipuzzle(self, message):
        """Handler for the channel layer message with type `hunt.team.minipuzzle`."""
        if not self.get_sibling_plugin('puzzle').has_puzzle_access:
            return

        if (message['puzzle_external_id'] == self.get_sibling_plugin('puzzle').puzzle_external_id):
            self.send_minipuzzles(message['minipuzzle_ref'])

    def send_minipuzzles(self, minipuzzle_ref=None):
        extra_filters = {} if minipuzzle_ref == None else {'ref': minipuzzle_ref}
        minipuzzles = Minipuzzle.objects.filter(
            team=self.parent.team,
            puzzle=self.get_sibling_plugin('puzzle').puzzle,
            **extra_filters
        )

        updates = list({
            'ref': m.ref,
            'solved': m.solved,
            'answer': self.answers_by_ref[m.ref] if m.solved else None,
            'submissions': list(
                {
                    'update_time': str(naturaltime(s.update_time)),
                    'answer': canonicalize_puzzle_answer_display(s.answer),
                    'correct': bool(s.correct),
                }
                for s in m.submissions.all().order_by('-update_time'))
        }  for m in minipuzzles)
        self.parent.send_json({
            'type': 'minipuzzle',
            'updates': updates,
        })

def on_minipuzzle_progressed(team, puzzle, minipuzzle_ref, **kwargs):
    if team.is_public:
        return
    async_to_sync(get_channel_layer().group_send)(
        get_team_puzzle_group_name(team, puzzle.external_id),
        {
            'type': 'hunt.team.minipuzzle',
            'puzzle_external_id': puzzle.external_id,
            'minipuzzle_ref': minipuzzle_ref,
        })

register(HuntEvent.MINIPUZZLE_ATTEMPTED, on_minipuzzle_progressed)
register(HuntEvent.MINIPUZZLE_COMPLETED, on_minipuzzle_progressed)
