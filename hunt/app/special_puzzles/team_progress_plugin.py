import logging, time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models, transaction
from django.forms.models import model_to_dict

from spoilr.core.api.progress import register_progress_model
from spoilr.core.models import Puzzle, Team

from hunt.app.core.helpers import omit
from hunt.app.core.plugins import Plugin

from .team_puzzle_plugin import get_team_puzzle_group_name

logger = logging.getLogger(__name__)

class TeamProgressModelBase(models.Model):
    """
    The partial base model for a team's progress on a puzzle.

    Note: All other fields added on child models should have defaults or allow
    blank values, as there's no way to initialize them otherwise.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = [['team', 'puzzle']]

def default_project_progress(progress):
    return omit(model_to_dict(progress), 'team', 'puzzle')

class TeamProgressPlugin(Plugin):
    """
    Plugin for a TeamConsumer that emits progress to the team when any member
    makes progress.

    It has an optional `project_progress` argument that transforms the progress model into
    what should be sent to the client as a dict.

    It has an optional `maybe_initialize_progress` argument that initializes the
    (already created) progress model if needed.

    It will send messages to the client with the following keys:
     - `type`: 'progress'.
     - `progress`: The result of projecting the team's progress.
    """
    plugin_name = 'progress'

    def __init__(self, ModelClass, project_progress=default_project_progress, maybe_initialize_progress=None):
        super().__init__()

        self.ModelClass = ModelClass
        self.project_progress = project_progress
        self.maybe_initialize_progress = maybe_initialize_progress

        assert issubclass(self.ModelClass, TeamProgressModelBase)
        register_progress_model(self.ModelClass, 'team', 'puzzle')

    def verify_plugin(self):
        self.parent.assert_has_plugin('puzzle')

    def joined(self):
        self.send_progress(initial=True)

    def hunt_team_progressed(self, message):
        """Handler for the channel layer message with type `hunt.team.progressed`."""
        if message['puzzle_external_id'] == self.get_sibling_plugin('puzzle').puzzle_external_id:
            self.send_progress(initial=False)

    def send_progress(self, initial):
        progress, _ = self.ModelClass.objects.get_or_create(
            team=self.parent.team,
            puzzle=self.get_sibling_plugin('puzzle').puzzle
        )
        if initial and self.maybe_initialize_progress:
            self.maybe_initialize_progress(progress)

        self.parent.send_json({
            'type': 'progress',
            'progress': self.project_progress(progress),
        })

def team_puzzle_progressed(ModelClass, team, puzzle, transform_progress=None):
    if transform_progress:
        with transaction.atomic():
            progress = get_team_puzzle_progress(ModelClass, team, puzzle)
            transform_progress(progress)
            progress.save()

    async_to_sync(get_channel_layer().group_send)(
        get_team_puzzle_group_name(team, puzzle.external_id),
        {
            'type': 'hunt.team.progressed',
            'puzzle_external_id': puzzle.external_id,
        })

def get_team_puzzle_progress(ModelClass, team, puzzle):
    progress, _ = ModelClass.objects.get_or_create(team=team, puzzle=puzzle)
    return progress
