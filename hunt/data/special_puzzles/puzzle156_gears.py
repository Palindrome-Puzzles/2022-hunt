"""
Puzzle backend for the "Gears and Arrows" puzzle.

The puzzle involves assigning letters to a set of interlocking gears. The
backend allows saving your progress and collaboratively solving with your team.
"""
import functools

from django.db import models, transaction
from django.forms.models import model_to_dict

from spoilr.core.models import Puzzle

from hunt.app.core.helpers import pick
from hunt.app.core.plugins import Plugin
from hunt.app.core.team_consumer import TeamConsumer
from hunt.app.special_puzzles.team_state_plugin import TeamStatePlugin, TeamStateModelBase, TeamStateClientAdaptor
from hunt.app.special_puzzles.team_state_list_plugin import TeamStateListPlugin
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_session_plugin import TeamSessionPlugin, TeamModelBase

GEARS = {
    'A': {'size': 11, 'fixed': set([2, 10])},
    'B': {'size': 7, 'fixed': set([7, 9])},
    'C': {'size': 13, 'fixed': set([14, 16])},
    'D': {'size': 9, 'fixed': set([7, 11])},
    'E': {'size': 10, 'fixed': set([14, 16])},
}
MAX_STOPS = 19
FIXED_LETTERS = set(['A', 'B', 'C', 'D', 'E'])
GEAR_LCM = functools.reduce(lambda acc, gear: acc * gear['size'], GEARS.values(), 1)
ROTATIONS_BEFORE_WRAPPING = 3;
ODD_GEARS = set(['B', 'D'])

class P156GearsModel(TeamModelBase):
    pass

class P156GearsGameModel(TeamStateModelBase):
    session = models.ForeignKey(P156GearsModel, on_delete=models.CASCADE)
    engaged = models.BooleanField()
    rotation = models.SmallIntegerField()

class P156GearsGearModel(models.Model):
    game = models.ForeignKey(P156GearsGameModel, on_delete=models.CASCADE, related_name='gears')
    name = models.CharField(max_length=1)
    offset = models.SmallIntegerField()

    class Meta:
        unique_together = [
            ['game', 'name'],
        ]

class P156GearsPegModel(models.Model):
    gear = models.ForeignKey(P156GearsGearModel, on_delete=models.CASCADE, related_name='pegs')
    index = models.SmallIntegerField()
    letter = models.CharField(max_length=1, null=True, blank=True)
    stop = models.BooleanField()

    class Meta:
        unique_together = [
            ['gear', 'index'],
        ]

class P156GearsConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        client_adaptor = P156StateClientAdaptor()

        scopes = [str(i) for i in range(1, 6)]
        self.add_plugin(TeamStateListPlugin(scopes))
        for scope in scopes:
            self.add_plugin(TeamStatePlugin(P156GearsGameModel, session_foreign_key_field='session', client_adaptor=client_adaptor, plugin_scope=scope))
        self.add_plugin(TeamSessionPlugin(P156GearsModel))
        self.add_plugin(TeamPuzzlePlugin(156))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

