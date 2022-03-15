"""
Puzzle backend for the Open, Pass minipuzzle in "Genius Game".
"""

import random
from enum import Enum

from django.db import models

from spoilr.core.api.answer import mark_minipuzzle_solved

from hunt.app.special_puzzles.session_puzzle import session_puzzle, PuzzleSessionModelBase

from .common import OPEN_PASS_TARGETS
from .open_pass_progress import mark_level_as_won, has_access_to_level

# Open/Pass rules explanation.
# ---
# Source: https://en.wikipedia.org/wiki/The_Genius:_Rules_of_the_Game#Episode_7:_Open,_Pass_(7_Contestants)
#
# There are 3 levels. In each level, we have a hardcoded deck of 30 cards and a
# target score.
#
# Each card is either a number, "plus" or "times" card. It has a certain color,
# and in Level 3, an orientation ("up" or "down").
#
# The game proceeds as follows:
#  - Solvers pick 20/30 of the cards and choose an orientation for each.
#  - The server shuffles the 20 cards, and emits the colors and orientations of
#    the shuffled deck.
#  - Solvers work their way through the deck from right to left and one card at
#    a time. They can choose to either flip the card ("open") or skip it ("pass").
#    They must open exactly 10 cards.
#  - The 10 cards are treated as an equation.
#     - If there are multiple numbers in a row or multiple operators in a row,
#       keep the leftmost one.
#     - If the sequence starts with an operator, place a 0 at the beginning.
#     - If the sequence ends with an operator, ignore it.
#  - The score is the result of evaluating the equation.

class GameState(str, Enum):
    NEW = 'new'
    # The solver is selecting which cards to play with.
    SELECTING = 'selecting'
    # The solver is playing through their selected cards.
    PLAYING = 'playing'

class GameAction(str, Enum):
    BEGIN = 'begin'
    SELECT = 'select'
    OPEN = 'open'
    PASS = 'pass'

class CardAction(str, Enum):
    OPEN = 'open'
    PASS = 'pass'

class CardColor(str, Enum):
    BLACK = 'black'
    BLUE = 'blue'
    RED = 'red'

class CardOrientation(str, Enum):
    UP = 'up'
    DOWN = 'down'

ALLOWED_CARDS = tuple(range(1, 11)) + ('+', '*')
DECKS = {
    1: (
        [{'card': card, 'color': CardColor.BLACK} for card in (4, 4, 6, 6, 6, 7, 7, 8, 8, 9, 9, 10)] +
        [{'card': card, 'color': CardColor.BLUE} for card in (7, 7, 7, 7, 7, 8, 8, 8, 8, 10, '+', '+')] +
        [{'card': card, 'color': CardColor.RED} for card in (5, 9, 10, '*', '*', '*')]
    ),
    2: (
        [{'card': card, 'color': CardColor.BLACK} for card in (5, 5, 6, 6, 6, 7, 7, 9, 9, '+', '+', '+', '+', '+')] +
        [{'card': card, 'color': CardColor.BLUE} for card in (6, 7, 8, '*', '*', '*', '*', '*')] +
        [{'card': card, 'color': CardColor.RED} for card in (4, 4, 5, 5, 6, 6, 6, 9)]
    ),
    3: (
        [{'card': card, 'color': CardColor.BLACK} for card in (6, 6, 6, 7, 7, 7, 8, 8, 9, '*', '*', '*')] +
        [{'card': card, 'color': CardColor.BLUE} for card in (6, 7, 7, 8, 8, 8, 9, 9, 9, 10, '+', '+', '*', '*')] +
        [{'card': card, 'color': CardColor.RED} for card in (6, 6, 7, 7)]
    ),
}
ORIENTATION_ALLOWED = set([3])
MAX_LEVEL = max(DECKS.keys())

DECK_SIZE = 30
SELECTED_DECK_SIZE = 20
OPEN_COUNT = 10

assert all(len(deck) == DECK_SIZE for deck in DECKS.values())
assert set(DECKS.keys()) == set(OPEN_PASS_TARGETS.keys())
# At most 10 multiplies per deck, to ensure we can rig the shuffle appropriately.
assert all(sum(card['card'] == '*' for card in deck) <= 10 for deck in DECKS.values())

