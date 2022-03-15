from spoilr.core.api.events import HuntEvent, register

def on_hint_requested(team, puzzle, hint, **kwargs):
    from spoilr.hq.models import Task

    hint.tasks.add(Task(), bulk=False)

def on_tick(last_tick, **kwargs):
    from spoilr.hints.models import HintSubmission
    from spoilr.hq.models import Task

    # Catch-up on missed hint tasks, just in case.
    hints_without_task = HintSubmission.objects.filter(resolved_time__isnull=True, tasks__isnull=True)
    for hint in hints_without_task:
        hint.tasks.add(Task(), bulk=False)

register(HuntEvent.HINT_REQUESTED, on_hint_requested)
register(HuntEvent.HUNT_TICK, on_tick)
