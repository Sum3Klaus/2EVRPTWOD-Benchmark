# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-14:32
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class AlnsParameters(object):
    """ alns parameters """

    def __init__(self):
        """  """
        self.rho = 0.4  # ## 0.6  update weight

        self.rank_1 = 30  # ##  r1 新解优于最优解时得分
        self.rank_2 = 25  # ##  r2 新解优于当前解时得分
        self.rank_3 = 10  # ##  r3 新解不优于当前解但接受
        self.rank_4 = 2  # ##  r4 新解不优于当前解且没接受

        # destroy operator RepairOperators : random destroy
        # self.random_destroy_min = 0.1  # ##  rand_d_min
        # self.random_destroy_max = 0.4  # ##  rand_d_max
        # destroy operator 2 : worst destroy
        self.worst_destroy_min = 0.1  # ## worst_d_min
        self.worst_destroy_max = 0.25  # ## worst_d_max
        # self.worst_d_min = 5
        # self.worst_d_max = 20
        # destroy operator 3 : shaw destroy
        self.shaw_destroy_min = 0.15  # ## worst_d_min
        self.shaw_destroy_max = 0.35  # ## worst_d_max

        self.common_destroy_min = 0.1  # ## paper parameters
        self.common_destroy_max = 0.4  # ## paper parameters

        self.dual_destroy_min = 0.1
        self.dual_destroy_max = 0.3  # ## paper parameters

        # repair operators
        # self.regret_min = 0.3  # ##  regret_n
        # self.regret_max = 0.6
        self.regret_n = 5

        self.tolerance = 1e-6  # 终止系数
        self.temperature = 0   # 解的接受参数，acceptance method ## The Great Deluge Algorithm

        self.epochs = 25  # 25
        self.pu = 60   # 60

        self.phi = 0.9

        # GBA
        self.gba_rain_speed = 0.52    # 0.728 * ini sol / iter time
        self.gda_alpha = 1.4

        # end
        self.max_compute_time = 1800
        self.grace_period = 160
        self.max_no_improve_iter = 51