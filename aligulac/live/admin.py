from django.contrib import admin
from live.models import *

admin.site.register(Tournament)
admin.site.register(TournamentHost)
admin.site.register(TournamentKey)

admin.site.register(Game)
admin.site.register(Match)
