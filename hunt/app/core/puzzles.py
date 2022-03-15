import dataclasses
import itertools
import logging
import typing
import typing_extensions

from django.conf import settings

from spoilr.core.api.hunt import release_puzzle, release_puzzles, release_round, release_rounds, is_site_launched
from spoilr.core.models import Round, Puzzle, Team, RoundAccess, PuzzleAccess

from hunt.app.core.constants import ROUND_SAMPLE_URL, ROUND_RD0_URL, ROUND_RD1_URL, ROUND_RD2_URL, ROUND_RD3_URLS, ROUND_RD3_UNLOCK_PUZZLE_ID, ROUND_RD3_SELF_HELP_URL, ROUND_RD3_META_URL, ROUND_ENDGAME_URL, ROUND_ENDGAME_UNLOCK_PUZZLE_ID, ROUND_EVENTS_URL
from hunt.app.core.cache import team_updated
from hunt.deploy.util import HUNT_REF, HUNT_RD0_REF, HUNT_PRELAUNCH_REF

logger = logging.getLogger(__name__)

ALL_PREHUNT_ROUND_URLS = [ROUND_SAMPLE_URL, ROUND_RD0_URL]

# TODO(sahil): Optimize so we don't need to scan all puzzles/rounds for the team.
# For example, if the event was a "tick", then we know it's because of time so
# we can look at unlocks due to time only.


def is_act3_unlocked(unlocked_round_urls):
    return any(round_url in unlocked_round_urls for round_url in ROUND_RD3_URLS)


PuzzleOrId = typing.Union[Puzzle, int]


@dataclasses.dataclass
class RoundStructure:
    round: Round
    # normal puzzles, sorted by .unlock_order
    unlock_order: typing.List[Puzzle]
    # metapuzzles, in no particular order
    metas: typing.List[Puzzle]
    # nonmetas that have .unlock_order=None, meaning they unlock under special
    # circumstances
    specials: typing.List[Puzzle]

    @property
    def url(self):
        return self.round.url


@dataclasses.dataclass
class HuntStructure:
    rounds_by_url: typing.Dict[str, RoundStructure]
    puzzles_by_id: typing.Dict[int, Puzzle]
    prehunt: typing.List[RoundStructure]
    events: RoundStructure
    act1: RoundStructure  # investigation
    act2: RoundStructure  # the ministry
    act3: typing.List[RoundStructure]  # bookspace (all rounds)
    device: RoundStructure  # the Device
    endgame: RoundStructure  # the endgame

    def get_puzzle(self, p_or_id: PuzzleOrId) -> Puzzle:
        if isinstance(p_or_id, Puzzle):
            return p_or_id
        return self.puzzles_by_id[p_or_id]

    def all_puzzles(self) -> typing.List[Puzzle]:
        return list(self.puzzles_by_id.values())

    def all_rounds(self) -> typing.List[RoundStructure]:
        return (
            self.prehunt
            + [self.events, self.act1, self.act2]
            + self.act3
            + [self.device, self.endgame])

    def round_by_url(self, url: str) -> typing.Optional[RoundStructure]:
        for r in self.all_rounds():
            if r.url == url:
                return r
        return None

    @staticmethod
    def load(omitted_rounds: typing.Container[str]) -> "HuntStructure":
        rounds = {}
        for round in Round.objects.all():
            assert round.url not in rounds, f'duplicate round url {round.url}?!'
            rounds[round.url] = RoundStructure(
                round=round,
                unlock_order=[],
                specials=[],
                metas=[])
        puzzles = (
            Puzzle.objects
            .select_related('puzzledata')
            .prefetch_related('puzzledata__solves_to_unlock')
        )
        pdict = {}
        for puzzle in puzzles:
            if puzzle.round.url in omitted_rounds:
                continue
            pdict[puzzle.external_id] = puzzle
            round = rounds[puzzle.round.url]
            if puzzle.is_meta:
                round.metas.append(puzzle)
            elif puzzle.puzzledata.unlock_order is not None:
                round.unlock_order.append(puzzle)
            else:
                round.specials.append(puzzle)
        for round in rounds.values():
            round.unlock_order.sort(
                key=lambda puzzle: puzzle.puzzledata.unlock_order)

        return HuntStructure(
            rounds_by_url=rounds,
            puzzles_by_id=pdict,
            prehunt=[rounds[u] for u in ALL_PREHUNT_ROUND_URLS if u not in omitted_rounds and u in rounds],
            events=rounds[ROUND_EVENTS_URL],
            act1=rounds[ROUND_RD1_URL],
            act2=rounds[ROUND_RD2_URL],
            act3=[rounds[u] for u in ROUND_RD3_URLS],
            device=rounds[ROUND_RD3_META_URL],
            endgame=rounds[ROUND_ENDGAME_URL],
        )


