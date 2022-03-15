import requests
from django.conf import settings

def pick(dict, *keys):
    return {k: dict[k] for k in keys}

def omit(dict, *keys):
    omit_set = set(keys)
    return {k: dict[k] for k in dict.keys() if k not in omit_set}

def dispatch_discord_alert(webhook, content, username='HuntBot'):
    if not webhook:
        return

    # content = '{} [{}]'.format(content, timezone.localtime().strftime('%H:%M:%S'))
    if len(content) >= 2000:
        content = content[:1996] + '...'
    if settings.DEBUG:
        print('Discord alert:\n' + content)
        return
    requests.post(webhook, data={'username': username, 'content': content})
