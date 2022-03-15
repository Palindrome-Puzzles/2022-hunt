import logging
import re
from django_hosts.resolvers import reverse as hosts_reverse
from django.conf import settings

from spoilr.core.api.events import HuntEvent, register, register_wildcard
from hunt.app.core.constants import ROUND_RD2_META_IDS, ROUND_RD2_URLS, ROUND_RD3_URLS, ROUND_RD3_META_IDS

def send_notification(team, puzzle_data):
    from .notifications import notify_team_log

    notification = puzzle_data['notification']
    deeplink = puzzle_data['slug']

    if notification != "":
        notify_team_log(
            team=team,
            event_type='story',
            message=notification,
            theme='story_beat',
            link="{}#{}".format(hosts_reverse('story', host='site-1'), deeplink),
        )

def send_email(team, puzzle_data):
    from django.core.mail import send_mail

    email_subject = puzzle_data['email_subject']
    email_body = puzzle_data['email_body']
    deeplink = puzzle_data['slug']
    link = "{}#{}".format(hosts_reverse('story', host='site-1'), deeplink)

    email_body = re.sub(r'\[link\]', link, email_body)

    if email_subject is not None and email_body is not None:
        email_body = re.sub(r'\[link\]', link, email_body)
        send_mail(
            email_subject,
            email_body,
            settings.STORY_FROM_EMAIL,
            [team.team_email]
        )

def on_puzzle_solved(team, puzzle, **kwargs):
    from spoilr.core.models import PuzzleAccess
    from .story import get_story_data
    if not team or team.is_public:
        return

    story_data = get_story_data()
    PUZZLE_STORY_DATA = {data['puzzle_id']: data for slug, data in story_data.items() if data['puzzle_id'] is not None}

    try:
        puzzle_data = PUZZLE_STORY_DATA[puzzle.external_id]

        send_notification(team, puzzle_data)
        send_email(team, puzzle_data)

        if puzzle.external_id in ROUND_RD2_META_IDS:
            rd2_meta_count = PuzzleAccess.objects.filter(team=team, puzzle__external_id__in=ROUND_RD2_META_IDS, puzzle__is_meta=True, solved=True).count()
            if rd2_meta_count == 2:
                send_notification(team, story_data['tock_1'])
                send_email(team, story_data['tock_1'])
        elif puzzle.external_id in ROUND_RD3_META_IDS:
            rd3_meta_count = PuzzleAccess.objects.filter(team=team, puzzle__round__url__in=ROUND_RD3_URLS, puzzle__is_meta=True, solved=True).count()
            if rd3_meta_count == 3:
                send_notification(team, story_data['tock_3'])
                send_email(team, story_data['tock_3'])
            elif rd3_meta_count == 6:
                send_notification(team, story_data['tock_4'])
                send_email(team, story_data['tock_4'])
    except KeyError as e:
        logger = logging.getLogger(__name__)
        logger.warning(e)

def on_round_unlocked(team, round, **kwargs):
    from django.core.mail import send_mail
    from .notifications import notify_team_log
    from .story import get_story_data
    if not team or team.is_public:
        return

    story_data = get_story_data()
    ROUND_STORY_DATA = {data['round_url']: data for slug, data in story_data.items() if data['round_url'] is not None}

    if round.url in ROUND_STORY_DATA:
        round_data = ROUND_STORY_DATA[round.url]
        send_notification(team, round_data)
        send_email(team, round_data)

    # Tock 2 (Bookspace opens)
    if round.url == ROUND_RD3_URLS[0]:
        try:
            send_notification(team, story_data['tock_2'])
            send_email(team, story_data['tock_2'])
        except KeyError as e:
            logger = logging.getLogger(__name__)
            logger.warning(e)



register(HuntEvent.PUZZLE_SOLVED, on_puzzle_solved)
register(HuntEvent.METAPUZZLE_SOLVED, on_puzzle_solved)
register(HuntEvent.ROUND_RELEASED, on_round_unlocked)
