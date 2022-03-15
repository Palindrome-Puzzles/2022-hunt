from spoilr.core.api.events import HuntEvent, register

def on_contact_requested(team, contact_request, **kwargs):
    from spoilr.hq.models import Task

    contact_request.tasks.add(Task(), bulk=False)

def on_tick(last_tick, **kwargs):
    from spoilr.contact.models import ContactRequest
    from spoilr.hq.models import Task

    # Catch-up on missed hint tasks, just in case.
    contact_requests_without_task = ContactRequest.objects.filter(resolved_time__isnull=True, tasks__isnull=True)
    for contact_request in contact_requests_without_task:
        contact_request.tasks.add(Task(), bulk=False)

register(HuntEvent.CONTACT_REQUESTED, on_contact_requested)
register(HuntEvent.HUNT_TICK, on_tick)
