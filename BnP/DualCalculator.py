# -*- coding: utf-8 -*-
# @Time     : 2024-08-07-11:00
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import itertools
from copy import deepcopy
from gurobipy import *
from Route import *


class DualCalculator(object):
    next_iter_time = itertools.count(start=1000)

    def __init__(self,
                 alns):

        self.alns = alns
        self.ins = alns.ins
        # self.sate_id = sate_id

        self.modelBuilder = None
        self.RMP = None
        self.SP = None

        self.RMP_duals = {}
        self.column_pool = None
        self.route_index = 0

    def set_model(self,
                  model_builder):
        self.modelBuilder = model_builder

        self.RMP = model_builder.RMP.copy()
        self.SP = model_builder.SP.copy()

        self.column_pool = model_builder.column_pool
        self.RMP_duals = model_builder.RMP_duals

    def add_init_column_into_rmp(self,
                                 routes):
        """ """
        for route in routes:
            self.route_index = next(self.next_iter_time)

            key_ = 'r_' + str(self.route_index)
            route_list = deepcopy(route.route_list)
            # route_list.insert(0, sate_id)
            # route_list.append(self.ins.graph.sate_to_depot[sate_id])
            self.column_pool[key_] = route_list
            column = self.get_column(route_list=route.route_list)
            self.add_column_into_rmp(route=route,
                                     new_column=column,
                                     iter_times=self.route_index)

    def add_column_into_rmp(self,
                            route,
                            new_column,
                            iter_times):
        # new_column.append(1)  # 车辆数量约束

        new_column_name = 'r_' + str(iter_times)
        new_rmp_col = Column(new_column, self.RMP.getConstrs())

        self.RMP.addVar(lb=0, ub=1,
                        obj=route.distance + self.ins.model_para.vehicle_2_cost,
                        vtype=GRB.CONTINUOUS,
                        name=new_column_name,
                        column=new_rmp_col)

        self.RMP.update()

    def get_column(self,
                   route_list):
        """ """
        column = [0 for i in range(len(self.ins.customer_list_alns))]
        route_list_ = deepcopy(route_list)
        route_list_ = [i for i in route_list_ if i not in (self.ins.graph.sate_list + self.ins.graph.sate_depot_list)]
        for cus in self.ins.customer_list_alns:
            if cus in route_list:
                column[self.ins.customer_list_alns.index(cus)] = 1

        return column

    def solve_rmp_and_get_duals(self):
        """
        solve the RMP and get the duals
        :return:
        """

        self.RMP.optimize()

        # get the duals
        if self.RMP.status == 2:
            for con in self.RMP.getConstrs():
                # each cons → dual variable
                con_name = con.ConstrName
                self.RMP_duals[con_name] = con.Pi
        # print()

    def update_sp(self):
        """
        update the objective coe of SP
        :return:
        """
        obj = LinExpr()

        visit_list = deepcopy(self.ins.customer_list_alns)
        visit_list = visit_list + self.ins.graph.sate_list + self.ins.graph.sate_depot_list

        for i in visit_list:
            for j in visit_list:
                if self.modelBuilder.judge_arc(arc_id=(i, j),
                                               graph=self.ins.graph.second_echelon_graph):
                    var_name = 'x_' + str(i) + '_' + str(j)
                    con_name = 'cons_' + str(i)

                    # coe = (self.ins.graph.arc_dict[
                    #            i, j].distance + self.ins.model_para.vehicle_2_cost) if i not in (
                    #             self.ins.graph.sate_list + self.ins.graph.sate_depot_list) else \
                    # self.ins.graph.arc_dict[i, j].distance
                    coe = self.ins.graph.arc_dict[i, j].distance
                    if i in self.ins.customer_list_alns:
                        coe -= self.RMP_duals[str(i)]

                    obj.addTerms(coe, self.SP.getVarByName(var_name))

        self.SP.setObjective(obj - self.RMP_duals[str(self.ins.graph.depot_list[1])], GRB.MINIMIZE)
        # self.SP.setObjective(obj + self.ins.model_para.vehicle_2_cost, GRB.MINIMIZE)

    def get_column_from_sp(self):
        """ """
        # sate_id = self.alns.target
        new_route = Route()
        # new_route.set_sate_route(sate=self.ins.graph.vertex_dict[sate_id])
        # new_route.set_start_time(ins=self.ins,
        #                          sate=sate_id)

        new_column = [0] * len(self.ins.customer_list_alns)

        visit_list = deepcopy(self.ins.customer_list_alns)
        visit_list = visit_list + self.ins.graph.sate_list + self.ins.graph.sate_depot_list

        # get the  start sate
        sate_start = None
        current_node = None
        for s in self.ins.graph.sate_list:
            for j in visit_list:
                if self.modelBuilder.judge_arc(arc_id=(s, j),
                                               graph=self.ins.graph.second_echelon_graph):
                    var_name = 'x_' + str(s) + '_' + str(j)
                    if self.SP.getVarByName(var_name).x > 0.5:
                        current_node = s
                        sate_start = s

        new_route.set_sate_route(sate=self.ins.graph.vertex_dict[sate_start])
        new_route.set_start_time(ins=self.ins,
                                 sate=sate_start)

        while current_node != self.ins.graph.sate_to_depot[sate_start]:
            for j in visit_list:
                if self.modelBuilder.judge_arc(arc_id=(current_node, j),
                                               graph=self.ins.graph.second_echelon_graph):

                    var_name = 'x_' + str(current_node) + '_' + str(j)
                    if self.SP.getVarByName(var_name).x > 0.5:
                        new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[j],
                                                        distance=self.ins.graph.arc_dict[current_node, j].distance,
                                                        service_time=self.ins.model_para.service_time)

                        current_node = j

        for cus in self.ins.customer_list_alns:
            if cus in new_route.route_list:
                new_column[self.ins.customer_list_alns.index(cus)] = 1

        # self.route_index = next(self.next_iter_time)
        print('iter cnt: %-8s, new route: %-50s | route length: %-8s' % (self.route_index,
                                                                         new_route.route_list, new_route.distance))

        return new_route, new_column

    def bound_solve(self):
        """ """
        """convert RLMP into IP"""

        if self.RMP.IsMIP != 1:
            for var in self.RMP.getVars():
                # vType: continuous to binary
                var.vType = "B"

        self.RMP.optimize()

        """get the solution"""
        print(f'ObjVal = {self.RMP.ObjVal}')

        for var in self.RMP.getVars():
            if var.x > 0.5:
                print('%6s = %3s, route: %s50s' % (var.varName, var.x,
                                                   self.column_pool[var.varName]))

    def column_generation(self):
        new_route_not_change_time = 0
        new_sol_not_change_time = 0
        sp_obj_pre = 0

        self.RMP.setParam('OutputFlag', 0)
        self.SP.setParam('OutputFlag', 0)
        self.SP.setParam('TimeLimit', 10)

        # self.SP_dict[sate_id].setParam('TimeLimit', 360)
        # self.RMP_dict[sate_id].write('RMP.lp')
        # self.SP_dict[sate_id].write('SP.lp')

        """solve RMP and get duals"""
        self.solve_rmp_and_get_duals()

        """update SP"""
        self.update_sp()

        """solve SP"""
        self.SP.optimize()
        sp_obj_pre = self.SP.ObjVal

        while self.SP.ObjVal < 1e-6:
            self.route_index = next(self.next_iter_time)

            self.RMP.update()

            """get column from SP"""
            new_route, new_column = self.get_column_from_sp()
            """add column into RMP"""
            # if new_route.route_list in self.column_pool.values() and (
            #         len(new_route.route_list) == 3) or new_route_not_change_time >= 80:
            #     break
            #
            # else:
            key_ = 'r_' + str(self.route_index)
            self.column_pool[key_] = new_route.route_list

            self.add_column_into_rmp(route=new_route,
                                     new_column=new_column,
                                     iter_times=self.route_index)

            if new_route.route_list in self.column_pool.values():
                new_route_not_change_time += 1

            """solve RLMP and get duals"""
            # vType of y is CONTINUOUS
            self.solve_rmp_and_get_duals()
            print(self.RMP_duals)

            print('--------------------------The solution of RMP--------------------------')
            print(f'RMP obj: {self.RMP.ObjVal}')
            print('--------------------------The variables of RMP--------------------------')
            for var in self.RMP.getVars():
                var_name = var.varName
                if var.x > 0.05:
                    # print(f'{self.column_pool[var_name]}')
                    print(f'{var_name} = {var.x} \t | Route: {self.column_pool[var_name]}')

            """update SP"""
            self.update_sp()

            """solve SP"""
            self.SP.optimize()
            print(f'SP.ObtVal = {self.SP.ObjVal}')

            if sp_obj_pre != self.SP.ObjVal:
                sp_obj_pre = self.SP.ObjVal
                new_sol_not_change_time = 0
            else:
                new_sol_not_change_time += 1

            if new_sol_not_change_time > 1000:
                break
        print(f'CG finished!')
        self.bound_solve()
