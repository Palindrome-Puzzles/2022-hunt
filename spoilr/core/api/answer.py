import dataclasses
import logging
import re
import typing
import typing_extensions
from unidecode import unidecode

from django.conf import settings
from django.utils.timezone import now
from django.utils.html import escape

from spoilr.core.models import Minipuzzle, MinipuzzleSubmission, Puzzle, PuzzleSubmission, PseudoAnswer, PuzzleAccess
from spoilr.core import models as m

from hunt.app.core.constants import INCORRECT_ATTEMPT_ALERT_THRESHOLD

from .events import dispatch, HuntEvent

logger = logging.getLogger(__name__)

_PUZZLE_ANSWER_INVALID_LETTERS = re.compile(r'[^A-Z0-9]')
_PUZZLE_ANSWER_DISPLAY_INVALID_LETTERS = re.compile(r'[^\'" \-A-Z0-9]')

# Unidecode will convert Æ -> AE which is not okay for pseudoanswers in rotten
# little scamps (the word translates differently). So skip unidecoding if the
# answer matches one of these.
_HAS_CUSTOM_NORMALIZATION = set(["WHAT KARTÖFLUÆTURNAR MEANS", "KARTÖFLUÆTURNAR"])

def canonicalize_puzzle_answer(answer):
    """Converts an answer to the canonical form for answer checking."""
    uppercased = answer.upper()
    if uppercased in _HAS_CUSTOM_NORMALIZATION:
        decoded = uppercased
    else:
        decoded = unidecode(answer, errors='preserve').upper()
    validated = _PUZZLE_ANSWER_INVALID_LETTERS.sub('', decoded)
    max_length = Puzzle._meta.get_field('answer').max_length
    return validated[:max_length]

def canonicalize_puzzle_answer_display(answer):
    """
    Converts an answer to the canonical form for answer display.

    This is like the canonical form, but spaces are allowed.
    """
    uppercased = answer.upper()
    if uppercased in _HAS_CUSTOM_NORMALIZATION:
        return uppercased
    validated = _PUZZLE_ANSWER_DISPLAY_INVALID_LETTERS.sub('', uppercased)
    max_length = Puzzle._meta.get_field('answer').max_length
    return validated[:max_length]


AnswerOrStr = typing.Union["AnswerStr", str]


@dataclasses.dataclass
class AnswerStr:
    '''AnswerStr wraps an answer and normalizes it for checking or display.'''
    raw: str
    disp: str

    @staticmethod
    def of(value: AnswerOrStr) -> "AnswerStr":
        if isinstance(value, str):
            return AnswerStr(value)
        return value

    @property
    def canon(self):
        '''Return the form we use to check if an answer is correct.'''
        return canonicalize_puzzle_answer(self.raw)


    def __init__(self, raw: str, disp: str=None):
        self.raw = raw
        if disp is None:
            disp = canonicalize_puzzle_answer_display(raw)
        self.disp = disp

    def matches(self, other: AnswerOrStr) -> bool:
        '''Returns true if self and other have identical canonical forms.'''
        return self.canon == AnswerStr.of(other).canon

    def __str__(self) -> str:
        return self.disp

    @staticmethod
    def from_true(raw:str) -> "AnswerStr":
        '''Build an AnswerStr for a true answer.

        The only difference is that the display version won't be canonicalized.
        This way puzzles can have answers/pseudoanswers with unusual characters
        and they'll be displayed correctly in guess lists etc.
        '''
        return AnswerStr(raw, disp=raw)


RespStatus = typing_extensions.Literal["correct", "incorrect", "partial", "instructions"]


@dataclasses.dataclass
class Response:
    '''The result of submitting an answer.

    It contains an answer, status, and optional message. The answer will always
    be the answer that was submitted, UNLESS the answer was correct or matched
    a pseudoanswer, in which case it'll be the form of that answer provided by
    the puzzle. For example, if puzzle.answer is 'THIS IS AN ANSWER', the
    response to '##thiSIS  Ana  swe R  !' will have the answer 'THIS IS AN
    ANSWER' instead, since that's how it should display.

    The status will be a valid RespStatus (e.g. 'correct', 'partial', etc.);
    the message can be any string.

    If the status is 'instructions', the message should be set.
    '''
    answer: AnswerStr
    status: RespStatus
    message: typing.Optional[str] = None

    def __init__(self, answer: AnswerOrStr, status: RespStatus, message: str = None):
        self.answer = AnswerStr.of(answer)
        self.status = status
        self.message = message

    @property
    def correct(self) -> bool:
        return self.status == 'correct'

    @staticmethod
    def from_pa(pa: m.PseudoAnswer, status: RespStatus = 'instructions') -> "Response":
        return Response(AnswerStr.from_true(pa.answer), status, pa.response)


