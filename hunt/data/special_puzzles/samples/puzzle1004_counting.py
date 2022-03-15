"""
Sample puzzle that shows how to share state between team members.

Solvers need to count to 10, and then the answer is shown to them. That is it
for now.
"""

import html, time, uuid

from django.db import models, transaction

from hunt.app.core.plugins import Plugin
from hunt.app.core.team_consumer import TeamConsumer
from hunt.app.special_puzzles.team_leader_plugin import TeamLeaderPlugin, TeamLeaderModelBase
from hunt.app.special_puzzles.team_puzzle_plugin import TeamPuzzlePlugin
from hunt.app.special_puzzles.team_session_plugin import TeamSessionPlugin, TeamModelBase

class P1004CountingModel(TeamLeaderModelBase, TeamModelBase):
    last_count = models.PositiveSmallIntegerField()

class P1004CountingConsumer(TeamConsumer):
    def __init__(self):
        super().__init__()

        self.add_plugin(TeamLeaderPlugin())
        self.add_plugin(TeamSessionPlugin(P1004CountingModel))
        self.add_plugin(TeamPuzzlePlugin(1004))
        self.add_plugin(P1004CountingPlugin())
        self.verify_plugins()

    @property
    def group_type(self):
        return self.get_plugin("puzzle").team_puzzle_group_type

class P1004CountingPlugin(Plugin):
    plugin_name = 'p1004'
    last_message_time = None

    def __init__(self):
        super().__init__()
        self.pseudonym = uuid.uuid4().hex[:6]

    def joined(self):
        self.broadcast_message(f'{self.pseudonym} is here')

        state = self.get_sibling_plugin('session').get()
        if state.last_count:
            self.parent.send_json({'type': 'message', 'message': f'The last number was {state.last_count}'})

    def disconnected(self, was_authed, close_code):
        if was_authed:
            self.broadcast_message(f'{self.pseudonym} left and probably hates you')

    def received_json(self, data):
        rate_limited = self.last_message_time and (time.time() - self.last_message_time) < 2
        if rate_limited:
            return

        # Avoid HTML-injection for other people - make sure to escape the message.
        self.broadcast_message(f'{self.pseudonym}: {html.escape(data["message"])}')

        try:
            number = int(data['message'])
            self.parent.notify_team({
                'type': 'hunt.team.p1004.count',
                'data': number,
            })
        except ValueError:
            pass

    def session_defaults(self):
        return {'last_count': 0}

    def hunt_team_p1004_count(self, event):
        if not self.get_sibling_plugin('leader').is_leader:
            return

        with transaction.atomic():
            state = self.get_sibling_plugin('session').get()
            if state.last_count + 1 == event['data']:
                state.last_count += 1
                success = True
            else:
                state.last_count = 0
                success = False
            state.save()

        # Could do things like kick off threads to inject fake counts here.
        # That's why we have a concept of a leader - so only one consumer is
        # running the threads, and so if they drop off, the new leader can pick
        # them up.

        if not success:
            self.broadcast_message('Hmm, that\'s not right')

        elif state.last_count == 10:
            answer = self.get_sibling_plugin('puzzle').puzzle.answer
            self.broadcast_message(f'Congratulations, the correct answer is <b>{answer}</b>')

    def broadcast_message(self, message):
        self.parent.notify_team_clients({'type': 'message', 'message': message})