class P156StateClientAdaptor(TeamStateClientAdaptor):
    def state_defaults(self):
        return {'engaged': False, 'rotation': 0}

    def initialize_state(self, game):
        for name, gear_info in GEARS.items():
            gear = P156GearsGearModel.objects.create(game=game, name=name, offset=0)
            is_odd = name in ODD_GEARS
            size = gear_info['size']

            peg_indices = range(1, 2*size, 2) if is_odd else range(0, 2*size, 2)
            for peg in peg_indices:
                if peg in GEARS[name]['fixed']:
                    continue

                P156GearsPegModel.objects.create(
                    gear=gear, index=peg, letter=None, stop=False)

    def prefetch_related(self):
        return ['gears', 'gears__pegs']

    def to_in_memory_state(self, game):
        return {
            'engaged': game.engaged,
            'rotation': game.rotation,
            'gears': {
                gear.name: {
                    'offset': gear.offset,
                    'pegs': {
                        peg.index: model_to_dict(peg) for peg in gear.pegs.all()
                    }
                } for gear in game.gears.all()
            },
        }

    def project_for_client(self, consumer, in_memory_state, updates=None):
        if updates:
            if updates['action'] == 'rotation':
                return {
                    'action': 'rotation',
                    'rotation': in_memory_state['rotation'],
                    'delta': updates['delta'],
                }
            elif updates['action'] == 'offset':
                return {
                    'action': 'offset',
                    'gear': updates['gear'],
                    'offset': in_memory_state['gears'][updates['gear']]['offset'],
                    'delta': updates['delta'],
                }
            else:
                return updates
        else:
            return in_memory_state

    def apply_updates(self, game, updates):
        if updates['action'] == 'engaged':
            game.engaged = updates['engaged']
            game.save()
        elif updates['action'] == 'rotation':
            game.rotation = normalize_gear_rotation(game.rotation + updates['delta'])
            game.save()
        elif updates['action'] == 'offset':
            assert updates['gear'] in GEARS
            size = GEARS[updates['gear']]['size']
            with transaction.atomic():
                gear = P156GearsGearModel.objects.get(game=game, name=updates['gear'])
                gear.offset = (gear.offset + updates['delta']) % size
                gear.save()
        elif updates['action'] == 'label':
            gears = (P156GearsGearModel.objects
                .prefetch_related('pegs')
                .filter(game=game))
            with transaction.atomic():
                for label in updates['labels']:
                    assert label['gear'] in GEARS
                    size = GEARS[label['gear']]['size']

                    assert label['peg'] < 2*size
                    assert label['peg'] not in GEARS[label['gear']]['fixed']

                    gear = next(gear for gear in gears if gear.name == label['gear'])
                    peg = next(peg for peg in gear.pegs.all() if peg.index == label['peg'])

                    if not label['value']:
                        peg.letter = None
                        peg.stop = False
                    elif label['value'] == 'STOP':
                        peg.letter = None
                        peg.stop = True
                    else:
                        assert len(label['value']) == 1
                        assert 'A' <= label['value'] <= 'Z'
                        assert label['value'] not in FIXED_LETTERS
                        peg.letter = label['value']
                        peg.stop = False
                    peg.save()

                # Post-condition checks.
                letter_set = set()
                stop_count = 0
                for gear in gears:
                    for peg in gear.pegs.all():
                        if peg.stop:
                            stop_count += 1
                        elif peg.letter:
                            assert peg.letter not in letter_set
                            letter_set.add(peg.letter)
                assert stop_count <= MAX_STOPS

    def apply_in_memory_updates(self, in_memory_state, updates, server_updates):
        if updates['action'] == 'engaged':
            in_memory_state['engaged'] = updates['engaged']

        elif updates['action'] == 'rotation':
            in_memory_state['rotation'] = normalize_gear_rotation(in_memory_state['rotation'] + updates['delta'])

        elif updates['action'] == 'offset':
            gear = in_memory_state['gears'][updates['gear']]
            size = GEARS[updates['gear']]['size']
            # Let this grow until it overflows. That way, we don't have visual glitches from gears wrapping back.
            gear['offset'] = gear['offset'] + updates['delta']

        elif updates['action'] == 'label':
            for label in updates['labels']:
                gear = in_memory_state['gears'][label['gear']]
                peg = gear['pegs'][label['peg']]

                if label['value'] == 'STOP':
                    peg['letter'] = None
                    peg['stop'] = True
                else:
                    peg['letter'] = label['value']
                    peg['stop'] = False
        return True

def normalize_gear_rotation(rotation_or_offset):
    min_value = -ROTATIONS_BEFORE_WRAPPING * GEAR_LCM
    max_value = ROTATIONS_BEFORE_WRAPPING * GEAR_LCM
    value_range = max_value - min_value

    return (rotation_or_offset - min_value) % value_range + min_value
