import collections, csv, logging

from django_hosts.resolvers import reverse as hosts_reverse
from django.utils.timezone import now
from spoilr.core.models import PuzzleAccess

from hunt.data_loader.hunt_info import get_hunt_info
from hunt.deploy.management.commands._common import row_get, row_get_int, row_get_yesno
from hunt.deploy.util import is_autopilot

from .constants import ROUND_RD1_URL, ROUND_RD2_URL, ROUND_RD3_HUB_URL, ROUND_RD3_UNLOCK_PUZZLE_ID, ROUND_RD3_URLS

# TODO(sahil): This is quite awkward, we shouldn't be depending on helpers (let alone
# private helpers) from a Django commands directory. Wrap this in some abstraction.
STORY_LIST_PATH = 'story.tsv'
_STORY_DATA = None

def get_story_data():
    # Lazy-load story data into memory, so that it doesn't happen for scripts
    # like collectpuzzlefiles.
    global _STORY_DATA
    if not _STORY_DATA:
        _STORY_DATA = {}
        with open(get_hunt_info(STORY_LIST_PATH)) as f:
            # Open puzzle list and skip header row.
            reader = csv.reader(f, delimiter='\t')
            next(reader)

            for row in reader:
                if len(row) == 0: continue

                section = row_get(row, 0)
                sticky = row_get_yesno(row, 1)
                slug = row_get(row, 2, None)
                story_page_headline = row_get(row, 3, None)
                story_page_text = row_get(row, 4, None)
                puzzle_id = row_get_int(row, 5, None)
                round_url = row_get(row, 6, None)
                yt_id = row_get(row, 7, None)
                notification = row_get(row, 8, None)
                email_subject = row_get(row, 9, None)
                email_body = row_get(row, 10, None)
                code = row_get(row, 11, None)

                # Note: This is super hacky, but relies on the autopilot override
                # appearing after the normal story beat in the spreadsheet, and
                # having a specific suffix in the ID.
                autopilot_suffix = '_autopilot'
                if slug and (not slug.endswith(autopilot_suffix) or is_autopilot()):
                    actual_slug = slug[:-len(autopilot_suffix)] if slug.endswith(autopilot_suffix) else slug
                    _STORY_DATA[slug] = {
                        'row': reader.line_num,
                        'slug': actual_slug,
                        'section': section,
                        'sticky': sticky,
                        'story_page_headline': story_page_headline,
                        'story_page_text': story_page_text,
                        'puzzle_id': puzzle_id,
                        'round_url': round_url,
                        'yt_id': yt_id,
                        'notification': notification,
                        'email_subject': email_subject,
                        'email_body': email_body,
                        'code': code,
                    }
    return _STORY_DATA

