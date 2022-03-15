import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model

from spoilr.core.api.team import get_shared_account_username
from spoilr.core.models import Team, TeamType, UserTeamRole

from hunt.app.models import TeamData
from hunt.app.core.teams import generate_team_auth
from hunt.registration.models import TeamRegistrationInfo
from hunt.data_loader.hunt_info import get_hunt_info

from ._common import confirm_command, TEAMS_LIST_PATH, row_get, row_get_int, row_get_yesno

class Command(BaseCommand):
    help = 'Updates teams in teams.tsv in-place'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

        parser.add_argument(
            '--change-passwords', action='store_true', dest='change_passwords',
            help="Do change the user's password.",
        )

    def handle(self, *args, **options):
        teams = _read_teams()
        if not options['interactive'] or confirm_command():
            _import_teams(teams, options)

def _import_teams(team_infos, options):
    for team_info in team_infos:
        print(f'Importing {team_info["username"]}')
        team_type = TeamType.PUBLIC if team_info["username"] == settings.HUNT_PUBLIC_TEAM_NAME else TeamType.INTERNAL
        team, _ = Team.objects.update_or_create(
            username=team_info['username'],
            defaults={
                'name': team_info['name'],
                'type': team_type,
            })

        print(f'Creating team data for {team_info["username"]}')
        team_data, _ = TeamData.objects.update_or_create(
            team=team,
            defaults={
                'auth': generate_team_auth(username=team_info['username'], password=team_info['password']),
            }
        )
        registration_info, _ = TeamRegistrationInfo.objects.update_or_create(
            team=team,
            defaults={
                'captain_phone': team_info['phone'],
                'size_total': team_info['number_of_members'],
                'locked': True,
            })

        UserModel = get_user_model()
        shared_user = UserModel.objects.filter(
            team=team, team_role=UserTeamRole.SHARED_ACCOUNT).first()
        if shared_user:
            # We make a shared user account with the same username as the team.
            print(f'Updating shared user account for {team_info["username"]}')
            shared_user.username = get_shared_account_username(team_info['username'])
            shared_user.email = team_info['email']
            shared_user.is_staff = team_info['is_admin']
            shared_user.is_superuser = team_info['is_admin']
            if options['change_passwords']:
                shared_user.set_password(team_info['password'])
            shared_user.save()
        else:
            print(f'Creating shared user account for {team_info["username"]}')
            shared_user = UserModel.objects.create_user(
                get_shared_account_username(team_info['username']),
                team_info['email'], team_info['password'],
                team=team, team_role=UserTeamRole.SHARED_ACCOUNT)
            shared_user.is_staff = team_info['is_admin']
            shared_user.save()

def _read_teams():
    teams = []
    with open(get_hunt_info(TEAMS_LIST_PATH)) as f:
        # Open team list and skip header row.
        reader = csv.reader(f, delimiter='\t')
        next(reader)

        for row in reader:
            if len(row) == 0: continue

            team = {}
            team['username'] = row_get(row, 0)
            team['name'] = row_get(row, 1)
            team['password'] = row_get(row, 2, '')
            team['email'] = row_get(row, 3)
            team['phone'] = row_get(row, 4)
            team['number_of_members'] = row_get_int(row, 5)
            team['is_admin'] = row_get_yesno(row, 6)

            if not team['username']:
                raise CommandError('A team is missing a username, cannot proceed')
            elif not _valid_username(team['username']):
                raise CommandError(f'Team {team["username"]} has an invalid username, cannot proceed')

            if not team['name']:
                print(f'Team {team["username"]} is missing a team name - skipping')
            elif not team['password'] and team['username'] != settings.HUNT_PUBLIC_TEAM_NAME:
                print(f'Team {team["username"]} is missing a password - skipping')
            else:
                teams.append(team)
    return teams

def _valid_username(username):
    # TODO(sahil): Implement
    return True

