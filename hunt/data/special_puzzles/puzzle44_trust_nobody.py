"""
Puzzle backend for the puzzle "Trust Nobody".

It's an interactive quiz where if you get a question wrong, you get sent back to
the start. It also contains a team-level flag for whether the quiz has been
completed successfully.
"""
import urllib.parse

from django.db import models

from hunt.app.core.assets.refs import get_puzzle_static_path
from hunt.app.core.team_consumer import TeamConsumer

from hunt.app.special_puzzles.session_puzzle import session_puzzle, PuzzleSessionModelBase
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_progress_plugin import TeamProgressPlugin, TeamProgressModelBase, team_puzzle_progressed

QUESTIONS = [
    {
        'q': 'Hoe noem je een onverwacht einde van een film of een garneri[n]g die op veel cocktails wordt gebruikt?',
        'options': ['highball', 'quarrel', 'ending', 'everclear', 'lemon'],
        'score': 10,
        'image': 'q1-z4dlyoAiky.png',
        'correct': 1,
    },
    {
        'q': 'In welke hoeveelheid zitten volgens een bakker dertien ding[e]n?',
        'options': ['granola', 'oil', 'boxes', 'elephant', 'dough'],
        'score': 10,
        'image': 'q2-39n0JPLfyP.png',
        'correct': 2,
    },
    {
        'q': 'Wat voor soort arts geeft een opzette[l]ijk bevooroordeelde kijk op een politieke situatie?',
        'options': ['web', 'executive', 'spider', 'rotate', 'kindergarten'],
        'score': 8,
        'image': 'q3-lYAhAInp2S.png',
        'correct': 2,
    },
    {
        'q': 'Welk woord beschrijft een donkere bierstij[l] en ook een theepot in een lied?',
        'options': ['naughty', 'rinse', 'empty', 'ornery', 'rye'],
        'score': 1,
        'image': 'q4-00gVebMGNF.png',
        'correct': 0,
    },
    {
        'q': 'Wat is het woord [v]oor een gepubliceerde verklaring die de reputatie van een persoon schaadt?',
        'options': ['dirty', 'dragonfly', 'epigram', 'ruin', 'tick'],
        'score': 10,
        'image': 'q5-U8Fuxu9lCC.png',
        'correct': 1,
    },
    {
        'q': 'Welk dier is een v[o]lwassen mannelijke kip met een felrode kam op zijn kop?',
        'options': ['horse', 'schedule', 'elevator', 'quinoa', 'unicorn'],
        'score': 5,
        'image': 'q6-kGWIhFuGli.png',
        'correct': 1,
    },
    {
        'q': 'Over wat voor soort romance zingt Lady Gaga in ee[n] single uit 2009?',
        'options': ['evening', 'shallow', 'telephone', 'bathtub', 'independent'],
        'score': 12,
        'image': 'q7-uk4wNNqwCn.png',
        'correct': 3,
    },
    {
        'q': 'Welk type kopje wordt vaak gebruikt om hete vloeistoffen zoals koffie of warme chocola[d]emelk in te bewaren?',
        'options': ['orange', 'nip', 'mosquito', 'stein', 'ant'],
        'score': 7,
        'image': 'q8-FnGxF0273p.png',
        'correct': 2,
    },
    {
        'q': 'Welk[e] boekwinkel in New York City heeft de slogan &lsquo;achttien mijl aan boeken&rsquo;?',
        'options': ['beach', 'lion', 'paperback', 'hardcover', 'appendix'],
        'score': 3,
        'image': 'q9-tpGWveRhuf.png',
        'correct': 0,
    },
    {
        'q': 'Welk woord volgt [n]agel, computer, of zaak?',
        'options': ['traffic jam', 'bite', 'electric', 'toe', 'individual'],
        'score': 5,
        'image': 'q10-RqAd5vqS6j.png',
        'correct': 0,
    },
    {
        'q': 'Welke n[a]am werd in de klassieke mythologie gebruikt voor een planeet en is ook de naam van een gevallen engel in de Bijbel?',
        'options': ['comet', 'apostle', 'lunar', 'lollipop', 'match'],
        'score': 15,
        'image': 'q11-3xqQIoZaKS.png',
        'correct': 4,
    },
    {
        'q': 'Als je een [M]cKroket bestelt, wat voor soort broodje krijg je dan?',
        'options': ['yogurt', 'bun', 'yellow', 'toast', 'citizen'],
        'score': 12,
        'image': 'q12-FgEio9lzqR.png',
        'correct': 4,
    },
    {
        'q': 'Welk schaakstuk wordt soms aangeduid [m]et hetzelfde woord dat wordt gebruikt voor een gebouw waar een koningin of koning woont?',
        'options': ['hill', 'estate', 'smoke', 'checkmate', 'outhouse'],
        'score': 4,
        'image': 'q13-txJ6brLJTH.png',
        'correct': 2,
    },
    {
        'q': 'Welk ijshockeyte[a]m speelt zijn thuiswedstrijden in de stad waar een beroemd theekransje werd gehouden?',
        'options': ['Rangers', 'Red Wings', 'Eagles', 'Browns', 'Cardinals'],
        'score': 6,
        'image': 'q14-bSEC62C0k7.png',
        'correct': 3,
    },
    {
        'q': 'Welk lid van de lookfamilie staat ook bek[e]nd als wilde prei?',
        'options': ['turnip', 'disaster', 'avalanche', 'niece', 'shallot'],
        'score': 7,
        'image': 'q15-rU6obRWXAV.png',
        'correct': 1,
    },
    {
        'q': 'Welk woord wordt gebruikt voor een grotesk of a[n]gstaanjagend wezen, zoals één die zogenaamd in een Schots meer leeft?',
        'options': ['whiskey', 'elevator', 'rhinoceros', 'sample', 'submarine'],
        'score': 8,
        'image': 'q16-BrwyUQprab.png',
        'correct': 3,
    }
]

