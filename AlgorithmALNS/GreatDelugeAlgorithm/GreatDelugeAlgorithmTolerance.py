# -*- coding: utf-8 -*-
# @Time     : 2024-09-05-14:14
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class GreatDelugeAlgorithm(object):
    """ accept method """

    def __init__(self,
                 alns,
                 alpha,
                 rain_speed):
        """
        self.tol_coe = 0.01
        self.phi = 0.9997    # reduction_factor
        self.psi = [1.00001, 1.1]    # increase factor
        """
        self.alns = alns
        self.best_obj = alns.best_sol.totalCost
        self.best_sol = alns.best_sol

        # GDA parameters
        self.alpha = 0.035  # 初始参数， tolerance = sol.obj * alpha

        self.rainSpeed = 0.99

        # 计算初始的 water level
        self.water_level = alns.best_sol.totalCost + sum(
            [route.distance for route in self.alns.best_sol.routes]) * self.alpha

        self.history = {'alpha': [],
                        'water_level': [],
                        'rain_speed': []}

    def record(self):
        self.history['alpha'].append(self.alpha)
        self.history['water_level'].append(self.water_level)
        self.history['rain_speed'].append(self.rainSpeed)

    def if_accept(self,
                  sol):

        if sol.totalCost < self.water_level:
            self.best_obj = sol.totalCost
            self.best_sol = sol
            self.water_level = sol.totalCost + sum([route.distance for route in sol.routes]) * self.alpha

            self.record()
            return True

        else:
            return False

    def iter_update_params(self):

        self.alpha *= self.rainSpeed
        self.water_level = self.best_obj + sum([route.distance for route in self.best_sol.routes]) * self.alpha
        print(f'water level = {self.water_level}')

    def decelerate_rain_speed(self):

        # 如果在多个迭代中没有改进，调整雨速
        self.rainSpeed *= 0.99

    def accelerate_rain_speed(self):

        self.rainSpeed *= 1.0005

    def adjust_rain_speed(self,
                          situation):

        if situation == 0:
            # 如果在多个迭代中没有改进，调整雨速  减速
            self.rainSpeed *= 0.999  # 0.9

        elif situation == 1:
            # 出现了可以接受的解
            self.rainSpeed *= 0.95  # 1.1

        elif situation == 2:
            # 出现了记录中的最优解
            self.rainSpeed *= 0.90  # 1.15

    def adjust_water_level(self):

        self.water_level = self.best_sol.totalCost + sum(
            [route.distance for route in self.alns.best_sol.routes]) * self.alpha
