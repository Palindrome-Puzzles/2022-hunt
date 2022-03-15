import logging, time

from django.db import models

from spoilr.core.api.progress import register_progress_model
from spoilr.core.models import Team, Puzzle

from hunt.app.core.plugins import Plugin
from hunt.app.core.team_consumer import AccessDeniedException

logger = logging.getLogger(__name__)

class TeamModelBase(models.Model):
    """The partial base model for a team puzzle."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class TeamSessionPlugin(Plugin):
    """
    Plugin for a TeamConsumer that has metadata for a team session.

    It exposes an additional reducer hook:
     - `session_defaults`: Handler to return partial defaults for the session
       model.

    Any puzzle data should be stored in a model that is a subclass of
    `TeamModelBase`. It can be accessed using `get()`.

    Note: this is generally used for backend-only data like who the leader is,
    or whether the team has solved the puzzle. Use `TeamStatePlugin` if the data
    should be shared, modified by, and synchronized across team member clients.
    """
    plugin_name = 'session'

    def __init__(self, ModelClass):
        super().__init__()

        assert issubclass(ModelClass, TeamModelBase)
        self.ModelClass = ModelClass
        register_progress_model(self.ModelClass, 'team', 'puzzle')

    def verify_plugin(self):
        self.parent.assert_has_plugin('puzzle')

    def get(self):
        """
        Gets the session object for the current team.

        It should only be called after the team has been authenticated, or an
        Exception will be thrown.
        """
        if self.parent.team:
            # Lazily create the session object when accessed.
            defaults = {}
            for extra_defaults in self.parent.iterate_plugins('session_defaults'):
                defaults.update(extra_defaults)
            return self.ModelClass.objects.get_or_create(
                team=self.parent.team, puzzle=self.get_sibling_plugin('puzzle').puzzle,
                defaults=defaults)[0]

        else:
            logger.info(
                f'Someone has tried to access the session object '
                f'{self.__class__.__name__} without authenticating')
            raise AccessDeniedException()

    def assert_has_subclass(self, subclass):
        assert issubclass(self.ModelClass, subclass)
