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
def verify_params(**kwargs):
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

# ?update=1&game_id=1&match_id=50&tournament_id=123&player_index=1
# &key=KEY&MineralsCurrent=123&MineralsIncome=123

# ?new=1&game_id=1&match_id=50&tournament_id=123&player_index=1
# &key=KEY&MineralsCurrent=123&MineralsIncome=123

@verify_key
@verify_params(game_id=int)
def push_livescore(request, t, game_id):
    
    # requires game_id and match_id
    game = get_object_or_404(Game, id=game_id)
        
    print("Game is", game)

    # Check for duplicates
    # q = LiveStat.objects.filter(update=request.GET["Update"], 
    #                             game_id=game.id,
    #                             player_index=request.GET["player_index"])
    # if q.count() > 0:
    #     print("Duplicate entry")
    #     return HttpResponse("Duplicate entry", status=201)

    stat = LiveStat()
    
    for k in LIVE_STATS_MAP:
        if k in request.GET:
            stat.__dict__[LIVE_STATS_MAP[k]] = int(request.GET[k])

    stat.player_index = request.GET["player_index"]
 
    stat.game = game

    stat.save()

    return HttpResponse("VALID")

@verify_key
def get_matches(request, t):
    q = Match.objects.filter(tournament_id=t)
    
    matches = [m.to_dict() for m in q]

    return JsonResponse(matches)

@verify_key
@verify_params(match_id=int)
def get_games(request, t, match_id):

    match = get_object_or_404(Match, id=match_id)
    if match.tournament != t:
        return HttpResponse("Tournament - match, missmatch", status=403)

    q = Game.objects.filter(match=match)
    
    games = [g.to_dict() for g in q]

    return JsonResponse(matches)

@verify_key
@verify_params(pla=int, plb=int)
def create_match(request, t, pla, plb):

    match = Match()

    match.tournament = t

    match.pla_id = pla
    match.plb_id = plb

    match.sca = 0
    match.scb = 0

    if 'sca' in request.GET:
        match.sca = request.GET['sca']

    if 'scb' in request.GET:
        match.sca = request.GET['scb']

    match.save()

    return JsonResponse(match.to_dict())

@verify_key
@verify_params(match_id=int, game_index=int)
def open_game(request, t, match_id, game_index):
    
    q = Game.objects.filter(match_id=match_id, game_index=game_index)

    if q.count() == 0:
        match = Match.objects.filter(id=match_id)[0]
    
        if match.tournament_id != t.id:
            return HttpResponse("Wrong tournament for this match", status=403)
        
        game = Game()
        game.match = match
        game.game_index = game_index
    
        #game.map = request.GET["map"]
        
        game.save()
    else:
        game = q[0]
        
    return JsonResponse(game.to_dict())

@verify_key
@verify_params(match_id=int, sca=int, scb=int)
def update_match(request, t, match_id, sca, scb):
    
    match = get_object_or_404(Match, id=match_id, tournament=t)

    match.sca = sca
    match.scb = scb
    
    match.save()

    return JsonResponse(match.to_dict())


def live(request):
    ctx = base_ctx("Live", "LIVE!", request)

    running = LiveStat.objects.filter(tournament__running=True).prefetch_related('tournament', 'tournament__host')
    
    ctx["stats"] = running

    return render_to_response("live.html", ctx)

# Static display of all live data
def live_game(request):
    ctx = base_ctx("Live", "LIVE!", request)

    game = get_object_or_404(Game, id=request.GET["id"])

    stats = LiveStat.objects.filter(game=game).order_by("-update", "player_index")
    
    ctx["charts"] = True
    ctx["game"] = game
    ctx["stats"] = join_stats_by_update(stats)

    return render_to_response("live_game.html", ctx)

def live_game_json(request):
    
    game = get_object_or_404(Game, id=request.GET["id"])

    stats = LiveStat.objects.filter(game=game).order_by("game_time", "player_index")
    
    stats = [(x.to_json(), y.to_json()) for (x, y) in 
             join_stats_by_update(stats, skip_singles=True)]

    if "latest" in request.GET and len(stats) > 0:
        stats = [stats[-1]]

    return JsonResponse(stats)
