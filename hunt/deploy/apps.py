from django.apps import AppConfig

class HuntDeployConfig(AppConfig):
   name = 'hunt.deploy'

   # Override the prefix for database model tables.
   label = 'hunt_deploy'
