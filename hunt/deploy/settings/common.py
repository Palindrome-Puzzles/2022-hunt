from pathlib import Path

# Base path to the root of the 2022-hunt package.
BASE_PATH = Path(__file__).parent.parent.parent.parent

HUNT_CACHE_NAME = 'default'
HQ_CACHE_NAME = 'hq'
SPOILR_CACHE_NAME = 'spoilr'
SESSION_CACHE_NAME = 'session'

def load_gcloud_secret(secret_name):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/mitmh-2022/secrets/{secret_name}/versions/latest"
    return client.access_secret_version(name=name).payload.data.decode("UTF-8")
