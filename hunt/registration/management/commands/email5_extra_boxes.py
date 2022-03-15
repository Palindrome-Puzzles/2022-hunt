from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email5_test.csv' if TEST_MODE else 'email5_real.csv'
FROM = SWAG_FROM
SUBJECT = '[MIT Mystery Hunt] Additional copies of swag puzzles for next 72 hours'
HTML = '''<html>
<p>Dear team captain,</p>

<p>We'd like to offer {{Team name}} additional copies of Box A and Box B. These are not necessary to solve the associated puzzle, but in our remote solving environment it allows additional people to be hands-on with these puzzles. As the captain, you're charged with distributing these codes around your team appropriately.</p>

<p>Like before, you'll order on our <a href="https://mitmysteryhunt2022.myshopify.com">Shopify store</a> with discount codes. Your new codes:<br>
Box A: {{Box A Code}}<br>
Box B: {{Box B Code}}
</p>

<p>Please note that if you're interested in additional copies of the boxes, you must order them (or get in touch) within 72 hours. In three days, we'll deactivate these codes so that we can offer additional copies to other teams.</p>

<p>Let us know if you have any questions.</p>

<p>
Thanks,<br>
Matt<br>
Team Palindrome
</p>

<p>PS: You should have already received codes for additional envelopes. Please let us know if you did not receive them.</p>
</html>'''
TEXT = '''
Dear team captain,

We'd like to offer {{Team name}} additional copies of Box A and Box B. These are not necessary to solve the associated puzzle, but in our remote solving environment it allows additional people to be hands-on with these puzzles. As the captain, you're charged with distributing these codes around your team appropriately.

Like before, you'll order on our Shopify store (https://mitmysteryhunt2022.myshopify.com) with discount codes. Your new codes:
Box A: {{Box A Code}}
Box B: {{Box B Code}}

Please note that if you're interested in additional copies of the boxes, you must order them (or get in touch) within 72 hours. In three days, we'll deactivate these codes so that we can offer additional copies to other teams.

Let us know if you have any questions.

Thanks,
Matt
Team Palindrome

PS: You should have already received codes for additional envelopes. Please let us know if you did not receive them.
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
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML,
                merge_values=merge_values)