def get_pseudos(puzzle: m.Puzzle) -> typing.Dict[str, Response]:
    '''Returns {canonical answer: Response} for all PseudoAnswers.'''
    pas = m.PseudoAnswer.objects.filter(puzzle=puzzle)
    responses = (Response.from_pa(pa) for pa in pas)
    return {r.answer.canon: r for r in responses}


def get_partials(puzzle: m.Puzzle) -> typing.Dict[str, AnswerStr]:
    return {
        a.canon: a for a in (AnswerStr.from_true(r) for r in puzzle.all_answers)
    }


def get_response(
        answer: AnswerStr,
        puzzle: m.Puzzle,
        pseudoanswers: typing.Dict[str, Response] = None) -> Response:
    '''Get a response for an answer based on whether it answers the puzzle.

    Does not include e.g. checks for empty or duplicate answers.'''
    # load pseudoanswers if we weren't given them
    if pseudoanswers is None:
        pseudoanswers = get_pseudos(puzzle)
    if answer.canon in pseudoanswers:
        return pseudoanswers[answer.canon]

    if answer.matches(puzzle.answer):
        return Response(AnswerStr.from_true(puzzle.answer), 'correct')

    # extract partial answers if applicable
    if puzzle.is_multi_answer:
        partials = get_partials(puzzle)
        if answer.canon in partials:
            return Response(partials[answer.canon], 'partial')

    return Response(answer, 'incorrect')


def submit_puzzle_answer(
        maybe_team: typing.Optional[m.Team],
        puzzle: m.Puzzle,
        answer: AnswerOrStr,
        *,
        noop_submission: bool = False,
        pseudoanswers: typing.Dict[str, Response] = None,
        previous_guesses: typing.Optional[typing.List[m.PuzzleSubmission]] = None) -> Response:
    """
    Submits an answer to the puzzle for the team. If `noop_submission` is True,
    then the submission won't create new PuzzleSubmission rows or trigger.

    `previous_guesses` by the team for the puzzle may be provided, and if so
    may drive business logic in case of an incorrect answer.

    Returns a Response.
    """
    answer = AnswerStr.of(answer)
    # reject empty answers immediately
    if not answer.canon:
        return Response(
            answer, 'incorrect',
            'All responses must contain letters and/or numbers.'
        )
    # magic answer used by admin team -> pretend they submitted the right answer
    if (maybe_team and maybe_team.is_admin and
        answer.canon == settings.SPOILR_ADMIN_MAGIC_ANSWER):
        logger.info(f"admin team {maybe_team} used magic answer to solve {puzzle}")
        answer = AnswerStr.from_true(puzzle.answer)

    # if there's a team, and this the last unsubmitted partial answer, pretend
    # they submitted the whole answer instead.
    if puzzle.is_multi_answer and maybe_team:
        partials = get_partials(puzzle)
        psubs = PuzzleSubmission.objects.filter(
            team=maybe_team, puzzle=puzzle, answer__in=partials.keys())
        found = {sub.answer for sub in psubs}
        if {answer.canon} | found == set(partials.keys()):
            answer = AnswerStr.from_true(puzzle.answer)

    response = get_response(answer, puzzle, pseudoanswers)

    # Log PuzzleSubmission if possible
    if not noop_submission and maybe_team:
        # Record the puzzle submission. Unconditionally update the correctness
        # in case due to errata, it was marked wrong earlier. For anonymous
        # users, we don't actually want to record the puzzle submissions.
        submission, created = PuzzleSubmission.objects.update_or_create(
            team=maybe_team, puzzle=puzzle, answer=answer.canon,
            defaults={
                'raw_answer': answer.raw,
                # anything besides an incorrect answer is marked 'correct' so
                # that it won't count towards rate limiting.
                'correct': response.status != 'incorrect',
            })
        # not created -> this was a duplicate submission, so reply with 'you
        # already submitted this' instead. We return immediately because
        # duplicates shouldn't trigger logging or popups.
        if not created and not submission.correct:
            return Response(
                response.answer, 'incorrect',
                f"{escape(answer.disp)} has already been submitted for this puzzle."
            )
    # Dispatch various events & trigger unlocks if needed
    if response.status == 'correct':
        _handle_puzzle_correct_answer(maybe_team, puzzle, noop_submission)
    elif response.status == 'incorrect':
        _handle_puzzle_incorrect_answer(maybe_team, puzzle, answer.raw, previous_guesses=previous_guesses)
    else:
        kind = 'pseudoanswer' if response.status == 'instructions' else 'partial answer'
        dispatch(
            HuntEvent.METAPUZZLE_ATTEMPTED if puzzle.is_meta else HuntEvent.PUZZLE_ATTEMPTED,
            team=maybe_team, puzzle=puzzle, object_id=puzzle.url,
            message=f'Submitted {kind} {answer.raw}')
    return response