class P44TrustNobodyGameModel(PuzzleSessionModelBase):
    question = models.PositiveSmallIntegerField()

class P44TrustNobodyProgressModel(TeamProgressModelBase):
    won = models.BooleanField(default=False)

def game_defaults():
    """Returns initial puzzle state."""
    return {
        'question': 1,
    }

def get_question_response(num):
    question = QUESTIONS[num - 1]
    prev_question_score = QUESTIONS[num - 2]['score'] if num > 1 else 0
    return {
        'num': num,
        'q': question['q'],
        'options': question['options'],
        'image': get_image_path(question['image']),
        'score': prev_question_score
    }

def get_image_path(filename):
    return urllib.parse.urljoin(
        get_puzzle_static_path('trust-nobody', 'puzzle'),
        f'images/{filename}')

@session_puzzle(
    P44TrustNobodyGameModel,
    defaults_factory=game_defaults,
    initial_response_factory=lambda defaults: get_question_response(1)
)
def game_view(request, client_request, game):
    """
    State transformer for the "Trust Nobody" puzzle.

    The request format is a dict with the following keys:
     - `answer`: a number from 0-4

    The response is a dict with the following keys:
     - `num`: the 1-based question number, or None if there are no more questions.
     - `q`: the text of the question with one letter wrapped in square brackets,
       or None if there are no more questions.
     - `options`: a list of 5 options, or None if there are no more questions.
       first question
     - `image`: the fingerprint image to use for the question, or None if there
       are no more questions.
     - `score`: the number of points awarded for the previous question, or 0.

    Or the response is an empty dict if there are no more questions.
    """
    assert 0 <= client_request['answer'] <= 4
    assert 1 <= game.question <= len(QUESTIONS)

    if client_request['answer'] == QUESTIONS[game.question - 1]['correct']:
        game.question += 1
    else:
        game.question = 1

    if game.question <= len(QUESTIONS):
        return get_question_response(game.question)
    else:
        def mark_as_won(progress):
            progress.won = True

        team_puzzle_progressed(
            P44TrustNobodyProgressModel, request.team, request.puzzle, mark_as_won)

        return {
            'num': None,
            'score': QUESTIONS[-1]['score'],
        }

class P44TrustNobodyProgressConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        self.add_plugin(TeamPuzzlePlugin(44))
        self.add_plugin(TeamProgressPlugin(P44TrustNobodyProgressModel, project_progress))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

def project_progress(progress):
    return [
        {**q, 'image': get_image_path(q['image'])} for q in QUESTIONS
    ] if progress.won else []
