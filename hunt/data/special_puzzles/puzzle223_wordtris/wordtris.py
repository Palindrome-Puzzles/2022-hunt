import copy, json, logging, re

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from hunt.app.views.puzzle_submit_views import minipuzzle_answers_view_factory
from hunt.app.views.common import require_puzzle_access

from . import words as words

logger = logging.getLogger(__name__)

# 1. Get a payload from the client containing level number, last word placed (nullable) and current grid state (nullable)
# 2. Validate current grid state
# 3. Confirm whether last placement is valid
# 4. Return valid, invalid (level failed) or success (level finished)
# 5. (if valid) Return next word in sequence

WORDLIST_ALL = [ ["THE", "RAT", "SIS", "ROPE", "STUN", "EVE", "O", ":*&#"], ["GIVEN", "WIN", "ERA", "SPOT", "FOR", "AD", "*@&"], ["WORDS", "STAR", "ATE", "TALE", "PIN", "A", "$;~@&"], ["ARE", "SPA", "LAIR", "EAST", "LAP", "IN", "EN", "!/@=+"], ["NOT", "LATE", "USE", "CAR", "MEN", "AI", "-&@?"], ["RELEVANT", "EAR", "SOL", "PART", "ACE", "ON", "%*$"] ]

SECRET_MAP = {"~":"S", "!":"F", "@":"O", "#":"Y", "$":"M", "%":"D", "&":"N", "*":"I", "-":"K", "+":"R", "=":"U", ":":"T", ";":"A", "?":"B", "/":"L"};

NUM_COLS = 12;
NUM_ROWS = 25;

class PuzzleRequest:
    level = 0
    last_word = []
    grid = []
    wordlist = []
    valid = False
    debug = []

    def __init__(self, payload):
        self.level = int(payload['level'])
        self.last_word = payload['last_word']
        self.grid = self.build_grid(json.loads(payload['grid']))
        self.wordlist = WORDLIST_ALL[self.level - 1]
        self.valid = self.verify_grid()

    def build_grid(self, grid):
        test_grid = []

        for x in range(NUM_COLS):
            test_grid.append(" ")

        test_grid = [test_grid]

        for y in range(NUM_ROWS):
            test_grid.append(copy.deepcopy(test_grid[0]))

        for x in range(NUM_COLS):
            for y in range(NUM_ROWS):
                test_grid[y][x] = SECRET_MAP[grid[y][x]] if grid[y][x] in SECRET_MAP.keys() else grid[y][x]

        return test_grid

    def verify_grid(self) -> bool:
        # check that all words are placed, naively
        try:
            if self.last_word:
                used_words = [ SECRET_MAP[c] if c in SECRET_MAP.keys() else c for c in ''.join(self.wordlist[:self.wordlist.index(self.last_word)+1]) ]
                self.debug.append('generate used words list')
            else:
                self.debug.append('bypass check empty')
                return True
        except ValueError: # LAST_WORD isn't in the wordlist for the level
            self.debug.append('bypass check fail')
            return False

        all_grid = [c for c in ''.join([gridcell for gridrow in self.grid for gridcell in gridrow]).replace(" ", "")]

        for c in all_grid:
            try:
                used_words.remove(c)
            except ValueError:
                # the letter in the grid is not in the used letters
                self.debug.append('grid letter not expected')
                self.debug.append(c)
                self.debug.append(used_words)
                self.debug.append(all_grid)
                return False

        if len(used_words) > 0:
            # there are letters that should have been used, but haven't
            self.debug.append('expected letters not in grid')
            return False

        # horizontal words
        for y in range(NUM_ROWS):
            row_join = ''.join( self.grid[y] )
            row_words = (re.sub("  +", " ", row_join)).split(" ")
            if len(row_join.strip()) > 0 and not all([word in words.WORD_LIST for word in row_words if len(word) > 1]):
                self.debug.append('horizontal word not in list')
                return False

        # vertical words
        for x in range(NUM_COLS):
            col_join = re.sub("  +", " ", ''.join([ self.grid[y][x] for y in range(NUM_ROWS) ]))
            col_words = col_join.split(" ")
            if len(col_join) > 0 and not all([word in words.WORD_LIST for word in col_words if len(word) > 1]):
                self.debug.append('vertical word not in list')
                return False

        return True

    def __dict__( self ) -> dict:
        return {
            'level': self.level,
            'last_word': self.last_word,
            'grid': json.dumps(self.grid),
            'wordlist': self.wordlist,
        }

    def return_response(self) -> JsonResponse:
        return JsonResponse({
            'level': self.level,
            # 'last_word': self.last_word,
            # 'grid': self.grid,
            'wordlist': self.wordlist,
            'success': self.valid,
            'debug': self.debug,
        }, safe=False)

@require_POST
@require_puzzle_access(allow_rd0_access=False)
def state_view(request: HttpRequest) -> JsonResponse:
    return PuzzleRequest(request.POST).return_response()


# Code for minipuzzle checking:
MINIPUZZLE_ANSWERS = {
    '1': 'TINY',
    '2': 'ION',
    '3': 'MASON',
    '4': 'FLOUR',
    '5': 'KNOB',
    '6': 'DIM',
}
LOCK_OUT_THRESHOLDS = {1:3}
answers_view = minipuzzle_answers_view_factory(MINIPUZZLE_ANSWERS,
    lock_out_thresholds=LOCK_OUT_THRESHOLDS, puzzlewide_lock_out=True,
    lock_out_message="Your team guessed incorrectly.")
