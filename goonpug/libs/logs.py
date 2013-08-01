# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

from __future__ import division, absolute_import

import re

import srcds.events.generic as generic_events
import srcds.events.csgo as csgo_events
from srcds.objects import BasePlayer

from ..apps.core.models import Match, Round


class GoonPugPlayer(BasePlayer):
    pass


class GoonPugActionEvent(generic_events.BaseEvent):

    """GoonPUG triggered action event"""

    regex = ''.join([
        generic_events.BaseEvent.regex,
        ur'GoonPUG triggered "(?P<action>.*?)"',
    ])

    def __init__(self, timestamp, action):
        super(GoonPugActionEvent, self).__init__(timestamp)
        self.action = action

    def __unicode__(self):
        msg = u'GoonPUG triggered "%s"' % (self.action)
        return ' '.join([super(GoonPugActionEvent, self).__unicode__(), msg])


class GoonPugParser(object):

    """GoonPUG log parser class"""

    def __init__(self, verbose=False):
        self.event_handlers = {
            generic_events.LogFileEvent: self.handle_log_file,
            generic_events.ChangeMapEvent: self.handle_change_map,
            generic_events.EnterGameEvent: self.handle_enter_game,
            generic_events.SuicideEvent: self.handle_suicide,
            generic_events.ConnectionEvent: self.handle_connection,
            generic_events.DisconnectionEvent: self.handle_disconnection,
            generic_events.KickEvent: self.handle_kick,
            generic_events.PlayerActionEvent: self.handle_player_action,
            generic_events.TeamActionEvent: self.handle_team_action,
            generic_events.WorldActionEvent: self.handle_world_action,
            generic_events.RoundEndTeamEvent: self.handle_round_end_team,
            csgo_events.CsgoKillEvent: self.handle_kill,
            csgo_events.CsgoAttackEvent: self.handle_attack,
            csgo_events.CsgoAssistEvent: self.handle_assist,
            csgo_events.SwitchTeamEvent: self.handle_switch_team,
            GoonPugActionEvent: self.handle_goonpug_action,
        }
        self.seen_players = {}
        self._compile_regexes()
        self._reset_matches()
        self.verbose = verbose

    def _reset_matches(self):
        self.matches = []
        self._reset_current_match()

    def _reset_current_match(self):
        self.current_match = {
            'match_maps': [],
        }
        self._reset_current_match_map()

    def _reset_current_match_map(self):
        self.current_match_map = {
            'current_period': 0,
            'rounds': [],
            'player_match_weapons': {},
            'player_matches': {},
        }
        self.current_round = {}
        self._reset_current_round()
        self.current_round['round_number'] = 0
        self.current_round['score_a'] = 0
        self.current_round['score_b'] = 0

    def _reset_current_round(self):
        defaults = {
            'bomb_planted': False,
            'bomb_defused': False,
            'bomb_exploded': False,
            'ct_win': False,
            't_win': False,
            'player_rounds': {},
            'kills': [],
        }
        self.current_round.update(defaults)

    def new_player_weapon(self):
        weapon = {
            'headshots': 0,
            'hits': 0,
            'damage': 0,
            'kills': 0,
            'deaths': 0,
        }
        return weapon

    def new_player_round(self, side):
        player_round = {
            'current_side': side,
            'kills': 0,
            'assists': 0,
            'deaths': 0,
            'defuses': 0,
            'plants': 0,
            'tks': 0,
            'clutch_v1': 0,
            'clutch_v2': 0,
            'clutch_v3': 0,
            'clutch_v4': 0,
            'clutch_v5': 0,
            'k1': 0,
            'k2': 0,
            'k3': 0,
            'k4': 0,
            'k5': 0,
            'damage': 0,
            'health': 100,
            'clutch': 0,
        }
        return player_round

    def _compile_regexes(self):
        """Add event types"""
        self.event_types = []
        for cls in self.event_handlers.keys():
            regex = re.compile(cls.regex)
            self.event_types.append((regex, cls))

    def parse_line(self, line):
        """Parse a single log line"""
        line = line.strip()
        if self.verbose:
            print line
        for (regex, cls) in self.event_types:
            match = regex.match(line)
            if match:
                event = cls.from_re_match(match)
                handler = self.event_handlers[type(event)]
                handler(event)
                return

    def _start_match(self, timestamp):
        self._reset_current_match()
        self.current_match['server'] = self.current_server
        self.current_match_map['map_name'] = self.current_map
        self.current_match_map['score_1'] = 0
        self.current_match_map['score_2'] = 0
        self.current_match_map['start_time'] = timestamp
        self.current_match_map['period'] = 1

    def _end_match(self, event):
        self.current_match['match_maps'].append(self.current_match_map)
        print self.current_match
        """
        for steam_id in self.team_a:
            player = Player.query.filter_by(steam_id=steam_id).first()
            db.session.execute(match_players.insert().values(
                player_id=player.id,
                match_id=self.match.id,
                team=CsgoMatch.TEAM_A,
            ))
            PlayerOverallStatsSummary._update_stats(player.id)
        for steam_id in self.team_b:
            player = Player.query.filter_by(steam_id=steam_id).first()
            db.session.execute(match_players.insert().values(
                player_id=player.id,
                match_id=self.match.id,
                team=CsgoMatch.TEAM_A,
            ))
            PlayerOverallStatsSummary._update_stats(player.id)
        self.team_a = None
        self.team_b = None
        self.match = None
        self.round = None
        """

    def _start_round(self):
        self._reset_current_round()
        self.current_round['round_number'] += 1
        for steam_id in self.cts:
            self.current_round['player_rounds'][steam_id] = \
                self.new_player_round(Match.SIDE_CT)
        for steam_id in self.ts:
            self.current_round['player_rounds'][steam_id] = \
                self.new_player_round(Match.SIDE_T)

    def _end_round(self, event):
        self.current_match_map['rounds'].append(self.current_round)
        rounds_played = self.current_round['round_number']
        if rounds_played == 0:
            self.current_match_map['period'] = 1
        elif rounds_played < 30 and (rounds_played % 15) == 0:
            self.current_match_map['period'] += 1
        elif rounds_played >= 30 and (rounds_played % 6) == 0:
            self.current_match_map['period'] += 1

    def _sfui_notice(self, winning_team, defused=False, exploded=False,
                     win_type=Round.WIN_TYPE_NORMAL):
        if winning_team == u'TERRORIST':
            self.current_round['t_win'] = True
            side = Match.SIDE_T
        elif winning_team == u'CT':
            self.current_round['ct_win'] = True
            side = Match.SIDE_CT
        else:
            # don't do anything with rws if it's a tie
            return

        team_damage = 0
        team_player_rounds = []
        for player_round in self.current_round['player_rounds'].values():
            if player_round['current_side'] == side:
                team_damage += player_round['damage']
                team_player_rounds.append(player_round)
            else:
                player_round['clutch'] = 0
                player_round['rws'] = 0.0

            if player_round['kills'] == 1:
                player_round['k1'] = 1
            elif player_round['kills'] == 2:
                player_round['k2'] = 1
            elif player_round['kills'] == 3:
                player_round['k3'] = 1
            elif player_round['kills'] == 4:
                player_round['k4'] = 1
            elif player_round['kills'] == 5:
                player_round['k5'] = 1

        if defused or exploded:
            multi = 70.0
        else:
            multi = 100.0

        for player_round in team_player_rounds:
            try:
                player_round['rws'] = multi * (player_round['damage']
                                               / team_damage)
            except ZeroDivisionError:
                player_round['rws'] = 0.0
            if defused and player_round['defuses']:
                player_round['rws'] += 30.0
            if exploded and player_round['plants']:
                player_round['rws'] += 30.0

            if player_round['clutch'] == 1:
                player_round['clutch_v1'] = 1
            elif player_round['clutch'] == 2:
                player_round['clutch_v2'] = 1
            elif player_round['clutch'] == 3:
                player_round['clutch_v3'] = 1
            elif player_round['clutch'] == 4:
                player_round['clutch_v4'] = 1
            elif player_round['clutch'] == 5:
                player_round['clutch_v5'] = 1

    def handle_log_file(self, event):
        if event.started:
            self.ts = set()
            self.cts = set()
            pattern = (r'.*L(?P<ip>\d+_\d+_\d+_\d+)_'
                       r'(?P<port>\d+)_(?P<time>\d+)_000.log')
            m = re.match(pattern, event.filename)
            if m:
                # TODO: If we support anything besides pugs this shouldn't be
                # reset
                self.match = {}
                ip = m.group('ip').replace('_', '.')
                port = int(m.group('port'))
                self.current_server = {'ip': ip, 'port': port}

    def handle_change_map(self, event):
        if event.started:
            mapname = event.mapname
            m = re.match(r'^(?P<workshop_name>workshop/\d+)/(?P<mapname>.*)',
                         mapname)
            if m:
                mapname = m.group('workshop_name')
            self.current_map = mapname

    def handle_connection(self, event):
        steam_id = event.player.steam_id.id64()
        if steam_id not in self.seen_players:
            self.seen_players[steam_id] = {}
        if event.address:
            self.seen_players[steam_id]['ip'] = event.address[0]

    def handle_enter_game(self, event):
        steam_id = event.player.steam_id.id64()
        if steam_id not in self.seen_players:
            self.seen_players[steam_id] = {}
        self.seen_players[steam_id]['name'] = event.player.name

    def _check_clutch(self):
        live_ts = []
        live_cts = []
        for player in self.cts:
            if player in self.current_round['player_rounds'] and \
                    self.current_round['player_rounds'][player]['health'] > 0:
                live_cts.append(player)
        for player in self.ts:
            if player in self.current_round['player_rounds'] and \
                    self.current_round['player_rounds'][player]['health'] > 0:
                live_ts.append(player)

        if len(live_ts) == 1:
            player = live_ts[0]
            clutch = len(live_cts)
        elif len(live_cts) == 1:
            player = live_cts[0]
            clutch = len(live_ts)
        else:
            return
        player_round = self.current_round['player_rounds'][player]
        if clutch > player_round['clutch']:
            player_round['clutch'] = clutch

    def handle_suicide(self, event):
        steam_id = event.player.steam_id.id64()
        player_round = self.current_round['player_rounds'][steam_id]
        player_round['deaths'] += 1
        player_round['health'] = 0
        kill = {
            'killer': steam_id,
            'killer_team': event.player.team,
            'victim': steam_id,
            'victim_team': event.player.team,
            'weapon': event.weapon,
            'headshot': False,
        }
        self.current_round['kills'].append(kill)
        self._check_clutch()

    def handle_disconnection(self, event):
        pass

    def handle_kick(self, event):
        # the leaving part should be taken care of by handle_disconnection
        pass

    def handle_player_action(self, event):
        steam_id = event.player.steam_id.id64()
        if steam_id in self.current_round['player_rounds']:
            player_round = self.current_round['player_rounds'][steam_id]
            if event.action == "Planted_The_Bomb":
                player_round['plants'] += 1
            elif event.action == "Defused_The_Bomb":
                player_round['defuses'] += 1

    def handle_team_action(self, event):
        if event.action == u"SFUI_Notice_Bomb_Defused":
            self._sfui_notice(event.team, defused=True,
                              win_type=Round.WIN_TYPE_DEFUSED)
        elif event.action == u"SFUI_Notice_Target_Bombed":
            self._sfui_notice(event.team, exploded=True,
                              win_type=Round.WIN_TYPE_EXPLODED)
        elif event.action == u"SFUI_Notice_Target_Saved":
            self._sfui_notice(event.team, win_type=Round.WIN_TYPE_SAVED)
        elif event.action == u"SFUI_Notice_Terrorists_Win" \
                or event.action == u"SFUI_Notice_CTs_Win":
            self._sfui_notice(event.team)

    def handle_world_action(self, event):
        if event.action == u'Round_Start':
            self._start_round()
        elif event.action == u'Round_End':
            self._end_round(event)

    def handle_goonpug_action(self, event):
        if event.action == u'Start_Match':
            self._start_match(event.timestamp)
        elif event.action in ['End_Match']:
            self._end_match(event)

    def handle_round_end_team(self, event):
        if event.team == u'CT':
            self.ct_score = event.score
        elif event.team == u'TERRORIST':
            self.t_score = event.score

    def handle_kill(self, event):
        killer_id = event.player.steam_id.id64()
        victim_id = event.target.steam_id.id64()

        killer_round = self.current_round['player_rounds'][killer_id]
        victim_round = self.current_round['player_rounds'][victim_id]
        killer_round['kills'] += 1
        if event.player.team == event.target.team:
            killer_round['tks'] += 1
        victim_round['deaths'] += 1

        killer_weapons = \
            self.current_match_map['player_match_weapons'][killer_id]
        victim_weapons = \
            self.current_match_map['player_match_weapons'][victim_id]
        killer_weapons[event.weapon]['kills'] += 1
        # headshots is updated in handle_attack
        victim_weapons[event.weapon]['deaths'] += 1
        kill = {
            'killer': killer_id,
            'killer_team': event.player.team,
            'victim': victim_id,
            'victim_team': event.target.team,
            'weapon': event.weapon,
            'headshot': event.headshot,
        }
        self.current_round['kills'].append(kill)
        self._check_clutch()

    def handle_attack(self, event):
        # ignore ff
        if event.player.team == event.target.team:
            return

        attacker_id = event.player.steam_id.id64()
        victim_id = event.target.steam_id.id64()
        attacker_round = self.current_round['player_rounds'][attacker_id]
        victim_round = self.current_round['player_rounds'][victim_id]

        if event.health > 0:
            damage = event.damage
        else:
            # target is dead, we have to adjust for overkill damage
            damage = victim_round['health']
        victim_round['health'] = event.health
        attacker_round['damage'] += damage

        weapon = event.weapon
        if attacker_id not in self.current_match_map['player_match_weapons']:
            self.current_match_map['player_match_weapons'][attacker_id] = {}
        attacker_weapons = \
            self.current_match_map['player_match_weapons'][attacker_id]
        if weapon not in attacker_weapons:
            attacker_weapons[weapon] = self.new_player_weapon()

        if victim_id not in self.current_match_map['player_match_weapons']:
            self.current_match_map['player_match_weapons'][victim_id] = {}
        victim_weapons = \
            self.current_match_map['player_match_weapons'][victim_id]
        if weapon not in victim_weapons:
            victim_weapons[weapon] = self.new_player_weapon()

        attacker_weapons[weapon]['damage'] += damage
        attacker_weapons[weapon]['hits'] += 1
        if event.hitgroup == 'head':
            attacker_weapons[weapon]['headshots'] += 1

    def handle_assist(self, event):
        steam_id = event.player.steam_id.id64()
        self.current_round['player_rounds'][steam_id]['assists'] += 1

    def handle_switch_team(self, event):
        steam_id = event.player.steam_id.id64()

        if event.orig_team == 'CT':
            self.cts.remove(steam_id)
        elif event.orig_team == 'TERRORIST':
            self.ts.remove(steam_id)

        if event.new_team == 'CT':
            self.cts.add(steam_id)
            if steam_id not in self.current_round['player_rounds']:
                self.current_round['player_rounds'][steam_id] = \
                    self.new_player_round(Match.SIDE_CT)
        elif event.new_team == 'TERRORIST':
            self.ts.add(steam_id)
            if steam_id not in self.current_round['player_rounds']:
                self.current_round['player_rounds'][steam_id] = \
                    self.new_player_round(Match.SIDE_T)
        elif steam_id in self.current_round['player_rounds']:
            self.current_round['player_rounds'][steam_id]['health'] = 0


def parse_match_log(data):
    parser = GoonPugParser()
    for line in data.splitlines():
        parser.parse_line(line)
