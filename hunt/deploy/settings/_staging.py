from ._base import *

DEBUG = False
ROOT_LOG_LEVEL = 'INFO'

SPOILR_ENABLE_DJANGO_ADMIN = True
SPOILR_ENABLE_DJANGO_ADMIN_DOCS = True

HUNT_LOAD_SAMPLE_ROUND = False
HUNT_PUZZLEVIEWER_ENABLED = True
HUNT_PUBLIC_TEAM_NAME = 'public'

HUNT_ASSETS_SERVE_STATICALLY = True
STATIC_URL = 'https://storage.googleapis.com/mitmh2022-staging/static/'

HUNT_WEBSITE_ACCESS_TOKEN = 'my-access-token'

HUNT_SHOULD_STUB_MISSING_PUZZLES = True

DEFAULT_FROM_EMAIL = 'hunt@staging-mail.mitmh2022.com'
SERVER_EMAIL = 'hunt-server@staging-mail.mitmh2022.com'
HUNT_SUBMISSIONS_EMAIL = 'submissions@staging-mail.mitmh2022.com'
HUNT_BOOKREPORT_EMAIL = 'bookreports@staging-mail.mitmh2022.com' # This isn't used
SPOILR_HQ_DEFAULT_FROM_EMAIL = 'hq@staging-mail.mitmh2022.com'
SPOILR_HINTS_FROM_EMAIL = 'hints@staging-mail.mitmh2022.com'
STORY_FROM_EMAIL = 'story@staging-mail.mitmh2022.com'
BOOK_REPORTS_EMAIL = 'bookreports@staging-mail.mitmh2022.com'
EMOJI_ART_EMAIL = 'emojiart@staging-mail.mitmh2022.com'

HUNT_SOLVES_BEFORE_HINTS_RELEASED = 3
HUNT_RD3_SOLVES_BEFORE_HINTS_RELEASED = 1
HUNT_ROUND_BREAKGLASS_UNLOCKS_ENABLED = True

HUNT_ENABLE_CACHING = True
HUNT_ENABLE_FILE_CACHING = True
PUZZLE_TECH_SUPPORT_EMAIL = 'no-reply+tech-support@staging.mitmh2022.com'
