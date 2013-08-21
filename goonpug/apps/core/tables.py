# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

import django_tables2 as tables
import itertools


class BasePlayerStatsTable(tables.Table):
    kills = tables.Column(verbose_name='K')
    assists = tables.Column(verbose_name='A')
    deaths = tables.Column(verbose_name='D')
    kdr = tables.Column(verbose_name='KDR')
    adr = tables.Column(verbose_name='ADR')
    rws = tables.Column(verbose_name='RWS')
    hsp = tables.Column(verbose_name='HSP')
    defuses = tables.Column(verbose_name='BD')
    plants = tables.Column(verbose_name='BP')
    tks = tables.Column(verbose_name='TK')
    clutch_v1 = tables.Column(verbose_name='1v1')
    clutch_v2 = tables.Column(verbose_name='1v2')
    clutch_v3 = tables.Column(verbose_name='1v3')
    clutch_v4 = tables.Column(verbose_name='1v4')
    clutch_v5 = tables.Column(verbose_name='1v5')
    k1 = tables.Column(verbose_name='1K')
    k2 = tables.Column(verbose_name='2K')
    k3 = tables.Column(verbose_name='3K')
    k4 = tables.Column(verbose_name='4K')
    k5 = tables.Column(verbose_name='5K')

    def render_kdr(self, value):
        return '%0.02f' % value

    def render_adr(self, value):
        return '%0.02f' % value

    def render_rws(self, value):
        return '%0.02f' % value

    def render_hsp(self, value):
        return '%0.03f' % value

    class Meta:
        template = 'table.html'


class PlayerSeasonTable(BasePlayerStatsTable):

    matches_won = tables.Column(verbose_name='W')
    matches_lost = tables.Column(verbose_name='L')
    matches_tied = tables.Column(verbose_name='T')
    rounds_won = tables.Column(verbose_name='RW')
    rounds_lost = tables.Column(verbose_name='RL')
    rounds_tied = tables.Column(verbose_name='RT')

    class Meta:
        attrs = {'class': 'table table-bordered table-condensed'}
        template = 'table.html'


class PlayerSeasonLeaderboard(PlayerSeasonTable):

    rank = tables.Column(verbose_name='#', orderable=False, empty_values=())
    player = tables.TemplateColumn('{{ value|safe }}', orderable=False)
    rating = tables.Column(verbose_name='GP Skill')

    def __init__(self, *args, **kwargs):
        super(PlayerSeasonLeaderboard, self).__init__(*args, **kwargs)
        self.counter = None

    def render_rating(self, value):
        return '%0.03f' % value

    def render_rank(self):
        if self.counter is None:
            self.counter = itertools.count(self.page.start_index())
        return '%d' % next(self.counter)

    class Meta:
        attrs = {'class': 'table table-bordered table-striped table-condensed'}
        sequence = ('rank', 'player', 'rating', '...')
        order_by = ('-rating', '-rws', '-kdr', '-adr')
        exclude = ('k1', 'k2', 'clutch_v1', 'clutch_v2')
        template = 'table.html'
