"""
Event dispatching mechanism for hunt events that occur in spoilr.

This allows hunt-specific code to react to events including logging them, or
performing extra logic.

It's very similar to Django's signals.

# TODO(sahil): Consider using Django signals?
"""

import collections, importlib, logging
from enum import Enum

logger = logging.getLogger(__name__)

class HandlerPriority(Enum):
    LOW = -5,
    MEDIUM = 0,
    HIGH = 5,

class HuntEvent(str, Enum):
    """Types of hunt events."""
    PUZZLE_RELEASED = 'puzzle-released'
    PUZZLE_SOLVED = 'puzzle-solved'
    PUZZLE_ATTEMPTED = 'puzzle-attempted'
    PUZZLE_INCORRECTLY_ATTEMPTED = 'puzzle-incorrectly-attempted'

    METAPUZZLE_RELEASED = 'metapuzzle-released'
    METAPUZZLE_SOLVED = 'metapuzzle-solved'
    METAPUZZLE_ATTEMPTED = 'metapuzzle-attempted'
    METAPUZZLE_INCORRECTLY_ATTEMPTED = 'metapuzzle-incorrectly-attempted'

    MINIPUZZLE_ATTEMPTED = 'minipuzzle-attempted'
    MINIPUZZLE_COMPLETED = 'minipuzzle-completed'

    ROUND_RELEASED = 'round-released'

    INTERACTION_RELEASED = 'interaction-released'
    INTERACTION_ACCOMPLISHED = 'interaction-accomplished'
    INTERACTION_REOPENED = 'interaction-reopened'

    HINT_REQUESTED = 'hint-requested'
    HINT_RESOLVED = 'hint-resolved'

    HUNT_SITE_LAUNCHED = 'hunt-site-launched'
    HUNT_ACTIVITY_RESET = 'hunt-activity-reset'
    HUNT_TICK = 'hunt-tick'
    HUNT_PUZZLE_SHORTCUT = 'hunt-puzzle-shortcut'

    TEAM_REGISTERED = 'team-registered'
    TEAM_UPDATED = 'team-updated'

    CONTACT_REQUESTED = 'contact-requested'
    CONTACT_REQUEST_RESOLVED = 'contact-request-resolved'

    # TODO(sahil): Split these events between the relevant spoilr module.
    UPDATE_SENT = 'update-sent'
    EMAIL_RECEIVED = 'email-received'
    TASK_UNSNOOZED = 'task-unsnoozed'

    EXTRA_PUZZLES_RELEASED = 'extra-puzzles-released'

wildcard_subscriptions = []
subscriptions = collections.defaultdict(list)

def register(event_type, subscriber, priority=HandlerPriority.MEDIUM):
    """
    Register for the subscriber to be called when the specified event type occurs.

    The priority is used to control whether some handlers are run before others. A
    handler registered with a higher `priority` value will run first.

    Note: wildcard subscriptions implicitly have the lowest priority.
    """
    subscriptions[event_type].append((subscriber, priority))
    subscriptions[event_type].sort(key=lambda sub: sub[1].value * -1)

def register_wildcard(subscriber):
    """Register for the subscriber to be called when any event type occurs."""
    wildcard_subscriptions.append(subscriber)

def dispatch(event_type, *, message, object_id=None, team=None, **kwargs):
    """Trigger an event that the hunt state has changed."""
    if event_type != HuntEvent.HUNT_TICK:
        logger.info('event type=%s message="%s" team=%s object=%s', event_type.value, message, team, object_id)
        # Lazily import the model, so that this can module can be imported at
        # configuration time.
        from spoilr.core.models import SystemLog
        SystemLog.objects.create(event_type=event_type, message=message, team=team, object_id=object_id)

    _dispatch_internal(
        event_type, message=message, team=team, **kwargs)

def _dispatch_internal(event_type, **kwargs):
    for subscriber, unused_priority in map(_resolve_subscriber, subscriptions[event_type]):
        subscriber(**kwargs)

    for subscriber in map(_resolve_subscriber, wildcard_subscriptions):
        subscriber(event_type, **kwargs)

def _resolve_subscriber(subscriber_or_name):
    if isinstance(subscriber_or_name, str):
        module_name, function_name = subscriber_or_name.rsplit('.', 1)
        return getattr(importlib.import_module(module_name), function_name)
    return subscriber_or_name
