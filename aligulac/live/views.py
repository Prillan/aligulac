from aligulac.tools import (
    Message,
    base_ctx,
    get_param,
)
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

from live.models import Tournament, TournamentKey, TournamentHost, LiveStat
from ratings.models import Player

# Create your views here.

def verify_key(request):
    if "key" not in request.GET:
        return False
    if "tournament_id" not in request.GET:
        return False
    
    q1 = TournamentKey.objects.filter(key=request.GET["key"])
    q2 = Tournament.objects.filter(id=request.GET["tournament_id"])
 
    try:
        key, tourny = q1[0], q2[0]
        print(key, tourny)
    except:
        return False

    if key.host == tourny.host:
        return True

def push(request):
    key  = verify_key(request)

    if not key:
        return HttpResponse("NOT VALID", status=403)

    if "update" in request.GET:
        stat = LiveStat.objects.filter(id=request.GET["statid"])[0]
    elif "new" in request.GET:
        stat = LiveStat()
        stat.pla_id = int(request.GET["pla"])
        stat.plb_id = int(request.GET["plb"])

        stat.tournament_id = int(request.GET["tournament_id"])
    else:
        return HttpResponse("NOT VALID", status=403)


    stat.sca = int(request.GET["sca"])
    stat.scb = int(request.GET["scb"])

    stat.save()

    return HttpResponse("VALID")

def live(request):
    ctx = base_ctx("Live", "LIVE!", request)

    running = LiveStat.objects.filter(tournament__running=True).prefetch_related('tournament', 'tournament__host')
    
    ctx["stats"] = running

    return render_to_response("live.html", ctx)
