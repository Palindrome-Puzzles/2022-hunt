"""
Registry for puzzle-specific models that should be cleared when puzzle progress is reset.

# TODO(sahil): Consider using Django signals?
"""

import collections, logging

logger = logging.getLogger(__name__)

progress_model_classes = []

def register_progress_model(progress_model_class, team_field, puzzle_field):
    """Register for the subscriber to be called when the specified event type occurs."""
    progress_model_classes.append((progress_model_class, team_field, puzzle_field))

def clear_all_progress(team, puzzle):
    for progress_model_class, team_field, puzzle_field in progress_model_classes:
        filters = {team_field: team, puzzle_field: puzzle}
        progress_model_class.objects.filter(**filters).delete()
