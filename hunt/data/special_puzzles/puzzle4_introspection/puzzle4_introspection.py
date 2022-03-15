"""
Puzzle backend for Introspection (the Self-Help meta)
"""
from django.http import JsonResponse
from django.core.cache import caches
from django.views.decorators.http import require_POST
from django import template
from django.template import Template, Context

import csv
import os

from hunt.app.core.interactions import get_submission_instructions
from hunt.app.views.common import require_puzzle_access
from hunt.app.views.common import get_puzzle_context
from hunt.data_loader.puzzle import get_puzzle_data_text
from hunt.deploy.util import is_autopilot
from spoilr.core.models import InteractionAccess, PuzzleAccess

# The list of alphabets used by the message, in given order of associated tasks.
ALPHABETS = []
alphabets_file_path  = os.path.join(os.path.dirname(__file__), "alphabets.tsv")
alphabets_file = open(alphabets_file_path, encoding='utf-8')
reader = csv.reader(alphabets_file,delimiter="\t")
for row in reader:
    ALPHABETS.append(row)
alphabets_file.close()

# The answer to the puzzle.
ANSWER = "MORALECOMPASS"

# Array whose elements are the percentages of the message that ought to be revealed
# for a team that completed [array index] tasks.
REVEAL_PERCENTAGES = [
    0, # completed 0 tasks
    0,
    1,
    2,
    4,
    6,
    10,
    20,
    30,
    40,
    50,
    60,
    75,
    100 # completed 13 tasks
]

# Map of puzzle URLs to task number
TASK_PUZZLE_URLS = {
    'bad-beginnings':1,
    'my-dinner-with-big-boi':2,
    '\u2764\ufe0f--\u262e\ufe0f':3, # Love and peace
    'book-reports':4,
    'lentalgram':5,
    'does-any-kid-still-do-this-anymore':6,
    'proof-by-induction':7,
    'first-you-go-to':8,
    'everybody-must-get-rosetta-stoned':9,
    'this-or-that':10,
    '49ers':11,
    'word-search-of-babel':12,
    'tech-support':13
}

# number: The task number
# text: The puzzle answer which is also the short task description
# accomplished: True iff the team has accomplished the task
# detailed_description: An HTML string that describes the task in detail
# submission_instruction: HTML instruction for submitting the interaction
class Task:
    def __init__(self, number, text, submitted, accomplished, autopilot, detailed_description, submission_instruction):
        self.number = number
        self.text = text
        self.submitted = submitted
        self.accomplished = accomplished
        self.autopilot = autopilot
        self.detailed_description = detailed_description
        self.submission_instruction = submission_instruction

    def to_dict(self):
        task_details = {
            "text" : self.text,
            "submitted" : self.submitted,
            "accomplished" : self.accomplished,
            "autopilot": self.autopilot,
            "detailed_description" : self.detailed_description
        }
        if(self.submission_instruction):
            task_details["submission_instruction"] = self.submission_instruction
        return task_details

# Returns a list of tasks the team has unlocked.
def get_tasks(team):
    solved_puzzles_accesses =  PuzzleAccess.objects.filter(team=team, puzzle__round__url='new-you-city', solved=True)
    tasks = {}
    for access in solved_puzzles_accesses:
        puzzle = access.puzzle
        if(puzzle.url not in TASK_PUZZLE_URLS):
            continue

        number = TASK_PUZZLE_URLS[puzzle.url]
        text = puzzle.answer

        # Get the interaction data. Every New You City puzzle should have an interaction.
        interaction = access.puzzle.interactiondata_set.select_related('interaction').first().interaction

        # Get instruction and whether the interaction is accomplished
        solved_puzzle = False
        accomplished = False
        autopilot = False

        if is_autopilot():
            solved_puzzle = True
            accomplished = True
            autopilot = True
        else:
            interaction_access = InteractionAccess.objects.filter(interaction=interaction, team=team).first()
            if interaction_access:
                solved_puzzle = True
                accomplished = interaction_access.accomplished

        # Only show instruction if interaction hasn't been accomplished
        submission_instruction = None
        if not accomplished:
            submission_instruction = get_submission_instructions(interaction, team, has_submitted=bool(interaction_access))

        puzzle_context = get_puzzle_context(team, puzzle)
        raw_message = get_puzzle_data_text(puzzle.url, 'message.tmpl')
        detailed_description = Template(raw_message).render(Context(puzzle_context))

        task = Task(number, text, solved_puzzle, accomplished, autopilot, detailed_description, submission_instruction)
        tasks[number] = task.to_dict()
    return tasks

