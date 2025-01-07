# -*- coding: utf-8 -*-
# @Time     : 2024-08-06-17:10
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
"""
在存在 depot selection 的问题中，需要重新设计 主问题 和 子问题
"""
from gurobipy import *
from copy import deepcopy
from itertools import *
from Route import *
from Common import *


class ModelBuilder(object):

    def __init__(self,
                 alns):

        self.alns = alns  # alns.is_select

        self.route_index = 0

        self.ins = alns.ins
        # self.sate_id = sate_id

        # RMP
        self.RMP = None  # RMP model
        self.RMP_cons = {}  # constraints of RMP
        self.RMP_duals = {}  # duals of RMP
        self.R = {}  # decision variables in RMP

        # SP
        self.SP = None  # pricing model
        self.sp_cons = {}
        self.X = {}  # routing variables of SP
        self.S = {}  # time variables of SP
        self.T = {}  # service time variables
        self.W = {}  # capacity variables
        self.Zeta = {}  # customer served by sate
        self.routes = {}  # routes in RMP    key = varname value = route

        self.column_pool = {}
        self.column_pool_route = {}

        self.VRP = None

    @staticmethod
    def judge_arc(arc_id,
                  graph):
        if arc_id in graph.arc_dict and graph.arc_dict[arc_id].adj == 1:
            return True

        else:
            return False

    def gen_route(self,
                  route_lst):
        """ """
        deport_start = route_lst[0]

        new_route = Route()
        new_route.route.append(self.ins.graph.vertex_dict[deport_start])
        new_route.route_list.append(deport_start)
        new_route.arriveTime[0] = self.ins.graph.vertex_dict[deport_start].ready_time
        new_route.timeTable[0] = self.ins.graph.vertex_dict[deport_start].ready_time

        for vertex_id in route_lst[1:]:
            service_time = self.ins.model_para.service_time if vertex_id in self.ins.graph.customer_list else 0
            new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[vertex_id],
                                            distance=self.ins.graph.arc_dict[
                                                new_route.route_list[-1], vertex_id].distance,
                                            service_time=service_time)

        return new_route

    def build_rmp_depot_select(self):

        self.RMP = Model('RMP')
        self.RMP.setParam('OutputFlag', 0)

        """ for each customer, generate a feasible path """
        vehicle_lp = LinExpr()
        vehicle_coe = []
        vehicle_var = []

        # 取默认的第一个sate作为初始选择的depot
        deport_start = self.ins.graph.sate_list[0]
        deport_return = self.ins.graph.sate_to_depot[deport_start]

        for customer_id in self.ins.customer_list_alns:
            var_name = 'r_' + str(customer_id)

            # route  [depot 0, customer_id, depot customer_id + 1]
            self.routes[var_name] = [deport_start, customer_id, deport_return]

            self.column_pool[var_name] = [deport_start, customer_id, deport_return]
            self.column_pool_route[var_name] = self.gen_route(route_lst=self.column_pool[var_name])

            obj_coe = self.ins.graph.arc_dict[
                          deport_start, customer_id].distance * 2 + self.ins.model_para.vehicle_2_cost

            self.R[customer_id] = self.RMP.addVar(lb=0, ub=1, obj=obj_coe, vtype=GRB.CONTINUOUS, name=var_name)

            """ add constraints into the RMP """
            # con_name = 'cons_' + str(customer_id)
            con_name = str(customer_id)
            self.RMP_cons[customer_id] = self.RMP.addConstr(self.R[customer_id] == 1, name=con_name)

            vehicle_coe.append(1)
            vehicle_var.append(self.R[customer_id])

        vehicle_lp.addTerms(vehicle_coe, vehicle_var)
        # con_name = 'cons_' + str(self.ins.graph.customer_num + 1)
        # con_name = str(str(self.ins.graph.depot_list[1]))
        # self.RMP_cons[str(self.ins.graph.depot_list[1])] = self.RMP.addConstr(
        #     vehicle_lp <= self.ins.vehicle_num_1st, name=con_name)

        self.RMP.update()

        """ initialize the dual variables """
        for key in self.RMP_cons.keys():
            # key = customer_id
            # key = 'cons_' + str(key)
            self.RMP_duals[str(key)] = 0  # or other valuable number
        # self.RMP_duals['cons_' + str(self.alns.target)] = 0
        # self.RMP_duals['cons_' + str(self.ins.graph.sate_to_depot[self.alns.target])] = 0
        for sate in self.ins.graph.sate_list:
            sate_depot = self.ins.graph.sate_to_depot[sate]
            self.RMP_duals[str(sate)] = 0
            self.RMP_duals[str(sate_depot)] = 0
        self.RMP_duals[str(self.ins.graph.depot_list[1])] = 0

    def build_rmp_no_select(self,
                            deport_start,
                            deport_return
                            ):

        self.RMP = Model('RMP')
        self.RMP.setParam('OutputFlag', 0)

        """ for each customer, generate a feasible path """
        vehicle_lp = LinExpr()
        vehicle_coe = []
        vehicle_var = []

        for customer_id in self.ins.customer_list_alns:
            var_name = 'r_' + str(customer_id)
            # route  [depot 0, customer_id, depot customer_id + 1]
            self.routes[var_name] = [deport_start, customer_id, deport_return]

            self.column_pool[var_name] = [deport_start, customer_id, deport_return]
            self.column_pool_route[var_name] = self.gen_route(route_lst=self.column_pool[var_name])

            obj_coe = self.ins.graph.arc_dict[
                          deport_start, customer_id].distance * 2 + self.ins.model_para.vehicle_2_cost

            self.R[customer_id] = self.RMP.addVar(lb=0, ub=1, obj=obj_coe, vtype=GRB.CONTINUOUS, name=var_name)

            """ add constraints into the RMP """
            # con_name = 'cons_' + str(customer_id)
            con_name = str(customer_id)
            self.RMP_cons[customer_id] = self.RMP.addConstr(self.R[customer_id] == 1, name=con_name)

            vehicle_coe.append(1)
            vehicle_var.append(self.R[customer_id])

        vehicle_lp.addTerms(vehicle_coe, vehicle_var)
        # con_name = 'cons_' + str(self.ins.graph.customer_num + 1)
        con_name = str(self.ins.graph.customer_num + 1)
        self.RMP_cons[self.ins.graph.customer_num + 1] = self.RMP.addConstr(
            vehicle_lp <= self.ins.vehicle_num_1st, name=con_name)

        self.RMP.update()

        """ initialize the dual variables """
        for key in self.RMP_cons.keys():
            # key = customer_id
            # key = 'cons_' + str(key)
            self.RMP_duals[str(key)] = 0  # or other valuable number

        self.RMP_duals[str(deport_start)] = 0
        self.RMP_duals[str(deport_return)] = 0

    def build_sp_depot_select(self):
        """  """
        self.SP = Model('SP')

        """define the decision variables"""
        visit_list = deepcopy(self.ins.customer_list_alns)
        visit_list = visit_list + self.ins.graph.sate_list + self.ins.graph.sate_depot_list

        for i in visit_list:
            # arrive time
            var_name_s = 's_' + str(i)
            self.S[i] = self.SP.addVar(lb=0,
                                       ub=self.ins.graph.vertex_dict[i].due_time, vtype=GRB.CONTINUOUS,
                                       name=var_name_s)

            # capacity
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            var_name_w = 'w_' + str(i)
            self.W[i] = self.SP.addVar(lb=demand, ub=self.ins.model_para.vehicle_2_capacity,
                                       vtype=GRB.CONTINUOUS,
                                       name=var_name_w)

            # service time
            var_name_t = 't_' + str(i)
            self.T[i] = self.SP.addVar(lb=self.ins.graph.vertex_dict[i].ready_time,
                                       ub=self.ins.graph.vertex_dict[i].due_time,
                                       vtype=GRB.CONTINUOUS,
                                       name=var_name_t)

            for j in visit_list:
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name_x = 'x_' + str(i) + '_' + str(j)
                        self.X[i, j] = self.SP.addVar(lb=0, ub=1,
                                                      vtype=GRB.BINARY,

                                                      name=var_name_x)
        for i in self.ins.customer_list_alns:
            for s in self.ins.graph.sate_list:
                # if self.judge_arc(arc_id=(s, i),
                #                   graph=self.ins.graph.second_echelon_graph):
                var_name_zeta = 'zeta_' + str(i) + '_' + str(s)
                self.Zeta[i, s] = self.SP.addVar(
                    lb=0,
                    ub=1,
                    vtype=GRB.BINARY,
                    name=var_name_zeta
                )

        """set the objective functions"""
        obj_1 = LinExpr()
        for i in visit_list:
            for j in visit_list:
                if self.judge_arc(arc_id=(i, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    cost = (self.ins.graph.arc_dict[
                                i, j].distance + self.ins.model_para.vehicle_2_cost) if i in self.ins.graph.sate_list else \
                        self.ins.graph.arc_dict[i, j].distance
                    # key = 'cons_' + str(i)
                    coe = cost - self.RMP_duals[str(i)]
                    # var_name_x = 'x_' + str(i) + '_' + str(j)
                    obj_1.addTerms(coe, self.X[i, j])

        """add constraints"""
        # vehicle 每辆车只能从一个satellite as depot 出发
        lhs_start = LinExpr()
        lhs_start_coe = []
        lhs_start_var = []

        for i in self.ins.graph.sate_list:
            for j in self.ins.customer_list_alns:
                if self.judge_arc(arc_id=(i, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.X[i, j])
        lhs_start.addTerms(lhs_start_coe, lhs_start_var)
        con_name_start = 'SP_start'
        self.sp_cons[con_name_start] = self.SP.addConstr(
            lhs_start == 1,
            name=con_name_start
        )

        # 每个客户只能分配给一个sate
        for c in self.ins.customer_list_alns:
            customer_assign = LinExpr()
            customer_assign_coe = []
            customer_assign_var = []

            for s in self.ins.graph.sate_list:
                if judge_arc(arc_id=(s, c),
                             graph=self.ins.graph.second_echelon_graph):
                    customer_assign_coe.append(1)
                    customer_assign_var.append(self.Zeta[c, s])
            customer_assign.addTerms(customer_assign_coe, customer_assign_var)

            con_customer_assign = '2nd-con_customer_assign-' + str(c)
            self.sp_cons[con_customer_assign] = self.SP.addConstr(
                customer_assign == 1,
                name=con_customer_assign
            )

        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        # 添加约束 sate 出发 和 返回 只能有 分配的 customer， var_y 和 zeta 的关系
        for s in self.ins.graph.sate_list:
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            # return
            lhs_return = LinExpr()
            lhs_return_coe = []
            lhs_return_var = []

            sate_depot = self.ins.graph.sate_to_depot[s]
            for j in self.ins.customer_list_alns:
                if judge_arc(arc_id=(s, j),
                             graph=self.ins.graph.second_echelon_graph):
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.X[s, j])

                if judge_arc(arc_id=(j, sate_depot),
                             graph=self.ins.graph.second_echelon_graph):
                    lhs_return_coe.append(1)
                    lhs_return_var.append(self.X[j, sate_depot])

            lhs_start.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = '2nd_con_start-' + str(s)
            self.sp_cons[con_name_start] = self.SP.addConstr(
                lhs_start <= 1,
                name=con_name_start
            )

            lhs_return.addTerms(lhs_return_coe, lhs_return_var)
            con_start_equ_return = '2nd_con_start_equ_return-' + str(s)
            self.sp_cons[con_start_equ_return] = self.SP.addConstr(
                lhs_start == lhs_return,
                name=con_start_equ_return
            )

        # 车可以有多个 satellite 选择，与客户的分配相关
        lhs_start_2 = LinExpr()
        lhs_start_2_coe = []
        lhs_start_2_var = []

        for s in self.ins.graph.sate_list:
            for i in self.ins.customer_list_alns:

                if judge_arc(arc_id=(s, i),
                             graph=self.ins.graph.second_echelon_graph):
                    lhs_start_2_coe.append(1)
                    lhs_start_2_var.append(self.X[s, i])
        lhs_start_2.addTerms(lhs_start_2_coe, lhs_start_2_var)

        for i in self.ins.customer_list_alns:
            for j in self.ins.customer_list_alns:
                if judge_arc(arc_id=(i, j),
                             graph=self.ins.graph.second_echelon_graph):
                    con_lhs_must_start_from_sate = '2nd_con_must_start_from_sate-' + str(i) + '_' + str(j)
                    self.sp_cons[con_lhs_must_start_from_sate] = self.SP.addConstr(
                        self.X[i, j] <= lhs_start_2,
                        name=con_lhs_must_start_from_sate
                    )

        # travel 限制，与分配联系起来
        for l in self.ins.customer_list_alns:
            for m in self.ins.customer_list_alns:

                if judge_arc(arc_id=(l, m),
                             graph=self.ins.graph.second_echelon_graph):

                    for i in self.ins.graph.sate_list:

                        lq_travel_assign = LinExpr()
                        lq_travel_assign_coe = []
                        lq_travel_assign_var = []

                        sate_list = deepcopy(self.ins.graph.sate_list)
                        sate_list.remove(i)
                        for s in sate_list:
                            lq_travel_assign_coe.append(1)
                            lq_travel_assign_var.append(self.Zeta[m, s])
                        lq_travel_assign.addTerms(lq_travel_assign_coe, lq_travel_assign_var)

                        con_travel_assign = '2nd_con_travel_assign-' + str(l) + str(m)
                        self.sp_cons[con_travel_assign] = self.SP.addConstr(
                            self.X[l, m] + self.Zeta[l, i] + lq_travel_assign <= 2,
                            name=con_travel_assign
                        )

        # for sate in self.ins.graph.sate_list:
        #     sate_depot = self.ins.graph.sate_to_depot[sate]
        #
        #     for c in self.ins.customer_list_alns:
        #         start_only_assign = LinExpr()
        #         start_only_assign_coe = []
        #         start_only_assign_var = []
        #         if judge_arc(arc_id=(sate, c),
        #                      graph=self.ins.graph.second_echelon_graph):
        #             start_only_assign_coe.append(1)
        #             start_only_assign_var.append(self.X[sate, c])
        #         start_only_assign.addTerms(start_only_assign_coe, start_only_assign_var)
        #
        #         con_start_only_assign = '2nd_con_start_only_assign-' + str(sate) + str(c)
        #         self.sp_cons[con_start_only_assign] = self.SP.addConstr(
        #             start_only_assign <= self.Zeta[c, sate],
        #             name=con_start_only_assign
        #         )
        #
        #         return_only_assign = LinExpr()
        #         return_only_assign_coe = []
        #         return_only_assign_var = []
        #         if judge_arc(arc_id=(c, sate_depot),
        #                      graph=self.ins.graph.second_echelon_graph):
        #             return_only_assign_coe.append(1)
        #             return_only_assign_var.append(self.X[c, sate_depot])
        #         return_only_assign.addTerms(return_only_assign_coe, return_only_assign_var)
        #         con_return_only_assign = '2nd_con_return_only_assign-' + str(sate) + str(c)
        #         self.sp_cons[con_return_only_assign] = self.SP.addConstr(
        #             return_only_assign <= self.Zeta[c, sate],
        #             name=con_return_only_assign
        #         )

        # 每个customer只能被访问一次
        for c in self.ins.customer_list_alns:
            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    lhs_coe_1.append(1)
                    lhs_var_1.append(self.X[i, c])

            lhs_1.addTerms(lhs_coe_1, lhs_var_1)
            con_name = 'customer_visit-' + str(c)
            self.sp_cons[con_name_start] = self.SP.addConstr(
                lhs_1 <= 1,
                name=con_name
            )

        # flow balance
        for c in self.ins.customer_list_alns:
            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    lhs_coe_2.append(1)
                    lhs_var_2.append(self.X[i, c])

            for j in visit_list:
                if self.judge_arc(arc_id=(c, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    lhs_coe_2.append(-1)
                    lhs_var_2.append(self.X[c, j])

            lhs_2.addTerms(lhs_coe_2, lhs_var_2)
            con_name = 'flow_balance-' + str(c)
            self.sp_cons[con_name] = self.SP.addConstr(
                lhs_2 == 0,
                name=con_name
            )

        # capacity
        for i in visit_list:
            capacity_1 = 'con_capacity-1_' + f'{i}'
            lq = LinExpr()
            lq.addTerms([1], [self.W[i]])
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            self.sp_cons[capacity_1] = self.SP.addConstr(
                demand <= lq,
                name=capacity_1
            )

            for j in visit_list:
                if self.judge_arc(arc_id=(i, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    lhs = self.W[i] - self.W[j] + (
                            self.ins.graph.vertex_dict[j].demand + self.ins.model_para.vehicle_2_capacity) * self.X[
                              i, j]
                    capacity_2 = 'con_capacity-2_' + f'{i}' + '_' + f'{j}'

                    if capacity_2 not in self.sp_cons.keys():
                        self.sp_cons[capacity_2] = self.SP.addConstr(
                            lhs <= self.ins.model_para.vehicle_2_capacity,
                            name=capacity_2
                        )

        # time windows
        for i in visit_list:
            con_name_time_1 = 'con_time_window-' + f'{i}'

            service_time = self.ins.model_para.service_time if i in self.ins.graph.customer_list else 0

            lq_t = LinExpr()
            lq_t.addTerms([1, -1], [self.S[i], self.T[i]])
            self.sp_cons[con_name_time_1] = self.SP.addConstr(
                lq_t <= 0,
                name=con_name_time_1
            )

            for j in visit_list:
                arc_id = (i, j)
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        con_name = 'con_time_window-' + f'{i}' + '_' + f'{j}'
                        lhs = self.T[i] + self.ins.graph.second_echelon_graph.arc_dict[
                            arc_id].distance + service_time - self.S[j]
                        rhs = (1 - self.X[i, j]) * self.ins.model_para.big_m

                        self.sp_cons[con_name] = self.SP.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )
        self.SP.update()

    def build_rmp_and_sp(self):
        self.build_rmp_depot_select()
        self.build_sp_depot_select()