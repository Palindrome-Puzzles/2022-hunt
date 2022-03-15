from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email3_test.csv' if TEST_MODE else 'jan4swag.csv'
FROM = SWAG_FROM
SUBJECT = 'Mystery Hunt swag discount codes'
HTML = '''<html>
<p>{{First name}},</p>

<p>As promised in the last email, here are your team’s personalized discount codes for our <a href="https://mitmysteryhunt2022.myshopify.com">Shopify store</a>. With a code, the cost of the boxes and envelope should be $0, and you’ll only pay for shipping.</p>

<p>
Box A: {{Box A Code}}<br>
Box B: {{Box B Code}}<br>
Envelope: {{Envelope 1 Code}}, {{Envelope 2 Code}}, {{Envelope 3 Code}}
</p>

<p>Please see the email with the subject line "Get ready to (quickly) order your swag puzzles!” for details. Per that email, you are tasked with distributing these codes appropriately to {{Team name}}.</p>

<p>Please remember to order as soon as possible.</p>

<p>
Thanks,<br>
Palindrome and MIT Puzzle Club
</p>
</html>'''
TEXT = '''
{{First name}},

As promised in the last email, here are your team's personalized discount codes for our Shopify store (https://mitmysteryhunt2022.myshopify.com). With a code, the cost of the boxes and envelope should be $0, and you'll only pay for shipping.

Box A: {{Box A Code}}
Box B: {{Box B Code}}
Envelope: {{Envelope 1 Code}}, {{Envelope 2 Code}}, {{Envelope 3 Code}}

Please see the email with the subject line "Get ready to (quickly) order your swag puzzles!"" for details. Per that email, you are tasked with distributing these codes appropriately to {{Team name}}.

Please remember to order as soon as possible.

Thanks,
Palindrome and MIT Puzzle Club'''

class Command(BaseCommand):
    help = 'Sends an email for swag codes'

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
