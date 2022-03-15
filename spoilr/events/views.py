import csv, io
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.forms.models import model_to_dict
from spoilr.hq.util.decorators import hq

from .models import Event, EventParticipant

@hq()
def export_view(request, event_url):
    event = get_object_or_404(Event.objects.prefetch_related('participants'), url=event_url)

    participants = [{
        **model_to_dict(p),
        'team_name': p.team.name,
    } for p in event.participants.all()]

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    for p in participants:
        writer.writerow(p.values())
    participants_csv = output.getvalue()

    return HttpResponse(participants_csv)
