from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, reverse
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from spoilr.hq.models import Handler
from spoilr.hq.util.decorators import hq

@require_POST
@hq()
def handler_sign_in_view(request):
    name = request.POST.get('name')
    discord = request.POST.get('discord')
    phone = request.POST.get('phone')
    if not name or not discord:
        return HttpResponseBadRequest('Missing required fields')

    handler, _ = Handler.objects.update_or_create(
        discord__iexact=discord,
        defaults={
            'name': name,
            'discord': discord,
            'phone': phone,
            'activity_time': now(),
            'sign_in_time': now(),
        })
    request.session['handler_id'] = handler.id
    request.session.save()

    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url or reverse('spoilr.hq:dashboard'))

@hq()
def handler_sign_out_view(request):
    discord = request.GET.get('discord')
    maybe_handler = Handler.objects.filter(discord__iexact=discord).first()
    if maybe_handler:
        maybe_handler.sign_in_time = None
        maybe_handler.save()

    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url or reverse('spoilr.hq:dashboard'))