def get_story_summary(context):
    story_data = get_story_data()
    is_round_unlocked = lambda round_url: any(round_info['round'].url == round_url for round_info in context['rounds'])

    def get_pa(round_url, puzzle_id):
        # pa = puzzle access
        if not is_round_unlocked(round_url): return None
        round = next((round for round in context['rounds'] if round['round'].url == round_url), None)
        for puzzle_info in round['puzzles']:
            if puzzle_info['puzzle'].external_id == puzzle_id:
                return puzzle_info

    def get_ra_timestamp(round_url):
        # ra = round access
        if not is_round_unlocked(round_url): return None
        round = next((round for round in context['rounds'] if round['round'].url == round_url), None)
        x = round['round'].roundaccess_set.filter(team=context['team']).first()
        return x.timestamp

    if context['team'].is_public:
        stub_solve_time = now()

        is_puzzle_solved = lambda round_url, puzzle_id: True
        when_puzzle_solved = lambda round_url, puzzle_id: stub_solve_time
        is_puzzle_unlocked = lambda round_url, puzzle_id: True
        when_puzzle_unlocked = lambda round_url, puzzle_id: stub_solve_time
        when_round_unlocked = lambda round_url: stub_solve_time

        tock_appears_time = stub_solve_time
        tock_blinks_time = stub_solve_time
        tock_disappears_time = stub_solve_time
    else:
        is_puzzle_solved = lambda round_url, puzzle_id: get_pa(round_url, puzzle_id) and get_pa(round_url, puzzle_id)['solved']
        when_puzzle_solved = lambda round_url, puzzle_id: get_pa(round_url, puzzle_id) and get_pa(round_url, puzzle_id)['solved'] and get_pa(round_url, puzzle_id)['solved_time']
        is_puzzle_unlocked = lambda round_url, puzzle_id: get_pa(round_url, puzzle_id)
        when_puzzle_unlocked = lambda round_url, puzzle_id: get_pa(round_url, puzzle_id)['timestamp']
        when_round_unlocked = lambda round_url: get_ra_timestamp(round_url)

        rd2 = next((round for round in context['rounds'] if round['round'].url == ROUND_RD2_URL), None)
        rd2_metas_solved = [puzzle_info for puzzle_info in rd2['puzzles'] if puzzle_info['puzzle'].is_meta and puzzle_info['solved']] if rd2 else []
        rd2_metas_solved_sorted = sorted(rd2_metas_solved, key = lambda meta: meta['solved_time'])
        tock_appears_time = rd2_metas_solved_sorted[1]['solved_time'] if len(rd2_metas_solved_sorted) >= 2 else None

        r3_metas_solved = list(PuzzleAccess.objects.filter(team=context['team'], puzzle__round__url__in=ROUND_RD3_URLS, puzzle__is_meta=True, solved=True).order_by('solved_time'))
        tock_blinks_time = r3_metas_solved[2].solved_time if len(r3_metas_solved) >= 3 else None
        tock_disappears_time = r3_metas_solved[5].solved_time if len(r3_metas_solved) >= 6 else None

    tasks = [
        {
            "text": "Hayden library has disappeared!  <strong>Your task is to <a href='{}'>investigate and find out what has happened</a></strong>.".format(hosts_reverse('puzzle_view', args=('the-investigation',), host='site-1')),
            "open": True,
            "done": is_puzzle_solved(ROUND_RD1_URL, 120), # Investigation solved
        },
        {
            "text": "Bookspace is being destroyed!  <strong>Your task is to <a href='{}'>find out what is causing the damage</a></strong>.".format(hosts_reverse('round_view', args=('the-ministry',), host='site-1')),
            "open": is_round_unlocked(ROUND_RD2_URL), # Ministry round open
            "done": is_puzzle_solved(ROUND_RD2_URL, 1), # Ministry metameta solved
        },
        {
            "text": "Bookspace is being destroyed! <strong>Your task is to <a href='{}'>make it stop</a></strong>.".format(hosts_reverse('puzzle_view', args=('fruit-around',), host='site-1')),
            "open": is_puzzle_unlocked(ROUND_RD2_URL, 508), # Ministry metameta solved
            "done": is_puzzle_solved(ROUND_RD2_URL, 508), # Fruit Around solved
        },
        {
            "text": "Bits of Bookspace keep disappearing!  <strong>Your task is to <a href='{}'>find the components of the Plot Device</a></strong>.".format(hosts_reverse('act3_hub', host='site-1')),
            "open": is_round_unlocked(ROUND_RD3_URLS[0]), # Round 3 (Bookspace) open
            "done": is_puzzle_unlocked('plot-device', 294), # Battery pack open
        },
        {
            "text": "You have all the components of the Plot Device!  <strong>Your task is to <a href='{}'>find what you need to activate it</a></strong>!".format(hosts_reverse('puzzle_view', args=('battery-pack',), host='site-1')),
            "open": is_puzzle_unlocked('plot-device', 294), # Battery pack open
            "done": is_puzzle_solved('plot-device', 294), # Battery pack solved
        },
        {
            "text": "The tollbooth is back, but your coins won't work!  <strong>Your task is to <a href='{}'>complete your story</a> so you'll have an appropriate coin</strong>.".format(hosts_reverse('endgame_puzzle', host='site-1')),
            "open": is_puzzle_solved('plot-device', 294), # Battery pack solved
            "done": is_puzzle_solved('endgame', 555), # Endgame solved
        },
    ]

    story_beats = collections.OrderedDict()
    story_beats['ministry_unlocked'] = when_round_unlocked(ROUND_RD2_URL)

    story_beats['barker_solved'] = when_puzzle_solved(ROUND_RD2_URL, 83)
    story_beats['dewey_solved'] = when_puzzle_solved(ROUND_RD2_URL, 152)
    story_beats['hayden_solved'] = when_puzzle_solved(ROUND_RD2_URL, 168)
    story_beats['lewis_solved'] = when_puzzle_solved(ROUND_RD2_URL, 201)
    story_beats['rotch_solved'] = when_puzzle_solved(ROUND_RD2_URL, 155)

    story_beats['tock_1'] = tock_appears_time
    story_beats['ministry_solved'] = when_puzzle_solved(ROUND_RD2_URL, 1)
    story_beats['fruit_around_solved'] = when_puzzle_solved(ROUND_RD2_URL, 508)

    story_beats['tock_2'] = when_round_unlocked(ROUND_RD3_URLS[0])

    story_beats['noirleans_solved'] = when_puzzle_solved('noirleans', 24)
    story_beats['lake_eerie_solved'] = when_puzzle_solved('lake-eerie', 43)
    story_beats['the_quest_coast_solved'] = when_puzzle_solved('the-quest-coast', 251)

    story_beats['tock_3'] = tock_blinks_time

    story_beats['new_you_city_solved'] = when_puzzle_solved('new-you-city', 4)
    story_beats['recipeoria_solved'] = when_puzzle_solved('recipeoria', 23)
    story_beats['heartford_solved'] = when_puzzle_solved('heartford', 80)

    story_beats['tock_4'] = tock_disappears_time

    story_beats['whoston_solved'] = when_puzzle_solved('whoston', 82)
    story_beats['reference_point_solved'] = when_puzzle_solved('reference-point', 2)
    story_beats['howtoona_solved'] = when_puzzle_solved('howtoona', 13)
    story_beats['sci_ficisco_solved'] = when_puzzle_solved('sci-ficisco', 66)

    story_beats['noirleans_unlocked'] = when_round_unlocked('noirleans')
    story_beats['lake_eerie_unlocked'] = when_round_unlocked('lake-eerie')
    story_beats['the_quest_coast_unlocked'] = when_round_unlocked('the-quest-coast')
    story_beats['new_you_city_unlocked'] = when_round_unlocked('new-you-city')
    story_beats['recipeoria_unlocked'] = when_round_unlocked('recipeoria')
    story_beats['heartford_unlocked'] = when_round_unlocked('heartford')
    story_beats['whoston_unlocked'] = when_round_unlocked('whoston')
    story_beats['reference_point_unlocked'] = when_round_unlocked('reference-point')
    story_beats['howtoona_unlocked'] = when_round_unlocked('howtoona')
    story_beats['sci_ficisco_unlocked'] = when_round_unlocked('sci-ficisco')

    # story_beats['plot_device_unlocked'] = when_round_unlocked('plot-device'), # currently not in data fil
    story_beats['tock_5'] = when_puzzle_solved('plot-device', 294)

    # story_beats['runaround_unlocked'] = when_round_unlocked('endgame'), # currently not in data fil
    story_beats['tock_6'] = when_puzzle_solved('endgame', 555)

    visible_beats = {}
    for k, timestamp in story_beats.items():
        if timestamp is not None and timestamp is not False:
            try:
                current_beat = story_data[k]
                current_beat['timestamp'] = timestamp
                visible_beats[k] = current_beat
            except KeyError as e:
                logger = logging.getLogger(__name__)
                logger.exception(e)

    sorted_beats = sorted(visible_beats.values(), key=lambda beat: beat['timestamp'])

    return {
        "beats": sorted_beats,
        "round3_unlocked": is_round_unlocked(ROUND_RD3_URLS[0]),
        "tasks": tasks,
    }
