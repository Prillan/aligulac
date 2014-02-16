# {{{

import re

from api.base import (
    OkResponse,
    ErrorResponse,
    api_view,
    choice_type
)

from aligulac.cache import cache_page
from aligulac.tools import (
    base_ctx
)

from ratings.tools import find_player

# }}}
@cache_page
@api_view([
    ("q", True, str),
    ("sort", False, choice_type([
        "lexasc", 
        "lexdesc",
        "ratingasc",
        "ratingdesc"
    ]))
])
def player_completion(q, sort="ratingdesc"):

    groups = re.findall(r"(?:^|\s*)(\w+)(?:\s*|$)", q)

    queryset = find_player(lst=groups, soft=True)
    
    if sort == "lexasc":
        queryset = queryset.order_by("tag")
    elif sort == "lexdesc":
        queryset = queryset.order_by("-tag")
    elif sort == "ratingasc":
        queryset = queryset.order_by("current_rating")
    elif sort == "ratingdesc":
        queryset = queryset.order_by("-current_rating")

    players = queryset

    return OkResponse(data=players)
