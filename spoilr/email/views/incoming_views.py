import json, logging, random, string

from anymail.exceptions import AnymailRequestsAPIError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from spoilr.email.models import IncomingMessage

from spoilr.core.api.events import dispatch, HuntEvent

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def incoming_email_view(request):
    print('Incoming email', request)
    # The payload is documented at
    # https://docs.sendgrid.com/for-developers/parsing-email/setting-up-the-inbound-parse-webhook#default-parameters.
    recipient = request.POST.get('to', '')
    sender = request.POST.get('from', '')
    subject = request.POST.get('subject', '')
    body_text = request.POST.get('text')
    body_html = request.POST.get('html')

    # Note: Other fields like the team and interaction are set in the dispatch
    # handler, so that hunt-specific code can extract them.
    incoming_message = IncomingMessage.objects.create(
        subject=subject, body_text=body_text, body_html=body_html,
        sender=sender, recipient=recipient)
    dispatch(
        HuntEvent.EMAIL_RECEIVED, message=f'Received email: “{subject}” from `{sender}`',
        incoming_message=incoming_message)

    relay_message(request, incoming_message)

    return HttpResponse('OK')

def relay_message(request, incoming_message):
    reply_to = None
    relay_from = incoming_message.sender

    # Some domains don't like us pretending the relayed email came from their
    # domain, and will reject it with a DMARC error.
    # Example: https://support.google.com/mail/answer/2451690
    for pattern, alias in settings.SPOILR_RELAY_IMPERSONATE_BLACKLIST.items():
        if pattern in incoming_message.sender:
            relay_from = inject_alias(settings.SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS, alias)
            reply_to = [incoming_message.sender]
            break

    stripped_recipient = incoming_message.stripped_recipient
    loc_of_at = [i for i, c in enumerate(stripped_recipient) if c == '@']
    recipient_prefix = stripped_recipient[:loc_of_at[0]] if len(loc_of_at) else None

    relay_recipient = inject_alias(settings.SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS, recipient_prefix)

    mail = EmailMultiAlternatives(
        incoming_message.subject, incoming_message.body_text or '<empty response>',
        relay_from, [relay_recipient], reply_to=reply_to)
    if incoming_message.body_html:
        mail.attach_alternative(incoming_message.body_html, 'text/html')

    try:
        num_attachments = int(request.POST.get('attachments', 0))
        all_attachment_info = json.loads(request.POST.get('attachment-info', '{}'))
        for num in range(1, (num_attachments + 1)):
            attachment_id = f'attachment{num}'
            content = request.FILES.get(attachment_id).read()
            attachment_info = all_attachment_info.get(attachment_id, {})
            if attachment_info.get('type'):
                filename = attachment_info.get('filename', '') or ('unknown-' + ''.join(random.choice(string.ascii_lowercase) for _ in range(16)))
                mail.attach(filename, content, attachment_info['type'])
    except:
        logger.exception('Error with attachments %s', request)

    try:
        mail.send()
    except AnymailRequestsAPIError:
        # NB: This has been observed to happen with "request too large" errors.
        logger.exception('Error with sending mail %s %s', request, incoming_message)

def inject_alias(email, alias):
    if alias:
        loc_of_at = email.index('@')
        return email[:loc_of_at] + '+' + alias + email[loc_of_at:]
    return email
