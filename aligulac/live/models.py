from django.db import models
from ratings.models import Player

KEY_TYPES = (
    ("m", "master"), 
    ("u", "upload")
)


class TournamentHost(models.Model):
    name = models.CharField("Name", max_length=25)

class Tournament(models.Model):
    name = models.CharField("Name", max_length=50)

    running = models.BooleanField("IsRunning", default=False)

    host = models.ForeignKey(TournamentHost, related_name="tournament")

class TournamentKey(models.Model):
    key = models.CharField("Key", max_length=64)
    
    key_type = models.CharField("Type", choices=KEY_TYPES, 
                                max_length=2)

    host = models.ForeignKey(TournamentHost, related_name="key")

class LiveStat(models.Model):
    pla = models.ForeignKey(Player, related_name='+')
    plb = models.ForeignKey(Player, related_name='+')

    sca = models.IntegerField()
    scb = models.IntegerField()

    tournament = models.ForeignKey(Tournament, related_name="live_stat")
