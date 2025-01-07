# -*- coding: utf-8 -*-
# @Time     : 2024-08-11-21:47
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Gba_TS_ALNS_depot_select import *


class AlnsModelBuilder(object):

    @staticmethod
    def build_alns(ins,
                   is_select,
                   depot_start=None,
                   depot_return=None):

        alns = GbaTsAlns()