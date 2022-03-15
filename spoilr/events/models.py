from django.db import models

from spoilr.core.models import Team, Puzzle
from spoilr.hq.models import Task

class EventStatus(models.TextChoices):
    UNAVAILABLE = 'unavailable', 'The event is not yet available for registration'
    OPEN = 'open', 'Teams can register for the event'
    CLOSED = 'closed', 'Teams can no longer register for the event'
    POST = 'post', 'The event is over and the event answer checker can be shown'

class Event(models.Model):
    url = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    expected_start_time = models.DateTimeField()
    max_participants = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.UNAVAILABLE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    pronouns = models.CharField(max_length=200, blank=True)

    dixit_category = models.PositiveSmallIntegerField(null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event}: {self.name} ({self.team})'
