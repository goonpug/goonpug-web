# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from __future__ import absolute_import, division

import requests
import skills
from skills.trueskill import TrueSkillGameInfo

from celery import task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.db.models import Sum

from .models import Match, MatchMap, Player, PlayerKill, \
    PlayerMatchWeapons, PlayerMatch, PlayerRound, PlayerSeason, \
    PlayerSeasonWeapons, Round
from .gpskill import GpSkillCalculator


logger = get_task_logger(__name__)


@task()
def deserialize_pug_match(match, data):
    logger.info('Deserializing match %d' % match.pk)
    for i, map_data in enumerate(data['match_maps']):
        match_map, created = MatchMap.objects.get_or_create(
            match=match,
            map_number=i
        )
        match_map.map_name = map_data['map_name']
        match_map.score_1 = map_data['score_1']
        match_map.score_2 = map_data['score_2']
        match_map.current_period = map_data['current_period']
        # this can be parsed from map_data, but for pugs we only have
        # one map per match so this works too
        match_map.start_time = match.start_time
        match_map.save()
        for round_data in map_data['rounds']:
            deserialize_round(match, match_map, round_data)
        for steamid, weapon_data in map_data['player_match_weapons'].items():
            deserialize_weapons(match, match_map, steamid, weapon_data)
    update_match_stats.delay(match)
    logger.info('Done: Match %d status = STATUS_COMPLETE' % match.pk)
    match.status = Match.STATUS_COMPLETE
    match.save()


