# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

from datetime import date
from django.http import Http404
from django.shortcuts import render
from django_tables2 import RequestConfig
from .models import Player, PlayerSeason, Season
from .tables import PlayerSeasonTable


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
