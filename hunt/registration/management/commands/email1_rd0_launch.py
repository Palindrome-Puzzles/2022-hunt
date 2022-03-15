from django.core.management.base import BaseCommand
from django.core.management import call_command

from spoilr.core.models import User, UserTeamRole

from ._common import confirm_emails, confirm_env, HUNT_FROM, send_mail

DISABLED = True
FROM = HUNT_FROM
SUBJECT = 'The 2022 MIT Mystery Hunt Prologue is here!'
HTML = '''<html>
<p>Don’t want to wait another whole month for the 2022 MIT Mystery Hunt to start? Surprise! We’re kicking things off a little early this year, with an introductory set of over a dozen puzzles!</p>

<p>Solving these puzzles is entirely optional. They will not give your team any benefit when the real Mystery Hunt begins on January 14, and teams that skip these puzzles will not be hindered in any way. These puzzles are simply an appetizer we’re serving up before the main event. We hope you enjoy them.</p>

<p>You can find the puzzles at <a href="https://www.starrats.org">https://www.starrats.org</a>, and check out the <a href="https://www.youtube.com/watch?v=glOx2eVTpFo">launch trailer</a>.</p>

<p>See you in a month!</p>

<p>Team Palindrome and MIT Puzzle Club</p>
</html>'''
TEXT = '''
Don't want to wait another whole month for the 2022 MIT Mystery Hunt to start? Surprise! We're kicking things off a little early this year, with an introductory set of over a dozen puzzles!

Solving these puzzles is entirely optional. They will not give your team any benefit when the real Mystery Hunt begins on January 14, and teams that skip these puzzles will not be hindered in any way. These puzzles are simply an appetizer we're serving up before the main event. We hope you enjoy them.

You can find the puzzles at https://www.starrats.org, and check out the launch trailer at https://www.youtube.com/watch?v=glOx2eVTpFo.

See you in a month!

Team Palindrome and MIT Puzzle Club
'''

class Command(BaseCommand):
    help = 'Sends an email for rd0 launch'

    def handle(self, *args, **options):
        assert not DISABLED, 'This has already been run'

        if not confirm_emails() or not confirm_env():
            return

        users = User.objects.select_related('team', 'team__teamregistrationinfo').filter(team_role=UserTeamRole.SHARED_ACCOUNT)
        for user in users:
            if user.team.is_internal:
                continue

            send_mail(
                to_name=user.first_name, to_email=user.email, frm=FROM, subject=SUBJECT,
                text=TEXT, html=HTML)
