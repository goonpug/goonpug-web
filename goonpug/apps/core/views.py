# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from __future__ import absolute_import, division

import copy
import pytz

from datetime import date, datetime

from django.contrib import messages
from django.db.models import Sum, Avg
from django.http import Http404
from django.shortcuts import render

from django_tables2 import RequestConfig

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, generics
from srcds.objects import SteamId

from .models import Match, Player, PlayerSeason, Season, Server
from .tables import PlayerSeasonTable, PlayerSeasonLeaderboard
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
        messages.error(request, 'No player stats for the requested season')
        raise Http404


def player_stats_pug_career(request, player_id):
    return player_stats_pug(request, player_id, career=True)


def player_stats_pug(request, player_id, year=None, month=None, career=False):
    try:
        p = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        messages.error(request, 'No such player')
        raise Http404
    kwargs = {'player': p}

    if career:
        kwargs['period'] = 'Career'
        player_seasons = PlayerSeason.objects.filter(
            player=p, season__event='pug-season'
        ).aggregate(
            kills=Sum('kills'), assists=Sum('assists'), deaths=Sum('deaths'),
            hsp=Avg('hsp'),
            defuses=Sum('defuses'), plants=Sum('plants'), tks=Sum('tks'),
            clutch_v1=Sum('clutch_v1'), clutch_v2=Sum('clutch_v2'),
            clutch_v3=Sum('clutch_v3'), clutch_v4=Sum('clutch_v4'),
            clutch_v5=Sum('clutch_v5'),
            k1=Sum('k1'), k2=Sum('k2'), k3=Sum('k3'), k4=Sum('k4'),
            k5=Sum('k5'),
            damage=Sum('damage'), rws=Sum('rws'),
            rounds_won=Sum('rounds_won'), rounds_lost=Sum('rounds_lost'),
            rounds_tied=Sum('rounds_tied'),
            matches_won=Sum('matches_won'), matches_lost=Sum('matches_lost'),
            matches_tied=Sum('matches_tied')
        ).values()
    else:
        if year is None:
            today = date.today()
            year = today.year
            month = today.month
        else:
            year = int(year)
        if month is None:
            month = 1
        else:
            month = int(month)
        season_name = 'pug-%04d-%02d' % (year, month)
        try:
            s = Season.objects.get(name=season_name)
            player_seasons = PlayerSeason.objects.filter(
                season=s,
                player=p,
            ).values()
            kwargs['period'] = s.start.strftime('%B %Y')
        except Season.DoesNotExist:
            messages.error(request, 'No such season')
            raise Http404

    rows = []
    for ps in player_seasons:
        row = copy.copy(ps)
        for key in row:
            if row[key] is None:
                row[key] = 0
        rounds_played = row['rounds_won'] + row['rounds_lost'] + \
            row['rounds_tied']
        if rounds_played == 0:
            row['adr'] = 0.0
            row['rws'] = 0.0
        else:
            row['adr'] = row['damage'] / rounds_played
            row['rws'] = row['rws'] / rounds_played
        if row['deaths'] == 0:
            row['kdr'] = 0.0
        else:
            row['kdr'] = row['kills'] / row['deaths']
    rows.append(row)

    table = PlayerSeasonTable(rows)
    RequestConfig(request).configure(table)

    kwargs['stats_table'] = table
    pug_seasons = Season.objects.filter(event='pug-season').order_by('-start')
    kwargs['periods'] = [
        ('Career', '/player/%d/stats/pug/career/' % int(player_id)),
        ('', ''),
    ]
    for season in pug_seasons:
        kwargs['periods'].append(
            (season.start.strftime('%B %Y'),
             '/player/%d/stats/pug/%d/%d/' %
             (int(player_id), season.start.year, season.start.month)))
    return render(request, 'player/player_stats_pug.html', kwargs)


def stats_pug_career(request):
    return stats_pug(request, career=True)


def stats_pug(request, year=None, month=None, career=False):
    kwargs = {}
    player_seasons = None
    try:
        if career:
            kwargs['period'] = 'Career'
            player_seasons = PlayerSeason.objects.filter(
                season__event='pug-season'
            ).values('player_id').annotate(
                kills=Sum('kills'), assists=Sum('assists'),
                deaths=Sum('deaths'), hsp=Avg('hsp'),
                defuses=Sum('defuses'), plants=Sum('plants'), tks=Sum('tks'),
                clutch_v1=Sum('clutch_v1'), clutch_v2=Sum('clutch_v2'),
                clutch_v3=Sum('clutch_v3'), clutch_v4=Sum('clutch_v4'),
                clutch_v5=Sum('clutch_v5'),
                k1=Sum('k1'), k2=Sum('k2'), k3=Sum('k3'),
                k4=Sum('k4'), k5=Sum('k5'),
                damage=Sum('damage'), rws=Sum('rws'),
                rounds_won=Sum('rounds_won'), rounds_lost=Sum('rounds_lost'),
                rounds_tied=Sum('rounds_tied'),
                matches_won=Sum('matches_won'),
                matches_lost=Sum('matches_lost'),
                matches_tied=Sum('matches_tied')
            )
        else:
            if year is None:
                today = date.today()
                year = today.year
                month = today.month
            else:
                year = int(year)
            if month is None:
                month = 1
            else:
                month = int(month)
            season_name = 'pug-%04d-%02d' % (year, month)
            s = Season.objects.get(name=season_name)
            player_seasons = PlayerSeason.objects.filter(
                season=s,
            ).values()
            kwargs['period'] = s.start.strftime('%b %y')
    except Season.DoesNotExist:
        messages.error(request, 'No such season')
        raise Http404

    rows = []
    for player_season in player_seasons:
        row = copy.copy(player_season)
        rounds_played = player_season['rounds_won'] + \
            player_season['rounds_lost'] + player_season['rounds_tied']
        if player_season['deaths'] == 0:
            row['kdr'] = 0.0
        else:
            row['kdr'] = player_season['kills'] / \
                player_season['deaths']
        if rounds_played == 0:
            continue
        else:
            row['adr'] = row['damage'] / rounds_played
            row['rws'] /= rounds_played
        player = Player.objects.get(pk=player_season['player_id'])
        row['player'] = '<a href="/player/%d/">%s</a>' % (
            player.pk, player.fullname)
        row['rating'] = player.get_conservative_rating()
        rows.append(row)

    table = PlayerSeasonLeaderboard(rows)
    RequestConfig(request, paginate={'per_page': 25}).configure(table)

    kwargs['stats_table'] = table
    pug_seasons = Season.objects.filter(event='pug-season').order_by('-start')
    kwargs['periods'] = [
        ('Career', '/stats/pug/career/'),
        ('', ''),
    ]
    for season in pug_seasons:
        kwargs['periods'].append(
            (season.start.strftime('%B %Y'),
             '/stats/pug/%d/%d/' %
             (season.start.year, season.start.month)))
    return render(request, 'stats/stats_pug.html', kwargs)


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
