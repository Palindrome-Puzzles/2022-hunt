# From https://stackoverflow.com/a/49825979

import datetime, environ, json, os, requests, pathlib

assert False, 'Script is disabled, be careful running it'

base_path = pathlib.Path(__file__).parent.parent

env = environ.Env()
env.read_env(base_path.joinpath('.env'))

DATETIME_FORMAT = '%d %B %Y %H:%M:%S -0000'

def get_logs(start_date, end_date, next_url=None):
    if next_url:
        logs = requests.get(next_url, auth=("api", env('MAILGUN_API_KEY')))
    else:
        logs = requests.get(
            'https://api.mailgun.net/v3/mg.mitmh2022.com/events',
            auth=("api", env('MAILGUN_API_KEY')),
            params={"begin"       : start_date.strftime(DATETIME_FORMAT),
                    "end"         : end_date.strftime(DATETIME_FORMAT),
                    "ascending"   : "yes",
                    "pretty"      : "yes",
                    "limit"       : 300,}
        )
    return logs.json()

start = datetime.datetime.now() - datetime.timedelta(days=10)
end = datetime.datetime.now() - datetime.timedelta(days=0)
log_items = []
current_page = get_logs(start, end)

while current_page.get('items'):
    items = current_page.get('items')
    log_items.extend(items)
    next_url = current_page.get('paging').get('next', None)
    current_page = get_logs(start, end, next_url=next_url)

file_path = base_path.parent.joinpath('data', 'mailgun{0}.json'.format(start.strftime('%Y-%M-%d-%H%M%S')))
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.write_text(json.dumps(log_items, indent=2))
