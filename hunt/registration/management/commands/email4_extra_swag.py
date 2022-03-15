from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email4_test.csv' if TEST_MODE else 'dec21swag.csv'
FROM = SWAG_FROM
SUBJECT = 'Mystery Hunt: Offering more swag envelopes to your team'
HTML = '''<html>
<p>{{First name}},</p>

<p>Physical puzzles have started to ship out, and we have plenty of the envelopes. As the captain of a medium or large sized team, we’d like to offer you some more discount codes for the envelope to share with your team. Like before, these can be used on our <a href="https://mitmysteryhunt2022.myshopify.com">Shopify store</a> to bring the price of an envelope down to $0, so that you just pay for shipping.</p>

<p>All envelopes are identical, and you do not need additional copies for solving. Providing these additional copies just lets even more members of your team have the physical items.</p>

<p>This code can be used {{Code quantity}} times: {{Envelope code}}</p>

<p>As your team's captain, you are the only member of your team receiving this email. You are responsible for distributing this code to your team as appropriate.</p>

<p>
Thanks,<br>
Team Palindrome
</p>
</html>'''
TEXT = '''
{{First name}},

Physical puzzles have started to ship out, and we have plenty of the envelopes. As the captain of a medium or large sized team, we'd like to offer you some more discount codes for the envelope to share with your team. Like before, these can be used on our Shopify store (https://mitmysteryhunt2022.myshopify.com) to bring the price of an envelope down to $0, so that you just pay for shipping.

All envelopes are identical, and you do not need additional copies for solving. Providing these additional copies just lets even more members of your team have the physical items.

This code can be used {{Code quantity}} times: {{Envelope code}}

As your team's captain, you are the only member of your team receiving this email. You are responsible for distributing this code to your team as appropriate.

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
                frm=FROM, subject=SUBJECT, text=TEXT, html=HTML,
                merge_values=merge_values)
