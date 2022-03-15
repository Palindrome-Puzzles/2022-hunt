"""
Minipuzzle answer checker for the puzzle "EndlessPractice".
"""

import os

from django.http.response import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from hunt.app.core.team_consumer import TeamConsumer
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_minipuzzle_plugin import TeamMinipuzzlePlugin
from hunt.app.views.common import require_puzzle_access
from hunt.app.views.puzzle_submit_views import minipuzzle_answers_view_factory
from spoilr.core.models import Minipuzzle


MINIPUZZLE_ANSWERS = {
    'playplace':'DROPS THE BALL',
    'sunblock':'BAHAMIAN',
    'mouse-taken':'HELLO KITTY',
    'to-do':'WINDOW PANE',
    'castle-crisis':"GIORGIO’S ROCOCO GNOCCHI",
    'the-cracked-crystal':'GOOSE BUMP',
    'the-pitch':'A LARGE ROOM',
    'off-the-grid':'FLYING',
    'historical-pictures':'CHAMELEON',
    'unfinished-symphonies':'MOTOR VEHICLE',
}

MINIPUZZLE_ALTS = {
    'playplace':'A mathematical assignment statement',
    'sunblock':'A mathematical assignment statement',
    'mouse-taken':'A mathematical assignment statement',
    'to-do':'A mathematical assignment statement',
    'castle-crisis':'A mathematical assignment statement',
    'the-cracked-crystal':'A mathematical assignment statement',
    'the-pitch':'A mathematical assignment statement',
    'off-the-grid':'A mathematical assignment statement',
    'historical-pictures':'A mathematical assignment statement',
    'unfinished-symphonies':'A mathematical assignment statement',
}

MINIPUZZLE_IMAGES = {}
for ref in MINIPUZZLE_ALTS.keys():
        file_path  = os.path.join(os.path.dirname(__file__),"_Equations",ref+".png")
        file = open(file_path, "rb")
        MINIPUZZLE_IMAGES[ref] = file.read()
        file.close()

answers_view = minipuzzle_answers_view_factory(MINIPUZZLE_ANSWERS)

class P308EndlessPracticeConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        self.add_plugin(TeamPuzzlePlugin(308))
        self.add_plugin(TeamMinipuzzlePlugin(MINIPUZZLE_ANSWERS))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type


@require_POST
@require_puzzle_access(allow_rd0_access=False)
def result(request, *args, **kwargs):
    minipuzzle_ref = request.GET.get('ref', '')

    if minipuzzle_ref not in MINIPUZZLE_ALTS:
        return HttpResponseBadRequest("No such minipuzzle found.")

    minipuzzle = Minipuzzle.objects.get(
        team=request.team, puzzle=request.puzzle, ref=minipuzzle_ref)

    response = None
    if minipuzzle.solved or request.team.is_public:
        response = HttpResponse(MINIPUZZLE_IMAGES[minipuzzle_ref], content_type="image/png")
        response['X-Image-Alt'] = MINIPUZZLE_ALTS[minipuzzle_ref]
    else:
        response= HttpResponse("", content_type="text/plain")
    return response