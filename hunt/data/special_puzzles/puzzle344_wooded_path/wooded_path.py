import csv
import json
import re
import pathlib

from django.http import JsonResponse

BRANCHES = list(csv.DictReader(pathlib.Path(__file__).parent.joinpath('branches.csv').open(encoding='utf-8')))
LEAVES = list(csv.DictReader(pathlib.Path(__file__).parent.joinpath('leaves.csv').open(encoding='utf-8')))
ROOT_ITEM = next(x for x in BRANCHES if x['path_code'] == '')


def question_view(request, **kwargs):
    question_code = re.sub(r'\D', '', json.loads(request.body)['question-code'].strip())
    try:
        if len(question_code) == 5:
            leaf_info = next(x for x in LEAVES if x['path_code'] == question_code)
            return JsonResponse({
                'question_code': leaf_info['path_code'],
                'text_before': leaf_info['prefix_text'].strip(),
                'species_name': leaf_info['species_name'].strip(),
                'text_after': leaf_info['suffix_text'].strip(),
                'image_code': leaf_info['image_code'],
                'type': 'leaf'
            })
        branch_info = next(x for x in BRANCHES if x['path_code'] == question_code)
        return JsonResponse({
            'question_code': branch_info['path_code'],
            'prompt': branch_info['prompt'].strip(),
            'left_option': branch_info['left_option'].strip(),
            'center_option': branch_info['center_option'].strip(),
            'right_option': branch_info['right_option'].strip(),
            'type': 'branch'
        })
    except StopIteration:
        return JsonResponse({
            'question_code': ROOT_ITEM['path_code'],
            'prompt': ROOT_ITEM['prompt'].strip(),
            'left_option': ROOT_ITEM['left_option'].strip(),
            'center_option': ROOT_ITEM['center_option'].strip(),
            'right_option': ROOT_ITEM['right_option'].strip(),
            'type': 'branch'
        })
