# -*- coding: utf-8 -*-
# @Time     : 2024-04-14-22:50
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Route import Route


class Sol(object):

    def __init__(self,
                 ins):
        """  """
        self.ins = ins
        self.routes = []  # [class route1, route2, ...]
        self.vertex_sequence = []  # [class vertex, 2, 3, ..., ]
        self.vertex_id_sequence = []  # [int, 1, 2, ...]
        self.totalCost = 0
        self.carbon_cost = 0
        self.cus_arriveTime = dict()

    def __repr__(self):
        return f'Solution-{self.routes} | total cost = {self.totalCost}'

    def print_sol(self):
        print('---------- Solution ----------- \n total cost = {self.totalCost}')
        for route in self.routes:
            print(route)
        print('------------------------------')

    def add_route_into_sol(self, route):
        self.routes.append(route)
        self.totalCost += route.cost

        for vertex in route.route:
            if (vertex.id_ not in self.ins.graph.depot_list) and (
                    vertex.id_ not in self.ins.graph.sate_depot_list) and (
                    vertex.id_ not in self.ins.graph.sate_list):
                self.vertex_sequence.append(vertex)
                self.vertex_id_sequence.append(vertex.id_)

                self.cus_arriveTime[vertex.id_] = route.arriveTime[route.route.index(vertex)]

    def remove_route(self,
                     route: Route):
        self.routes.remove(route)
        self.totalCost -= route.cost

        for vertex in route.route:
            if vertex in self.vertex_sequence:
                self.vertex_sequence.remove(vertex)

    def replace_route(self,
                      index_: int,
                      route: Route):
        temp_route = self.routes[index_]
        self.routes[index_] = route
        self.totalCost += route.cost - temp_route.cost

    def ini_sol(self):

        self.routes.clear()
        # self.vertex_sequence.clear()
        self.totalCost = 0
        self.cus_arriveTime = dict()

    @staticmethod
    def copy_sol(sol):
        new_sol = Sol(ins=sol.ins)

        new_sol.routes = sol.routes
        new_sol.vertex_sequence = sol.vertex_sequence
        new_sol.totalCost = sol.totalCost

        return new_sol

    def update_sate_arrive_time(self):
        """  """

    def calc_carbon_cost(self):
        """  """
        tra_dist = self.totalCost - len(self.routes) * self.ins.model_para.vehicle_2_cost
        """
        coe_3_2.append(arc.distance * self.grb_params.rho_2 * self.grb_params.c_r)
        self.objs['2nd carbon cost'] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_2 - self.grb_params.Q_q_2))
        """

        # self.carbon_cost = self.ins.model_para.c_p * (
        #         (tra_dist * self.ins.model_para.rho_2 * self.ins.model_para.c_r) * self.ins.model_para.phi
        #         - self.ins.model_para.Q_q_2
        # )

        self.carbon_cost = self.ins.model_para.c_p * (
                self.ins.model_para.phi * (
                tra_dist * self.ins.model_para.rho_2 * self.ins.model_para.c_r
        ) - self.ins.model_para.Q_q_2
        )

    def calc_carbon_cost_1st(self):
        """  """
        tra_dist = self.totalCost - len(self.routes) * self.ins.model_para.vehicle_2_cost

        self.carbon_cost = self.ins.model_para.c_p * (
                self.ins.model_para.phi * (
                tra_dist * self.ins.model_para.rho_2 * self.ins.model_para.c_r
        ) - self.ins.model_para.Q_q_1
        )