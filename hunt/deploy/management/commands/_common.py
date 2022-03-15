def confirm_command(message = 'This command is dangerous!'):
    print(message)
    try:
        response = input('Are you sure (y/n): ')
    except KeyboardInterrupt:
        return False
    return response.lower() == 'y'

PUZZLES_LIST_PATH = 'puzzles.tsv'
ROUNDS_LIST_PATH = 'rounds.tsv'
TEAMS_LIST_PATH = 'teams.tsv'
INTERACTIONS_LIST_PATH = 'interactions.tsv'

def row_get(row, i, default=None):
    return row[i] if i < len(row) and row[i] != '' else default

def row_get_int(row, i, default=0):
    raw = row_get(row, i, default='')
    return int(raw) if raw != '' else default

def row_get_yesno(row, i):
    return row_get(row, i, default='').lower() == 'yes'
