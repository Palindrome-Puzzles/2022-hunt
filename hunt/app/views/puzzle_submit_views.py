import dataclasses
import datetime
import typing

from django.shortcuts import render, redirect
from django.utils.html import escape
from django.utils.timezone import now

from spoilr.core.api.answer import (
    AnswerStr, AnswerOrStr, Response, RespStatus,
    get_response, get_pseudos, get_partials,
    submit_puzzle_answer, submit_minipuzzle_answer, maybe_initialize_minipuzzle
)
from spoilr.core import models as m

from hunt.app.core.rewards import get_bonus_content
from hunt.app.core.assets.refs import get_round_static_path
from hunt.app.core.constants import (
    PUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES,
    DEFAULT_MINIPUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES,
)
from hunt.deploy.util import is_autopilot

from .common import (
    require_puzzle_access,
    use_noop_puzzle_submission,
    xframe_sameorigin_if_post
)

MINIPUZZLE_MAX_SUBMISSIONS_TO_SHOW = 5


@dataclasses.dataclass
class AnswerRow:
    response: Response
    update_time: datetime.datetime

    @property
    def answer(self) -> AnswerStr:
        return self.response.answer

    @property
    def message(self) -> typing.Optional[str]:
        return self.response.message

    @property
    def status(self) -> RespStatus:
        return self.response.status

    @property
    def correct(self) -> bool:
        return self.response.correct

    @staticmethod
    def from_submission(
            ps: m.PuzzleSubmission,
            pseudoanswers: typing.Dict[str, Response]) -> "AnswerRow":
        answer = AnswerStr.of(ps.raw_answer)
        response = get_response(answer, ps.puzzle, pseudoanswers)
        if response.status == 'partial' and not response.message:
            response.message = "This is one answer to this puzzle."
        return AnswerRow(response, ps.update_time)

    @staticmethod
    def from_mini_submission(
            ps: m.MinipuzzleSubmission,
            correct_answer: AnswerOrStr) -> "AnswerRow":
        answer = AnswerStr.of(ps.answer)
        if answer.matches(correct_answer):
            return AnswerRow(Response(correct_answer, 'correct'), ps.update_time)
        return AnswerRow(Response(answer, 'incorrect'), ps.update_time)


@require_puzzle_access(allow_rd0_access=True, skip_cache=True)
@xframe_sameorigin_if_post
def submit_puzzle_view(request):
    noop_submission = use_noop_puzzle_submission(request)
    maybe_team = request.team
    puzzle = request.puzzle

    solved = bool(request.puzzle_access and request.puzzle_access.solved)
    submissions = (
        [] if noop_submission
        else list(m.PuzzleSubmission.objects
            .filter(team=maybe_team, puzzle=puzzle)
            .order_by('-update_time')))
    lock_out_time = (
        get_lock_out_time(
            solved=solved, answers=[s for s in submissions if not s.correct],
            lock_out_thresholds=PUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES,
            get_timestamp=lambda answer: answer.timestamp)
        if maybe_team else None)
    pseudoanswers = get_pseudos(puzzle)

    context = {
        'team': maybe_team,
        'puzzle': puzzle,
        'solved': solved,
        'is_minipuzzle': False,
        'allow_guessing': True,
        'time_left': lock_out_time,
        'response': None,
    }

    if request.method == 'POST' and not lock_out_time and request.POST['answer']:
        answer = AnswerStr.of(request.POST['answer'])
        response = submit_puzzle_answer(
            maybe_team, puzzle, answer,
            noop_submission=noop_submission,
            pseudoanswers=pseudoanswers,
            previous_guesses=submissions)

        # When there isn't a team, submissions are nooped, so inject a response.
        if noop_submission and not response.message:
            if response.status == 'correct':
                response.message = f'{escape(response.answer.disp)} is correct.'
                # We don't want the public to have any solve sounds.
                if not maybe_team or not maybe_team.is_public:
                    context['solve_sound_url'] = get_round_static_path(
                        puzzle.round.url, variant='round') + 'answer.mp3'
                context['bonus_content'] = get_bonus_content(puzzle, maybe_team) if maybe_team else None
            else:
                response.message = f'{escape(response.answer.disp)} is incorrect.'
        # reload submissions and recompute lockout time to reflect posted
        # changes
        if maybe_team and not noop_submission:
            submissions = list(m.PuzzleSubmission.objects
                .filter(team=maybe_team, puzzle=puzzle)
                .order_by('-update_time'))
            context['solved'] = solved = response.status == 'correct'
            lock_out_time = get_lock_out_time(
                solved=solved,
                answers=[s for s in submissions if not s.correct],
                lock_out_thresholds=PUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES,
                get_timestamp=lambda answer: answer.timestamp)
            context['time_left'] = lock_out_time
        context['response'] = response
    context['answers'] = [
        AnswerRow.from_submission(ps, pseudoanswers)
        for ps in submissions
    ]

    if puzzle.is_multi_answer:
        partials = get_partials(puzzle)
        found = len({s.answer for s in submissions if s.answer in partials})
        context['progress'] = (found, len(partials))
    return render(request, 'puzzle/submissions.tmpl', context)

