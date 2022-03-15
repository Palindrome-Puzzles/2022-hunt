"""
Puzzle backend for the puzzle "Replicator Droid".

It's a game where you combine colored cards to form components, and certain
components lead to story progress.
"""
from enum import Enum
from django.db import models

from hunt.app.special_puzzles.session_puzzle import session_puzzle, PuzzleSessionModelBase

class Card(str, Enum):
    BLUE = 'blue'
    BROWN = 'brown'
    GREEN = 'green'
    GREY = 'grey'
    ORANGE = 'orange'
    PINK = 'pink'
    PURPLE = 'purple'
    RED = 'red'
    WHITE = 'white'
    YELLOW = 'yellow'

    # Are not available at the start.
    BLACK = 'black'
    GOLD = 'gold'
    MAROON = 'maroon'
    TURQUOISE = 'turquoise'

INITIAL_CARDS = [Card.BLUE, Card.BROWN, Card.GREEN, Card.GREY, Card.ORANGE, Card.PINK, Card.PURPLE, Card.RED, Card.WHITE, Card.YELLOW]
COMBINATIONS = {
    Card.BROWN: {
        Card.RED: Card.BLUE,
        Card.GREY: Card.PURPLE,
        Card.GREEN: Card.ORANGE,
        Card.BLUE: Card.GOLD,
        Card.PINK: Card.GREY,
        Card.WHITE: Card.GREY,
        Card.PURPLE: Card.MAROON,
        Card.YELLOW: Card.GREEN,
        Card.ORANGE: Card.WHITE,
    },
    Card.RED: {
        Card.BROWN: Card.GOLD,
        Card.GREY: Card.TURQUOISE,
        Card.GREEN: Card.PURPLE,
        Card.BLUE: Card.PINK,
        Card.PINK: Card.ORANGE,
        Card.WHITE: Card.BLUE,
        Card.PURPLE: Card.BLUE,
        Card.YELLOW: Card.ORANGE,
        Card.ORANGE: Card.YELLOW,
    },
    Card.GREY: {
        Card.BROWN: Card.MAROON,
        Card.RED: Card.GOLD,
        Card.GREEN: Card.BLACK,
        Card.BLUE: Card.GOLD,
        Card.PINK: Card.YELLOW,
        Card.WHITE: Card.BLUE,
        Card.PURPLE: Card.TURQUOISE,
        Card.YELLOW: Card.PINK,
        Card.ORANGE: Card.PURPLE,
    },
    Card.GREEN: {
        Card.BROWN: Card.TURQUOISE,
        Card.RED: Card.WHITE,
        Card.GREY: Card.TURQUOISE,
        Card.BLUE: Card.MAROON,
        Card.PINK: Card.PURPLE,
        Card.WHITE: Card.BLACK,
        Card.PURPLE: Card.BLACK,
        Card.YELLOW: Card.WHITE,
        Card.ORANGE: Card.YELLOW,
    },
    Card.BLUE: {
        Card.BROWN: Card.YELLOW,
        Card.RED: Card.GREY,
        Card.GREY: Card.ORANGE,
        Card.GREEN: Card.PURPLE,
        Card.PINK: Card.GOLD,
        Card.WHITE: Card.BROWN,
        Card.PURPLE: Card.TURQUOISE,
        Card.YELLOW: Card.GREEN,
        Card.ORANGE: Card.RED
    },
    Card.PINK: {
        Card.BROWN: Card.BLACK,
        Card.RED: Card.GREEN,
        Card.GREY: Card.GREEN,
        Card.GREEN: Card.BLACK,
        Card.BLUE: Card.PURPLE,
        Card.WHITE: Card.YELLOW,
        Card.PURPLE: Card.GOLD,
        Card.YELLOW: Card.WHITE,
        Card.ORANGE: Card.GREEN,
    },
    Card.WHITE: {
        Card.BROWN: Card.GOLD,
        Card.RED: Card.YELLOW,
        Card.GREY: Card.YELLOW,
        Card.GREEN: Card.GREY,
        Card.BLUE: Card.PINK,
        Card.PINK: Card.MAROON,
        Card.PURPLE: Card.MAROON,
        Card.YELLOW: Card.MAROON,
        Card.ORANGE: Card.WHITE,
    },
    Card.PURPLE: {
        Card.BROWN: Card.MAROON,
        Card.RED: Card.TURQUOISE,
        Card.GREY: Card.WHITE,
        Card.GREEN: Card.GOLD,
        Card.BLUE: Card.RED,
        Card.PINK: Card.BLACK,
        Card.WHITE: Card.BLUE,
        Card.YELLOW: Card.PINK,
        Card.ORANGE: Card.BLACK,
    },
    Card.YELLOW: {
        Card.BROWN: Card.PURPLE,
        Card.RED: Card.RED,
        Card.GREY: Card.WHITE,
        Card.GREEN: Card.PINK,
        Card.BLUE: Card.GOLD,
        Card.PINK: Card.MAROON,
        Card.WHITE: Card.TURQUOISE,
        Card.PURPLE: Card.BLUE,
        Card.ORANGE: Card.TURQUOISE,
    },
    Card.ORANGE: {
        Card.BROWN: Card.RED,
        Card.RED: Card.TURQUOISE,
        Card.GREY: Card.BLACK,
        Card.GREEN: Card.GREY,
        Card.BLUE: Card.TURQUOISE,
        Card.PINK: Card.BROWN,
        Card.WHITE: Card.YELLOW,
        Card.PURPLE: Card.PINK,
        Card.YELLOW: Card.GREEN,
    }
}
RECIPES = [
    {
        'inputs': set([Card.RED, Card.WHITE, Card.MAROON]),
        'name': 'DEY-YIC',
        'message': 'It auto-activates, and in the nearby Subzero Kitchen Delta (SKD), the ship\u2019s Sleeping Secondary Captain (SSC) is released from a Suspended Animation Tank (SAT).',
        'result': {
            'progress': 2,
            'under_progress_message': 'The captain cannot breathe the lack of air, and quickly dies.',
            'at_progress_message': None,
        }
    },
    {
        'inputs': set([Card.ORANGE, Card.GOLD, Card.TURQUOISE]),
        'name': 'TEL-AST-URY',
        'message': 'It auto-activates, and in the Subzero Kitchen Delta (SKD), a Developments Information Monitor (DIM) powers on, and displays the recent happenings with the ship. It then turns off.',
        'result': {
            'progress': 3,
            'under_progress_message': None,
            'at_progress_message': 'The captain, now briefed, nods to you and walks down the Upper Hallway Alpha (UHA) to stand on the Matter Teleport Dais (MTD).',
        }
    },
    {
        'inputs': set([Card.YELLOW, Card.PURPLE]),
        'name': 'CMD',
        'message': None,
        'result': {
            'progress': 4,
            'under_progress_message': 'It auto-activates, and you can see the Matter Teleport Dais (MTD) in nearby Upper Hallway Alpha (UHA) glows briefly.',
            'at_progress_message': 'It auto-activates, and teleports the captain from the Matter Teleport Dais (MTD) to the bridge, where they negotiate with the aliens. You soon receive a message from the captain, thanking you for saving the ship and possibly the entire Trigra-M civilization. It would be good to find a simple reply, that conveys what you saw during all this. You know the triads of components that come out of your replicator, and the designations of various items you have encountered. Perhaps by relating them you can form some appropriate message.',
        }
    },
    {
        'inputs': set([Card.GREEN, Card.BLUE, Card.GREY]),
        'name': 'YST-ARS',
        'message': 'It auto-activates.  Just outside your Droid Storage Alcove (DSA), you see the Hull Repair Machine (HRM) repair the hole in the ship\u2019s Duranium Inner Hull (DIH).',
        'result': {
            'progress': 0,
            'under_progress_message': None,
            'at_progress_message': None,
        }
    },
    {
        'inputs': set([Card.BLUE, Card.PINK, Card.BLACK]),
        'name': 'TRY',
        'message': 'It auto-activates.  You can hear Traditional Dioxygenated Air (TDA) from the Concentrated Air Supply (CAS) being pumped into the Large Upper Yard (LUY) outside your Droid Storage Alcove (DSA).',
        'result': {
            'progress': 1,
            'under_progress_message': 'It immediately escapes through the hole in the ship\u2019s hull.',
            'at_progress_message': None,
        }
    }
]

