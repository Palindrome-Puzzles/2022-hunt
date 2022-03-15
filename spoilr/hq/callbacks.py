from spoilr.core.api.events import HuntEvent, register, dispatch

def on_tick(tick, **kwargs):
    from spoilr.hq.models import Task, TaskStatus

    # Unsnooze tasks. Do an awkward query and update flow because I want to notify
    # about the unsnoozing.
    to_unsnooze = list(Task.objects.prefetch_related('content_object').filter(status=TaskStatus.SNOOZED, snooze_until__lte=tick))
    for task in to_unsnooze:
        task.status = TaskStatus.PENDING
        task.snooze_time = None
        task.snooze_until = None
        task.handler = None
        task.claim_time = None

        dispatch(
            HuntEvent.TASK_UNSNOOZED,
            team=getattr(task.content_object, 'team', None),
            object_id=task.id,
            message=f'Unsnoozed task {task.content_object}')

    Task.objects.bulk_update(to_unsnooze, ['status', 'snooze_time', 'snooze_until', 'handler', 'claim_time'])

register(HuntEvent.HUNT_TICK, on_tick)
