from collections import deque
from django.http import HttpResponse
from itertools import groupby
import json

class JsonResponse(HttpResponse):
    
    def __init__(self, content, *args, **kwargs):
        scontent = json.dumps(content)

        if "content_type" not in kwargs:
            kwargs["content_type"] = "application/json"
        
        super().__init__(scontent, *args, **kwargs)

# Needs to be sorted by update
def join_stats_by_update(livestats, skip_singles=False):
    for k, g in groupby(livestats, lambda s: s.update):
        l = tuple(g)
        if len(l) == 2:
            yield l
        elif skip_singles:
            continue
        elif l[0].player_index == 1:
            yield l[0], None
        else:
            yield None, l[0]
