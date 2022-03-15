"""
Puzzle progress tracking for the "Completing The Story" endgame puzzle.
"""

from django.db import models
from django.shortcuts import redirect, reverse

from spoilr.core.models import Minipuzzle

from hunt.app.core.constants import PUZZLE_ENDGAME_URL, SESSION_BOOK_DISCOVERED
from hunt.app.core.cache import team_updated
from hunt.app.core.team_consumer import TeamConsumer
from hunt.app.views.common import require_puzzle_access

from hunt.app.special_puzzles.team_minipuzzle_plugin import TeamMinipuzzlePlugin
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_progress_plugin import TeamProgressPlugin, team_puzzle_progressed, get_team_puzzle_progress, TeamProgressModelBase
from .common import MINIPUZZLE_ANSWERS, ENDGAME_DATA

class P555CTSProgressModel(TeamProgressModelBase):
    pass

class P555CTSBookModel(models.Model):
    progress = models.ForeignKey(P555CTSProgressModel, on_delete=models.CASCADE, related_name='books')
    book = models.CharField(max_length=20)
    found_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['progress', 'book']]

class P555CTSConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        self.add_plugin(TeamPuzzlePlugin(555))
        self.add_plugin(TeamMinipuzzlePlugin(MINIPUZZLE_ANSWERS))
        self.add_plugin(TeamProgressPlugin(
            P555CTSProgressModel,
            project_progress=project_progress,
            maybe_initialize_progress=maybe_initialize_progress))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

def maybe_initialize_progress(progress):
    if progress.team.is_public:
        for book in ENDGAME_DATA:
            P555CTSBookModel.objects.update_or_create(
                progress=progress, book=book)

def project_progress(progress):
    minipuzzles_by_ref = {
        minipuzzle.ref: minipuzzle
        for minipuzzle in Minipuzzle.objects.filter(team=progress.team, puzzle=progress.puzzle)
    }
    discovered_books = progress.books.order_by('found_time')

    unsolved_books = []
    solved_books = []
    for book in discovered_books:
        if book.book not in minipuzzles_by_ref: continue

        if minipuzzles_by_ref[book.book].solved or (progress.team and progress.team.is_public):
            solved_books.append({
                'book': book.book,
                'type': 'solved',
                'pdf': '{}.pdf'.format(ENDGAME_DATA[book.book]['code']), # [4:] to remove "cts-" prefix
                'flavor': ENDGAME_DATA[book.book]['clue'],
                'answer': ENDGAME_DATA[book.book]['book'],
            })

        if not minipuzzles_by_ref[book.book].solved:
            unsolved_books.append({
                'book': book.book,
                'type': 'unsolved',
                'found_time': book.found_time.isoformat(),
                'flavor': ENDGAME_DATA[book.book]['clue'],
            })

    return {
        'unsolved': unsolved_books,
        'solved': solved_books,
    }

@require_puzzle_access(allow_rd0_access=False)
def discover_book_view(request, book):
    progress = get_team_puzzle_progress(
        P555CTSProgressModel, request.team, request.puzzle)

    _, newly_found = P555CTSBookModel.objects.update_or_create(
        progress=progress, book=book)
    if newly_found:
        request.session[SESSION_BOOK_DISCOVERED] = True
        request.session.save()
        team_puzzle_progressed(P555CTSProgressModel, request.team, request.puzzle)
        team_updated(request.team)

    # TODO: Redirect to an interstitial page with a "congrats, you found a book"
    # view. Maybe check newly_found first.
    return redirect(reverse('puzzle_view', args=(PUZZLE_ENDGAME_URL,)))
