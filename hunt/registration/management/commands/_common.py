import csv, pathlib, random, requests, string, os

HUNT_FROM = 'MIT Mystery Hunt 2022 <hunt@mitmh2022.com>'
HQ_FROM = 'HQ <hq@mitmh2022.com>'
SWAG_FROM = 'MIT Mystery Hunt Swag <swag@mitmh2022.com>'

def confirm_emails():
    token = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
    print('This command is dangerous as it will send emails!')
    print(f'Please enter: {token}')
    try:
        response = input('')
    except KeyboardInterrupt:
        return False
    return response == token

def confirm_env():
    print(f'Please enter the current env')
    try:
        response = input('')
    except KeyboardInterrupt:
        return False
    return response == os.environ['DJANGO_ENV']

def confirm_filename(expected_filename):
    print(f'Please enter the filename you think you\'re using')
    try:
        response = input('')
    except KeyboardInterrupt:
        return False
    return response == expected_filename

def read_csv_rows(filename, *, skip_header):
    with pathlib.Path(__file__).parent.joinpath('data', filename).open(encoding="utf8") as f:
        # Open team list and skip header row.
        reader = csv.reader(f)
        if skip_header:
            next(reader)
        return list(reader)

def read_csv(filename):
    rows = read_csv_rows(filename, skip_header=False)
    keys = rows[0]
    return [
        {key: row_get(row, i) for i, key in enumerate(keys)}
        for row in rows[1:]
    ]

def row_get(row, i, default=None):
    return row[i] if i < len(row) else default

def confirm_live_mode(*, test_mode):
    if not test_mode:
        print(f'Please enter "for real"')
        try:
            response = input('')
        except KeyboardInterrupt:
            return False
        return response == "for real"
    return True

def send_mail(*, to_email, frm, subject, text, html, to_name=None, merge_values=None):
    # TODO(sahil): Can almost certainly use Django's send_mail, but it's not
    # worth rewriting to use that instead.
    api_key = os.environ.get('MAILGUN_API_KEY')
    assert api_key, 'Need to set up the mailgun API key first'

    to = f'{to_name} <{to_email}>' if to_name else to_email
    merged_text = mail_merge(text, merge_values)
    merged_html = mail_merge(html, merge_values)

    print('Sending email to:', to)
    requests.post(
        'https://api.mailgun.net/v3/mg.mitmh2022.com/messages',
        auth=('api', api_key),
        data={'from': frm,
              'to': [to],
              'subject': subject,
              'text': merged_text,
              'html': merged_html})

def mail_merge(body, merge_values):
    if merge_values:
        assert '{{' in body
        for key, value in merge_values.items():
            body = body.replace('{{' + key + '}}', value)
    assert '{{' not in body
    return body
