# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from __future__ import absolute_import

import pytz
from datetime import date, datetime
from django.http import Http404
from django.shortcuts import render
from django_tables2 import RequestConfig
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, generics
from srcds.objects import SteamId

from .models import Match, Player, PlayerSeason, Season, Server
from .tables import PlayerSeasonTable
from .serializers import MatchSerializer, PlayerSerializer
from .tasks import deserialize_pug_match


def player_profile(request, player_id):
    return player_stats(request, player_id)


def player_stats(request, player_id, season='pug'):
    seasons = {
        'pug': player_stats_pug,
    }
    try:
        return seasons[season](request, player_id)
    except KeyError:
        raise Http404


def player_stats_pug_career(request, player_id):
    return player_stats_pug(request, player_id, career=True)


def player_stats_pug(request, player_id, year=None, month=None, career=False):
    try:
        p = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise Http404
    kwargs = {'player': p}

    if career:
        pass
    else:
        if year is None:
            today = date.today()
            year = today.year
            month = today.month
        elif month is None:
            month = 1
        year = 2013
        month = 07
        season_name = 'pug-%04d-%02d' % (year, month)
        try:
            s = Season.objects.get(name=season_name)
            player_season = PlayerSeason.objects.get(
                player=p,
                season=s,
            )
        except Season.DoesNotExist:
            raise Http404

    table = PlayerSeasonTable(player_season)
    RequestConfig(request).configure(table)

    kwargs['stats_table'] = table
    kwargs['period'] = 'July 2012'
    kwargs['periods'] = [
        'Career',
        '',
        'July 2012',
        'June 2012',
    ]
    return render(request, 'player/player_stats_pug.html', kwargs)


class PlayerList(mixins.ListModelMixin, generics.GenericAPIView):
    """List all players"""

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PlayerDetail(APIView):
    """Retrieve a single player instance"""

    def get_object(self, steamid):
        try:
            steamid = int(steamid)
        except ValueError:
            pass
        steamid = SteamId(steamid).id64()
        try:
            return Player.objects.get(steamid=steamid)
        except Player.DoesNotExist:
            raise Http404

    def get(self, request, steamid, format=None):
        player = self.get_object(steamid)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)


@api_view(['POST'])
def post_pug_match(request):
    """Create a new match"""
    data = request.DATA
    server = None
    timestamp = pytz.utc.localize(datetime.strptime(data['start_time'],
                                  '%Y-%m-%dT%H:%M:%SZ'))
    try:
        server = Server.objects.get(ip=data['server']['ip'],
                                    port=data['server']['port'])
    except Server.DoesNotExist:
        server = Server(name='', ip=data['server']['ip'],
                        port=data['server']['port'],
                        gotv_ip=data['server']['ip'])
        server.save()
    season = None
    try:
        start = date(timestamp.year, timestamp.month, 1)
        season = Season.objects.get(event='pug-season', start=start)
    except Season.DoesNotExist:
        if start.month == 12:
            end = date(start.year + 1, 1, 1)
        else:
            end = date(start.year, start.month + 1, 1)
        now = datetime.utcnow()
        if start.month == now.month and start.year == now.year:
            active = True
        else:
            active = False
        season = Season(
            name='pug-%s' % start.strftime('%Y-%m'),
            event='pug-season',
            start=start,
            end=end,
            link='',
            logo='',
            is_active=active)
        season.save()
    match = None
    try:
        match = Match.objects.get(server=server, start_time=timestamp)
    except Match.DoesNotExist:
        match = Match(
            server=server,
            season=season,
            start_time=timestamp,
            status=Match.STATUS_UNKNOWN)
        match.save()
        match.name = 'PUG Match %d' % match.id
        match.save()
    if match.status != Match.STATUS_COMPLETE:
        deserialize_pug_match.delay(match, data)
    serializer = MatchSerializer(match)
    return Response(serializer.data)
