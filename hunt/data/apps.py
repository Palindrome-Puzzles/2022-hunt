from django.apps import AppConfig

# Register hunt callbacks for spoilr integration.
import hunt.data.callbacks

class HuntDataConfig(AppConfig):
    name = 'hunt.data'

    # Override the prefix for database model tables.
    label = 'hunt_data'