def get_available_recipes(components):
    components_set = set(components)
    return [
        i + 1
        for i, recipe in enumerate(RECIPES)
        if all(input in components_set for input in recipe['inputs'])
    ]

class P64ReplicatorDroidGameModel(PuzzleSessionModelBase):
    # A dict with the following keys:
    #  - `progress`: an integer from 0-4 with the current progress
    #  - `cards`: a list of available cards to use (arbitrary order)
    #  - `components`: a list of components on the conveyor belt in order
    state = models.JSONField()

def game_defaults():
    return {
        'state': {
            'progress': 0,
            'cards': INITIAL_CARDS,
            'components': [],
        },
    }

def game_response(state, message=None):
    return {
        'cards': state['cards'],
        'components': state['components'],
        'recipes': get_available_recipes(state['components']),
        'message': None,
    }

class GameAction(str, Enum):
    COMPONENT = 'component'
    DEVICE = 'device'

@session_puzzle(
    P64ReplicatorDroidGameModel,
    defaults_factory=game_defaults,
    initial_response_factory=lambda defaults: game_response(defaults['state'])
)
def game_view(request, client_request, game):
    """
    State transformer for the "Replicator Droid" puzzle.

    The request format is a dict with the following keys:
     - `action`: 'component'
     - `cards`: a list of exactly two cards. (These must be available or an
        error will be returned.)

    OR
     - `action`: 'device'
     - `recipe`: a number from 1-5. (The recipe must be available or an error
        will be returned.)

    The response format is a dict with the following keys:
     - `cards`: a list of available cards to use (arbitrary order)
     - `components`: a list of components on the conveyor belt in order
     - `recipes`: a list of recipes that can be used (arbitrary order). Each
        entry is a number 1-5.
     - `message`: an optional message to append to the game log, or None if no
        message should be appended.
    """
    assert 'action' in client_request, 'Missing required field `action`'

    if client_request['action'] == GameAction.COMPONENT:
        assert 'cards' in client_request and len(client_request['cards']) == 2, 'Must pass exactly two cards'

        available_cards = set(game.state['cards'])
        used_cards = client_request['cards']
        assert all(card in available_cards for card in used_cards)
        assert used_cards[0] in COMBINATIONS and used_cards[1] in COMBINATIONS[used_cards[0]], 'Invalid card combination'

        created = COMBINATIONS[used_cards[0]][used_cards[1]]
        did_drop_items = len(game.state['components']) >= 3

        message = f'''
        <p>The Component Replicator Unit (CRU) takes the <em>{used_cards[0]}</em> and <em>{used_cards[1]}</em> cards, rattles a bit, and creates a triad of components on your conveyor belt.</p>
        <p>You get, in order: <em>{used_cards[0]}</em> component, <em>{created}</em> component, and <em>{used_cards[1]}</em> component.</p>
        '''

        if did_drop_items:
            message += '<p>Your conveyor belt only has room for 5 components, so the oldest fell on the floor and broke.</p>'

        game.state = {
            **game.state,
            'cards': [card for card in game.state['cards'] if card not in used_cards],
            'components': (game.state['components'] + [used_cards[0], created, used_cards[1]])[-5:]
        }
        return {
            **game_response(game.state),
            'message': message,
        }

    elif client_request['action'] == GameAction.DEVICE:
        assert 'recipe' in client_request, 'Missing required field `recipe`'
        assert 1 <= client_request['recipe'] < len(RECIPES) + 1

        recipe = RECIPES[client_request['recipe'] - 1]
        available_components = set(game.state['components'])
        assert all(input in available_components for input in recipe['inputs'])

        components_in_use_order = [component for component in available_components if component in recipe['inputs']]

        should_advance = game.state['progress'] == recipe['result']['progress']
        message_parts = []
        if len(components_in_use_order) == 3:
            message_parts.append(f'<p>You combine the {components_in_use_order[0]} component, the {components_in_use_order[1]} component, and the {components_in_use_order[2]} component to build the {recipe["name"]} device.</p>')
        else:
            message_parts.append(f'<p>You combine the {components_in_use_order[0]} component and the {components_in_use_order[1]} component to build the {recipe["name"]} device.</p>')
        if recipe['message']:
            message_parts.append(f'<p>{recipe["message"]}</p>')
        if should_advance and recipe['result']['at_progress_message']:
            message_parts.append(
                f'<p>{recipe["result"]["at_progress_message"]}</p>')
        if not should_advance and recipe['result']['under_progress_message']:
            message_parts.append(
                f'<p>{recipe["result"]["under_progress_message"]}</p>')

        message = '\n'.join(message_parts)

        # If there are multiple components of the same color, be careful to only
        # remove one of them.
        new_components = game.state['components'][::]
        for input in recipe['inputs']:
            new_components.remove(input)

        game.state = {
            **game.state,
            'progress': game.state['progress'] + 1 if should_advance else game.state['progress'],
            'components': new_components,
        }
        return {
            **game_response(game.state),
            'message': message,
        }

    else:
        raise Exception('Unknown action')
