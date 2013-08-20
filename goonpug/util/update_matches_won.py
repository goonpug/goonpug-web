#!/usr/bin/env python

from apps.core.models import *

for pm in pms:
    pr = PlayerRound.objects.filter(player=pm.player, round__match_map=pm.match_map)[0]
    if pr.round.get_period() % 2:
        pm.first_side = pr.current_side
    else:
        if pr.current_side == Match.SIDE_T:
            pm.first_side = Match.SIDE_CT
        elif pr.current_side == Match.SIDE_CT:
            pm.first_side = Match.SIDE_T
    pm.save()
    season = pm.match.season
    ps, created = PlayerSeason.objects.get_or_create(player=pm.player, season=season)
    if pm.match_map.score_1 > pm.match_map.score_2:
        if pm.first_side == Match.SIDE_CT:
            ps.matches_won += 1
        elif pm.first_side == Match.SIDE_T:
            ps.matches_lost += 1
    elif pm.match_map.score_1 < pm.match_map.score_2:
        if pm.first_side == Match.SIDE_CT:
            ps.matches_lost += 1
        elif pm.first_side == Match.SIDE_T:
            ps.matches_won += 1
    else:
        ps.matches_tied += 1
    ps.save()
