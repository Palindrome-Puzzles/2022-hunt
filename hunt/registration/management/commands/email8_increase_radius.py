from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, HQ_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email8_test.csv' if TEST_MODE else 'email8_real.csv'
FROM = HQ_FROM
SUBJECT = '[MIT Mystery Hunt] Unlocking Free Feeders'
HTML = '''<html>
<p>Hello {{Team name}}.</p>

<p>We are emailing you to offer to unlock more puzzles! We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.</p>

<p>We are offering to unlock 3 for you. If you want those puzzles unlocked, you can do so at the following link: <a href="https://bookspace.world/release/unlock-more/">https://bookspace.world/release/unlock-more/</a>. If you choose not to do so now, you may click the link at any time this weekend. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.</p>

<p>–<br>
Team Palindrome</p>
</html>'''
TEXT = '''
Hello {{Team name}}.

We are emailing you to offer to unlock more puzzles! We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.

We are offering to unlock 3 for you. If you want those puzzles unlocked, you can do so at the following link: https://bookspace.world/release/unlock-more/. If you choose not to do so now, you may click the link at any time this weekend. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.

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
