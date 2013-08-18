# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from skills import GaussianRating
from skills.trueskill import TrueSkillGameInfo

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    UserManager
from django.utils import timezone

from srcds.objects import SteamId


class Match(models.Model):

    STATUS_UNKNOWN = 0
    STATUS_PENDING = 1
    STATUS_LIVE = 2
    STATUS_COMPLETE = 3
    STATUS_CANCELLED = 4
    STATUS = (
        (STATUS_UNKNOWN, 'Unknown'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_LIVE, 'Live'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    RULESET_CUSTOM = 0
    RULESET_ESEA = 1
    RULESET_CEVO = 2
    RULESET = (
        (RULESET_CUSTOM, 'Custom'),
        (RULESET_ESEA, 'ESEA/ESL'),
        (RULESET_CEVO, 'CEVO'),
    )

    MAP_MODE_BO1 = 0
    MAP_MODE_BO2 = 1
    MAP_MODE_BO3 = 2
    MAP_MODE = (
        (MAP_MODE_BO1, 'Standard'),
        (MAP_MODE_BO2, 'Best of 2'),
        (MAP_MODE_BO3, 'Best of 3'),
    )

    TEAM_OTHER = 0
    TEAM_A = 1
    TEAM_B = 2
    TEAM = (
        (TEAM_OTHER, 'Other'),
        (TEAM_A, 'Team A'),
        (TEAM_B, 'Team B'),
    )

    SIDE_OTHER = 0
    SIDE_CT = 1
    SIDE_T = 2
    SIDE = (
        (SIDE_OTHER, 'Other'),
        (SIDE_CT, 'CT'),
        (SIDE_T, 'T'),
    )

    SIDES = {
        'CT': SIDE_CT,
        'TERRORIST': SIDE_T
    }

    name = models.CharField(max_length=64, blank=True)
    server = models.ForeignKey('Server')
    season = models.ForeignKey('Season')
    team_a = models.ForeignKey('Team', related_name='match_team_a',
                               blank=True, null=True)
    team_b = models.ForeignKey('Team', related_name='match_team_b',
                               blank=True, null=True)
    status = models.IntegerField(choices=STATUS, default=STATUS_PENDING)
    paused = models.BooleanField(default=False)
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    ruleset = models.IntegerField(choices=RULESET, default=RULESET_ESEA)
    config_ot = models.BooleanField(default=True)
    config_knife_round = models.BooleanField(default=False)
    config_password = models.CharField(max_length=64, blank=True)
    map_mode = models.IntegerField(choices=MAP_MODE, default=MAP_MODE_BO1)
    current_map = models.IntegerField(default=0)
    start_time = models.DateTimeField()

    class Meta:
        unique_together = (('server', 'start_time',),)


class MatchMap(models.Model):

    match = models.ForeignKey('Match')
    map_number = models.IntegerField()
    map_name = models.CharField(max_length=64, default='')
    score_1 = models.IntegerField(default=0)
    score_2 = models.IntegerField(default=0)
    current_period = models.IntegerField(default=0)
    zip_url = models.CharField(max_length=256, default='')
    sha1sum = models.CharField(max_length=40, blank=True)
    has_demo = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = (('match', 'map_number',))


class MatchMapScore(models.Model):

    SCORE_TYPE_REGULATION = 0
    SCORE_TYPE_OT = 1
    SCORE_TYPE = (
        (SCORE_TYPE_REGULATION, 'Regulation'),
        (SCORE_TYPE_OT, 'OT')
    )

    match_map = models.ForeignKey('MatchMap')
    score_type = models.IntegerField(choices=SCORE_TYPE,
                                     default=SCORE_TYPE_REGULATION)
    score1_half1 = models.IntegerField()
    score1_half2 = models.IntegerField()
    score2_half1 = models.IntegerField()
    score2_half2 = models.IntegerField()


class PlayerManager(UserManager):

    def get_or_create_from_steamid(self, steamid):
        try:
            steamid = int(steamid)
        except ValueError:
            steamid = SteamId(steamid).id64()
        try:
            player = self.get(username=unicode(steamid))
            return (player, False)
        except Player.DoesNotExist:
            player = self.create(username=unicode(steamid), steamid=steamid)
            return (player, True)


class Player(AbstractBaseUser, PermissionsMixin):

    # django auth fields
    username = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    fullname = models.CharField(max_length=128)

    objects = PlayerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['steamid']

    # steam community fields
    steamid = models.BigIntegerField(unique=True)
    profileurl = models.CharField(max_length=256, default='')
    avatar = models.CharField(max_length=256, default='')
    avatarmedium = models.CharField(max_length=256, default='')
    avatarfull = models.CharField(max_length=256, default='')

    # goonpug specific fields
    is_banned = models.BooleanField(default=False)
    reputation = models.IntegerField(default=0)
    rating = models.FloatField(default=25.0)
    rating_variance = models.FloatField(default=8.333)

    def get_full_name(self):
        return self.fullname

    def get_short_name(self):
        return self.fullname

    def get_conservative_rating(self):
        rating = GaussianRating(self.rating, self.rating_variance)
        game_info = TrueSkillGameInfo()
        return rating.conservative_rating(game_info)

    def get_steamid(self):
      return SteamId.id64_to_str(self.steamid)


class PlayerBan(models.Model):

    player = models.ForeignKey('Player')
    start = models.DateField()
    end = models.DateField()
    reason = models.CharField(max_length=256)
    link = models.CharField(max_length=256)


class PlayerIp(models.Model):

    player = models.ForeignKey('Player')
    ip = models.CharField(max_length=16)

    class Meta:
        unique_together = (('player', 'ip'),)


class PlayerKill(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    round = models.ForeignKey('Round')
    killer = models.ForeignKey(
        'Player', related_name='playerkill_player_killer')
    killer_team = models.IntegerField(choices=Match.SIDE, default=0)
    victim = models.ForeignKey(
        'Player', related_name='playerkill_player_victim')
    victim_team = models.IntegerField(choices=Match.SIDE, default=0)
    weapon = models.CharField(max_length=64, blank=True)
    headshot = models.BooleanField(default=False)

    class Meta:
        unique_together = (('round', 'killer', 'victim',))


class PlayerMatch(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    player = models.ForeignKey('Player')
    team = models.IntegerField(choices=Match.TEAM, default=Match.TEAM_OTHER)
    first_side = models.IntegerField(choices=Match.SIDE,
                                     default=Match.TEAM_OTHER)
    current_side = models.IntegerField(choices=Match.SIDE,
                                       default=Match.TEAM_OTHER)
    kills = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    hsp = models.FloatField(default=0.0)
    defuses = models.IntegerField(default=0)
    plants = models.IntegerField(default=0)
    tks = models.IntegerField(default=0)
    clutch_v1 = models.IntegerField(default=0)
    clutch_v2 = models.IntegerField(default=0)
    clutch_v3 = models.IntegerField(default=0)
    clutch_v4 = models.IntegerField(default=0)
    clutch_v5 = models.IntegerField(default=0)
    k1 = models.IntegerField(default=0)
    k2 = models.IntegerField(default=0)
    k3 = models.IntegerField(default=0)
    k4 = models.IntegerField(default=0)
    k5 = models.IntegerField(default=0)
    damage = models.FloatField(default=0.0)
    rws = models.FloatField(default=0.0)
    rounds_won = models.IntegerField(default=0)
    rounds_lost = models.IntegerField(default=0)
    rounds_tied = models.IntegerField(default=0)

    class Meta:
        unique_together = (('match_map', 'player'),)


class PlayerMatchWeapons(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    player = models.ForeignKey('Player')
    weapon = models.CharField(max_length=64)
    headshots = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)

    class Meta:
        unique_together = (('match_map', 'player', 'weapon'))


class PlayerRound(models.Model):

    round = models.ForeignKey('Round')
    player = models.ForeignKey('Player')
    first_side = models.IntegerField(choices=Match.SIDE, default=0)
    current_side = models.IntegerField(choices=Match.SIDE, default=0)
    kills = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    defuses = models.IntegerField(default=0)
    plants = models.IntegerField(default=0)
    tks = models.IntegerField(default=0)
    clutch_v1 = models.IntegerField(default=0)
    clutch_v2 = models.IntegerField(default=0)
    clutch_v3 = models.IntegerField(default=0)
    clutch_v4 = models.IntegerField(default=0)
    clutch_v5 = models.IntegerField(default=0)
    k1 = models.IntegerField(default=0)
    k2 = models.IntegerField(default=0)
    k3 = models.IntegerField(default=0)
    k4 = models.IntegerField(default=0)
    k5 = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)
    rws = models.FloatField(default=0.0)

    class Meta:
        unique_together = (('round', 'player',),)


class PlayerSeason(models.Model):

    player = models.ForeignKey('Player')
    season = models.ForeignKey('Season')
    kills = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    hsp = models.FloatField('headshot percentage', default=0.0)
    defuses = models.IntegerField('bomb defusals', default=0)
    plants = models.IntegerField(default=0)
    tks = models.IntegerField(default=0)
    clutch_v1 = models.IntegerField(default=0)
    clutch_v2 = models.IntegerField(default=0)
    clutch_v3 = models.IntegerField(default=0)
    clutch_v4 = models.IntegerField(default=0)
    clutch_v5 = models.IntegerField(default=0)
    k1 = models.IntegerField(default=0)
    k2 = models.IntegerField(default=0)
    k3 = models.IntegerField(default=0)
    k4 = models.IntegerField(default=0)
    k5 = models.IntegerField(default=0)
    damage = models.FloatField(default=0)
    rws = models.FloatField(default=0.0)
    rounds_won = models.IntegerField(default=0)
    rounds_lost = models.IntegerField(default=0)
    rounds_tied = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    matches_lost = models.IntegerField(default=0)
    matches_tied = models.IntegerField(default=0)

    class Meta:
        unique_together = (('player', 'season',),)


class PlayerSeasonWeapons(models.Model):

    player = models.ForeignKey('Player')
    season = models.ForeignKey('Season')
    weapon = models.CharField(max_length=64)
    headshots = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)

    class Meta:
        unique_together = (('player', 'season', 'weapon',),)


class Round(models.Model):

    WIN_TYPE_NORMAL = 0
    WIN_TYPE_DEFUSED = 1
    WIN_TYPE_EXPLODED = 2
    WIN_TYPE_SAVED = 3
    WIN_TYPE = (
        (WIN_TYPE_NORMAL, 'Normal'),
        (WIN_TYPE_DEFUSED, 'Bomb was defused'),
        (WIN_TYPE_EXPLODED, 'Bomb was exploded'),
        (WIN_TYPE_SAVED, 'Bomb site was saved')
    )

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    round_number = models.IntegerField(default=0)
    bomb_planted = models.BooleanField(default=False)
    bomb_defused = models.BooleanField(default=False)
    bomb_exploded = models.BooleanField(default=False)
    win_type = models.IntegerField(choices=WIN_TYPE, default=WIN_TYPE_NORMAL)
    team_win = models.IntegerField(choices=Match.TEAM,
                                   default=Match.TEAM_OTHER)
    ct_win = models.BooleanField(default=False)
    t_win = models.BooleanField(default=False)
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    backup_file_name = models.CharField(max_length=256, blank=True)

    class Meta:
        unique_together = (('match_map', 'round_number',),)


class Season(models.Model):

    name = models.CharField(max_length=64)
    event = models.CharField(max_length=64)
    start = models.DateField()
    end = models.DateField()
    link = models.CharField(max_length=128)
    logo = models.CharField(max_length=256)
    is_active = models.BooleanField()


class Server(models.Model):

    name = models.CharField(max_length=128, blank=True)
    ip = models.CharField(max_length=16)
    port = models.IntegerField(default=27015)
    gotv_ip = models.CharField(max_length=16, blank=True)
    gotv_port = models.IntegerField(default=27020)
    rcon = models.CharField(max_length=64, blank=True)

    class Meta:
        unique_together = (('ip', 'port'),)


class Team(models.Model):

    name = models.CharField(max_length=128)
    shorthandle = models.CharField(max_length=64)
    link = models.CharField(max_length=128)


class TeamSeason(models.Model):

    team = models.ForeignKey('Team')
    season = models.ForeignKey('Season')
