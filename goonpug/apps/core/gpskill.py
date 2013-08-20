# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.

from skills import GaussianRating, RatingFactory
from skills.numerics import Range
from skills.trueskill import TwoTeamTrueSkillCalculator


class GpSkillCalculator(TwoTeamTrueSkillCalculator):

    def __init__(self):
        super(TwoTeamTrueSkillCalculator, self).__init__(
            Range.exactly(2),
            Range.at_least(1),
            allow_partial_play=True,
            allow_partial_update=True
        )
        RatingFactory.rating_class = GaussianRating
