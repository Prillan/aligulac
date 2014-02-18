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
from live.tools import (
    JsonResponse, 
    join_stats_by_update,
    verify_key,
    verify_api_params
)
from ratings.models import Player

import re


@verify_key
@verify_api_params(game_id=int)
def push_livescore(request, t, game_id):

    # TODO: This should actually accept a log file and parse it here instead of
    #       in the tool on the observer computer.

    game = get_object_or_404(Game, id=game_id)

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
@verify_api_params(match_id=int)
def get_games(request, t, match_id):

    match = get_object_or_404(Match, id=match_id)
    if match.tournament != t:
        return HttpResponse("Tournament - match, missmatch", status=403)

    q = Game.objects.filter(match=match)
    
    games = [g.to_dict() for g in q]

    return JsonResponse(matches)

@verify_key
@verify_api_params(pla=int, plb=int)
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
@verify_api_params(match_id=int, game_index=int)
def open_game(request, t, match_id, game_index):
    
    q = Game.objects.filter(match_id=match_id, game_index=game_index)

    if q.count() == 0:
        match = Match.objects.filter(id=match_id)[0]
    
        if match.tournament_id != t.id:
            return HttpResponse("Wrong tournament for this match", status=403)
        
        game = Game()
        game.match = match
        game.game_index = game_index
        
        game.is_live = "live" in request.GET
        
        game.save()
    else:
        game = q[0]
        if "live" in request.GET and not game.is_live:
            game.is_live = True
            game.save()
        
    return JsonResponse(game.to_dict())

@verify_key
@verify_api_params(game_id=int)
def end_game(request, t, game_id):
    # TODO: Should be used when a game has ended. Perhaps with a replay 
    #       upload or a link to the replay.
    raise NotImplemented()

@verify_key
@verify_api_params(game_id=int)
def update_game(request, t, game_id):
    raise NotImplemented()

@verify_key
@verify_api_params(match_id=int, sca=int, scb=int)
def update_match(request, t, match_id, sca, scb):
    
    match = get_object_or_404(Match, id=match_id, tournament=t)

    match.sca = sca
    match.scb = scb
    
    match.save()

    return JsonResponse(match.to_dict())

def live_game_json(request):
    
    game = get_object_or_404(Game, id=request.GET["id"])

    stats = LiveStat.objects.filter(game=game).order_by("game_time", "player_index")
    
    stats = [(x.to_json(), y.to_json()) for (x, y) in 
             join_stats_by_update(stats, skip_singles=True)]

    if "latest" in request.GET and len(stats) > 0:
        stats = [stats[-1]]

    return JsonResponse(stats)
