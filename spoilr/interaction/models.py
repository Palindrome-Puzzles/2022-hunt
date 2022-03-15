from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from spoilr.core.models import InteractionAccess, Puzzle
from spoilr.hq.models import Task

class InteractionAccessTask(models.Model):
    interaction_access = models.OneToOneField(InteractionAccess, on_delete=models.CASCADE)
    tasks = GenericRelation(Task, related_query_name='task')

    replied = models.BooleanField(default=False)

    def __str__(self):
        return str(self.interaction_access)
