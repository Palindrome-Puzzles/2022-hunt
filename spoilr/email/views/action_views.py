from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from spoilr.email.models import IncomingMessage, OutgoingMessage
from spoilr.hq.models import HqLog, TaskStatus
from spoilr.hq.util.decorators import hq
from spoilr.hq.util.redirect import redirect_with_message

assert settings.SPOILR_HQ_DEFAULT_FROM_EMAIL, 'No default from email'

FROM_EMAIL_DOMAIN = settings.SPOILR_HQ_DEFAULT_FROM_EMAIL[settings.SPOILR_HQ_DEFAULT_FROM_EMAIL.rindex('@'):]

@require_POST
@hq(require_handler=True)
def reply_view(request):
    confirm = request.POST.get('confirm')
    if confirm.lower() != 'reply':
        return redirect_with_message(request, 'spoilr.email:dashboard', 'Email reply was not sent.')

    body_text = request.POST.get('body')
    message_id = int(request.POST.get('id'))
    message = IncomingMessage.objects.filter(id=message_id).prefetch_related('tasks').first() if message_id else None

    if not body_text or not message:
        return HttpResponseBadRequest('Missing or invalid fields')

    new_subject = 'Re: ' + message.subject
    new_recipient = message.sender
    new_sender = message.recipient
    send_mail(new_subject, body_text, new_sender, [new_recipient])

    task = message.tasks.first()
    if task:
        task.status = TaskStatus.DONE
        task.snooze_time = None
        task.snooze_until = None
        task.save()

    outgoing_message = OutgoingMessage.objects.create(
        subject=new_subject, body_text=body_text, sender=new_sender, recipient=new_recipient,
        reply_to=message, automated=False, handler=request.handler)
    HqLog.objects.create(
        handler=request.handler, event_type='email-reply', object_id=outgoing_message.id,
        message=f'Replied to email {message}')

    return redirect_with_message(request, 'spoilr.email:dashboard', 'Email reply sent.')

@hq(require_handler=True)
def send_view(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        recipient = request.POST.get('recipient')
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        body_text = request.POST.get('body')

        error = None
        if not recipient or not sender or not subject or not body_text:
            error = 'Missing fields'
        if not sender.endswith(FROM_EMAIL_DOMAIN):
            error = 'Can\'t use that sender'
        if confirm.lower() != 'send':
            error = 'Did not confirm sending the email'

        if error:
            return render(
                request, 'hq/email_send.tmpl',
                {
                    'recipient': recipient or '',
                    'sender': sender  or '',
                    'subject': subject or '',
                    'body_text': body_text or '',
                    'error': error,
                })

        send_mail(subject, body_text, sender, [recipient])

        message = OutgoingMessage.objects.create(
            subject=subject, body_text=body_text, sender=sender, recipient=recipient,
            automated=False, handler=request.handler)
        HqLog.objects.create(
            handler=request.handler, event_type='email-send', object_id=message.id,
            message=f'Sent email {message}')

        return redirect_with_message(request, 'spoilr.email:dashboard', 'Email sent.')

    return render(
        request, 'spoilr/email/send.tmpl', {
            'recipient': '',
            'sender': settings.SPOILR_HQ_DEFAULT_FROM_EMAIL,
            'subject': '',
            'body_text': '',
        })

@require_POST
@hq(require_handler=True)
def hide_view(request):
    id = request.POST.get('id')
    type = request.POST.get('type')
    if type == 'in':
        message = IncomingMessage.objects.filter(id=id).first() if id else None
    else:
        message = OutgoingMessage.objects.filter(id=id).first() if id else None

    if not message:
        return HttpResponseBadRequest('Missing or invalid fields')

    message.hidden = not message.hidden
    message.save()

    if message.hidden:
        HqLog.objects.create(
            handler=request.handler, event_type='email-hide', object_id=message.id,
            message=f'Hid email {message}')
    else:
        HqLog.objects.create(
            handler=request.handler, event_type='email-unhide', object_id=message.id,
            message=f'Unhid email {message}')

    return redirect_with_message(request, 'spoilr.email:dashboard', 'Email hidden.' if message.hidden else 'Email unhidden.')
