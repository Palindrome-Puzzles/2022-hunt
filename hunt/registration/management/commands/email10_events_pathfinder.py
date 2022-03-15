from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email10_test.csv' if TEST_MODE else 'email10_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] Discord Invitation for Event 1 — The Let\'s Play That Goes Wrong'
HTML = '''<html>
<p>Dear {{First name}},</p>

<p>For the upcoming event "The Let's Play that Goes Wrong", you will be a part of team {{Discordteam}}.</p>

<p>Please send the two members you registered for the event to join our server at: https://discord.gg/fGvXUrmT</p>

<p>-- Team Palindrome</p>
</html>'''
TEXT = '''
Dear {{First name}},

For the upcoming event "The Let's Play that Goes Wrong", you will be a part of team {{Discordteam}}.

Please send the two members you registered for the event to join our server at: https://discord.gg/fGvXUrmT

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
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML, merge_values=merge_values)
