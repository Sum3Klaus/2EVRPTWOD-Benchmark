# -*- coding: utf-8 -*-
# @Time     : 2024-07-10-13:56
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class GreatDelugeAlgorithm1(object):
    """ accept method """

    def __init__(self,
                 alns_model):

        """
        self.tol_coe = 0.01
        self.phi = 0.9997    # reduction_factor
        self.psi = [1.00001, 1.1]    # increase factor
        """

        self.alns_model = alns_model

        # GDA parameters
        self.alpha = 1.20
        self.water_level = alns_model.best_sol.totalCost * self.alpha  # 初始水位为初始解的目标函数值 * 水位系数
        self.best_water_level = alns_model.best_sol.totalCost * self.alpha

        self.rainSpeed = 0.52
        self.decayRate = alns_model.best_sol.totalCost * self.rainSpeed / (
                    alns_model.params.pu * alns_model.params.epochs)

    def iter_update_params(self,
                           sol):
        cur_water_level = deepcopy(self.water_level)

        # if sol.totalCost < cur_water_level:
        #     self.water_level = sol.totalCost * self.alpha
        #     self.water_level = self.water_level - self.decayRate
        # elif cur_water_level == (sol.totalCost * self.alpha - self.decayRate):
        #     self.water_level = self.water_level - self.decayRate
        # else:
        #     self.water_level -= self.decayRate

        if sol.totalCost < self.best_water_level:
            self.water_level = sol.totalCost * self.alpha
            # self.water_level = self.water_level - self.decayRate
            self.best_water_level = self.water_level

        elif sol.totalCost > self.water_level:
            self.water_level -= self.decayRate

        else:
            self.water_level -= self.decayRate

        print(f'water level = {self.water_level}')

    def if_accept(self,
                  sol):

        if (sol.totalCost < self.alns_model.best_sol.totalCost) or sol.totalCost < self.water_level:
            return True

        else:
            return False


class GreatDelugeAlgorithm(object):
    """ accept method """

    def __init__(self,
                 alns,
                 alpha,
                 rain_speed):

        self.alns = alns
        self.totalIter = alns.params.epochs * alns.params.pu
        self.alpha = alpha
        self.rainSpeed = rain_speed

        # 计算初始的 water level
        self.water_level = alns.best_sol.totalCost * alpha

        # 计算水位下降的速度
        # self.decayRate = alns.best_sol.totalCost * self.rainSpeed / self.totalIter
        self.decayRate = alns.best_sol.totalCost * self.rainSpeed / 1e6

    def if_accept(self,
                  sol):

        if sol.totalCost <= self.water_level:
            return True

        else:
            return False

    def iter_update_params(self):

        self.water_level -= self.decayRate
        print(f'water level = {self.water_level}')

    def decelerate_rain_speed(self):

        # 如果在多个迭代中没有改进，调整雨速
        self.decayRate *= 0.9

    def accelerate_rain_speed(self):

        self.decayRate *= 1.1

    def adjust_rain_speed(self,
                          situation):

        if situation == 0:
            # 如果在多个迭代中没有改进，调整雨速  减速
            self.decayRate *= 0.95  # 0.9

        elif situation == 1:
            # 出现了可以接受的解
            self.decayRate *= 1.0005  # 1.1

        elif situation == 2:
            # 出现了记录中的最优解
            self.decayRate *= 1  # 1.15

    def adjust_water_level(self):

        self.water_level = self.alns.best_sol.totalCost * self.alpha