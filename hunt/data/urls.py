from django.conf import settings
from django.urls import re_path
from ratelimit.core import is_ratelimited
from ratelimit.decorators import ratelimit

from hunt.app.views.puzzle_views import puzzle_subview

from .special_puzzles.samples import puzzle1002_blackjack
from .special_puzzles.samples import puzzle1003_maths_quiz

from .special_puzzles import puzzle44_trust_nobody
from .special_puzzles import puzzle64_replicator_droid
from .special_puzzles import puzzle216_captcha
from .special_puzzles import puzzle113_babel
from .special_puzzles import puzzle251_once_upon_a_time_in_the_quest
from .special_puzzles import puzzle508_fruit_around
from .special_puzzles import puzzle331_tech_support # File doesn't exist. Commented out below too.

from .special_puzzles.puzzle93_the_day_you_begin import views as puzzle93_the_day_you_begin_views
from .special_puzzles.puzzle477_sorcery import sorcery as puzzle477_sorcery
from .special_puzzles.puzzle344_wooded_path import wooded_path as puzzle344_wooded_path
from .special_puzzles.puzzle246_strange_garnets import checker as puzzle246_checker
from .special_puzzles.puzzle246_strange_garnets import open_pass as puzzle246_open_pass
from .special_puzzles.puzzle246_strange_garnets import twelve_janggi as puzzle246_twelve_janggi
from .special_puzzles.puzzle4_introspection import puzzle4_introspection
from .special_puzzles.puzzle269_loves_labors_crossed import request as puzzle269_request
from .special_puzzles.puzzle223_wordtris import wordtris as puzzle223_wordtris
from .special_puzzles.puzzle308_endless_practice import puzzle308_endless_practice
from .special_puzzles.puzzle555_completing_the_story import checker as puzzle555_cts_checker
from .special_puzzles.puzzle555_completing_the_story import progress as puzzle555_cts_progress


# groups requests together if they come from the same user and are against the same url
def bucket_by_user(group, request):
    return (request.session.session_key if request.session.session_key else 'no session key ') + request.path

def bucket_by_team(group, request):
    return request.user.team.name + request.path


basic_ratelimit = ratelimit(rate='20/10s', key=bucket_by_user, block=True)

extra_ratelimit = ratelimit(rate='30/10s', key=bucket_by_user, block=True)

team_ratelimit = ratelimit(rate='10/10s', key=bucket_by_team, block=True)