# Show decks to users sorted by number instead of color.
for deck in DECKS.values():
    deck.sort(key=lambda card:
        11 if card['card'] == '+'
        else 12 if card['card'] == '*'
        else card['card'])

class P246OpenPassGameModel(PuzzleSessionModelBase):
    # GameState
    state = models.CharField(max_length=20)
    # 1-3
    level = models.PositiveSmallIntegerField(blank=True, null=True)
    # An array of dicts, where each dict has the following keys:
    #  - card: 1-10 or '+' or '*'.
    #  - color: CardColor.
    #  - orientation: CardOrientation.
    #  - action: CardAction or None.
    deck = models.JSONField(blank=True, null=True)

def game_defaults():
    """Returns initial puzzle state."""
    return {
        'state': GameState.NEW,
    }

@session_puzzle(P246OpenPassGameModel, defaults_factory=game_defaults)
def game_view(request, client_request, game):
    """
    State transformer for the "Open, Pass" game.

    The request and response format can be the following.

    Beginning the game:
     - request: { action: 'begin', level: <1-3> }
     - response: { deck: <deck>, target: <number>, allowOrientation: <boolean> }
        - deck is an array of dicts where each has keys `card` and `color`.

    Selecting a deck:
     - request: { action: 'select': deck: <deck> }
        - deck is an array of dicts, where each dict has keys: `card`, `color` and `orientation`.
     - response: { deck: <deck> }
        - deck is an array of dicts, where each dict has keys: `card`, `color`, `chosen`, and `orientation`.
          The value for `card` will be `null`.

    Opening or passing on a card:
     - request: { action: 'open' | 'pass' }
     - response: { opened: number, played: number, score?: number, deck: <deck> }
        - opened is the number of cards opened so far
        - played is the number of cards opened so far
        - deck is an array of dicts, where each dict has keys: `color`,
          `orientation`, `chosen` and `card`. The value for `card` will be `null` if the
          card hasn't been revealed or was passed.
        - score is present if all future moves are forced, and is the game score.
    """
    assert 'action' in client_request, 'Missing required field `action`'

    if client_request['action'] == GameAction.BEGIN:
        assert game.state == GameState.NEW, 'Can\'t begin game'
        assert 'level' in client_request, 'Missing required field `level`'
        assert client_request['level'] in DECKS
        assert has_access_to_level(request.team, request.puzzle, client_request['level']), 'No access to level'

        return begin_game_view(game, client_request['level'])

    elif client_request['action'] == GameAction.SELECT:
        assert game.state == GameState.SELECTING, 'Can\'t select cards'
        assert 'deck' in client_request, 'Missing required field `deck`'
        assert len(client_request['deck']) == SELECTED_DECK_SIZE

        for card in client_request['deck']:
            assert card['card'] in ALLOWED_CARDS, 'Invalid card'
            assert card['color'] in tuple(e.value for e in CardColor), 'Invalid color'
            if game.level in ORIENTATION_ALLOWED:
                assert card['orientation'] in tuple(e.value for e in CardOrientation), 'Invalid orientation'
            else:
                assert 'orientation' not in card, 'Orientation not allowed'

        return select_game_view(game, client_request['deck'])

    elif client_request['action'] == GameAction.OPEN or client_request['action'] == GameAction.PASS:
        assert game.state == GameState.PLAYING, 'Can\'t play'
        return play_game_view(request, game, client_request['action'])

    else:
        raise Exception('Unknown action')

def begin_game_view(game, level):
    game.state = GameState.SELECTING
    game.level = level
    return {
        'deck': DECKS[level],
        'allowOrientation': level in ORIENTATION_ALLOWED
    }

def select_game_view(game, requested_deck):
    full_deck = DECKS[game.level]
    deck = []
    used = set()
    for card in requested_deck:
        for i in range(len(full_deck)):
            if i in used: continue
            if full_deck[i]['card'] == card['card'] and full_deck[i]['color'] == card['color']:
                used.add(i)
                deck.append({
                    'card': card['card'],
                    'color': card['color'],
                    'orientation': card.get('orientation', CardOrientation.UP),
                    'action': None,
                })
                break
        else:
            raise Exception('Tried to select invalid card')

    shuffled = rigged_shuffle(deck)

    game.state = GameState.PLAYING
    game.deck = shuffled
    return {
        'deck': [
            {
                'card': None,
                'color': card['color'],
                'orientation': card['orientation'],
                'chosen': False,
            } for card in shuffled
        ]
    }

