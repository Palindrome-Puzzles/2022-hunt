from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, HQ_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email7_test.csv' if TEST_MODE else 'email7_real.csv'
FROM = HQ_FROM
SUBJECT = '[MIT Mystery Hunt] Unlocking The Ministry'
HTML = '''<html>
<p>Hello {{Team name}}.</p>

<p>We are emailing you to offer to unlock the next act. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.</p>

<p>This will unlock the following things:</p>
<ul>
<li>The next act of the Hunt.</li>
<li>Enough feeder (non-meta) puzzles to get you up to 8 feeders unlocked.</li>
<li>Some non-zero number of meta puzzles in the next act.</li>
<li>The scavenger hunt.</li>
</ul>

<p>There are some reasons why you may or may not want to click the link.</p>
<ul>
<li>Reasons Why:
    <ul>
    <li>You’re not planning on solving the Investigation meta anytime soon, and you want to continue to see the rest of the Hunt.</li>
    <li>You want to solve the events without worrying about spoilers that are revealed by going into Act 2.</li>
    <li>You just don’t have enough feeder puzzles unlocked to satisfy the size of your team.</li>
    </ul>
</li>
<li>
    Reasons Why Not:
    <ul>
    <li>You don’t want to overwhelm your team with more puzzles.</li>
    <li>You want your team to focus on solving the Investigation meta before unlocking other things, and you believe you will finish before the first event.</li>
    </ul>
</li>
</ul>

<p>If you wish to unlock the next Act now, you can do so with the following link: https://starrats.org/release/act2. If you choose not to do so now, you may click the link at any time this weekend up until you open Act 2 normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.</p>

<p>–<br>
Team Palindrome</p>
</html>'''
TEXT = '''
Hello {{Team name}}.

We are emailing you to offer to unlock the next act. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.

This will unlock the following things:
- The next act of the Hunt.
- Enough feeder (non-meta) puzzles to get you up to 8 feeders unlocked.
- Some non-zero number of meta puzzles in the next act.
- The scavenger hunt.

There are some reasons why you may or may not want to click the link.
- Reasons Why:
    - You're not planning on solving the Investigation meta anytime soon, and you want to continue to see the rest of the Hunt.
    - You want to solve the events without worrying about spoilers that are revealed by going into Act 2.
    - You just don't have enough feeder puzzles unlocked to satisfy the size of your team.
- Reasons Why Not:
    - You don't want to overwhelm your team with more puzzles.
    - You want your team to focus on solving the Investigation meta before unlocking other things, and you believe you will finish before the first event.

If you wish to unlock the next Act now, you can do so with the following link: https://starrats.org/release/act2. If you choose not to do so now, you may click the link at any time this weekend up until you open Act 2 normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.

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
