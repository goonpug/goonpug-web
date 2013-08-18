# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from __future__ import absolute_import

from rest_framework import serializers

from .models import *


class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = ('name', 'server', 'season', 'team_a', 'team_b',
                  'status', 'paused', 'score_a', 'score_b', 'ruleset',
                  'config_ot', 'config_knife_round', 'map_mode',
                  'current_map', 'start_time',)


class MatchMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchMap
        fields = ('match', 'map_name', 'score_1', 'score_2',
                  'current_period', 'zip_url', 'sha1sum', 'has_demo',
                  'start_time', 'end_time',)


class PlayerSerializer(serializers.ModelSerializer):

    rating = serializers.FloatField(source='get_rating', read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'username', 'steamid', 'is_banned', 'profileurl',)


class RoundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Round
        fields = ('match', 'match_map', 'round_number', 'bomb_planted',
                  'bomb_defused', 'bomb_exploded', 'win_type', 'team_win',
                  'ct_win', 't_win', 'score_a', 'score_b', 'backup_file_name',)


class SeasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Season
        fields = ('name', 'event', 'start', 'end', 'link', 'logo',
                  'is_active',)
