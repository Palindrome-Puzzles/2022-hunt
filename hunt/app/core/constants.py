ROUND_SAMPLE_URL = 'sample-round'
ROUND_RD0_URL = 'prologue'
ROUND_EVENTS_URL = 'events'

ROUND_RD1_URL = 'the-investigation'
ROUND_RD2_URL = 'the-ministry'

SITE_1_ROUND_URLS = set([
    ROUND_SAMPLE_URL,
    ROUND_RD0_URL,
    ROUND_RD1_URL,
])

ROUND_RD2_URLS = [
    'billie-barker',
    'danni-dewey',
    'herschel-hayden',
    'alexei-lewis',
    'randy-and-riley-rotch',
]

ROUND_RD2_META_IDS = [
    83,
    152,
    168,
    201,
    155,
]

ROUND_RD3_URLS = [
    'noirleans',
    'lake-eerie',
    'the-quest-coast',
    'new-you-city',
    'recipeoria',
    'heartford',
    'whoston',
    'reference-point',
    'howtoona',
    'sci-ficisco',
]

ROUND_RD3_UNLOCK_PUZZLE_ID = 508

ROUND_RD3_HUB_URL = 'pen-station'
ROUND_RD3_META_URL = 'plot-device'

ROUND_RD3_URLS = [
    'noirleans',
    'lake-eerie',
    'the-quest-coast',
    'new-you-city',
    'recipeoria',
    'heartford',
    'whoston',
    'reference-point',
    'howtoona',
    'sci-ficisco',
]
ROUND_RD3_SELF_HELP_URL = 'new-you-city'

ROUND_RD3_META_IDS = [
    24,
    43,
    251,
    4,
    23,
    80,
    82,
    2,
    13,
    66,
]

ROUND_URLS_WITH_BONUS_CONTENT = ['new-you-city', 'the-quest-coast', 'lake-eerie']
PUZZLES_WITH_REWARDS = [('prologue', 20), ('the-ministry', 508), ('endgame', 555)]

PUZZLE_THIS_IS_NOW_A_PUZZLE_ID = 549

ROUND_ENDGAME_UNLOCK_PUZZLE_ID = 294
ROUND_ENDGAME_URL = 'endgame'
PUZZLE_ENDGAME_URL = 'completing-the-story'

PUZZLES_SKIP_CACHE_URLS = set([
    # Swag puzzles may have a countdown timer.
    'diced-turkey-hash',
    'whats-in-the-box-whats-in-the-box',
    'where-the-wild-things-are',

    # The endgame puzzle has page content change depending on the session
    # and when pages are discovered.
    PUZZLE_ENDGAME_URL,
])

# If a team makes more than this many incorrect attempt at a single puzzle,
# admins should be notified of that.
INCORRECT_ATTEMPT_ALERT_THRESHOLD = 10

# If a team's guess for a puzzle answer is at least the KEYth wrong one,
# minimum timeout is VALUE minutes
PUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES = {
    1: 0,
    4: 1,
    5: 2,
    6: 5,
}

# If a team's guess for a minipuzzle answer is at least the KEYth wrong
# one, minimum timeout is VALUE minutes. This table may be overridden
# for individual puzzles.
DEFAULT_MINIPUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES = {
    1: 0,
    8: 1,
    12: 3,
}

INTERACTION_MANUSCRIP = 'manuscrips'

EVENT_PUZZLE_MANUSCRIP = {
    # Crisis In Publishing
    468: .5,
    # Picaboo
    494: 1,
    # The Let’s Play That Goes Wrong
    496: .5,
    # Cryptic Dixit
    568: 1,
}


USE_POSTHUNT_ON_HUNT_COMPLETE = set([
    'a-handful-of-dishes',
    'crow-facts-3000',
    'loves-labors-crossed',
    'nowhere-to-hide',
    'please-prove-you-are-human',
    'replicator-droid',
    'sorcery-for-dummies',
    'strange-garnets',
    'tech-support',
    'the-day-you-begin',
    'trust-nobody',
    'word-search-of-babel',
    'wooded-path',
])
# Same as above, but only shows posthunt version to public teams when the hunt
# is complete, and continues showing original version to other teams. Use this
# when the posthunt version degrades the experience in some way (as opposed to
# just being spoilery).
USE_POSTHUNT_ON_PUBLIC_AND_HUNT_COMPLETE = set([
    'completing-the-story',
    'endless-practice',
    'introspection',
])

SESSION_BOOK_DISCOVERED = 'hunt:book-discovered'
