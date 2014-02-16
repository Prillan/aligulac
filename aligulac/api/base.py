# {{{ Imports
import json
from django.http import HttpResponse
from django.db.models.query import QuerySet

from ratings.models import (
    Group,
    Period,
    Player,
    Rating
)
# }}}

class JSONResponse(HttpResponse):
    def __init__(self, status, message=None, data=None):
        d = {"status": status}
        if message is not None and isinstance(message, str):
            d["message"] = message
        if data is not None:
            d["data"] = data
        super().__init__(json.dumps(d, cls=ApiJSONEncoder))

class OkResponse(JSONResponse):
    def __init__(self, data=None, message=None):
        super().__init__("ok", data=data, message=message)

class ErrorResponse(JSONResponse):
    def __init__(self, message):
        super().__init__("error", message=message)

class ApiJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Player):
            return {
                "tag": obj.tag,
                "id": obj.id,
                "race": obj.race,
                "team": obj.get_current_team(),
                "rating": obj.get_current_rating()
            }
        if isinstance(obj, Rating):
            return {
                "value": obj.rating,
                "period": obj.period
                }
        if isinstance(obj, Group):
            return obj.name
        if isinstance(obj, Period):
            return obj.id
        if isinstance(obj, QuerySet):
            return list(obj)

        return json.JSONEncoder.default(self, obj)

# {{{ 
# Decorator to wrap calls to the api
#  and parse the parameters.
# Usage:
# @api_view([
# (name, required, type)
# ...
# ])
#
# Where
#  name       str       name of the parameter
#  required   bool      True if required. False if optional
#  type       function  A function that parses the value and 
#                       raises an exception on failure.
def api_view(parameters):
    def decorator(func):
        def wrapper(request):
            values = dict()
            for name, required, type in parameters:
                if required and name not in request.GET:
                    return ErrorResponse("Missing query parameter: %s" % name)
                if name not in request.GET:
                    continue
                try:
                    value = type(request.GET[name])
                except Exception as e:
                    return ErrorResponse("Parameter '%s' error: %s" % \
                                         (name, str(e)))
                values[name] = value
            return func(**values)
        return wrapper
    return decorator
# }}}

# {{{
# Specifies a function
#        / x            if x in l
#  f(x)= |
#        \ undefined    otherwise  
def choice_type(l):
    def wrapper(x):
        if x in l:
            return x
        else:
            raise Exception("Choose from %s" % ','.join(l))
    return wrapper
# }}}
