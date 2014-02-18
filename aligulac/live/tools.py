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

# {{{ Decorators

# Verify key and tournament id wrapper
def verify_key(f):
    def wrapper(request):
        if "key" not in request.GET:
            return HttpResponse("Missing key", status=403)
        if "tournament_id" not in request.GET:
            return HttpResponse("Missing tournament_id", status=403)
    
        q1 = TournamentKey.objects.filter(key=request.GET["key"])
        q2 = Tournament.objects.filter(id=request.GET["tournament_id"])
 
        try:
            key, tourney = q1[0], q2[0]
        except:
            return HttpResponse("No such tournament or key", status=404)

        if key.host != tourney.host:
            return HttpResponse("Tournament and key doesn't match", status=403)

        return f(request, tourney)
    return wrapper

# Verify get parameters with ("key_name", type)
def verify_api_params(**kwargs):
    def outer(f):
        def wrapper(request, *args, **innerkwargs):
            for k in kwargs:
                if k not in request.GET:
                    return HttpResponse("Missing value '{}'".format(k), status=403)
                try:
                    x = kwargs[k](request.GET[k])
                    innerkwargs[k] = x
                except:
                    return HttpResponse("Invalid value for param '{}'".format(k),
                                        status=403)
            return f(request, *args, **innerkwargs)
        return wrapper
    return outer
# }}}
