# To access our Redis instance, we need to be running in the Google Cloud network.
# We can do that with a Cloud Function. This defines a cloud function to nuke
# any cache dbs in our redis instance.

# *Note*: The magic numbers below should be kept in sync with the Django settings.

from flask import abort
from google.cloud import secretmanager

import functions_framework
import os
import redis

def load_gcloud_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    name = f'projects/mitmh-2022/secrets/{secret_name}/versions/latest'
    return client.access_secret_version(name=name).payload.data.decode('UTF-8')

redis_host = load_gcloud_secret('redis-host')
redis_port = 6379

@functions_framework.http
def nuke_cache(request):
    env = request.args.get('env')
    if env == 'prod_gcloud':
        db_offset = 1
    elif env == 'staging_gcloud':
        db_offset = 8
    else:
        abort(403)

    for db in range(db_offset+1, db_offset+4):
        # redis-py doesn't implement the `select` command because of thread
        # safety, so make a separate client each time. Internally, it uses
        # connection pools so this isn't as inefficient as it looks.
        redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=db)
        redis_client.flushdb()

    return 'OK'