def deserialize_round(match, match_map, data):
    round, created = Round.objects.get_or_create(
        match=match,
        match_map=match_map,
        round_number=data['round_number']
    )
    round.bomb_planted = data['bomb_planted']
    round.bomb_defused = data['bomb_defused']
    round.bomb_exploded = data['bomb_exploded']
    round.ct_win = data['ct_win']
    round.t_win = data['t_win']
    if data['bomb_defused']:
        round.win_type = Round.WIN_TYPE_DEFUSED
    elif data['bomb_exploded']:
        round.win_type = Round.WIN_TYPE_EXPLODED
    if data['round_number'] <= 15:
        period = 1
    elif data['round_number'] <= 30:
        period = 2
    else:
        period = 3 + ((data['round_number'] - 31) // 3)
    if data['ct_win']:
        if period % 2:
            round.team_win = Match.TEAM_A
        else:
            round.team_win = Match.TEAM_B
    elif data['t_win']:
        if period % 2:
            round.team_win = Match.TEAM_B
        else:
            round.team_win = Match.TEAM_A
    round.score_a = data['score_a']
    round.score_b = data['score_b']
    round.save()
    for steamid, player_round in data['player_rounds'].items():
        deserialize_player_round(round, steamid, player_round, period)
    for kill_data in data['kills']:
        deserialize_kill(round, kill_data)


def deserialize_player_round(round, steamid, data, period):
    player, created = Player.objects.get_or_create_from_steamid(steamid)
    player_round, created = PlayerRound.objects.get_or_create(round=round,
                                                              player=player)
    if period % 2:
        player_round.first_side = player_round.current_side
    else:
        if data['current_side'] == Match.SIDE_CT:
            player_round.first_side = Match.SIDE_T
        elif data['current_side'] == Match.SIDE_T:
            player_round.first_side = Match.SIDE_CT
    player_round.current_side = data['current_side']
    player_round.kills = data['kills']
    player_round.assists = data['assists']
    player_round.deaths = data['deaths']
    player_round.defuses = data['defuses']
    player_round.plants = data['plants']
    player_round.tks = data['tks']
    player_round.clutch_v1 = data['clutch_v1']
    player_round.clutch_v2 = data['clutch_v2']
    player_round.clutch_v3 = data['clutch_v3']
    player_round.clutch_v4 = data['clutch_v4']
    player_round.clutch_v5 = data['clutch_v5']
    player_round.k1 = data['k1']
    player_round.k2 = data['k2']
    player_round.k3 = data['k3']
    player_round.k4 = data['k4']
    player_round.k5 = data['k5']
    player_round.damage = data['damage']
    if 'rws' in data:
        player_round.rws = data['rws']
    else:
        player_round.rws = 0
    player_round.save()


def deserialize_kill(round, data):
    killer, created = Player.objects.get_or_create_from_steamid(data['killer'])
    victim, created = Player.objects.get_or_create_from_steamid(data['victim'])
    kill, created = PlayerKill.objects.get_or_create(
        match=round.match, match_map=round.match_map, round=round,
        killer=killer, victim=victim)
    kill.killer_team = Match.SIDES[data['killer_team']]
    kill.victim_team = Match.SIDES[data['victim_team']]
    kill.headshot = data['headshot']
    kill.weapon = data['weapon']
    kill.save()


def deserialize_weapons(match, match_map, steamid, data):
    player, created = Player.objects.get_or_create_from_steamid(steamid)
    for weapon, stats in data.items():
        match_weapon, created = PlayerMatchWeapons.objects.get_or_create(
            match=match, match_map=match_map, player=player, weapon=weapon)
        match_weapon.headshots = stats['headshots']
        match_weapon.hits = stats['hits']
        match_weapon.damage = stats['damage']
        match_weapon.kills = stats['kills']
        match_weapon.deaths = stats['deaths']
        match_weapon.save()


@task()
def update_match_stats(match):
    match_maps = MatchMap.objects.filter(match=match)
    for match_map in match_maps:
        rounds = Round.objects.filter(match_map=match_map)
        for round in rounds:
            player_rounds = PlayerRound.objects.filter(round=round).order_by(
                'round')
            for player_round in player_rounds:
                player_match, created = PlayerMatch.objects.get_or_create(
                    match=match, match_map=match_map,
                    player=player_round.player)
                player_match.first_side = player_round.first_side
                player_match.current_side = player_round.current_side
                player_match.kills += player_round.kills
                player_match.assists += player_round.assists
                player_match.deaths += player_round.deaths
                player_match.defuses += player_round.defuses
                player_match.plants += player_round.plants
                player_match.tks += player_round.tks
                player_match.clutch_v1 += player_round.clutch_v1
                player_match.clutch_v2 += player_round.clutch_v2
                player_match.clutch_v3 += player_round.clutch_v3
                player_match.clutch_v4 += player_round.clutch_v4
                player_match.clutch_v5 += player_round.clutch_v5
                player_match.k1 += player_round.k1
                player_match.k2 += player_round.k2
                player_match.k3 += player_round.k3
                player_match.k4 += player_round.k4
                player_match.k5 += player_round.k5
                player_match.damage += player_round.damage
                player_match.rws += player_round.rws
                if player_round.current_side == Match.SIDE_CT:
                    if round.ct_win:
                        player_match.rounds_won += 1
                    elif round.t_win:
                        player_match.rounds_lost += 1
                    else:
                        player_match.rounds_tied += 1
                elif player_round.current_side == Match.SIDE_T:
                    if round.t_win:
                        player_match.rounds_won += 1
                    elif round.ct_win:
                        player_match.rounds_lost += 1
                    else:
                        player_match.rounds_tied += 1
                headshots = PlayerMatchWeapons.objects.filter(
                    match_map=match_map,
                    player=player_match.player
                ).aggregate(Sum('headshots'))['headshots__sum']
                hits = PlayerMatchWeapons.objects.filter(
                    match_map=match_map,
                    player=player_match.player
                ).aggregate(Sum('hits'))['hits__sum']
                if headshots is None:
                    headshots = 0
                if hits is None:
                    hits = 0
                if hits == 0:
                    player_match.hsp = 0.0
                else:
                    player_match.hsp = headshots / hits
                player_match.save()
        update_season_weapons.delay(match_map)
        update_rating.delay(match_map)
    update_season_stats.delay(match)


@task
def update_season_weapons(match_map):
    match_weapons = PlayerMatchWeapons.objects.filter(match_map=match_map)
    for match_weapon in match_weapons:
        season_weapon, created = PlayerSeasonWeapons.objects.get_or_create(
            player=match_weapon.player, season=match_map.match.season,
            weapon=match_weapon.weapon)
        season_weapon.headshots += match_weapon.headshots
        season_weapon.hits += match_weapon.hits
        season_weapon.damage += match_weapon.damage
        season_weapon.kills += match_weapon.kills
        season_weapon.deaths += match_weapon.deaths
        season_weapon.save()


@task
def update_season_stats(match):
    season = match.season
    match_maps = MatchMap.objects.filter(match=match)
    for match_map in match_maps:
        player_matches = PlayerMatch.objects.filter(match_map=match_map)
        for player_match in player_matches:
            if player_match.first_side == 0:
                pr = PlayerRound.objects.filter(
                    player=player_match.player,
                    round__match_map=player_match.match_map
                )[0]
                if pr.round.get_period() % 2:
                    player_match.first_side = pr.current_side
                else:
                    if pr.current_side == Match.SIDE_T:
                        player_match.first_side = Match.SIDE_CT
                    elif pr.current_side == Match.SIDE_CT:
                        player_match.first_side = Match.SIDE_T
                player_match.save()
            player_season, created = PlayerSeason.objects.get_or_create(
                player=player_match.player, season=season)
            player_season.kills += player_match.kills
            player_season.assists += player_match.assists
            player_season.deaths += player_match.deaths
            player_season.score = player_match.score
            player_season.defuses += player_match.defuses
            player_season.plants += player_match.plants
            player_season.tks += player_match.tks
            player_season.clutch_v1 += player_match.clutch_v1
            player_season.clutch_v2 += player_match.clutch_v2
            player_season.clutch_v3 += player_match.clutch_v3
            player_season.clutch_v4 += player_match.clutch_v4
            player_season.clutch_v5 += player_match.clutch_v5
            player_season.k1 += player_match.k1
            player_season.k2 += player_match.k2
            player_season.k3 += player_match.k3
            player_season.k4 += player_match.k4
            player_season.k5 += player_match.k5
            player_season.damage += player_match.damage
            player_season.rws += player_match.rws
            player_season.rounds_won += player_match.rounds_won
            player_season.rounds_lost += player_match.rounds_lost
            player_season.rounds_tied += player_match.rounds_tied
            if match_map.score_1 > match_map.score_2:
                if player_match.first_side == Match.SIDE_CT:
                    player_season.matches_won += 1
                elif player_match.first_side == Match.SIDE_T:
                    player_season.matches_lost += 1
            elif match_map.score_1 < match_map.score_2:
                if player_match.first_side == Match.SIDE_CT:
                    player_season.matches_lost += 1
                elif player_match.first_side == Match.SIDE_T:
                    player_season.matches_won += 1
            else:
                player_season.matches_tied += 1
            headshots = PlayerSeasonWeapons.objects.filter(
                season=season,
                player=player_season.player
            ).aggregate(Sum('headshots'))['headshots__sum']
            hits = PlayerSeasonWeapons.objects.filter(
                season=season,
                player=player_season.player
            ).aggregate(Sum('hits'))['hits__sum']
            if headshots is None:
                headshots = 0
            if hits is None:
                hits = 0
            if hits == 0:
                player_season.hsp = 0.0
            else:
                player_season.hsp = headshots / hits
            player_season.save()


@task
def update_rating(match_map):
    logger.info('Updating ratings for match_map %d' % match_map.pk)
    cts = PlayerMatch.objects.filter(
        match_map=match_map, first_side=Match.SIDE_CT
    )
    ts = PlayerMatch.objects.filter(
        match_map=match_map, first_side=Match.SIDE_T
    )
    if len(cts) == 0:
        logger.warning('Got empty CT team for match_map %d' % match_map.pk)
        return
    if len(ts) == 0:
        logger.warning('Got empty T team for match_map %d' % match_map.pk)
        return
    ct_team = []
    for pm in cts:
        partial_play = (pm.rounds_won + pm.rounds_lost + pm.rounds_tied) / \
            (match_map.score_1 + match_map.score_2)
        if partial_play < 0.0001:
            partial_play = 0.0001
        if partial_play > 1.0:
            logger.error('Got partial play percentage > 1 for match_map %d' %
                         match_map.pk)
            partial_play = 1.0
        player = skills.Player(player_id=pm.player.pk,
                               partial_play_percentage=partial_play)
        rating = skills.GaussianRating(pm.player.rating,
                                       pm.player.rating_variance)
        ct_team.append((player, rating,))
    t_team = []
    for pm in ts:
        partial_play = (pm.rounds_won + pm.rounds_lost + pm.rounds_tied) / \
            (match_map.score_1 + match_map.score_2)
        if partial_play < 0.0001:
            partial_play = 0.0001
        if partial_play > 1.0:
            logger.error('Got partial play percentage > 1 for match_map %d' %
                         match_map.pk)
            partial_play = 1.0
        player = skills.Player(player_id=pm.player.pk,
                               partial_play_percentage=partial_play)
        rating = skills.GaussianRating(pm.player.rating,
                                       pm.player.rating_variance)
        t_team.append((player, rating,))
    if match_map.score_1 > match_map.score_2:
        rank = [1, 2]
    elif match_map.score_1 < match_map.score_2:
        rank = [2, 1]
    else:
        rank = [1, 1]

    teams = skills.Match([ct_team, t_team], rank=rank)
    calc = GpSkillCalculator()
    game_info = TrueSkillGameInfo()
    new_ratings = calc.new_ratings(teams, game_info)
    for team in [cts, ts]:
        for pm in team:
            player = pm.player
            old_skill = player.get_conservative_rating()
            rating = new_ratings.rating_by_id(player.pk)
            player.rating = rating.mean
            player.rating_variance = rating.stdev
            player.save()
            new_skill = player.get_conservative_rating()
            logger.info('Player %s: %f -> %f (%+f)' % (
                player.fullname, old_skill, new_skill, new_skill - old_skill))


@task
def update_steam_details(player):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    payload = {'key': settings.STEAM_API_KEY, 'steamids': player.username}
    r = requests.get(url, params=payload)
    try:
        data = r.json()
        for details in data['response']['players']:
            p = Player.objects.get(username=details['steamid'])
            p.fullname = details['personaname']
            p.profileurl = details['profileurl']
            p.avatar = details['avatar']
            p.avatarmedium = details['avatarmedium']
            p.avatarfull = details['avatarfull']
            p.save()
    except ValueError:
        pass


@task
def update_steam_details_all():
    for p in Player.objects.all():
        update_steam_details.delay(p)