def minipuzzle_answers_view_factory(minipuzzle_answers_by_ref, message_list={}, label_list={},
    puzzlewide_lock_out=False, lock_out_message=None,
    # If a team's guess for the puzzle is at least the KEYth wrong one, minimum timeout is VALUE minutes
    lock_out_thresholds=DEFAULT_MINIPUZZLE_ANSWER_WRONG_GUESSES_TIMEOUT_MINUTES):
    @require_puzzle_access(allow_rd0_access=False, skip_cache=True)
    @xframe_sameorigin_if_post
    def minipuzzle_answers_view(request):
        noop_submission = use_noop_puzzle_submission(request)
        minipuzzle_ref = request.GET.get('ref')
        allow_guessing = request.GET.get('guess') == '1'
        if minipuzzle_ref not in minipuzzle_answers_by_ref:
            print('For an unknown reason, invalid minipuzzle_ref', request.get_full_path())
        assert minipuzzle_ref in minipuzzle_answers_by_ref

        maybe_initialize_minipuzzle(request.team, request.puzzle, minipuzzle_ref)

        correct_answer = minipuzzle_answers_by_ref[minipuzzle_ref]
        message = message_list.get(minipuzzle_ref, None)
        label = label_list.get(minipuzzle_ref, None)

        minipuzzle = m.Minipuzzle.objects.get(
            team=request.team, puzzle=request.puzzle, ref=minipuzzle_ref)
        answers = (
            [] if noop_submission
            else list(m.MinipuzzleSubmission.objects
                .filter(minipuzzle=minipuzzle)
                .order_by('-update_time')))
        response = None
        answers_for_lock_out = answers

        # If puzzlewide_lock_out is set, include answers across all minipuzzles
        # in the same puzzle when calculating the lockout.
        if puzzlewide_lock_out:
            minipuzzles_for_team_and_puzzle = list(m.Minipuzzle.objects.filter(
                team=request.team, puzzle=request.puzzle))
            answers_for_lock_out = list(m.MinipuzzleSubmission.objects
                .filter(minipuzzle__in = minipuzzles_for_team_and_puzzle, correct=False))
        lock_out_time = get_lock_out_time(solved=minipuzzle.solved, answers=answers_for_lock_out,
            lock_out_thresholds=lock_out_thresholds,
            get_timestamp=lambda answer : answer.create_time)

        if request.method == 'POST' and not lock_out_time and request.POST['answer']:
            response = submit_minipuzzle_answer(
                request.team, request.puzzle, minipuzzle_ref,
                noop_submission=noop_submission,
                answer=request.POST['answer'], correct_answer=correct_answer)
            if not noop_submission:
                # Refresh if we submitted an answer, to refetch the answers and avoid
                # the notification about re-submitting a POST request if you refresh.
                return redirect(request.get_full_path())
            else:
                if response.status == 'correct':
                    response.message = f'{escape(response.answer.disp)} is correct.'
                else:
                    response.message = f'{escape(response.answer.disp)} is incorrect.'

        # Only show the last five answers
        answers_to_show = answers[:MINIPUZZLE_MAX_SUBMISSIONS_TO_SHOW]

        context = {
            'team': request.team,
            'puzzle': request.puzzle,
            'solved': minipuzzle.solved,
            'answer': correct_answer if minipuzzle.solved else None,
            'correct_answer': correct_answer,
            'answers': [AnswerRow.from_mini_submission(a, correct_answer)
                        for a in answers_to_show],
            'is_minipuzzle': True,
            'allow_guessing': allow_guessing,
            'time_left': lock_out_time,
            'lock_out_message': lock_out_message,
            'message': message,
            'response': response,
            'label': label,
        }
        return render(request, 'puzzle/submissions.tmpl', context)
    return minipuzzle_answers_view

def get_lock_out_time(*, solved, answers, lock_out_thresholds, get_timestamp):
    """
    `solved`: True iff the guessing team has solved the puzzle
    `answers`: List of answer submissions that should be considered when calculating lockout
    `lock_out_thresholds`: If a team's guess for the puzzle is at least the KEYth wrong one, minimum timeout is VALUE minutes
    `get_timestamp`: A lambda to get the submission time for a member of `answers`
    """
    # When autopilot is on, double the number of incorrect guesses and halve the lockout time.
    scale_factor = 2 if is_autopilot() else 1
    if not solved and len(answers) >= 1:
        total_timeout = 0
        for threshold in lock_out_thresholds.keys():
            if len(answers) >= threshold * scale_factor:
                total_timeout = max(total_timeout, lock_out_thresholds[threshold] / scale_factor)
        if total_timeout <= 0:
            return None
        most_recent_guess = max(answers, key=get_timestamp)
        timeout_end = get_timestamp(most_recent_guess) + datetime.timedelta(minutes=total_timeout)
        current_time = now()
        if(current_time > timeout_end):
            return None
        return timeout_end - now()
    return None
