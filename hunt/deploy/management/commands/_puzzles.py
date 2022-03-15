import collections, csv, json, logging
from enum import Enum

from django.conf import settings

from spoilr.core.api.answer import canonicalize_puzzle_answer, canonicalize_puzzle_answer_display

from hunt.data_loader.hunt_info import get_hunt_info
from hunt.data_loader.puzzle import get_puzzle_asset_urls, get_puzzle_data_text
from hunt.data_loader.round import get_round_data_text, get_round_asset_urls

from ._common import PUZZLES_LIST_PATH, ROUNDS_LIST_PATH, row_get, row_get_int, row_get_yesno

logger = logging.getLogger(__name__)

class Level(str, Enum):
    WARN = 'warn'
    ERROR = 'error'

def read_puzzle_assets():
    """
    Checks the puzzle assets for consistency, and returns the inconsistencies and
    puzzle metadatas by external ID.
    """
    inconsistencies = []
    info_lookup = {}
    names = set()

    # Note: no need to check if URL is unique, because of asset_url being fetched
    # from the filesystem, so at least that is guaranteed to be unique.

    for asset_url in get_puzzle_asset_urls():
        metadata_content = get_puzzle_data_text(asset_url, 'metadata.json')
        config_content = get_puzzle_data_text(asset_url, 'config.json')
        if not metadata_content:
            logger.error(f'Puzzle with URL {asset_url} is missing metadata.json - skipping')
            continue

        metadata = json.loads(metadata_content)
        config = json.loads(config_content) if config_content else {}
        external_id = metadata.get('puzzle_idea_id')
        metadata_url = metadata.get('puzzle_slug')
        name = metadata.get('puzzle_title')
        answer = metadata.get('answer', '')
        pseudo = config.get('pseudo', {})

        hints_content = get_puzzle_data_text(asset_url, 'hints.json')
        hints = json.loads(hints_content) if hints_content else []
        if not _verify_hints(hints):
            inconsistencies.append((Level.ERROR, f'badly formed hints.json for {asset_url}'))

        if not external_id or not metadata_url or not name or not answer:
            inconsistencies.append((Level.ERROR, f'missing fields from metadata {metadata}'))
        if metadata_url and asset_url != metadata_url:
            inconsistencies.append((Level.ERROR, f'asset_url {asset_url} does not match metadata_url={metadata_url}'))
        if external_id in info_lookup:
            inconsistencies.append((Level.ERROR, f'multiple assets with external ID {external_id}'))
        if name in names:
            inconsistencies.append((Level.ERROR, f'multiple assets with name {name} (including {asset_url}'))
        if answer != canonicalize_puzzle_answer_display(answer):
            inconsistencies.append((Level.WARN, f'answer for {asset_url} is {answer} which is not in canonical format'))
        if not all(answer == canonicalize_puzzle_answer_display(answer) for answer in pseudo.keys()):
            inconsistencies.append((Level.WARN, f'some pseudoanswers for {asset_url} are not in canonical format: {pseudo}'))
        if not all(isinstance(response, str) for response in pseudo.values()):
            inconsistencies.append((Level.ERROR, f'pseudoanswer responses for {asset_url} are not strings: {pseudo}'))
        if len(pseudo) != len(set(canonicalize_puzzle_answer(answer) for answer in pseudo.keys())):
            inconsistencies.append((Level.ERROR, f'pseudoanswers are not unique after normalization: {pseudo}'))

        index_html = get_puzzle_data_text(asset_url, 'index.html')
        if index_html == None:
            if get_puzzle_data_text(asset_url, 'index.template.html') != None:
                inconsistencies.append((Level.WARN, f'asset with url={asset_url} has not been compiled yet, it may not work'))
            else:
                inconsistencies.append((Level.WARN, f'asset with url={asset_url} missing index.html'))

        solution_index_html = get_puzzle_data_text(asset_url, 'solution/index.html')
        if solution_index_html == None:
            inconsistencies.append((Level.WARN, f'asset with url={asset_url} missing solution/index.html'))

        index_style = get_puzzle_data_text(asset_url, 'style.css')
        solution_index_style = get_puzzle_data_text(asset_url, 'solution/style.css')

        if external_id:
            # Re-create the dict so consumers don't need to guard against missing fields.
            info_lookup[external_id] = {
                'url': asset_url,
                'name': name,
                'answer': answer,
                'credits': metadata.get('credits', ''),
                'pseudo': {
                    canonicalize_puzzle_answer_display(k): v for k, v in pseudo.items()
                },
                'hints': hints,
            }
        if name:
            names.add(name)

    return inconsistencies, info_lookup

