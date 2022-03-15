from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'events_test.csv' if TEST_MODE else 'events_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] Event 3: Cryptic Dixit - Register by 1pm'
HTML = '''<html>
<p>Dear solvers,</p>

<p>This is a reminder that you have 1 hour left to register for our third event, Cryptic Dixit! Please head over to the Events page and register a member of your team before the deadline passes.</p>

<p>– Team Palindrome</p>
</html>'''
TEXT = '''
Dear solvers,

This is a reminder that you have 1 hour left to register for our third event, Cryptic Dixit! Please head over to the Events page and register a member of your team before the deadline passes.

– Team Palindrome
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
