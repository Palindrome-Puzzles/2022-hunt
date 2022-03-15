from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email7_test.csv' if TEST_MODE else 'email7_real.csv'
FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
SUBJECT = '[MIT Mystery Hunt] Ready at 1:00pm'
HTML = '''<html>
<p>As you've seen, we've had a change of plans. It's going to take us a little bit to collect those swirling papers and get them on the website. We'll just reuse that <a href="https://www.starrats.org">starrats.org</a> domain. Log in there at 1:00pm and we'll have everything ready for you.</p>

<p>
Thanks,<br>
Team Palindrome
</p>
</html>'''
TEXT = '''
As you've seen, we've had a change of plans. It's going to take us a little bit to collect those swirling papers and get them on the website. We'll just reuse that starrats.org domain. Log in there at 1:00pm and we'll have everything ready for you.

Thanks,
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
                to_email=merge_values['Email'], to_name=merge_values['First name'],
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML)
