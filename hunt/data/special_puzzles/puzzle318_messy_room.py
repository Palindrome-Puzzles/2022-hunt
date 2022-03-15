"""
Puzzle backend for the "Messy Room" puzzle.

The puzzle involves solving a dropquote variant. The backend allows saving your
progress and collaboratively solving with your team.
"""
import collections

from django.db import models
from django.forms.models import model_to_dict

from spoilr.core.models import Puzzle

from hunt.app.core.helpers import pick
from hunt.app.core.plugins import Plugin
from hunt.app.core.team_consumer import TeamConsumer
from hunt.app.special_puzzles.team_state_plugin import TeamStatePlugin, TeamStateModelBase, TeamStateClientAdaptor
from hunt.app.special_puzzles.team_state_list_plugin import TeamStateListPlugin
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_session_plugin import TeamSessionPlugin, TeamModelBase

class P318MessyRoomModel(TeamModelBase):
    pass

class P318MessyRoomGameModel(TeamStateModelBase):
    session = models.ForeignKey(P318MessyRoomModel, on_delete=models.CASCADE)

class P318MessyRoomGameCellModel(models.Model):
    game = models.ForeignKey(P318MessyRoomGameModel, on_delete=models.CASCADE, related_name='cells')
    board = models.PositiveSmallIntegerField()
    row = models.PositiveSmallIntegerField()
    col = models.PositiveSmallIntegerField()
    letter = models.CharField(max_length=1)

    class Meta:
        unique_together = [
            ['game', 'board', 'row', 'col'],
        ]

class P318MessyRoomGameUsedIndexModel(models.Model):
    game = models.ForeignKey(P318MessyRoomGameModel, on_delete=models.CASCADE, related_name='used_indices')
    board = models.PositiveSmallIntegerField()
    col = models.PositiveSmallIntegerField()
    index = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [
            ['game', 'board', 'col', 'index'],
        ]

class P318MessyRoomConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        client_adaptor = P318StateClientAdaptor()

        scopes = [str(i) for i in range(1, 6)]
        self.add_plugin(TeamStateListPlugin(scopes))
        for scope in scopes:
            self.add_plugin(TeamStatePlugin(P318MessyRoomGameModel, session_foreign_key_field='session', client_adaptor=client_adaptor, plugin_scope=scope))
        self.add_plugin(TeamSessionPlugin(P318MessyRoomModel))
        self.add_plugin(TeamPuzzlePlugin(318))
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

class P318StateClientAdaptor(TeamStateClientAdaptor):
    def prefetch_related(self):
        return ['cells', 'used_indices']

    def to_in_memory_state(self, state):
        nested_dict = lambda: collections.defaultdict(nested_dict)
        result = {
            'cells': nested_dict(),
            'used_indices': nested_dict(),
        }
        for cell in state.cells.all():
            result['cells'][cell.board][cell.row][cell.col] = cell.letter

        for used_index in state.used_indices.all():
            result['used_indices'][used_index.board][used_index.col][used_index.index] = True

        return result

    def project_for_client(self, consumer, in_memory_state, updates=None):
        if updates:
            return updates

        # Project full state.
        cells = []
        used_indices = []
        for board, board_info in in_memory_state['cells'].items():
            for row, row_info in board_info.items():
                for col, letter in row_info.items():
                    if letter:
                        cells.append({'board': board, 'row': row, 'col': col, 'letter': letter})

        for board, board_info in in_memory_state['used_indices'].items():
            for col, col_info in board_info.items():
                for index, used in col_info.items():
                    if used:
                        used_indices.append({'board': board, 'col': col, 'index': index})

        return {
            'cells': cells,
            'usedIndices': used_indices,
        }

    def apply_updates(self, game, updates):
        if updates['action'] == 'cell':
            if updates['letter']:
                cell = P318MessyRoomGameCellModel.objects.update_or_create(
                    game=game, **pick(updates, 'board', 'row', 'col'),
                    defaults={'letter': updates['letter']})
            else:
                P318MessyRoomGameCellModel.objects.filter(
                    game=game, **pick(updates, 'board', 'row', 'col')
                ).delete()

        elif updates['action'] == 'usedIndex':
            if updates['used']:
                P318MessyRoomGameUsedIndexModel.objects.get_or_create(
                    game=game, **pick(updates, 'board', 'col', 'index'))
            else:
                P318MessyRoomGameUsedIndexModel.objects.filter(
                    game=game, **pick(updates, 'board', 'col', 'index')
                ).delete()

    def apply_in_memory_updates(self, in_memory_state, updates, server_updates):
        if updates['action'] == 'cell':
            in_memory_state['cells'][updates['board']][updates['row']][updates['col']] = updates['letter']
        elif updates['action'] == 'usedIndex':
            in_memory_state['used_indices'][updates['board']][updates['col']][updates['index']] = updates['used']
        return True