def _handle_puzzle_correct_answer(maybe_team, puzzle, noop_submission):
    if not noop_submission and maybe_team:
        # A team might not have access if it was an admin team using break-glass
        # access.
        puzzle_access = PuzzleAccess.objects.get(team=maybe_team, puzzle=puzzle)
        if puzzle_access and not puzzle_access.solved:
            puzzle_access.solved = True
            puzzle_access.solved_time = now()
            puzzle_access.save()

    dispatch(
        HuntEvent.METAPUZZLE_SOLVED if puzzle.is_meta else HuntEvent.PUZZLE_SOLVED,
        team=maybe_team, puzzle=puzzle, object_id=puzzle.url, noop_submission=noop_submission,
        message=f'Solved {puzzle}')

def _handle_puzzle_incorrect_answer(maybe_team, puzzle, answer, previous_guesses):
    threshold_message = ""
    if previous_guesses is not None and len(previous_guesses) >= INCORRECT_ATTEMPT_ALERT_THRESHOLD:
        threshold_message = f' *** THIS IS WRONG GUESS #{len(previous_guesses)} ***'
    dispatch(
        HuntEvent.METAPUZZLE_INCORRECTLY_ATTEMPTED if puzzle.is_meta else HuntEvent.PUZZLE_INCORRECTLY_ATTEMPTED,
        team=maybe_team, puzzle=puzzle, object_id=puzzle.url, answer=answer, previous_guesses=previous_guesses,
        message=f'Incorrect answer “{answer}” for {puzzle}{threshold_message}')

def maybe_initialize_minipuzzle(team, puzzle, minipuzzle_ref):
    Minipuzzle.objects.get_or_create(team=team, puzzle=puzzle, ref=minipuzzle_ref)

def submit_minipuzzle_answer(team, puzzle, minipuzzle_ref, *, noop_submission, answer, correct_answer):
    canonical_answer = canonicalize_puzzle_answer(answer)
    if team.is_admin and canonical_answer == settings.SPOILR_ADMIN_MAGIC_ANSWER:
        logger.info(f"admin team {team} used magic answer to solve minipuzzle {puzzle.external_id} {minipuzzle_ref}")
        answer = correct_answer
        canonical_answer = canonicalize_puzzle_answer(correct_answer)

    is_correct = canonical_answer == canonicalize_puzzle_answer(correct_answer)
    minipuzzle = Minipuzzle.objects.get(team=team, puzzle=puzzle, ref=minipuzzle_ref)
    if not noop_submission:
        submission, _ = MinipuzzleSubmission.objects.update_or_create(
            minipuzzle=minipuzzle, answer=canonical_answer,
            defaults={
                'raw_answer': answer,
                'correct': is_correct,
            })

    if is_correct:
        mark_minipuzzle_solved(team, puzzle, minipuzzle_ref, skip_notify=True)

    dispatch(
        HuntEvent.MINIPUZZLE_ATTEMPTED,
        team=team, puzzle=puzzle, object_id=f'{puzzle.url}:{minipuzzle_ref}',
        message=
            f'Attempted minipuzzle {minipuzzle_ref} with answer '
            f'“{answer}” for {puzzle} '
            'correct' if is_correct else 'incorrect',
        answer=answer, minipuzzle_ref=minipuzzle_ref, is_correct=is_correct)

    return Response(answer, 'correct' if is_correct else 'incorrect')

def mark_minipuzzle_solved(team, puzzle, minipuzzle_ref, *, skip_notify=False):
    if team.is_public:
        return

    minipuzzle, _ = Minipuzzle.objects.update_or_create(
        team=team, puzzle=puzzle, ref=minipuzzle_ref,
        defaults={'solved': True, 'solved_time': now()})

    if not skip_notify:
        dispatch(
            HuntEvent.MINIPUZZLE_COMPLETED,
            team=team, puzzle=puzzle, object_id=f'{puzzle.url}:{minipuzzle_ref}',
            message=f'Completed minipuzzle {minipuzzle_ref} for {puzzle}',
            minipuzzle_ref=minipuzzle_ref)
