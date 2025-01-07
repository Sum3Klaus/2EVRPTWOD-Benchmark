# -*- coding: utf-8 -*-
# @Time     : 2024-07-18-17:00
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from gurobipy import *
from copy import deepcopy
from itertools import *
from Route import *


class ModelBuilder(object):

    def __init__(self,
                 alns):

        self.alns = alns

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

    def build_rmp(self):

        self.RMP = Model('RMP')
        self.RMP.setParam('OutputFlag', 0)

        """ for each customer, generate a feasible path """
        vehicle_lp = LinExpr()
        vehicle_coe = []
        vehicle_var = []

        for customer_id in self.ins.graph.customer_list:
            var_name = 'r_' + str(customer_id)
            # route  [depot 0, customer_id, depot customer_id + 1]
            self.routes[var_name] = [self.alns.target, customer_id, self.ins.graph.sate_to_depot[self.alns.target]]

            self.column_pool[var_name] = [self.alns.target, customer_id, self.ins.graph.sate_to_depot[self.alns.target]]
            self.column_pool_route[var_name] = self.gen_route(route_lst=self.column_pool[var_name])

            obj_coe = self.ins.graph.arc_dict[
                          self.alns.target, customer_id].distance * 2 + self.ins.model_para.vehicle_2_cost

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
        # self.RMP_duals['cons_' + str(self.alns.target)] = 0
        # self.RMP_duals['cons_' + str(self.ins.graph.sate_to_depot[self.alns.target])] = 0
        self.RMP_duals[str(self.alns.target)] = 0
        self.RMP_duals[str(self.ins.graph.sate_to_depot[self.alns.target])] = 0

    def build_rmp_sate(self):

        self.RMP = Model('RMP')
        self.RMP.setParam('OutputFlag', 0)

        """ for each customer, generate a feasible path """
        vehicle_lp = LinExpr()
        vehicle_coe = []
        vehicle_var = []
        for customer_id in self.ins.alns_dict[self.alns.target]:
            var_name = 'r_' + str(customer_id)
            # route  [depot 0, customer_id, depot customer_id + 1]
            self.routes[var_name] = [self.alns.target, customer_id, self.ins.graph.sate_to_depot[self.alns.target]]

            self.column_pool[var_name] = [self.alns.target, customer_id, self.ins.graph.sate_to_depot[self.alns.target]]
            self.column_pool_route[var_name] = self.gen_route(route_lst=self.column_pool[var_name])

            obj_coe = self.ins.graph.arc_dict[
                          self.alns.target, customer_id].distance * 2 + self.ins.model_para.vehicle_2_cost

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
        # self.RMP_duals['cons_' + str(self.alns.target)] = 0
        # self.RMP_duals['cons_' + str(self.ins.graph.sate_to_depot[self.alns.target])] = 0
        self.RMP_duals[str(self.alns.target)] = 0
        self.RMP_duals[str(self.ins.graph.sate_to_depot[self.alns.target])] = 0

    def gen_route(self,
                  route_lst):
        """ """
        new_route = Route()
        new_route.route.append(self.ins.graph.vertex_dict[self.alns.target])
        new_route.route_list.append(self.alns.target)
        new_route.set_start_time(ins=self.ins,
                                 sate=self.alns.target)

        for vertex_id in route_lst[1:]:
            service_time = self.ins.model_para.service_time if vertex_id in self.ins.graph.customer_list else 0
            new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[vertex_id],
                                            distance=self.ins.graph.arc_dict[
                                                new_route.route_list[-1], vertex_id].distance,
                                            service_time=service_time)

        return new_route

    def build_sp(self):
        """  """
        self.SP = Model('SP')
        sate_id = self.alns.target
        # self.RMP_duals = {i: 0 for i in self.ins.alns_dict[sate_id]}
        # self.RMP_duals[sate_id] = 0
        # self.RMP_duals[self.ins.graph.sate_to_depot[sate_id]] = 0

        """define the decision variables"""
        visit_list = deepcopy(self.ins.alns_dict[sate_id])
        visit_list.insert(0, sate_id)
        visit_list.append(self.ins.graph.sate_to_depot[sate_id])

        for i in visit_list:
            # arrive time
            var_name_s = 's_' + str(i)
            self.S[var_name_s] = self.SP.addVar(lb=self.ins.sate_arrive_time[sate_id],
                                                ub=self.ins.graph.vertex_dict[i].due_time, vtype=GRB.CONTINUOUS,
                                                name=var_name_s)

            # capacity
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            var_name_w = 'w_' + str(i)
            self.W[var_name_w] = self.SP.addVar(lb=demand, ub=self.ins.model_para.vehicle_2_capacity,
                                                vtype=GRB.CONTINUOUS,
                                                name=var_name_w)

            # service time
            var_name_t = 't_' + str(i)
            self.T[var_name_t] = self.SP.addVar(lb=self.ins.graph.vertex_dict[i].ready_time,
                                                ub=self.ins.graph.vertex_dict[i].due_time,
                                                vtype=GRB.CONTINUOUS,
                                                name=var_name_t)

            for j in visit_list:
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name_x = 'x_' + str(i) + '_' + str(j)
                        self.X[var_name_x] = self.SP.addVar(lb=0, ub=1,
                                                            vtype=GRB.BINARY,
                                                            name=var_name_x)
                        # obj = self.ins.graph.arc_dict[i, j].distance

        """set the objective functions"""
        obj_1 = LinExpr()
        for i in visit_list:
            for j in visit_list:
                if self.judge_arc(arc_id=(i, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    """
                    Pricing Sub problem
                    min
                    c_k - \sum a_{i, k} * dualVar_i - 1*dualVar_0
                    or max
                    \sum a_{i, k} * dualVar_i - 1*dualVar_0
                    """
                    cost = (self.ins.graph.arc_dict[
                                i, j].distance + self.ins.model_para.vehicle_2_cost) if i == sate_id else \
                        self.ins.graph.arc_dict[i, j].distance
                    # key = 'cons_' + str(i)
                    coe = cost - self.RMP_duals[str(i)]
                    var_name_x = 'x_' + str(i) + '_' + str(j)
                    obj_1.addTerms(coe, self.X[var_name_x])

        # start
        lhs_start = LinExpr()
        lhs_start_coe = []
        lhs_start_var = []

        for j in self.ins.alns_dict[sate_id]:
            if self.judge_arc(arc_id=(sate_id, j),
                              graph=self.ins.graph.second_echelon_graph):
                var_x_name = 'x_' + str(sate_id) + '_' + str(j)
                lhs_start_coe.append(1)
                lhs_start_var.append(self.X[var_x_name])
        lhs_start.addTerms(lhs_start_coe, lhs_start_var)
        con_name_start = 'start_' + str(sate_id)
        self.sp_cons[con_name_start] = self.SP.addConstr(
            lhs_start == 1,
            name=con_name_start
        )

        # 每个customer只能被访问一次
        for c in self.ins.alns_dict[sate_id]:
            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(c)
                    lhs_coe_1.append(1)
                    lhs_var_1.append(self.X[var_x_name])

            lhs_1.addTerms(lhs_coe_1, lhs_var_1)
            con_name = 'customer_visit-' + str(c)
            self.sp_cons[con_name_start] = self.SP.addConstr(
                lhs_1 <= 1,
                name=con_name
            )

        # flow balance
        for c in self.ins.alns_dict[sate_id]:
            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(c)
                    lhs_coe_2.append(1)
                    lhs_var_2.append(self.X[var_x_name])

            for j in visit_list:
                if self.judge_arc(arc_id=(c, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(c) + '_' + str(j)
                    lhs_coe_2.append(-1)
                    lhs_var_2.append(self.X[var_x_name])

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
            var_w = 'w_' + str(i)
            lq.addTerms([1], [self.W[var_w]])
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            self.sp_cons[capacity_1] = self.SP.addConstr(
                demand <= lq,
                name=capacity_1
            )

            for j in visit_list:
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name = 'x_' + f'{i}' + '_' + f'{j}'
                        capacity_2 = 'con_capacity-2_' + f'{i}' + '_' + f'{j}'
                        var_w_2 = 'w_' + str(j)

                        if capacity_2 not in self.sp_cons.keys():
                            self.sp_cons[capacity_2] = self.SP.addConstr(
                                self.W[var_w_2] - self.W[var_w] <= self.ins.graph.vertex_dict[
                                    j].demand + self.ins.model_para.vehicle_2_capacity * (1 - self.X[var_name]),
                                name=capacity_2
                            )

        # time windows
        for i in visit_list:
            var_arrive = 's_' + str(i)
            var_service = 't_' + str(i)
            con_name_time_1 = 'con_time_window-' + f'{i}'

            lq_t = LinExpr()
            lq_t.addTerms([1, -1], [self.S[var_arrive], self.T[var_service]])
            self.sp_cons[con_name_time_1] = self.SP.addConstr(
                lq_t <= 0,
                name=con_name_time_1
            )

            for j in visit_list:
                arc_id = (i, j)
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name = 'x_' + f'{i}' + '_' + f'{j}'
                        var_arrive_2 = 's_' + str(j)
                        con_name = 'con_time_window-' + f'{i}' + '_' + f'{j}'
                        lhs = self.T[var_service] + self.ins.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - self.S[var_arrive_2]
                        rhs = (1 - self.X[var_name]) * self.ins.model_para.big_m

                        self.sp_cons[con_name] = self.SP.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )
        self.SP.update()

    def build_sp_sate(self):
        """  """
        self.SP = Model('SP')
        sate_id = self.alns.target
        # self.RMP_duals = {i: 0 for i in self.ins.alns_dict[sate_id]}
        # self.RMP_duals[sate_id] = 0
        # self.RMP_duals[self.ins.graph.sate_to_depot[sate_id]] = 0

        """define the decision variables"""
        visit_list = deepcopy(self.ins.alns_dict[sate_id])
        visit_list.insert(0, sate_id)
        visit_list.append(self.ins.graph.sate_to_depot[sate_id])

        for i in visit_list:
            # arrive time
            var_name_s = 's_' + str(i)
            self.S[var_name_s] = self.SP.addVar(lb=self.ins.sate_arrive_time[sate_id],
                                                ub=self.ins.graph.vertex_dict[i].due_time, vtype=GRB.CONTINUOUS,
                                                name=var_name_s)

            # capacity
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            var_name_w = 'w_' + str(i)
            self.W[var_name_w] = self.SP.addVar(lb=demand, ub=self.ins.model_para.vehicle_2_capacity,
                                                vtype=GRB.CONTINUOUS,
                                                name=var_name_w)

            # service time
            var_name_t = 't_' + str(i)
            self.T[var_name_t] = self.SP.addVar(lb=self.ins.graph.vertex_dict[i].ready_time,
                                                ub=self.ins.graph.vertex_dict[i].due_time,
                                                vtype=GRB.CONTINUOUS,
                                                name=var_name_t)

            for j in visit_list:
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name_x = 'x_' + str(i) + '_' + str(j)
                        self.X[var_name_x] = self.SP.addVar(lb=0, ub=1,
                                                            vtype=GRB.BINARY,
                                                            name=var_name_x)
                        # obj = self.ins.graph.arc_dict[i, j].distance

        """set the objective functions"""
        obj_1 = LinExpr()
        for i in visit_list:
            for j in visit_list:
                if self.judge_arc(arc_id=(i, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    """
                    Pricing Sub problem
                    min
                    c_k - \sum a_{i, k} * dualVar_i - 1*dualVar_0
                    or max
                    \sum a_{i, k} * dualVar_i - 1*dualVar_0
                    """
                    cost = (self.ins.graph.arc_dict[
                                i, j].distance + self.ins.model_para.vehicle_2_cost) if i == sate_id else \
                        self.ins.graph.arc_dict[i, j].distance
                    # key = 'cons_' + str(i)
                    coe = cost - self.RMP_duals[str(i)]
                    var_name_x = 'x_' + str(i) + '_' + str(j)
                    obj_1.addTerms(coe, self.X[var_name_x])

        # start
        lhs_start = LinExpr()
        lhs_start_coe = []
        lhs_start_var = []

        for j in self.ins.alns_dict[sate_id]:
            if self.judge_arc(arc_id=(sate_id, j),
                              graph=self.ins.graph.second_echelon_graph):
                var_x_name = 'x_' + str(sate_id) + '_' + str(j)
                lhs_start_coe.append(1)
                lhs_start_var.append(self.X[var_x_name])
        lhs_start.addTerms(lhs_start_coe, lhs_start_var)
        con_name_start = 'start_' + str(sate_id)
        self.sp_cons[con_name_start] = self.SP.addConstr(
            lhs_start == 1,
            name=con_name_start
        )

        # 每个customer只能被访问一次
        for c in self.ins.alns_dict[sate_id]:
            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(c)
                    lhs_coe_1.append(1)
                    lhs_var_1.append(self.X[var_x_name])

            lhs_1.addTerms(lhs_coe_1, lhs_var_1)
            con_name = 'customer_visit-' + str(c)
            self.sp_cons[con_name_start] = self.SP.addConstr(
                lhs_1 <= 1,
                name=con_name
            )

        # flow balance
        for c in self.ins.alns_dict[sate_id]:
            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(c)
                    lhs_coe_2.append(1)
                    lhs_var_2.append(self.X[var_x_name])

            for j in visit_list:
                if self.judge_arc(arc_id=(c, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(c) + '_' + str(j)
                    lhs_coe_2.append(-1)
                    lhs_var_2.append(self.X[var_x_name])

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
            var_w = 'w_' + str(i)
            lq.addTerms([1], [self.W[var_w]])
            demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
            self.sp_cons[capacity_1] = self.SP.addConstr(
                demand <= lq,
                name=capacity_1
            )

            for j in visit_list:
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name = 'x_' + f'{i}' + '_' + f'{j}'
                        capacity_2 = 'con_capacity-2_' + f'{i}' + '_' + f'{j}'
                        var_w_2 = 'w_' + str(j)

                        if capacity_2 not in self.sp_cons.keys():
                            self.sp_cons[capacity_2] = self.SP.addConstr(
                                self.W[var_w_2] - self.W[var_w] <= self.ins.graph.vertex_dict[
                                    j].demand + self.ins.model_para.vehicle_2_capacity * (1 - self.X[var_name]),
                                name=capacity_2
                            )

        # time windows
        for i in visit_list:
            var_arrive = 's_' + str(i)
            var_service = 't_' + str(i)
            con_name_time_1 = 'con_time_window-' + f'{i}'

            lq_t = LinExpr()
            lq_t.addTerms([1, -1], [self.S[var_arrive], self.T[var_service]])
            self.sp_cons[con_name_time_1] = self.SP.addConstr(
                lq_t <= 0,
                name=con_name_time_1
            )

            for j in visit_list:
                arc_id = (i, j)
                if i != j:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.ins.graph.second_echelon_graph):
                        var_name = 'x_' + f'{i}' + '_' + f'{j}'
                        var_arrive_2 = 's_' + str(j)
                        con_name = 'con_time_window-' + f'{i}' + '_' + f'{j}'
                        lhs = self.T[var_service] + self.ins.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - self.S[var_arrive_2]
                        rhs = (1 - self.X[var_name]) * self.ins.model_para.big_m

                        self.sp_cons[con_name] = self.SP.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )
        self.SP.update()

    def build_rmp_and_sp(self):
        self.build_rmp_sate()
        self.build_sp()

    def build_vrp(self):
        """ """
        self.VRP = Model('VRP')
        self.VRP.setParam('OutputFlag', 0)
        vehicle_num = self.ins.vehicle_num_2nd
        sate_id = self.alns.target

        visit_list = deepcopy(self.ins.alns_dict[sate_id])
        visit_list.insert(0, sate_id)
        visit_list.append(self.ins.graph.sate_to_depot[sate_id])

        """create decision variables"""
        x_dict = dict()  # travel
        w_dict = dict()  # capacity
        s_dict = dict()  # arrive
        t_dict = dict()  # service

        for i in visit_list:
            for k in range(vehicle_num):
                # arrive time
                var_name_s = 's_' + str(i) + '_' + str(k)
                s_dict[var_name_s] = self.VRP.addVar(lb=self.ins.sate_arrive_time[sate_id],
                                                     ub=self.ins.graph.vertex_dict[i].due_time, vtype=GRB.CONTINUOUS,
                                                     name=var_name_s)

                # capacity
                demand = self.ins.graph.vertex_dict[i].demand if i in self.ins.graph.customer_list else 0
                var_name_w = 'w_' + str(i) + '_' + str(k)
                w_dict[var_name_w] = self.VRP.addVar(lb=demand, ub=self.ins.model_para.vehicle_2_capacity,
                                                     vtype=GRB.CONTINUOUS,
                                                     name=var_name_w)

                # service time
                var_name_t = 't_' + str(i) + '_' + str(k)
                t_dict[var_name_t] = self.VRP.addVar(lb=self.ins.graph.vertex_dict[i].ready_time,
                                                     ub=self.ins.graph.vertex_dict[i].due_time,
                                                     vtype=GRB.CONTINUOUS,
                                                     name=var_name_t)

                for j in visit_list:
                    if i != j:
                        if self.judge_arc(arc_id=(i, j),
                                          graph=self.ins.graph.second_echelon_graph):
                            var_name_x = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                            x_dict[var_name_x] = self.VRP.addVar(lb=0, ub=1,
                                                                 vtype=GRB.BINARY,
                                                                 name=var_name_x)
                            # obj = self.ins.graph.arc_dict[i, j].distance

        """ set obj """
        obj = 0
        obj_1 = LinExpr()
        coe_1 = []
        vars_1 = []

        for i in visit_list:
            for k in range(vehicle_num):
                for j in visit_list:
                    if i != j:
                        if self.judge_arc(arc_id=(i, j),
                                          graph=self.ins.graph.second_echelon_graph):
                            var_name_x = 'x_' + str(i) + '_' + str(j) + '_' + str(k)

                            coe_1.append(self.ins.graph.arc_dict[i, j].distance)
                            vars_1.append(x_dict[var_name_x])

        obj_1.addTerms(coe_1, vars_1)
        obj += obj_1

        obj_2 = LinExpr()
        lhs_2_coe = []
        lhs_2_var = []
        for c in self.ins.alns_dict[sate_id]:
            for k in range(vehicle_num):
                if self.judge_arc(arc_id=(sate_id, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(sate_id) + '_' + str(c) + '_' + str(k)
                    lhs_2_coe.append(self.ins.model_para.vehicle_2_cost)
                    lhs_2_var.append(x_dict[var_x_name])
        obj_2.addTerms(lhs_2_coe, lhs_2_var)
        obj += obj_2

        self.VRP.update()
        self.VRP.setObjective(obj, GRB.MINIMIZE)

        # start
        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        for k in range(vehicle_num):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.ins.alns_dict[sate_id]:
                if self.judge_arc(arc_id=(sate_id, j),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(sate_id) + '_' + str(j) + '_' + str(k)
                    lhs_start_coe.append(1)
                    lhs_start_var.append(x_dict[var_x_name])
            lhs_start.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = 'start_' + str(sate_id) + '_' + str(k)
            self.VRP.addConstr(lhs_start <= 1,
                               name=con_name_start
                               )

            # return
            lhs_return = LinExpr()
            lhs_return_coe = []
            lhs_return_var = []
            for i in self.ins.alns_dict[sate_id]:
                if self.judge_arc(arc_id=(i, self.ins.graph.sate_to_depot[sate_id]),
                                  graph=self.ins.graph.second_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(self.ins.graph.sate_to_depot[sate_id]) + '_' + str(k)
                    lhs_return_coe.append(1)
                    lhs_return_var.append(x_dict[var_x_name])
            lhs_return.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = 'return_' + str(self.ins.graph.sate_to_depot[sate_id]) + '_' + str(k)
            self.VRP.addConstr(lhs_return <= 1,
                               name=con_name_start
                               )

            con_name = 'start_and_return-' + str(k)
            self.VRP.addConstr(
                lhs_start == lhs_return,
                name=con_name
            )

        # 每个customer只能被访问一次
        for c in self.ins.alns_dict[sate_id]:

            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in visit_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.ins.graph.second_echelon_graph):
                    for k in range(vehicle_num):
                        var_x_name = 'x_' + str(i) + '_' + str(c) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(x_dict[var_x_name])
            lhs_2.addTerms(lhs_coe_2, lhs_var_2)

            con_name = 'customer_visit-' + str(c)
            self.VRP.addConstr(
                1 == lhs_2,
                name=con_name
            )

        # flow balance
        # 流平衡应该是对于每个车的
        for l in self.ins.alns_dict[sate_id]:

            for k in range(vehicle_num):
                lhs = LinExpr()
                lhs_coe = []
                lhs_var = []

                # in
                visit_list_1 = self.ins.alns_dict[sate_id] + [sate_id]
                for i in visit_list_1:
                    # if self.judge_arc(arc_id=(i, l),
                    #                   graph=self.graph.second_echelon_graph):
                    if i != l:
                        if self.ins.graph.second_echelon_graph.arc_dict[i, l].adj == 1:
                            var_x_name_1 = 'x_' + str(i) + '_' + str(l) + '_' + str(k)
                            lhs_coe.append(1)
                            lhs_var.append(x_dict[var_x_name_1])

                # out
                visit_list_2 = self.ins.alns_dict[sate_id] + [self.ins.graph.sate_to_depot[sate_id]]
                for j in visit_list_2:
                    # if self.judge_arc(arc_id=(l, j),
                    #                   graph=self.graph.second_echelon_graph):
                    if j != l:
                        if self.ins.graph.second_echelon_graph.arc_dict[l, j].adj == 1:
                            var_x_name_2 = 'x_' + str(l) + '_' + str(j) + '_' + str(k)
                            lhs_coe.append(-1)
                            lhs_var.append(x_dict[var_x_name_2])

                lhs.addTerms(lhs_coe, lhs_var)
                con_name = 'flow_balance-' + str(l) + '_' + str(k)
                self.VRP.addConstr(
                    lhs == 0,
                    name=con_name
                )

        # capacity
        # customers to satellites
        for i in visit_list:
            for k in range(vehicle_num):
                con_name_capacity_1 = 'capacity-1_' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                var_w_1 = 'w_' + str(i) + '_' + str(k)
                lq.addTerms([1], [w_dict[var_w_1]])
                self.VRP.addConstr(
                    self.ins.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )

                for j in visit_list:
                    arc_id = (i, j)
                    if arc_id in self.ins.graph.second_echelon_graph.arc_dict and \
                            self.ins.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        con_name = 'capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_w_2 = 'w_' + str(j) + '_' + str(k)

                        self.VRP.addConstr(
                            w_dict[var_w_2] - w_dict[var_w_1] <= self.ins.graph.vertex_dict[
                                j].demand + self.ins.model_para.vehicle_2_capacity * (1 - x_dict[var_name]),
                            name=con_name
                        )

        # time windows
        for k in range(vehicle_num):
            for i in visit_list:
                var_arrive_name = 's_' + str(i) + '_' + str(k)
                var_service_name = 't_' + str(i) + '_' + str(k)
                con_name_time_1 = 'time_window_1-' + f'{i}' + '_' + f'{k}'

                lq = LinExpr()
                lq.addTerms([1, -1], [s_dict[var_arrive_name], t_dict[var_service_name]])
                self.VRP.addConstr(
                    lq <= 0,
                    name=con_name_time_1
                )

                for j in visit_list:
                    arc_id = (i, j)
                    if arc_id in self.ins.graph.second_echelon_graph.arc_dict and \
                            self.ins.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_arrive_name_2 = 's_' + str(j) + '_' + str(k)
                        con_name = 'time_window_2-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = t_dict[var_service_name] + self.ins.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - s_dict[var_arrive_name_2]
                        rhs = (1 - x_dict[var_name]) * self.ins.model_para.big_m

                        self.VRP.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

        self.VRP.update()
