import hashlib

from django.conf import settings

def generate_team_auth(*, username, password):
    # TODO(sahil): Consider using Django utils for this. Also consider the timestamped signer
    # or the user session ID to avoid auth secrets being stolen.
    # https://docs.djangoproject.com/en/3.2/topics/signing/
    m = hashlib.sha256()
    m.update(_to_bytes(settings.SECRET_KEY))
    m.update(_to_bytes(username))
    m.update(_to_bytes(password))
    return m.hexdigest()

def _to_bytes(string):
    return string.encode('utf-8')