# Generate the full message to display to the team, before characters are stripped out.
# username: The team's username
def generate_full_message(username):
    name_upper = username.upper()

    # Vigenere-encode the answer, store as list of 0-index ints
    encoded_answer = []
    for i in range(13):
        answer_value = ord(ANSWER[i]) - 65
        # If the name is shorter than the answer, mod the index
        name_value = ord(name_upper[i % len(name_upper)]) - 65
        encoded_value = ((answer_value + name_value) % 26)
        encoded_answer.append(encoded_value)

    # All the terms in the message
    terms = []
    # For each task, select the correct value in its alphabet
    for i in range(13):
        alphabet = ALPHABETS[i]
        terms.append(alphabet[encoded_answer[i]])
    terms.sort()
    terms.append("AND NOW VIGENERE")

    return " ".join(terms)

# Given a message string, returns a map from each character in the string
# to the number of times that characters occurs in the string
def frequency_map(message):
    frequencies = {}
    for c in message:
        if not (c in frequencies):
            frequencies[c] = 0
        frequencies[c] = frequencies[c] + 1
    return frequencies

# Returns the given message with characters occluded based on number of tasks
# completed and the message's letter frequencies
def occlude(message, number_tasks):
    frequencies = frequency_map(message)
    # Sort characters by frequency order, lowest first, breaking ties in alphabetical order
    frequency_order = map(lambda x:x[0],
                            sorted(frequencies.items(),  key=lambda x:(x[1] + 0.001*ord(x[0]))))

    revealed_characters = []
    total_revealed = 0
    goal = REVEAL_PERCENTAGES[number_tasks]
    for c in frequency_order:
        if ((total_revealed + frequencies[c]) * 100.0 / len(message)) > goal:
            break
        revealed_characters.append(c)
        total_revealed += frequencies[c]

    occluded_string = ""
    for c in message:
        if c in revealed_characters:
            occluded_string += c + "<wbr>"
        else:
            if c != ' ':
              occluded_string += '?<wbr>'

    return occluded_string

# Generate the message to display to the team.
# username: The team's username
# number_tasks: The numebr of tasks successfully completed by the team (0<= numberTasks <=13)
def generate_message(username, number_tasks):
    full_message = generate_full_message(username)
    if(number_tasks == 13):
        return full_message
    return occlude(full_message, number_tasks)

# Get the data for the metapuzzle. Data fields include:
# - 'message': The message string customized for the team, pre-filtered to include
#              only the information the team should see
# - 'tasks': The dictionary of tasks. Each task is keyed with its number and consists of:
# -- 'text': Task text (the puzzle answer)
# -- 'submitted': Whether or not the task has been submitted
# -- 'accomplished': Whether or not the task has been accomplished
# -- 'detailed_description': An HTML string that describes the task in detail
# -- 'submission_instruction': An HTML string with instruction for submitting the interaction (absent if the task has been accomplished)
@require_POST
@require_puzzle_access(allow_rd0_access=False)
def data(request, *args, **kwargs):
    team = request.team
    username = team.username

    tasks = get_tasks(team)

    accomplished_count = len([task for task in tasks.values() if task['accomplished']])
    message = generate_message(username,accomplished_count)

    data = {'introspection':message,'tasks':tasks}
    return JsonResponse(data)