def play_game_view(request, game, action):
    played, opened = get_counts(game.deck)

    # Play the next card.
    # Don't do anything if we're trying to open/pass an 11th card (due to
    # frontend spamming).
    if played - opened < OPEN_COUNT and opened < OPEN_COUNT:
        current = game.deck[played]
        played += 1
        if action == GameAction.OPEN:
            current['action'] = CardAction.OPEN
            opened += 1
        else:
            current['action'] = CardAction.PASS

    # Make rest of the moves if forced.
    complete = False
    if opened == OPEN_COUNT:
        complete = True
        for i in range(played, SELECTED_DECK_SIZE):
            game.deck[i]['action'] = CardAction.PASS
            played += 1
    elif opened + SELECTED_DECK_SIZE - played == OPEN_COUNT:
        complete = True
        for i in range(played, SELECTED_DECK_SIZE):
            game.deck[i]['action'] = CardAction.OPEN
            opened += 1
            played += 1

    # Generate response.
    score = None
    if complete:
        game.complete = True
        used = get_used_cards(game.deck)
        for card in used:
            card['used'] = True
        score = get_score(used)

    # Update team progress if they won!
    if complete and score >= OPEN_PASS_TARGETS[game.level]:
        mark_level_as_won(request.team, request.puzzle, game.level)

    deck = [
        {
            'card': card['card'] if card['action'] == CardAction.OPEN else None,
            'color': card['color'],
            'orientation': card['orientation'],
            'chosen': card['action'] == CardAction.OPEN,
            'used': card.get('used') == True
        }
        for card in game.deck
    ]

    return { 'score': score, 'deck': deck, 'opened': opened, 'played': played }

def get_counts(deck):
    played = 0
    opened = 0
    for card in deck:
        if not card['action']:
            break
        played += 1
        if card['action'] == CardAction.OPEN:
            opened += 1
    return played, opened

def is_operator(card):
    return card == '+' or card == '*'

def get_used_cards(deck):
    effective = []
    last_type = None
    for card in reversed(deck):
        if card['action'] != CardAction.OPEN: continue
        curr_type = 'op' if is_operator(card['card']) else 'num'
        if last_type != curr_type:
            effective.append(card)
        last_type = curr_type

    if is_operator(effective[-1]['card']):
        effective = effective[:-1]

    return effective

def get_score(used_cards):
    effective = [card['card'] for card in used_cards]
    if is_operator(effective[0]):
        effective = [0] + effective

    # Super-inefficient BODMAS impl.
    while len(effective) > 1:
        done = False
        for i in range(len(effective)):
            if effective[i] == '*':
                effective = effective[:i-1] + [effective[i-1] * effective[i+1]] + effective[i+2:]
                done = True
                break
        if done: continue

        for i in range(len(effective)):
            if effective[i] == '+':
                effective = effective[:i-1] + [effective[i-1] + effective[i+1]] + effective[i+2:]
                done = True
                break

    return effective[0]

def rigged_shuffle(deck):
    # To make games winnable, have the following constraints:
    #  - no "*" next to each other
    #
    # We implement this by first placing "*" in positions, then shuffle the rest.
    times_cards = []
    other_cards = []
    for card in deck:
        if card['card'] == '*':
            times_cards.append(card)
        else:
            other_cards.append(card)

    # If there are K "*", and N cards, then we can treat it as if each of the K
    # cards has a blank card on the right. The "*" can also be in the final position
    # with the blank card hanging over the edge.
    N = len(deck)
    K = len(times_cards)
    times_pos_domain = range((N+1) - K)
    times_pos = random.sample(times_pos_domain, K)
    times_pos.sort()

    for i in range(len(times_pos)):
        times_pos[i] += i

    times_pos_set = set(times_pos)
    other_pos = [i for i in range(N) if i not in times_pos_set]

    # Our positions are ordered, so shuffle the partitioned cards instead.
    random.shuffle(times_cards)
    random.shuffle(other_cards)

    # And finally collate.
    shuffled = [None for _ in range(N)]
    for i in range(K):
        shuffled[times_pos[i]] = times_cards[i]
    for i in range(N - K):
        shuffled[other_pos[i]] = other_cards[i]
    return shuffled
