from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email7_test.csv' if TEST_MODE else 'email7_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] From the Desk of Director Carlton Sinclair-Jones - 1 hour until our discussion kicks off'
HTML = '''<html>
<p>Reminder, our discussion commences in approximately one hour.</p>

<hr style="width:30%;text-align:left;margin-left:0"> 

<p>Greetings from the Institution for the Acquisition and Study of Hyperintelligent Creatures. We will soon be sending representatives to campus to discuss the troubling situation with the super-powered rodents and their assault on Hayden Library. We invite you to a discussion of the matter at 12:00 noon, at the following link:<p>

<p><a href="https://youtu.be/llmzLHExcnw">https://youtu.be/llmzLHExcnw</a></p>

<p>
Sincerely,<br>
Carlton Sinclair-Jones, Director
</p>
</html>'''
TEXT = '''
Reminder, our discussion commences in approximately one hour.

----------

Greetings from the Institution for the Acquisition and Study of Hyperintelligent Creatures. We will soon be sending representatives to campus to discuss the troubling situation with the super-powered rodents and their assault on Hayden Library. We invite you to a discussion of the matter at 12:00 noon, at the following link:

https://youtu.be/llmzLHExcnw

Sincerely,
Carlton Sinclair-Jones, Director
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
