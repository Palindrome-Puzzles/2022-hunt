from ._prod import *
from .common import load_gcloud_secret

SECRET_KEY = load_gcloud_secret('hunt-secret-key-prod')
