"""
Sample puzzle that demonstrates a "session puzzle" by implementing a blackjack game.

Solvers need to hit exactly 21, and then the answer is shown to them.
"""

import random

from django.db import models

from hunt.app.special_puzzles.session_puzzle import session_puzzle, PuzzleSessionModelBase

class P1002BlackjackGameModel(PuzzleSessionModelBase):
    pass

class P1002BlackjackCardsModel(models.Model):
    game = models.ForeignKey(P1002BlackjackGameModel, on_delete=models.CASCADE, related_name='cards')
    rank = models.CharField(max_length=10)
    suit = models.CharField(max_length=10)

SUITS = ['clubs', 'hearts', 'diamonds', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Optional factory for defaults to use when creating the session. If determistic,
# this could be done using default fields on the model. Or it could generate a
# random initial state.
def game_defaults():
    return {}

def get_best_score(*cards):
    score = 0
    num_aces = 0
    for card in cards:
        if card.rank == 'A':
            num_aces += 1
        elif card.rank in ('J', 'Q', 'K'):
            score += 10
        else:
            score += int(card.rank)

    ace_scores = [0]
    for i in range(num_aces):
        new_ace_scores = []
        for s in ace_scores:
            new_ace_scores += [s + 1, s + 11]
        ace_scores = new_ace_scores

    scores = [s + score for s in ace_scores]
    if any(s == 21 for s in scores):
        return 21
    else:
        return min(scores)

@session_puzzle(P1002BlackjackGameModel, defaults_factory=game_defaults)
def state_view(request, client_request, game):
    cards = game.cards.all()
    while True:
        suit = random.choice(SUITS)
        rank = random.choice(RANKS)
        if not any(card.suit == suit and card.rank == rank for card in cards):
            break

    card = P1002BlackjackCardsModel.objects.create(game=game, rank=rank, suit=suit)

    score = get_best_score(card, *cards)
    answer = None
    if score >= 21:
        game.completed = True
    if score == 21:
        answer = request.puzzle.answer

    return {
        'suit': suit,
        'rank': rank,
        'answer': answer,
    }
