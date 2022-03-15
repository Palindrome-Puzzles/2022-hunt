from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, HQ_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email9_test.csv' if TEST_MODE else 'email9_real.csv'
FROM = HQ_FROM
SUBJECT = '[MIT Mystery Hunt] "Unlocking Free Feeders" sent in error'
HTML = '''<html>
<p>Hello {{Team name}}.</p>

<p>The email you received with the subject line Unlocking Free Feeders was sent in error. Please ignore it.</p>

<p>We apologize for the inconvenience.</p>

<p>–<br>
Team Palindrome</p>
</html>'''
TEXT = '''
Hello {{Team name}}.

The email you received with the subject line Unlocking Free Feeders was sent in error. Please ignore it.

We apologize for the inconvenience.

–
Team Palindrome
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
                to_email=merge_values['Email'],
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML,
                merge_values=merge_values)