urlpatterns = [
     re_path('^puzzle/(?P<puzzle>trust-nobody)/state$', extra_ratelimit(puzzle44_trust_nobody.game_view)),
     re_path('^puzzle/(?P<puzzle>replicator-droid)/build$', basic_ratelimit(puzzle64_replicator_droid.game_view)),
     re_path('^puzzle/(?P<puzzle>please-prove-you-are-human)/state$', extra_ratelimit(puzzle216_captcha.state_view)),
     re_path('^puzzle/(?P<puzzle>nowhere-to-hide)/state$', extra_ratelimit(puzzle223_wordtris.state_view)),
     re_path('^puzzle/(?P<puzzle>strange-garnets)/answer$', puzzle246_checker.answers_view),
     re_path('^puzzle/(?P<puzzle>strange-garnets)/game8/board$', basic_ratelimit(puzzle246_twelve_janggi.board_view)),
     re_path('^puzzle/(?P<puzzle>strange-garnets)/game8/check$', basic_ratelimit(puzzle246_twelve_janggi.check_view)),
     re_path('^puzzle/(?P<puzzle>strange-garnets)/game6/play$', extra_ratelimit(puzzle246_open_pass.game_view)),
     re_path('^puzzle/(?P<puzzle>loves-labors-crossed)/check-word-square$', basic_ratelimit(puzzle269_request.check_word_square)),
     re_path('^puzzle/(?P<puzzle>word-search-of-babel)/state$', basic_ratelimit(puzzle113_babel.state_view)),
     re_path('^puzzle/(?P<puzzle>sorcery-for-dummies)/cast$', basic_ratelimit(puzzle477_sorcery.cast_view)),
     re_path('^puzzle/(?P<puzzle>the-day-you-begin)/findstudents/?$', puzzle93_the_day_you_begin_views.find_students),
     re_path('^puzzle/(?P<puzzle>once-upon-a-time-in-the-quest)/step$', puzzle251_once_upon_a_time_in_the_quest.answers_view),
     re_path('^puzzle/(?P<puzzle>fruit-around)/answer$', puzzle508_fruit_around.answers_view),
     re_path('^puzzle/(?P<puzzle>wooded-path)/state$', basic_ratelimit(puzzle344_wooded_path.question_view)),
     re_path('^puzzle/(?P<puzzle>introspection)/data/?$', basic_ratelimit(puzzle4_introspection.data)),
     re_path('^puzzle/(?P<puzzle>endless-practice)/answer/?$', puzzle308_endless_practice.answers_view),
     re_path('^puzzle/(?P<puzzle>endless-practice)/result/?$', puzzle308_endless_practice.result),
     re_path('^puzzle/(?P<puzzle>nowhere-to-hide)/answer/?$', puzzle223_wordtris.answers_view),
     re_path('^puzzle/(?P<puzzle>tech-support)/msg/?$', extra_ratelimit(puzzle331_tech_support.chat_bot), name='puzzle_tech_support_msg'),
     re_path('^puzzle/(?P<puzzle>tech-support)/chat/?$', extra_ratelimit(puzzle331_tech_support.chat), name='puzzle_tech_support_chat'),
     re_path('^puzzle/(?P<puzzle>tech-support)/help/?$', puzzle331_tech_support.website_page, name='puzzle_tech_support_help'),
     re_path('^puzzle/(?P<puzzle>tech-support)/reset/?$', basic_ratelimit(puzzle331_tech_support.password_reset), name='puzzle_tech_support_reset'),
     re_path('^puzzle/(?P<puzzle>completing-the-story)/answer/?$', puzzle555_cts_checker.answers_view),
     re_path('^puzzle/(?P<puzzle>completing-the-story)/discover/(?P<book>[^/]+)/?$', basic_ratelimit(puzzle555_cts_progress.discover_book_view), name='cts_discover_book'),
]

# Extra pages within a puzzle or a puzzle solution.

# Big Boi task
urlpatterns += [
     re_path('^puzzle/(?P<puzzle>my-dinner-with-big-boi)/(?P<subview>task)/?$', puzzle_subview, {'variant': 'puzzle', 'require_solved': True}),
]

#  task
urlpatterns += [
     re_path('^puzzle/(?P<puzzle>midterm-of-unspeakable-chaos)/(?P<subview>dictionary)/?$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>midterm-of-unspeakable-chaos)/(?P<subview>grammar)/?$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
]

# Lessons Learned…
urlpatterns += [
     re_path('^puzzle/(?P<puzzle>lessons-learned-from-porcine-construction)/(?P<subview>photos-envelope)/?$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
]

# How to Do Quality Reviews
urlpatterns += [
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>appoggiatura.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>appogiatura.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>bougainvillea.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>bouganvillea.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>diphthongal.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>dipthongal.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>grandaughter.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>granddaughter.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>noticable.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>noticeable.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>opalescent.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>opalesent.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>safflower.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>saflower.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>shibboleth.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>shiboleth.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>skateboarder.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
     re_path('^puzzle/(?P<puzzle>how-to-do-quality-reviews)/(?P<subview>skateborder.html)$', puzzle_subview, {'variant': 'puzzle', 'require_solved': False}),
]

# Tech Support
urlpatterns += [
     re_path("^puzzle/(?P<puzzle>tech-support)/(?P<subview>chat)$", puzzle_subview, {'variant':'puzzle', 'require_solved': False})
]

if settings.HUNT_LOAD_SAMPLE_ROUND:
     urlpatterns += [
          re_path('^puzzle/(?P<puzzle>sample-blackjack-session-puzzle)/state$', basic_ratelimit(puzzle1002_blackjack.state_view)),
          re_path('^puzzle/(?P<puzzle>sample-quiz-oracle-puzzle)/state$', basic_ratelimit(puzzle1003_maths_quiz.state_view)),
     ]
