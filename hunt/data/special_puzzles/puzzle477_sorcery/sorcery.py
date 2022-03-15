import requests
import pathlib
import pprint
import json5
import json
import re

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from hunt.app.views.common import require_puzzle_access
from hunt.app.core.helpers import dispatch_discord_alert

from . import sorcery_functions as sorcery_functions

SOLUTIONS = {
    'skeleton': 'apv',
    'kraken': 'bzq',
    'dragon': 'cwi',
    'ghost': 'dmx',
    'mummy': 'en',
    'zombie': 'foj',
    'orc': 'gk',
    'cyclops': 'hs',
    'achillesheel': 'truly',
}

CODENAMES = {
    'cyclops': '0',
    'dragon': '1',
    'ghost': '2',
    'kraken': '3',
    'mummy': '4',
    'orc': '5',
    'skeleton': '6',
    'zombie': '7',
    'achillesheel': 'final',
}

INPUTS = {
    'cyclops': 'gelatinous',
    'dragon': 'dimwit',
    'ghost': 'vowel',
    'kraken': 'obsolescent',
    'mummy': 'miracle',
    'orc': 'acumen',
    'skeleton': 'leopard',
    'zombie': 'profound',
}

# Note: This was redacted before making the repository public.
DISCORD_WEBHOOK = None

@require_POST
@require_puzzle_access(allow_rd0_access=False)
def cast_view(request, *args, **kwargs):
    data = {}
    # if request.method != 'POST':
    #     raise Http404

    data = json.loads(request.body)
    spell = data['spell']
    correct_spells = data['spells']

    if spell == "":
        return JsonResponse({
            'status': 'fail',
            'reason': 'No spell present.'
        })

    spell = spell.strip().lower()
    spell = re.sub(r'\s+',' ', spell)

    if len(re.sub(r'[a-z\s]','',spell)) > 0:
        return JsonResponse({
            'status': 'fail',
            'reason': 'Letters only, please.'
        })

    if len(spell) > 60:
        return JsonResponse({
            'status': 'fail',
            'reason': 'Too long.'
        })

    words = spell.split(" ")
    outputs = []

    for word in words:
        valid = False
        if len(word) < 3:
            return JsonResponse({
                'status': 'fail',
                'reason': 'Each word must be three letters or longer.'
            })
        with pathlib.Path(__file__).parent.joinpath('words.txt').open() as wordlist:
            lines = wordlist.readlines()
            for line in lines:
                if word == line.strip():
                    valid = True
                    break

        if not valid:
            return JsonResponse({
                'status': 'fail',
                'reason': 'Each word must be in the dictionary.'
            })

    input = words.pop()
    output = input
    pattern = ""
    message = ""

    if len(words) == 0:
        return JsonResponse({
            'status': 'fail',
            'reason': 'Spells must be two words or longer.'
        })

    # if you're reusing a spell, say so…
    # collect all first letters, but not from the last words
    depleted_letters = ""
    for correct_spell in correct_spells.values():
        depleted_letters += "".join(x[0].lower() for x in correct_spell.split(" ")[:-1])

    print(depleted_letters)

    if spell == "truly powerful":
        alert = "{} `{}` by **{}**".format(":mage:", spell.upper(), request.team.name)
        dispatch_discord_alert(DISCORD_WEBHOOK, alert, username='Sorcery Bot')

        return JsonResponse({
            'status': 'success',
            'message': 'You certainly are. 😉'
        })

    depleted = False
    # cycle thru and apply transformations
    for word in reversed(words):
        letter = word[:1]

        if letter in depleted_letters:
            depleted = True

        pattern = letter + pattern
        output = getattr(sorcery_functions, letter)(word, output).lower()
        outputs.append(output.upper())

    output = re.sub(r' ','', output.lower())
    sol = SOLUTIONS.get(output, None)
    codename = CODENAMES.get(output, None)
    proper_input = INPUTS.get(output, None)
    proper_length = len(SOLUTIONS.get(output, ''))
    status = ""
    if sol != None and pattern != '':
        emoji = ':person_shrugging:'
        message = "Well this is awkward. Looks like you somehow found another way to defeat that monster. Alas, this isn't the intended spell for {}. Keep going.".format(output.upper())

        if output == 'achillesheel' and sol == pattern:
            output = 'achilles heel'
            outputs[-1] = 'ACHILLES HEEL'
            emoji = ':trophy:'
            message = "Now that's what I call a spell. Call it in!"
            status = "final"
        elif input not in INPUTS.values():
            emoji = ':no_entry_sign:'
            message = "Nice work, but you need a different final word."
        elif proper_length != len(words):
            emoji = ':no_entry_sign:'
            message = "Nice work, but that monster's spell requires a different number of words."
        elif input != proper_input:
            emoji = ':pinching_hand:'
            message = "Clever! But that monster only responds to a different final word."
        elif sol == pattern:
            emoji = ':white_check_mark:'
            message = "Hooray! You destroyed the {}!".format(output.upper())
            codename = codename
            status = "monster"

        alert = "{} `{}` via `{}` by **{}**".format(emoji, output.upper(), spell.upper(), request.team.name)
        dispatch_discord_alert(DISCORD_WEBHOOK, alert, username='Sorcery Bot')
    elif depleted:
        return JsonResponse({
                'status': 'fail',
                'reason': 'One or more of these transformations has exhausted its magic.'
            })

    data = {
        'status': status,
        'spell': spell,
        'message': message,
        'codename': "monster{}".format(codename),
        # 'outputs': outputs,
        'output': output.upper(),
    }
    return JsonResponse(data)
