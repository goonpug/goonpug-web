from django.conf.urls import patterns, url


urlpatterns = patterns(
    'apps.core.views',
    url(r'player/(?P<player_id>\d+)/$', 'player_profile', name='player_profile'),
    url(r'player/(?P<player_id>\d+)/stats/(?P<season>\w+)/$', 'player_stats'),
    url(r'player/(?P<player_id>\d+)/stats/pug/career/$', 'player_stats_pug_career'),
    url(r'player/(?P<player_id>\d+)/stats/pug/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'player_stats_pug'),
    #url(r'player/(?P<player_id>\d+)/matches/(?P<sort>\w+)/(?P<page>\d+)$',
    #    'player_match_history'),
)
