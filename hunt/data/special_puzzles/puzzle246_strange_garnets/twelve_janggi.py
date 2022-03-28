"""
Puzzle backend for the Twelve Janggi minipuzzle in "Genius Game".
"""
import json
from enum import Enum

from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from spoilr.core.api.answer import mark_minipuzzle_solved
from hunt.app.views.common import require_puzzle_access

from .common import TWELVE_JANGGI_MINIPUZZLE_REF

# Twelve Janggi rules explanation.
# ---
# Sources:
#  - https://demmunicate.tistory.com/entry/Twelve-gang-game
#  - https://www.mafiathesyndicate.com/viewtopic.php?t=1632
#
# It's a chess variant played on a 3x4 board.
#  - Kings can move in any direction.
#  - Ministers can move diagonally.
#  - Generals can move horizontally or vertically.
#  - Men can only move forward.
#  - Lords can move horizontally, vertically, or diagonally forwards.
#  - When a man reaches the final rank, it's promoted to a lord and turned around.
#  - When a piece is captured, it is removed from the board and now belongs to
#    the other player. (If it's a lord, it reverts to a man.)
#  - On your turn, you can either move a piece, or place a piece you own from
#    off the board. You can place it in empty square except the final rank.
#  - You win the game when you take the opponent's king, or your king makes it
#    onto the final rank, and isn't in check.
#
# Very similar to http://nekomado.com/data/dobutsushogi_rule/en.pdf, except you
# can't drop a piece into the final rank.

class Piece(str, Enum):
    KING = 'king'
    GENERAL = 'general'
    MINISTER = 'minister'
    MAN = 'man'
    FEUDAL_LORD = 'feudal-lord'

# Moves are (type, from_rank, from_file, to_rank, to_file) tuples.
OPTIMAL_MOVES = set([
    (
        (Piece.GENERAL, None, None, 3, 2),
        (Piece.MINISTER, None, None, 4, 2),
        (Piece.GENERAL, None, None, 2, 1),
        (Piece.MAN, 4, 3, 3, 3),
        (Piece.MAN, None, None, 3, 1),
        (Piece.MINISTER, 4, 2, 3, 1),
        (Piece.GENERAL, 2, 1, 3, 1),
    ),
    (
        (Piece.GENERAL, None, None, 3, 2),
        (Piece.MINISTER, None, None, 3, 1),
        (Piece.GENERAL, None, None, 2, 1),
        (Piece.MINISTER, 3, 1, 2, 2),
        (Piece.KING, 1, 3, 2, 2),
        (Piece.MAN, 4, 3, 3, 3),
        (Piece.GENERAL, 2, 1, 3, 1),
    ),
    (
        (Piece.GENERAL, None, None, 3, 2),
        (Piece.MINISTER, None, None, 3, 1),
        (Piece.GENERAL, None, None, 2, 1),
        (Piece.MINISTER, 3, 1, 4, 2),
        (Piece.MAN, None, None, 3, 1),
        (Piece.MINISTER, 4, 2, 3, 1),
        (Piece.GENERAL, 2, 1, 3, 1),
    ),
])

INITIAL_PIECES = [
    # Player 1's initial pieces.
    { 'type': Piece.KING, 'player': 1, 'rank': 1, 'file': 3},
    { 'type': Piece.MINISTER, 'player': 1, 'rank': 2, 'file': 3},
    { 'type': Piece.MAN, 'player': 1, 'rank': None, 'file': None},
    { 'type': Piece.GENERAL, 'player': 1, 'rank': None, 'file': None},
    { 'type': Piece.GENERAL, 'player': 1, 'rank': None, 'file': None},
    # Player 2's initial pieces.
    { 'type': Piece.KING, 'player': 2, 'rank': 4, 'file': 1},
    { 'type': Piece.MAN, 'player': 2, 'rank': 4, 'file': 3},
    { 'type': Piece.MINISTER, 'player': 2, 'rank': None, 'file': None},
]


@require_POST
@require_puzzle_access(allow_rd0_access=False)
def board_view(request, *args, **kwargs):
    return JsonResponse({
        'playerTurn': 1,
        'moveNumber': 1,
        'pieces': INITIAL_PIECES,
    })

@require_POST
@require_puzzle_access(allow_rd0_access=False)
def check_view(request, *args, **kwargs):
    moves = json.loads(request.body)
    normalized_moves = tuple(
        (move['type'], move['fromRank'], move['fromFile'], move['toRank'], move['toFile'])
        for move in moves
    )
    optimal = normalized_moves in OPTIMAL_MOVES
    if optimal:
        mark_minipuzzle_solved(request.team, request.puzzle, TWELVE_JANGGI_MINIPUZZLE_REF)
    return JsonResponse({
        'optimal': optimal
    })
