from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from spoilr.core.models import Team, Interaction
from spoilr.hq.models import Handler, Task

class IncomingMessage(models.Model):
    subject = models.CharField(max_length=1000)
    body_text = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    sender = models.CharField(max_length=500)
    recipient = models.CharField(max_length=500)
    received_time = models.DateTimeField(auto_now_add=True)

    hidden = models.BooleanField(default=False)

    @property
    def stripped_recipient(self):
        if '<' in self.recipient:
            return self.recipient[self.recipient.index('<')+1:self.recipient.index('>')]
        return self.recipient

    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    interaction = models.ForeignKey(Interaction, blank=True, null=True, on_delete=models.SET_NULL)

    tasks = GenericRelation(Task, related_query_name='task')

    def __str__(self):
        return '%s from %s' % (self.subject, self.sender)

    class Meta:
        ordering = ['-received_time']

class OutgoingMessage(models.Model):
    subject = models.CharField(max_length=1000)
    body_text = models.TextField()
    sender = models.CharField(max_length=500)
    recipient = models.CharField(max_length=500)
    sent_time = models.DateTimeField(auto_now_add=True)

    handler = models.ForeignKey(Handler, null=True, blank=True, on_delete=models.SET_NULL)
    automated = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    reply_to = models.ForeignKey(IncomingMessage, blank=True, null=True, on_delete=models.CASCADE)
    interaction = models.ForeignKey(Interaction, blank=True, null=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s to %s' % (self.subject, self.recipient)

    class Meta:
        ordering = ['-sent_time']