def unlock_available_puzzles(maybe_team=None):
    """Unlock any puzzles that are available for the team, or for all teams if no team was specified."""
    teams = [maybe_team] if maybe_team else Team.objects.all()

    omitted_rounds = set()
    if not settings.HUNT_LOAD_SAMPLE_ROUND:
        omitted_rounds.add(ROUND_SAMPLE_URL)
    if not is_site_launched(HUNT_RD0_REF):
        omitted_rounds.add(ROUND_RD0_URL)

    hunt = HuntStructure.load(omitted_rounds)
    initial_rounds = [r.round for r in hunt.prehunt]
    initial_puzzles = sum(
        (r.unlock_order + r.specials + r.metas for r in hunt.prehunt), [])

    unlock_site_puzzles = is_site_launched(HUNT_REF) or is_site_launched(HUNT_PRELAUNCH_REF)

    total = len(teams)
    logger.info(f'Unlocking puzzles for {total} teams')
    count = 0
    for team in teams:
        if team.is_public:
            _release_all_rounds_and_puzzles(team)
            continue

        release_rounds(team, initial_rounds)
        release_puzzles(team, initial_puzzles)

        if unlock_site_puzzles:
            _unlock_site_rounds_and_puzzles(team, hunt)

        count += 1
        logger.info(f'{count:03}/{total:03}: Unlocked team {team.name} ({team.username})')
    logger.info(f'Unlocked all {total} teams')


def _release_all_rounds_and_puzzles(team):
    release_rounds(team, Round.objects.all())
    release_puzzles(team, Puzzle.objects.all())

def _unlock_site_rounds_and_puzzles(team: Team, hunt: HuntStructure):
    _unlock_by_interaction(team)
    u = Unlocker.load(team, hunt)
    u.unlock_start()
    u.maybe_unlock_act2()
    u.maybe_unlock_act3()
    u.maybe_unlock_act3_rounds()
    u.maybe_unlock_device()
    u.maybe_unlock_endgame()
    u.unlock_by_feeders()
    u.unlock_to_radius()


def _unlock_by_interaction(team):
    '''Release puzzles due to completed interactions.'''
    available_puzzles = list(Puzzle.objects
        .filter(
            puzzledata__interaction_to_unlock__isnull=False,
            puzzledata__interaction_to_unlock__interactionaccess__team=team,
            puzzledata__interaction_to_unlock__interactionaccess__accomplished=True)
        .exclude(puzzleaccess__team=team))
    if len(available_puzzles):
        release_puzzles(team, available_puzzles)


PuzzleStatus = typing_extensions.Literal["locked", "unlocked", "solved"]


