from django.apps import AppConfig

class HuntPuzzleviewerConfig(AppConfig):
    name = 'hunt.puzzleviewer'

    # Override the prefix for database model tables.
    label = 'hunt_puzzleviewer'
