"""
Minipuzzle answer checker for the puzzle "Once Upon A Time In The Quest".
"""
from hunt.app.views.puzzle_submit_views import minipuzzle_answers_view_factory

MINIPUZZLE_ANSWERS = {
    'quest474b': "GUINEA-BISSAU", #magically delicious
    'quest474c': "PORTUGUESE", #magically delicious
    'quest477b': "SUPERMAN", #sorcery for dummies
    'quest477c': "KRYPTONITE", #sorcery for dummies
    'quest373b': "CHAPEL", #a number of games
    'quest373c': "APSE", #a number of games
    'quest110b': "DO NOT GO GENTLE INTO THAT GOOD NIGHT", #curious customs
    'quest110c': "VILLANELLE", #curious customs
    'quest452b': "LIFE", #enchanted garden
    'quest452c': "VARIETY", #enchanted garden
    'quest276b': "BEAST", #potions
    'quest276c': "WEREWOLF", #potions
    'quest492b': "TENNESSEE", #royal steeds
    'quest492c': "KNOXVILLE", #royal steeds
    'quest163b': "KNIGHT", #something command
    'quest163c': "BATMAN", #something command
}

MINIPUZZLE_MESSAGES = {}
MINIPUZZLE_LABELS = {}

for p in MINIPUZZLE_ANSWERS:
    messages = {
        'b': 'is another step to completing this quest!',
        'c': 'is the end of this quest! Well done!',
    }
    labels = {
        'b': 'Step 2:',
        'c': 'Step 3:',
    }
    which = p[-1]
    MINIPUZZLE_MESSAGES[p] = messages[which]
    MINIPUZZLE_LABELS[p] = labels[which]

answers_view = minipuzzle_answers_view_factory(MINIPUZZLE_ANSWERS, message_list=MINIPUZZLE_MESSAGES, label_list=MINIPUZZLE_LABELS)
