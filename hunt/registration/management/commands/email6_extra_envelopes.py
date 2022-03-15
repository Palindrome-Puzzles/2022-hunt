from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True

FILENAME = 'email6_test.csv' if TEST_MODE else 'email6_real.csv'
FROM = SWAG_FROM
SUBJECT = '[MIT Mystery Hunt] Additional stock of swag puzzles available, minor forms, and shirts'
HTML = '''<html>
<p>MIT Mystery Hunt 2022 teams,</p>

<p><b>Exciting news: We are now able to fully open orders for the envelope swag puzzle.</b> All envelopes are identical, and additional orders aren't needed for your team to solve the puzzle - but this gives more people the ability to get a copy.</p>

<p>We have over four hundred envelopes available in <a href="https://mitmysteryhunt2022.myshopify.com">our Shopify store</a> on a first come, first served basis. Like all swag puzzles, you'll pay shipping costs. Codes are no longer needed to order an envelope; when checking out the price of one envelope should automatically drop to $0. (All teams have received discount codes to order the other swag puzzles. If for some reason your team captain has not received any, please let us know immediately.)</p>

<p>Shipping details: It will take us 1-2 days to get your package in the mail, and shipping services are often taking 1-2 days longer than Shopify predicts. US-based players will almost certainly receive their envelope before hunt. If you're based outside the United States, please carefully consider timing before ordering.</p>

<p>Also remember: <b>The MIT Mystery Hunt t-shirt</b> is not part of a puzzle, but it is available to order now!</p>

<p>Questions? Get in touch!</p>

<p>
Thanks,<br>
Team Palindrome
</p>

<p>PS: <b>If you have hunters under the age of 18, minor release forms will be coming out shortly.</b> Please watch your email for these important forms; they are required to finalize your team's registration. And captains, please ensure the number of minors on <a href="https://www.mitmh2022.com/team">your team's registration</a> is up to date.</p>
</html>'''
TEXT = '''
MIT Mystery Hunt 2022 teams,

Exciting news: We are now able to fully open orders for the envelope swag puzzle. All envelopes are identical, and additional orders aren't needed for your team to solve the puzzle - but this gives more people the ability to get a copy. 

We have over four hundred envelopes available in our Shopify store (https://mitmysteryhunt2022.myshopify.com) on a first come, first served basis. Like all swag puzzles, you'll pay shipping costs. Codes are no longer needed to order an envelope; when checking out the price of one envelope should automatically drop to $0. (All teams have received discount codes to order the other swag puzzles. If for some reason your team captain has not received any, please let us know immediately.)

Shipping details: It will take us 1-2 days to get your package in the mail, and shipping services are often taking 1-2 days longer than Shopify predicts. US-based players will almost certainly receive their envelope before hunt. If you're based outside the United States, please carefully consider timing before ordering.

Also remember: The MIT Mystery Hunt t-shirt is not part of a puzzle, but it is available to order now!

Questions? Get in touch!

Thanks,
Team Palindrome

PS: If you have hunters under the age of 18, minor release forms will be coming out shortly. Please watch your email for these important forms; they are required to finalize your team's registration. And captains, please ensure the number of minors on your team's registration (https://www.mitmh2022.com/team) is up to date.
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
