from aligulac.tools import (
    Message,
    base_ctx,
    get_param,
)
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

from live.models import (
    Tournament,
    TournamentHost,
    TournamentKey,
    LiveStat,
    Match,
    Game,
    LIVE_STATS_MAP
)
from live.tools import JsonResponse, join_stats_by_update
from ratings.models import Player

import re

def live_home(request):
    ctx = base_ctx("Live", "LIVE!", request)
    ctx["live"] = True
    
    running = Tournament.objects.filter(running=True).order_by("host__name")

    ctx["running"] = running
    ctx["title"] = "Live Games"

    return render_to_response("live.html", ctx)

# Static display of all live data
def live_game(request):
    ctx = base_ctx("Live", "LIVE!", request)
    ctx["live"] = True

    game = get_object_or_404(Game, id=request.GET["id"])

    stats = LiveStat.objects.filter(game=game).order_by("-update", "player_index")
    
    ctx["charts"] = True
    ctx["game"] = game
    ctx["title"] = str(game)
    ctx["stats"] = join_stats_by_update(stats)

    return render_to_response("live_game.html", ctx)
