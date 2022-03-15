from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from spoilr.core.models import Team
from spoilr.hq.models import Task

class ContactRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    email = models.EmailField(max_length=200)
    comment = models.TextField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    result = models.TextField(null=True, blank=True)
    resolved_time = models.DateTimeField(null=True, blank=True)

    tasks = GenericRelation(Task, related_query_name='task')

    def __str__(self):
        return '%s: %s wants to talk to HQ' % (self.create_time, self.team)

    class Meta:
        ordering = ['-create_time']
