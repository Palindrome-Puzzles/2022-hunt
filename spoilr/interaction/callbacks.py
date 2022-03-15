from django.conf import settings
from django.db import models

from spoilr.core.api.events import HuntEvent, register, dispatch

def on_interaction_released(interaction_access, **kwargs):
    from spoilr.core.models import InteractionAccess
    from spoilr.hq.models import Task, TaskStatus
    from spoilr.interaction.models import InteractionAccessTask

    # We may re-open interaction tasks for certain interactions like answer unlocks.
    iat, _ = InteractionAccessTask.objects.get_or_create(interaction_access=interaction_access)
    task = iat.tasks.first()
    if task:
        task.status = TaskStatus.PENDING
        task.handler = None
        task.snooze_time = None
        task.snooze_until = None
        task.save()
    else:
        iat.tasks.add(Task(), bulk=False)

def on_tick(last_tick, **kwargs):
    from spoilr.core.models import InteractionAccess
    from spoilr.email.models import IncomingMessage
    from spoilr.hq.models import Task, TaskStatus
    from spoilr.interaction.models import InteractionAccessTask

    # Catch-up on missed interaction access tasks, just in case.
    ias_without_task = (
        InteractionAccess.objects.filter(accomplished=False, interactionaccesstask__tasks__isnull=True))
    for interaction_access in ias_without_task:
        iat, _ = InteractionAccessTask.objects.get_or_create(interaction_access=interaction_access)
        iat.tasks.add(Task(), bulk=False)

    # If an email was received for a snoozed interaction, and unsnooze it.
    messages = IncomingMessage.objects.filter(team__isnull=False, interaction__isnull=False)
    if last_tick:
        messages = messages.filter(received_time__gte=last_tick)

    for message in messages:
        interaction_access = (InteractionAccess.objects
            .prefetch_related('interactionaccesstask__tasks')
            .filter(team=message.team, interaction=message.interaction)
            .filter(
                interactionaccesstask__tasks__isnull=False,
                interactionaccesstask__tasks__status=TaskStatus.SNOOZED,
                interactionaccesstask__tasks__snooze_time__lte=message.received_time)
            .first())
        if interaction_access:
            task = interaction_access.interactionaccesstask.tasks.first()
            task.status = TaskStatus.PENDING
            task.snooze_time = None
            task.snooze_until = None
            task.handler = None
            task.claim_time = None
            task.save()

            dispatch(
                HuntEvent.TASK_UNSNOOZED,
                team=message.team,
                object_id=task.id,
                message=f'Unsnoozed task {task.content_object}')

def on_puzzle_solved(team, puzzle, **kwargs):
    from hunt.app.models import FreeUnlockStatus, FreeUnlockRequest

    (FreeUnlockRequest.objects
        .filter(team=team, puzzle=puzzle, status=FreeUnlockStatus.NEW)
        .update(status=FreeUnlockStatus.WITHDRAWN))

register(HuntEvent.INTERACTION_RELEASED, on_interaction_released)
register(HuntEvent.INTERACTION_REOPENED, on_interaction_released)
register(HuntEvent.PUZZLE_SOLVED, on_puzzle_solved)
register(HuntEvent.METAPUZZLE_SOLVED, on_puzzle_solved)
register(HuntEvent.HUNT_TICK, on_tick)
