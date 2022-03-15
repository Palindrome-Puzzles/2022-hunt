from ._staging import *
from .common import load_gcloud_secret

SECRET_KEY = load_gcloud_secret('hunt-secret-key-staging')
