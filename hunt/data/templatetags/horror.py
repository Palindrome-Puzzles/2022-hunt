from django import template

from hunt.app.core.assets.refs import get_round_static_path

register = template.Library()

HORROR_SOUNDS = {
    255: {
        "track": "album-4wz3PDOHwR.mp3",
        "text": "Reverse alphabetize the whole string.",
    },
    290: {
        "track": "assistant-WK2HLGfaaV.mp3",
        "text": "Change a word to its opposite.",
    },
    356: {
        "track": "box-c5MKT8NRld.mp3",
        "text": "Move the middle letter to the front.",
    },
    346: {
        "track": "called-nBJBlsQDeH.mp3",
        "text": "Divide the third letter in half.",
    },
    79: {
        "track": "colour-tHUKFBggRx.mp3",
        "text": "Divide in half, switch halves.",
    },
    308: {
        "track": "endless-EbHcAaoZKU.mp3",
        "text": "Take the middle four letters.",
    },
    162: {
        "track": "frank-dL5gjuaerZ.mp3",
        "text": "Switch the last two letters.",
    },
    574: {
        "track": "jump-yJ0gaaQTAd.mp3",
        "text": "Delete any letter appearing more than once.",
    },
    119: {
        "track": "lessons-VrM0gvTofj.mp3",
        "text": "Reverse the string.",
    },
    29: {
        "track": "lord-vlaX1A8SgZ.mp3",
        "text": "Insert an A between the first two consonants.",
    },
    91: {
        "track": "lsa-JEQoSsYXzZ.mp3",
        "text": "Move the second letter forward two spaces in the alphabet.",
    },
    479: {
        "track": "rack-jvUSYcx2RN.mp3",
        "text": "Turn the penultimate letter upside down.",
    },
    139: {
        "track": "rebus-7ogKTeHi6Z.mp3",
        "text": "Change the last letter to the penultimate letter.",
    },
    89: {
        "track": "scream-VK2YESAAFo.mp3",
        "text": "Double the last letter.",
    },
    136: {
        "track": "shields-RCJjZ3U4OH.mp3",
        "text": "Move a note to the front.",
    },
    44: {
        "track": "trust-CNOihpnJF5.mp3",
        "text": "Drop the first letter.",
    },
}


@register.simple_tag()
def horror_submission(puzzle, team):
    id = puzzle.external_id
    sound_obj = HORROR_SOUNDS.get(id, None)
    if sound_obj:
        track = sound_obj.get('track')
        text = sound_obj.get('text')
        return {
            'audio': track,
            'text': text,
            'rd_root': get_round_static_path(puzzle.round.url, variant='round'),
        }
    else:
        return {
            'audio': None,
        }
