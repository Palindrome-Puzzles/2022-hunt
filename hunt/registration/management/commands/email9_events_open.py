from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email7_test.csv' if TEST_MODE else 'email7_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] HQ Update: Events Now Available for Registration'
HTML = '''<html>
<p>(Some teams may be receiving this for the second time; apologies if you are one of them.)</p>

<p>Dear teams,</p>

<p>Events are now open for registration! Our first event, The Let's Play That Goes Wrong, starts tonight at 9:00pm. Due to the delay in opening registration, the deadline for registering for this event has been extended to 8:00pm. You can register for events on the Events page, which can be found in the Hunt dropdown menu on the site's navigation bar.</p>

<p>Please register as soon as you can and we look forward to seeing you soon!</p>

<p>-- Team Palindrome</p>
</html>'''
TEXT = '''
(Some teams may be receiving this for the second time; apologies if you are one of them.)

Dear teams,

Events are now open for registration! Our first event, The Let's Play That Goes Wrong, starts tonight at 9:00pm. Due to the delay in opening registration, the deadline for registering for this event has been extended to 8:00pm. You can register for events on the Events page, which can be found in the Hunt dropdown menu on the site's navigation bar.

Please register as soon as you can and we look forward to seeing you soon!

-- Team Palindrome
'''

class Command(BaseCommand):
    help = 'Sends an email for additional envelope codes'

    def handle(self, *args, **options):
        assert not DISABLED, 'This has already been run'

        if not confirm_emails() or not confirm_filename(FILENAME) or not confirm_live_mode(test_mode=TEST_MODE):
            return

        merge_values_list = read_csv(FILENAME)
        for merge_values in merge_values_list:
            send_mail(
                to_email=merge_values['Email'], to_name=merge_values['First name'],
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML)
