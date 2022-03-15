import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

class Handler(models.Model):
    name = models.CharField(max_length=100)
    discord = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    activity_time = models.DateTimeField(null=True, blank=True)
    sign_in_time = models.DateTimeField(null=True, blank=True)

    @property
    def status(self) -> str:
        status = 'off duty'
        if self.activity_time and (now () - self.activity_time > datetime.timedelta(minutes=5)):
            status = 'on duty, idle'
        elif self.activity_time:
            status = 'on duty'
        return status

    def __str__(self):
        return f'{self.name} ({self.discord}) [{self.status}]'

class HqLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    handler = models.ForeignKey(Handler, blank=True, null=True, on_delete=models.SET_NULL)
    event_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        prefix = f'[{self.handler.discord}] ' if self.handler else ''
        return f'{prefix} {self.timestamp}: {self.message}'

    class Meta:
        verbose_name_plural = "HQ log"

class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    DONE = 'done', 'Done'
    IGNORED = 'ignored', 'Ignored'
    SNOOZED = 'snoozed', 'Snoozed'

class Task(models.Model):
    """Metadata about a task to be completed in HQ."""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)

    claim_time = models.DateTimeField(null=True, blank=True)
    handler = models.ForeignKey(Handler, blank=True, null=True, on_delete=models.SET_NULL)

    snooze_time = models.DateTimeField(null=True, blank=True)
    snooze_until = models.DateTimeField(null=True, blank=True)

    @property
    def is_snoozed(self):
        return self.status == TaskStatus.SNOOZED

    def __str__(self):
        return f'`{self.content_object}`' + (f' -- `{self.handler.discord}`' if self.handler else '')

    class Meta:
        unique_together = ('content_type', 'object_id')
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_status_valid",
                check=models.Q(status__in=TaskStatus.values),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_snooze_valid",
                check=(
                    (~models.Q(status=TaskStatus.SNOOZED) & models.Q(snooze_time__isnull=True, snooze_until__isnull=True)) |
                    models.Q(status=TaskStatus.SNOOZED, snooze_time__isnull=False, snooze_until__isnull=False))
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_handler_has_claim_time",
                check=(
                    models.Q(claim_time__isnull=False, handler__isnull=False) |
                    models.Q(handler__isnull=True))
            ),
        ]
