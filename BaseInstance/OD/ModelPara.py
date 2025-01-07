# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-18:23
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class ModelParameters(object):

    def __init__(self):
        # Q: Vehicle capacity
        self.vehicle_1_capacity = 5000
        self.vehicle_2_capacity = 2000
        self.vehicle_od_capacity = 150

        # F: Vehicle cost
        self.vehicle_1_cost = 200  # F_1
        self.vehicle_2_cost = 80  # F_2

        # Vehicle num
        # self.vehicle_1_num = 10
        # self.vehicle_2_num = 20

        # compensation
        self.compensation = 10

        # m_s: store capacity of satellite
        self.m_s = 150000

        # big M
        self.big_m = 2000

        # T^unload: unload time at satellites
        self.t_unload = 10
        # service_time
        self.p = 5
        # service_time
        self.service_time = 5

        # c^c_f: Fixed compensation for occasional drivers
        self.c_f = 5
        # c^c: Travel compensation proportional to travel time for occasional drivers
        self.c_c = 0.2

        # F_1: fixed cost of unit 1st-level vehicle
        self.f_1 = 20
        # F_2: fixed cost of unit 2nd-level vehicle
        self.f_2 = 5

        # #### Carbon ####
        # \phi: The coefficient value of CO2 emission
        self.phi = 2.63
        # C_p: The unit carbon trading price
        self.c_p = 1
        # F_c: The total fuel consumption in the entire distribution
        self.f_c = 2
        # Q_q: The carbon quota which is allocated by government
        self.Q_q_1 = 100
        self.Q_q_2 = 100

        # rho_1
        self.rho_1 = 0.377
        # rho_2
        self.rho_2 = 0.165

        """
        P = 2000
        c_r = 7.25
        phi = 2.63
        0.3777
        """