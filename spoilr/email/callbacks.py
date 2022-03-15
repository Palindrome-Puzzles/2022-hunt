from django.db import models

from spoilr.core.api.events import HuntEvent, register

# Only create email tasks when the hunt has been prelaunched. Until then, we are
# manually checking the shared email inbox, and using that as the source of truth.

def should_create_email_tasks():
    from spoilr.core.api.hunt import is_site_launched
    from hunt.deploy.util import HUNT_REF, HUNT_PRELAUNCH_REF
    return is_site_launched(HUNT_REF) or is_site_launched(HUNT_PRELAUNCH_REF)

def on_email_received(incoming_message, **kwargs):
    from spoilr.hq.models import Task

    if should_create_email_tasks() and not incoming_message.interaction:
        incoming_message.tasks.add(Task(), bulk=False)

def on_tick(**kwargs):
    from spoilr.core.api.hunt import get_site_launch_time
    from spoilr.email.models import IncomingMessage
    from spoilr.hq.models import Task
    from hunt.deploy.util import HUNT_REF

    if should_create_email_tasks():
        hunt_launch_time = get_site_launch_time(HUNT_REF)

        messages_without_task = (IncomingMessage.objects
            # Catch up on email submissions that were badly formed and for which we
            # can't make an interaction automatically. We need to do it in the tick
            # and not the on_email_received callback, as interaction and team are
            # filled in a callback for on_email_received and there's no guarantees
            # on callback order.
            .filter(models.Q(team__isnull=True) | models.Q(interaction__isnull=True))
            # Catch-up on missed emails, just in case.
            .filter(received_time__gte=hunt_launch_time, tasks__isnull=True))
        for message in messages_without_task:
            message.tasks.add(Task(), bulk=False)

register(HuntEvent.EMAIL_RECEIVED, on_email_received)
register(HuntEvent.HUNT_TICK, on_tick)
