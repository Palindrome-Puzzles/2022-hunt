"""
Puzzle backend for The Day You Begin
"""
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from hunt.app.views.common import require_puzzle_access
from .query import run_query_in_process

# TODO(sahil): Add auditing to log queries.
@require_POST
@require_puzzle_access(allow_rd0_access=False)
def find_students(request, *args, **kwargs):
    name = request.GET.get('name','')
    query = "select * from students where name = '{}'".format(name)
    result = run_query_in_process(query)
    if isinstance(result, HttpResponseServerError):
        return result
    data = {'rows': result}
    return JsonResponse(data)
