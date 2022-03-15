import logging

from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from spoilr.hq.util.decorators import hq
from spoilr.contact.models import ContactRequest
from spoilr.email.models import IncomingMessage
from spoilr.hints.models import HintSubmission
from spoilr.interaction.models import InteractionAccessTask
from spoilr.hq.models import Task, TaskStatus

logger = logging.getLogger(__name__)

@hq()
def dashboard(request):
    hint_count = (Task.objects
        .filter(
            content_type=ContentType.objects.get_for_model(HintSubmission),
            status=TaskStatus.PENDING)
        .count)
    task_count = (Task.objects
        .filter(
            content_type=ContentType.objects.get_for_model(InteractionAccessTask),
            status=TaskStatus.PENDING)
        .count)
    contact_count = (Task.objects
        .filter(
            content_type=ContentType.objects.get_for_model(ContactRequest),
            status=TaskStatus.PENDING)
        .count)
    email_count = (
        IncomingMessage.objects
           .prefetch_related('tasks')
           .filter(tasks__isnull=False, tasks__status__in=(TaskStatus.PENDING, TaskStatus.SNOOZED),
                   hidden=False)
           .count)

    return render(request, 'hq/main.html', {
        'hint_count': hint_count,
        'task_count': task_count,
        'contact_count': contact_count,
        'email_count': email_count,
    })
