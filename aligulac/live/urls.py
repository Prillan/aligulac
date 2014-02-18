try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here

urlpatterns = patterns('',
    # HTML
    url(r'^$', 'live.views.live_home'),
    url(r'^game/$', 'live.views.live_game'),
    # API
    url(r'^push/livescore/', 'live.api_views.push_livescore'),
    url(r'^get/livestats/$', 'live.api_views.live_game_json'),
    url(r'^get/matches/$', 'live.api_views.get_matches'),
    url(r'^create/match/$', 'live.api_views.create_match'),
    url(r'^update/match/$', 'live.api_views.update_match'),
    url(r'^open/game/$', 'live.api_views.open_game')
)
