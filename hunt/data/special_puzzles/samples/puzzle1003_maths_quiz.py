"""
Sample puzzle that shows how to hide logic on the server without storing any state.

It's a really dumbed down version of https://2020.galacticpuzzlehunt.com/puzzle/make-your-own-math-quiz,
but shows how information and validity checking can be performed by the server
to protect puzzle integrity.
"""

import json, logging

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from hunt.app.views.common import require_puzzle_access

logger = logging.getLogger(__name__)

TARGETS = ['3+2', '2+1', '7+9']
PROMPTS = [f'Write `{target}`' for target in TARGETS]

@require_POST
@require_puzzle_access(allow_rd0_access=False)
def state_view(request):
    try:
        request_data = json.loads(request.body)

        statuses = []
        for i, response in enumerate(request_data):
            # Obviously, we could actually check the responses are correct here.
            if not response:
                statuses.append('')
            elif i < len(TARGETS) and response == TARGETS[i]:
                statuses.append('correct')
            else:
                statuses.append('incorrect')

        answer = None
        if all(s == 'correct' for s in statuses):
            if len(statuses) == len(PROMPTS):
                answer = request.puzzle.answer
            else:
                statuses.append('')

        prompts = [{'prompt': PROMPTS[i], 'status': statuses[i]} for i in range(len(statuses))]
        return JsonResponse({
            'answer': answer,
            'prompts': prompts,
        })

    except Exception as e:
        logger.exception("Unhandled exception in p1003")
        raise HttpResponseBadRequest()