@dataclasses.dataclass
class Unlocker:
    team: Team
    hunt: HuntStructure
    round_access: typing.Dict[str, RoundAccess]
    puzzle_access: typing.Dict[str, PuzzleAccess]

    @staticmethod
    def load(team: Team, hunt: HuntStructure) -> "Unlocker":
        # load all accesses for this team
        round_access = {
            r.round.url: r for r in RoundAccess.objects.filter(team=team)
        }
        puzzle_access = {
            p.puzzle.external_id: p for p in PuzzleAccess.objects.filter(team=team)
        }
        return Unlocker(team, hunt, round_access, puzzle_access)

    def release_round(self, round: RoundStructure):
        '''Release a RoundStructure to our team.

        Updates internal tracking, and also releases any puzzles in that round
        with unlock_order==0.
        '''
        if self.sees_round(round):
            return
        access = release_round(self.team, round.round)
        logger.debug("Releasing %s to team %s", round.round, self.team)
        self.round_access[round.url] = access
        for puzzle in round.unlock_order:
            if puzzle.puzzledata.unlock_order == 0:
                self.release_puzzle(puzzle)

    def release_puzzle(self, p: PuzzleOrId):
        if self.status(p) != 'locked':
            return
        puzzle = self.hunt.get_puzzle(p)
        logger.debug("Releasing %s to team %s", puzzle, self.team)
        access = release_puzzle(self.team, puzzle)
        self.puzzle_access[puzzle.external_id] = access

    def sees_round(self, round: typing.Union[RoundStructure, Round]) -> bool:
        '''Returns True exactly when self.team has access to this round.'''
        return round.url in self.round_access

    def get_access(self, pid: PuzzleOrId) -> typing.Optional[PuzzleAccess]:
        puzzle = self.hunt.get_puzzle(pid)
        return self.puzzle_access.get(puzzle.external_id)

    def status(self, pid: PuzzleOrId) -> PuzzleStatus:
        puzzle = self.hunt.get_puzzle(pid)
        if not self.sees_round(puzzle.round):
            return "locked"
        pa = self.get_access(puzzle)
        if pa is None:
            return "locked"
        if pa.solved:
            return "solved"
        return "unlocked"

    def is_unlocked(self, pid: PuzzleOrId) -> bool:
        return self.status(pid) != 'locked'

    def unlock_start(self):
        '''Unlock act 1 and events.'''
        self.release_round(self.hunt.act1)
        self.release_round(self.hunt.events)
        release_puzzles(self.team, self.hunt.events.specials)

    def maybe_unlock_act2(self):
        '''Unlock Act 2 if the Act 1 meta is solved.'''
        if self.status(self.hunt.act1.metas[0]) == "solved":
            self.release_round(self.hunt.act2)

    def maybe_unlock_act3(self):
        '''Unlock Act 3 if Act 2's Fruit Around puzzle is solved.

        This specifically unlocks the first two rounds of Act 3.
        '''
        if self.status(ROUND_RD3_UNLOCK_PUZZLE_ID) == "solved":
            self.release_round(self.hunt.act3[0])
            self.release_round(self.hunt.act3[1])

    def maybe_unlock_act3_rounds(self):
        '''Unlock additional Act 3 rounds if needed.

        We unlock a new round when 2/3 of reachable, unlockable Act 3 puzzles
        are solved.

        A puzzle is reachable and unlockable if it has .unlock_order set
        (as opposed to having custom unlock conditions) and it belongs to an
        unlocked round (even if that specific puzzle hasn't been unlocked in
        that round yet).

        Self-Help puzzles count as two half-puzzles, one for solving the puzzle
        itself and one for accomplishing the resulting interaction.
        '''
        if not self.sees_round(self.hunt.act3[0]):
            # haven't unlocked act 3 yet.
            return

        # all currently unlocked act 3 rounds
        unlocked_rounds = []
        next_round = None
        for r in self.hunt.act3:
            if self.sees_round(r):
                unlocked_rounds.append(r)
            else:
                next_round = r
                break

        if next_round is None:
            # No rounds left to unlock
            return

        # All puzzles with unlock_order in the unlocked act 3 rounds
        reachable_puzzles = sum((r.unlock_order for r in unlocked_rounds), [])

        # Load all accomplished interactions (needed for evaluating self-help)
        interactions = {}
        for iaccess in self.team.interactionaccess_set.filter(accomplished=True):
            p = iaccess.interaction.interactiondata.puzzle_trigger
            if p is not None:
                interactions.setdefault(p.external_id, []).append(iaccess)

        # Count solved reachable puzzles
        act3_solves = 0.0
        for puzzle in reachable_puzzles:
            if self.status(puzzle) != "solved":
                continue
            if puzzle.round.url == ROUND_RD3_SELF_HELP_URL:
                # self help puzzles are only worth .5 points unless their
                # interaction is complete.
                if any(i.accomplished for i in interactions.get(puzzle.external_id, {})):
                    act3_solves += 1
                else:
                    act3_solves += .5
            else:
                act3_solves += 1

        # if they've solved 2/3+ of the reachable puzzles, release the next
        # round.
        if act3_solves >= len(reachable_puzzles) * 2 / 3:
            self.release_round(next_round)

        # NB: it's technically possible that we should unlock multiple rounds if our
        # puzzle unlocks fall really far behind, but ignore that. We can always just
        # run multiple "ticks".

    def maybe_unlock_device(self):
        '''Unlock the device if any round 3 meta is solved.'''
        for round in self.hunt.act3:
            for meta in round.metas:
                if self.status(meta) == 'solved':
                    self.release_round(self.hunt.device)
                    return

    def maybe_unlock_endgame(self):
        '''Unlock everything when the device is solved.'''
        if self.status(ROUND_ENDGAME_UNLOCK_PUZZLE_ID) == 'solved':
            for round in self.hunt.all_rounds():
                self.release_round(round)
                for puzzle in round.unlock_order + round.specials + round.metas:
                    self.release_puzzle(puzzle)
            team_updated(self.team)

    ## Iterators for finding what to unlock next by radius

    def unlockable_act2_puzzles(self) -> typing.Iterator[Puzzle]:
        '''Iterate over all locked puzzles in act2.unlock_order.'''
        if not self.sees_round(self.hunt.act2):
            # still in act 1, nothing to unlock yet.
            return
        for puzzle in self.hunt.act2.unlock_order:
            if self.status(puzzle) == 'locked':
                yield puzzle

    def unlockable_act3_early_puzzles(self) -> typing.Iterator[Puzzle]:
        '''Iterate over locked puzzles from the first two rounds of act 3.

        Puzzles will be yielded in unlock order from each, and interleaved to
        keep the total number of open puzzles in each round the same.'''
        a, b = self.hunt.act3[:2]
        if not self.sees_round(a) or not self.sees_round(b):
            # round not unlocked yet, nothing to unlock yet.
            return
        una = len([p for p in a.unlock_order if self.status(p) == "unlocked"])
        unb = len([p for p in b.unlock_order if self.status(p) == "unlocked"])
        a_puzzles = [p for p in a.unlock_order[::-1] if self.status(p) == "locked"]
        b_puzzles = [p for p in b.unlock_order[::-1] if self.status(p) == "locked"]
        while True:
            if not a_puzzles and not b_puzzles:
                # nothing left to unlock
                return
            if not a_puzzles or (b_puzzles and una > unb):
                # a is empty or has more unlocks, release from b
                unb += 1
                yield b_puzzles.pop()
            else:
                # a has puzzles and fewer unlocks, release from a
                una += 1
                yield a_puzzles.pop()

    def unlockable_act3_late_puzzles(self) -> typing.Iterator[Puzzle]:
        '''Iterate over locked puzzles from the third round on in Act 3.'''
        for round in self.hunt.act3[2:]:
            if not self.sees_round(round):
                # ran out of unlocked rounds, nothing left to unlock
                return
            for puzzle in round.unlock_order:
                if self.status(puzzle) == 'locked':
                    yield puzzle


    def unlock_to_radius(self):
        '''Unlock puzzles based on current radius.'''
        # For radius work, we only care about acts 1-3, not the endgame or
        # prehunt puzzles.
        rounds = [self.hunt.act1, self.hunt.act2] + self.hunt.act3
        open_rounds = [r for r in rounds if self.sees_round(r)]
        act3_open = self.sees_round(self.hunt.act3[0])
        puzzle_radius = 4 + len(open_rounds) + (2 if act3_open else 0)
        puzzle_radius += self.team.teamdata.extra_puzzle_radius

        # All puzzles in the rounds we care about
        reachable_puzzles = sum([r.unlock_order for r in open_rounds], [])
        available_puzzles = [p for p in reachable_puzzles if self.status(p) == 'unlocked']
        # number of puzzles we need to unlock to maintain the radius.
        shortfall = puzzle_radius - len(available_puzzles)

        if shortfall <= 0:
            return

        # For each of the <shortfall> most recent solves, look for the next
        # puzzle to unlock in the same round.
        recent_solves = [
            pa for pa in self.puzzle_access.values()
            if pa.solved and pa.solved_time and not pa.puzzle.is_meta and pa.puzzle.puzzledata.unlock_order is not None]
        recent_solves.sort(key=lambda pa: pa.solved_time, reverse=True)

        act2_credits = 0
        act3_credits = 0
        for solve in recent_solves[:shortfall]:
            round = self.hunt.round_by_url(solve.puzzle.round.url)
            if round is None:
                # this should be impossible
                continue
            for p in round.unlock_order:
                if self.status(p) == 'locked':
                    self.release_puzzle(p)
                    break
            else:
                # Got here without breaking -> no eligible puzzles left in this
                # round.
                if round == self.hunt.act1:
                    act2_credits += 1
                else:
                    act3_credits += 1

        # each act2 credit (generated by act 1 overflow) will unlock in act 2
        # if possible and if not will spill over to act 3.
        act2_unlockables = itertools.chain(
            self.unlockable_act2_puzzles(),
            self.unlockable_act3_early_puzzles(),
            self.unlockable_act3_late_puzzles()
        )
        for _, puzzle in zip(range(act2_credits), act2_unlockables):
            self.release_puzzle(puzzle)

        # each act3 credit (generated by act 2 or 3 overflow) will unlock in
        # act 3.
        act3_unlockables = itertools.chain(
            self.unlockable_act3_early_puzzles(),
            self.unlockable_act3_late_puzzles()
        )

        for _, puzzle in zip(range(act3_credits), act3_unlockables):
            self.release_puzzle(puzzle)

    def unlock_by_feeders(self):
        '''Unlock puzzles that don't use normal unlocking if applicable.'''
        for round in self.hunt.all_rounds():
            if not self.sees_round(round):
                continue
            for puzzle in round.specials + round.metas:
                if self.status(puzzle) != 'locked':
                    continue
                round_count = puzzle.puzzledata.round_solve_count_to_unlock
                if round_count != None:
                    count = len([
                        p for p in round.unlock_order
                        if self.status(p) == 'solved'])
                    if count >= round_count:
                        self.release_puzzle(puzzle)
                solves = puzzle.puzzledata.solves_to_unlock.all()
                if solves:
                    if all(self.status(p) == 'solved' for p in solves):
                        self.release_puzzle(puzzle)
