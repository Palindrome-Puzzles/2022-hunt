import datetime

from django.shortcuts import render
import spoilr.core.models as models
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from django import forms
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template import RequestContext, loader
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.core.models import Team, PuzzleAccess, InteractionAccess
from spoilr.core.api.events import HuntEvent, dispatch
from spoilr.core.api.hunt import get_site_launch_time
from spoilr.email.models import OutgoingMessage
from spoilr.hq.util.decorators import hq

# TODO(sahil): This needs to be rewritten to use some kind of task queue. Sending
# emails often times out in app engine, which is bad as then only some teams receive
# an email about the update. And if we uncomment the OutgoingMessage model creation,
# then almost no mails get sent.
@hq(require_handler=True)
def updates_view(request):
    if request.method == "POST":
        updates_to_publish = models.HQUpdate.objects.filter(id__in=request.POST.getlist('update_ids'))
        for update in updates_to_publish:
            teams = []
            if update.team:
                teams = [update.team]
            elif update.puzzle:
                pa_teams = PuzzleAccess.objects.filter(puzzle=update.puzzle).select_related('team')
                teams = [pa.team for pa in pa_teams]
            else:
                teams = Team.objects.all()
            update.publish_time = now()
            update.published = True
            update.save()
            if update.send_email:
                outgoing_messages = []
                for t in teams:
                    if t.team_email and '@' in t.team_email:
                        subject = 'HQ Update: %s' % (update.subject)
                        send_mail(
                            'HQ Update: %s' % (update.subject), update.body,
                            settings.SPOILR_HQ_DEFAULT_FROM_EMAIL,
                            [t.team_email])
                        # outgoing_messages.append(
                        #     OutgoingMessage(
                        #         subject=subject, body_text=update.body,
                        #         sender=settings.SPOILR_HQ_DEFAULT_FROM_EMAIL, recipient=t.team_email,
                        #         team=t, automated=True, handler=request.handler))
                # OutgoingMessage.objects.bulk_create(outgoing_messages)

            dispatch(
                HuntEvent.UPDATE_SENT,
                update=update,
                teams=teams, puzzle=update.puzzle,
                message=f'HQ update sent {update.subject}')
        return redirect(request.path)

    hqupdates = models.HQUpdate.objects.order_by('-creation_time')
    context = { 'updates': hqupdates }
    return render(request, 'hq/updates.html', context)
