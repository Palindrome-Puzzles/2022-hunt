from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'event4_test.csv' if TEST_MODE else 'event4_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] Invitation for Event 4: Picaboo'
HTML = '''<html>
<p>Dear {{First name}},</p>

<p>You are receiving this email because you are registered for our last event, Picaboo!  The event will be starting in 1 hour at 9pm. Use the link <a href="https://discord.gg/fGvXUrmT">https://discord.gg/fGvXUrmT</a> to join our server approximately 15 minutes before the scheduled start time.</p>

<p>For this event, you have been assigned to Team {{Team name}}.</p>

<p>– Team Palindrome</p>
</html>'''
TEXT = '''
Dear {{First name}},

You are receiving this email because you are registered for our last event, Picaboo!  The event will be starting in 1 hour at 9pm. Use the link https://discord.gg/fGvXUrmT to join our server approximately 15 minutes before the scheduled start time. 

For this event, you have been assigned to Team {{Team name}}.

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
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML, merge_values=merge_values)
