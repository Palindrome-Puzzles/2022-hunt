"""
Helpers for writing session puzzles.

Session puzzles are interactive puzzles with internal state, where the state
needs to be stored server-side so that solvers can't just read the client source
code to find the answer.

A good example is a text adventure game. The solver's current inventory and
location needs to be tracked, but can't be stored and verified on the client
because they could read or modify the javascript to find the solution or give
themselves extra items.

A session puzzle stores state for each tab separately. Compare this to a
teamwork puzzle where the entire team shares the state. Session puzzles are
easier to implement, and more appropriate for non-cooperative games so each team
member can attempt it separately.

(Note: we don't use Django session IDs, so that solvers can have different state
per tab.)

For the client-side, you can use `session-puzzle.js` to interact with the
endpoint.

See `sample-blackjack-session-puzzle` for an example.
"""

import contextlib, json, logging, uuid

from django.db import transaction, models
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from hunt.app.views.common import require_puzzle_access

logger = logging.getLogger(__name__)

class PuzzleSessionModelBase(models.Model):
    """The base model for a session puzzle."""

    # A UUID for the solver's puzzle session.
    sid = models.CharField(max_length=32, unique=True, null=False)
    # The message sequence ordinal, used to de-dupe messages that have been retried.
    seq = models.IntegerField()
    # A cached version of the previous request, for message de-duping.
    previous_request = models.JSONField(blank=True, null=True)
    # A cached version of the previous response, for message de-duping.
    previous_response = models.JSONField(blank=True, null=True)
    # Whether the session has finished and can't progress any more. Set this to
    # force the client to begin a new session.
    completed = models.BooleanField()

    class Meta:
        abstract = True

def session_puzzle(ModelClass, *, defaults_factory=None, use_transaction=True, initial_response_factory=None):
    """
    Decorator for a session puzzle POST view that automatically takes care of
    fetching, de-duping, and persisting the puzzle session.

    The team needs to be authenticated and have access to the puzzle. The URL for
    the view should contain a `puzzle` kwarg with the puzzle URL.

    Any puzzle state should be stored in a model that is a subclass of
    `PuzzleSessionModelBase`.

    The decorated function describes how to transform the puzzle state. It
    receives the full request, the client request, and the current puzzle state.
    It can modify the puzzle state in place, and should return the client response
    as a `dict`.

    The decorated function is run within an atomic transaction, so it shouldn't
    do anything too long-lived. This behaviour can be disabled with the optional
    decorator parameter `use_transaction=False`.

    The decorator accepts an optional `defaults_factory` parameter. This is a no
    argument function that returns initial values for `ModelClass` when creating
    a new session.

    The decorator accepts an optional `initial_response_factory` parameter. This
    is a one-argument function that accepts the defaults returned by
    `defaults_factory` and returns the client's initial state for the puzzle.

    If the request is invalid or inconsistent with the state, raise an exception.
    The exception will be logged, and a generic error will be returned to the
    solver.

    If the request moves the session into an end state where further requests
    don't make sense, then set `completed=True` on the session model. This will
    ensure a new session is created for any future requests by that user. It
    will also let the client know that the session is completed in an internal
    response field.

    This is designed for use with `session-puzzle.js`. In particular, requests
    must have a `__seq` and optional `__sid` parameter. Responses will have a
    `__status` parameter. These are automatically consumed or injected by the
    decorator or by `session-puzzle.js`.
    """
    assert issubclass(ModelClass, PuzzleSessionModelBase)

    def decorator(fn):
        @require_POST
        @require_puzzle_access(allow_rd0_access=False)
        def view_fn(request):
            try:
                request_data = json.loads(request.body)
                seq = int(request_data['__seq'])
                if seq < 0:
                    raise Exception("__seq should be nonnegative")

                client_request = {
                    k: v for k, v in request_data.items() if k not in ('__seq', '__sid')
                }

                if seq == 0:
                    # First message - create a new session.
                    sid = uuid.uuid4().hex
                    defaults = defaults_factory() if defaults_factory else {}
                    initial_response = initial_response_factory(defaults) if initial_response_factory else {}
                    session = ModelClass.objects.create(sid=sid, seq=1, completed=False, **defaults)
                    return JsonResponse({'__sid': sid, '__status': 'success', **initial_response})

                # Continuation of existing session
                sid = request_data['__sid']

                # Execute the view and save the session atomically.
                context_manager = transaction.atomic() if use_transaction else contextlib.nullcontext()
                with context_manager:
                    try:
                        session = ModelClass.objects.get(sid=sid, completed=False)
                    except ModelClass.DoesNotExist:
                        raise Exception("No session found for sid '%s'" % sid)

                    if seq not in (session.seq, session.seq - 1):
                        raise Exception("Invalid seq %d for session id '%s'" % (seq, sid))

                    if seq == session.seq - 1:
                        # This request is a retry of a request that was already processed.
                        # Check that the request is actually the same, then return the same response.
                        if session.previous_request != client_request:
                            raise Exception("Request does not match previous request with same seq")
                        return JsonResponse(session.previous_response)

                    response = fn(request, client_request, session)
                    response['__status'] = 'complete' if session.completed else 'success'

                    session.seq += 1
                    session.previous_request = client_request
                    session.previous_response = response
                    session.save()

                    return JsonResponse(response)

            except Exception as e:
                logger.exception("Unhandled exception in session_puzzle for '%s'" % fn.__name__)
                return JsonResponse({"__status": "error"})
        return view_fn
    return decorator
