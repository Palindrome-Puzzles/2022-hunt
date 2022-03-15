from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_live_mode, SWAG_FROM, read_csv_rows, row_get, send_mail, confirm_filename

DISABLED = True
TEST_MODE = True
INCLUDE_RESEND_HEADER = True

FILENAME = 'email2_test.txt' if TEST_MODE else 'email2_swag_launch.txt'
FROM = SWAG_FROM
SUBJECT = 'Get ready to order your swag!'
HTML = f'''<html>
''' + ('<p><b>Apologies if you receive this twice - we\'ve had some reports that the MIT spam filter ate up our first swag email.</b><br>--</p>' if INCLUDE_RESEND_HEADER else '') + '''
<p>MIT Mystery Hunt 2022 teams,</p>

<p>This year’s hunt will include some puzzles with physical components. As we are not meeting on MIT’s campus this year, we’ll be shipping out these items in advance of the hunt — and asking recipients to not open them until instructed to do so during the weekend.</p>
<p>There are four items for sale on our <a href="https://mitmysteryhunt2022.myshopify.com">Shopify store</a>: three puzzle-y items, and the MIT Mystery Hunt t-shirt (not a puzzle, available to order now and will be shipped after Mystery Hunt).</p>
<p>The puzzle items’ listed prices likely make them cost-prohibitive. We’re going to be sending discount codes to the team captains, bringing down the price of the puzzle items to $0 — you’ll just pay the shipping costs. (If you hunted in 2021, this is similar to what happened last year.) And if shipping is more expensive than your team can afford, please get in touch.</p>
<p>Coupon codes will be emailed to team captains in the next few days. Captains, you are in charge of who to distribute these codes to — and ensuring they order promptly. You’ll get one discount code for each box and three for the envelope. (All envelopes are identical; this is just a chance for additional people to receive the item.)</p>
<p>International shipping is available through the US Postal Service, UPS, and DHL.</p>
<p>We recommend ordering as soon as possible after receiving your codes. With the quantity of packages going out, we expect some to be delayed or lost, and we anticipate having to re-ship a few items. If items are ordered by December 20th we are confident that we’ll be able to ensure receipt before the hunt.</p>
<p>Questions? Get in touch!</p>

<p>
Thanks,<br>
Palindrome and MIT Puzzle Club
</p>

<p>PS: Like the Shopify site, nothing in this email is a puzzle.</p>
</html>'''
TEXT = ('''
*Apologies if you receive this twice - we\'ve had some reports that the MIT spam filter ate up our first swag email.*
--
''' if INCLUDE_RESEND_HEADER else '') + '''
MIT Mystery Hunt 2022 teams,

This year's hunt will include some puzzles with physical components. As we are not meeting on MIT's campus this year, we'll be shipping out these items in advance of the hunt — and asking recipients to not open them until instructed to do so during the weekend.

There are four items for sale on our Shopify store (https://mitmysteryhunt2022.myshopify.com): three puzzle-y items, and the MIT Mystery Hunt t-shirt (not a puzzle, available to order now and will be shipped after Mystery Hunt).

The puzzle items' listed prices likely make them cost-prohibitive. We're going to be sending discount codes to the team captains, bringing down the price of the puzzle items to $0 — you'll just pay the shipping costs. (If you hunted in 2021, this is similar to what happened last year.) And if shipping is more expensive than your team can afford, please get in touch.

Coupon codes will be emailed to team captains in the next few days. Captains, you are in charge of who to distribute these codes to — and ensuring they order promptly. You'll get one discount code for each box and three for the envelope. (All envelopes are identical; this is just a chance for additional people to receive the item.)

International shipping is available through the US Postal Service, UPS, and DHL.

We recommend ordering as soon as possible after receiving your codes. With the quantity of packages going out, we expect some to be delayed or lost, and we anticipate having to re-ship a few items. If items are ordered by December 20th we are confident that we'll be able to ensure receipt before the hunt.

Questions? Get in touch!

Thanks,
Palindrome and MIT Puzzle Club

PS: Like the Shopify site, nothing in this email is a puzzle.'''

class Command(BaseCommand):
    help = 'Sends an email for swag announcement'

    def handle(self, *args, **options):
        assert not DISABLED, 'This has already been run'

        if not confirm_emails() or not confirm_filename(FILENAME) or not confirm_live_mode(test_mode=TEST_MODE):
            return

        emails = [row_get(row, 0) for row in read_csv_rows(FILENAME, skip_header=False)]
        assert len(emails) == len(set(emails)), 'There are duplicate emails'

        for email in emails:
            send_mail(to_email=email, frm=FROM, subject=SUBJECT, text=TEXT, html=HTML)
