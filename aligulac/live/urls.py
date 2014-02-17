try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here

urlpatterns = patterns('',
    url(r'^$', 'live.views.live'),
    url(r'^game/$', 'live.views.live_game'),
    url(r'^push/livescore/', 'live.views.push_livescore'),
    url(r'^get/livestats/$', 'live.views.live_game_json'),
    url(r'^get/matches/$', 'live.views.get_matches'),
    url(r'^create/match/$', 'live.views.create_match'),
    url(r'^update/match/$', 'live.views.update_match'),
    url(r'^open/game/$', 'live.views.open_game')
)
