from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from spoilr.core.models import Team, Puzzle
from spoilr.hq.models import Task

class HintSubmission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    question = models.TextField()
    # Optional email to notify when the hint is processed.
    email = models.CharField(max_length=200, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # The response to the hint provided by a staff member.
    result = models.TextField(null=True, blank=True)
    # Whether the hint has been resolved by a staff member.
    resolved_time = models.DateTimeField(null=True, blank=True)

    tasks = GenericRelation(Task, related_query_name='task')

    def __str__(self):
        if self.result:
            return '%s: %s asked for %s; result %s' % (self.update_time, self.team, self.puzzle, self.result)
        return '%s: %s asked for %s; unanswered' % (self.update_time, self.team, self.puzzle)

    class Meta:
        unique_together = ('team', 'puzzle', 'question')
        ordering = ['-update_time']