def read_puzzle_list():
    inconsistencies = []
    info_lookup = {}
    orders_by_round = collections.defaultdict(set)

    with open(get_hunt_info(PUZZLES_LIST_PATH)) as f:
        # Open puzzle list and skip header row.
        reader = csv.reader(f, delimiter='\t')
        next(reader)

        for row in reader:
            if len(row) == 0: continue

            round_url = row_get(row, 0)
            external_id = row_get_int(row, 1)
            order = row_get_int(row, 2, None)
            unlock_order = row_get_int(row, 3, None)
            round_solve_count_to_unlock = row_get_int(row, 4, None)
            interaction_to_unlock = row_get(row, 6)
            is_meta = row_get_yesno(row, 7)

            raw_solves_to_unlock = row_get(row, 5, '')
            solves_to_unlock = list(map(int, raw_solves_to_unlock.split(', '))) if raw_solves_to_unlock else []

            if not external_id or not round_url or not order:
                inconsistencies.append((Level.ERROR, f'missing fields in puzzle row {row}'))
            if external_id in info_lookup:
                inconsistencies.append((Level.ERROR, f'multiple puzzle rows with external ID {external_id}'))
            if round_url and order and order in orders_by_round[round_url]:
                inconsistencies.append((Level.ERROR, f'duplicate puzzle order {order} in round {round_url}'))
            # Puzzles either unlock by solving enough puzzles within the meta,
            # or by solving some feeder puzzles, but not both.
            if sum([unlock_order != None, round_solve_count_to_unlock != None, len(solves_to_unlock) > 0]) > 1:
                inconsistencies.append((Level.ERROR, f'unlock for puzzle is not well defined {unlock_order} {round_solve_count_to_unlock} {solves_to_unlock}'))

            if external_id:
                # Re-create the dict so consumers don't need to guard against missing fields.
                info_lookup[external_id] = {
                    'round_url': round_url,
                    'order': order,
                    'is_meta': is_meta,
                    'unlock_order': unlock_order,
                    'round_solve_count_to_unlock': round_solve_count_to_unlock,
                    'solves_to_unlock': solves_to_unlock,
                    'interaction_to_unlock': interaction_to_unlock,
                }
            if round_url and order:
                orders_by_round[round_url].add(order)

    return inconsistencies, info_lookup

def read_round_assets():
    inconsistencies = []
    round_asset_urls = set(get_round_asset_urls())

    for asset_url in round_asset_urls:
        required_files = ('puzzle.tmpl', 'puzzle_solution.tmpl', 'round.tmpl')
        for required_file in required_files:
            html = get_round_data_text(asset_url, required_file)
            if not html:
                inconsistencies.append((Level.WARN, f'round with url={asset_url} missing {required_file}'))

    return inconsistencies, round_asset_urls

def read_round_list():
    inconsistencies = []
    info_lookup = {}
    names = set()
    orders = set()

    with open(get_hunt_info(ROUNDS_LIST_PATH)) as f:
        # Open round list and skip header row.
        reader = csv.reader(f, delimiter='\t')
        next(reader)

        for row in reader:
            if len(row) == 0: continue

            url = row_get(row, 0)
            name = row_get(row, 1)
            order = row_get_int(row, 2)
            is_sample = row_get_yesno(row, 3)

            if not url or not name or not order:
                inconsistencies.append((Level.ERROR, f'missing fields in round row {row}'))
            if url in info_lookup:
                inconsistencies.append((Level.ERROR, f'multiple rounds with url {url}'))
            if name in names:
                inconsistencies.append((Level.ERROR, f'multiple rounds with name {name} (including {url})'))
            if order in orders:
                inconsistencies.append((Level.ERROR, f'multiple rounds with order {order} (including {url})'))

            if url:
                # Re-create the dict so consumers don't need to guard against missing fields.
                info_lookup[url] = {
                    'name': name,
                    'order': order,
                    'is_sample': is_sample,
                }
            if name: names.add(name)
            if order: orders.add(order)

    return inconsistencies, info_lookup

def read_puzzles_and_rounds():
    asset_inconsistencies, asset_info_lookup = read_puzzle_assets()
    list_inconsistencies, list_info_lookup = read_puzzle_list()
    round_asset_inconsistencies, round_asset_urls = read_round_assets()
    round_list_inconsistencies, round_list_info_lookup = read_round_list()

    inconsistencies = (
        asset_inconsistencies + list_inconsistencies +  round_asset_inconsistencies + round_list_inconsistencies)

    consistent_round_info_lookup = {}
    for round_url in round_list_info_lookup.keys():
        if round_url not in round_asset_urls:
            inconsistencies.append((Level.WARN, f'round {round_url} missing assets'))
        consistent_round_info_lookup[round_url] = round_list_info_lookup[round_url]

    for round_asset_url in round_asset_urls:
        if round_asset_url not in consistent_round_info_lookup:
            inconsistencies.append((Level.WARN, f'round {round_asset_url} missing from list - skipping'))

    consistent_puzzle_info_lookup = {}
    for external_id in list_info_lookup.keys():
        if external_id in asset_info_lookup:
            consistent_puzzle_info_lookup[external_id] = {
                **asset_info_lookup[external_id],
                **list_info_lookup[external_id],
            }
        elif settings.HUNT_SHOULD_STUB_MISSING_PUZZLES:
            inconsistencies.append((Level.WARN, f'puzzle {external_id} missing assets - stubbing'))
            stub_asset_info = {
                'url': f'stub{external_id}',
                'name': f'Stub puzzle {external_id}',
                'answer': f'STUB ANSWER {external_id}',
                'credits': '',
                'pseudo': {},
                'hints': [],
            }
            consistent_puzzle_info_lookup[external_id] = {
                **stub_asset_info,
                **list_info_lookup[external_id],
            }
        else:
            inconsistencies.append((Level.WARN, f'puzzle {external_id} missing assets - skipping'))

    for external_id in asset_info_lookup.keys():
        if external_id not in list_info_lookup:
            inconsistencies.append((Level.WARN, f'puzzle {external_id} missing from list - skipping'))

    return inconsistencies, consistent_puzzle_info_lookup, consistent_round_info_lookup

# TODO(sahil): Implement the following.
def _verify_hints(hints):
    return True
