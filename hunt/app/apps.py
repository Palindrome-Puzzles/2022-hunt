from django.apps import AppConfig

# Register hunt callbacks for spoilr integration.
import hunt.app.core.callbacks
import hunt.app.core.story_callbacks

class HuntAppConfig(AppConfig):
    name = 'hunt.app'

    # Override the prefix for database model tables.
    label = 'hunt_app'
