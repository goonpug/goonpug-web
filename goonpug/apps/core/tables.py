# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

import django_tables2 as tables
from .models import PlayerSeason


class PlayerSeasonTable(tables.Table):

    class Meta:
        model = PlayerSeason
