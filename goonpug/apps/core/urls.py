from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

import views


urlpatterns = patterns(
    'apps.core.views',
    url(r'^player/(?P<player_id>\d+)/$', 'player_profile', name='player_profile'),
    url(r'^player/(?P<player_id>\d+)/stats/(?P<season>\w+)/$', 'player_stats'),
    url(r'^player/(?P<player_id>\d+)/stats/pug/career/$', 'player_stats_pug_career'),
    url(r'^player/(?P<player_id>\d+)/stats/pug/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'player_stats_pug'),
    #url(r'player/(?P<player_id>\d+)/matches/(?P<sort>\w+)/(?P<page>\d+)$',
    #    'player_match_history'),
    url(r'^api/pugmatch/$', 'post_pug_match'),
)

urlpatterns += patterns(
    '',
    url(r'^api/player/$', views.PlayerList.as_view()),
    url(r'^api/player/(?P<steamid>\d+)/$', views.PlayerDetail.as_view()),
    url(r'(?i)^api/player/(?P<steamid>steam_\d:\d:\d+)/$',
        views.PlayerDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
