from django.conf import settings
from django.urls import re_path

from .special_puzzles.samples import puzzle1004_counting

from .special_puzzles import puzzle44_trust_nobody
from .special_puzzles import puzzle156_gears
from .special_puzzles import puzzle318_messy_room

from .special_puzzles.puzzle246_strange_garnets import consumer as puzzle246_consumer
from .special_puzzles.puzzle555_completing_the_story import progress as puzzle555_progress
from .special_puzzles.puzzle308_endless_practice import puzzle308_endless_practice

websocket_urlpatterns = [
    re_path('^ws/puzzle/trust-nobody$', puzzle44_trust_nobody.P44TrustNobodyProgressConsumer.as_asgi()),
    re_path('^ws/puzzle/gears-and-arrows$', puzzle156_gears.P156GearsConsumer.as_asgi()),
    re_path('^ws/puzzle/strange-garnets$', puzzle246_consumer.P246StrangeGarnetsConsumer.as_asgi()),
    re_path('^ws/puzzle/the-messy-room$', puzzle318_messy_room.P318MessyRoomConsumer.as_asgi()),
    re_path('^ws/puzzle/endless-practice$', puzzle308_endless_practice.P308EndlessPracticeConsumer.as_asgi()),
    re_path('^ws/puzzle/completing-the-story$', puzzle555_progress.P555CTSConsumer.as_asgi()),
]

if settings.HUNT_LOAD_SAMPLE_ROUND:
    websocket_urlpatterns += [
        re_path('^ws/puzzle/counting$', puzzle1004_counting.P1004CountingConsumer.as_asgi()),
    ]
