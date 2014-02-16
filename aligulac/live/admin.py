from django.contrib import admin
from live.models import Tournament, TournamentKey, TournamentHost, LiveStat

class TournamentAdmin(admin.ModelAdmin):
    pass
class TournamentHostAdmin(admin.ModelAdmin):
    pass
class TournamentKeyAdmin(admin.ModelAdmin):
    pass
class LiveStatAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(TournamentHost, TournamentHostAdmin)
admin.site.register(TournamentKey, TournamentKeyAdmin)
admin.site.register(LiveStat, LiveStatAdmin)
