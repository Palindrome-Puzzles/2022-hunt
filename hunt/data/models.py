# Models that are only used in WebSocket based puzzles aren't discovered by Django
# until too late. So reference them here to make sure Django can find them.

from .special_puzzles.samples import puzzle1004_counting

from .special_puzzles import puzzle156_gears
from .special_puzzles import puzzle318_messy_room
