# -*- coding: utf-8 -*-
# @Time     : 2024-08-16-16:25
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from gurobipy import *
from copy import deepcopy
from Common import *
from collections import defaultdict


class GrbModelWithoutOD(object):

    def __init__(self,
                 ins,
                 od_list):
        """  """
        self.ins = deepcopy(ins)
        self.graph = self.ins.graph
        self.grb_params = self.ins.model_para
        self.od_list = od_list

        self.model = Model('gurobi_model')
        self.objs = {}

        """ first echelon """
        self.var_x = {}  # 路径
        self.w_s_k1 = {}  # capacity
        self.varzeta_s_k1 = {}  # arrive time
        self.tau_s_k1 = {}  # service start time

        self.travel_cost_1 = 0

        self.first_cons = {}  # {cons_1: {} }

        """ second echelon """
        self.var_y = {}
        self.zeta_c_s = {}
        self.w_c_k2 = {}
        self.varzeta_c_k2 = {}  # 数学模型需要修改 #########################################################
        self.tau_c_k2 = {}
        self.sate_demand = {}
        self.travel_cost_2 = 0

        self.second_cons = {}

        self.binding_cons = {}

        self.delete_od_arcs()

    def delete_od_arcs(self):

        for c in self.od_list:

            for key, value in list(self.ins.graph.arc_dict.items()):

                if c in key:
                    self.ins.graph.arc_dict[key].adj = 0

            for key, value in list(self.ins.graph.second_echelon_graph.arc_dict.items()):

                if c in key:
                    self.ins.graph.second_echelon_graph.arc_dict[key].adj = 0

            self.graph.customer_list.remove(c)

    def build_model(self):
        self.add_variables()
        self.set_objs()
        self.add_cons()

    def add_variables(self):
        self.add_first_variables()

        if self.ins.is_select is True:
            # 1st
            # self.add_first_variables_sate_select()
            # 2nd
            self.add_second_variables_sate_select()

        else:
            # 1st
            # self.add_first_variables_no_select()
            # 2nd
            self.add_second_variables_no_select()

    def set_objs(self):
        self.set_first_obj()
        self.set_second_obj()

        self.model.setObjective(self.objs[1] + self.objs[2] + self.objs[3], sense=GRB.MINIMIZE)
        # self.model.setObjective(self.objs[1] + self.objs[2], sense=GRB.MINIMIZE)
        # self.model.setObjective(self.objs[1], sense=GRB.MINIMIZE)

    def add_cons(self):
        self.add_binding_cons()

        if self.ins.is_select is True:
            # 1st
            self.add_first_cons_sate_select()
            # 2nd
            self.add_second_cons_sate_select()

        else:
            # 1st
            self.add_first_cons_no_select()
            # 2nd
            self.add_second_cons_no_select()

    def set_first_obj(self):
        """travel cost"""
        self.objs[1] = 0
        self.objs[3] = 0  # carbon cost

        """1st echelon"""
        # travel cost
        obj_1_1 = LinExpr()
        coe_1_1 = []
        vars_1_1 = []

        # carbon cost
        obj_3_1 = LinExpr()
        coe_3_1 = []

        for arc_id, arc in self.graph.first_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_1st):
                    from_id = arc_id[0]
                    to_id = arc_id[1]
                    # var_name = 'x_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                    # coe_1_1.append(arc.distance * 3)
                    coe_1_1.append(arc.distance)
                    vars_1_1.append(self.var_x[from_id, to_id, k])

                    coe_3_1.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)

        obj_1_1.addTerms(coe_1_1, vars_1_1)
        self.travel_cost_1 = obj_1_1
        self.objs[1] += obj_1_1

        obj_3_1.addTerms(coe_3_1, vars_1_1)
        self.objs[3] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_1 - self.grb_params.Q_q_1))

        """2nd echelon"""
        # travel cost
        obj_1_2 = LinExpr()
        coe_1_2 = []
        vars_1_2 = []

        # carbon cost
        obj_3_2 = LinExpr()
        coe_3_2 = []

        for arc_id, arc in self.graph.second_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_2nd):
                    from_id = arc_id[0]
                    to_id = arc_id[1]

                    # quantity
                    # var_name = 'y_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                    # coe_1_2.append(arc.distance * 2)
                    coe_1_2.append(arc.distance)
                    vars_1_2.append(self.var_y[from_id, to_id, k])

                    coe_3_2.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)

        obj_1_2.addTerms(coe_1_2, vars_1_2)
        self.travel_cost_2 = obj_1_2
        self.objs[1] += obj_1_2

        obj_3_2.addTerms(coe_3_2, vars_1_2)
        # self.objs[3] += (obj_3_2 - self.grb_params.Q_q_2)
        self.objs[3] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_2 - self.grb_params.Q_q_2))

    def set_second_obj(self):
        """ vehicle usage cost """
        self.objs[2] = 0

        """1st echelon"""
        lhs_1 = LinExpr()
        lhs_1_coe = []
        lhs_1_var = []
        for s in self.graph.sate_list:
            if judge_arc(arc_id=(0, s),
                         graph=self.graph.first_echelon_graph):
                for k in range(self.ins.vehicle_num_1st):
                    # var_x_name = 'x_' + str(0) + '_' + str(s) + '_' + str(k)
                    lhs_1_coe.append(self.grb_params.vehicle_1_cost)
                    lhs_1_var.append(self.var_x[0, s, k])
        lhs_1.addTerms(lhs_1_coe, lhs_1_var)
        self.objs[2] += lhs_1

        # 2nd
        lhs_2 = LinExpr()
        lhs_2_coe = []
        lhs_2_var = []
        for c in self.graph.customer_list:
            for s in self.graph.sate_list:
                for k in range(self.ins.vehicle_num_2nd):
                    if judge_arc(arc_id=(s, c),
                                 graph=self.graph.second_echelon_graph):
                        # var_y_name = 'y_' + str(s) + '_' + str(c) + '_' + str(k)
                        lhs_2_coe.append(self.grb_params.vehicle_2_cost)
                        lhs_2_var.append(self.var_y[s, c, k])
        lhs_2.addTerms(lhs_2_coe, lhs_2_var)
        self.objs[2] += lhs_2

    def add_binding_cons(self):
        """
        \varzeta_j^{k2} >= \tau_i^{k1} + c_{ij} + ServiveTime_i + M(2 - y_{ijk2} - \sum_{(hi)\in Arc1}x_{hik1} )
        :return:
        """
        for k2 in range(self.ins.vehicle_num_2nd):
            for j in self.graph.customer_list:

                for k1 in range(self.ins.vehicle_num_1st):
                    for i in self.graph.sate_list:
                        if judge_arc(arc_id=(i, j),
                                     graph=self.graph.second_echelon_graph):
                            # var_zeta_name1 = 'var_zeta_' + str(i) + '_' + str(k1) + '_k1'

                            lhs = LinExpr()
                            lhs_coe = []
                            lhs_var = []

                            for h in self.graph.first_echelon_list:
                                if judge_arc(arc_id=(h, i),
                                             graph=self.graph.first_echelon_graph):
                                    lhs_coe.append(1)
                                    lhs_var.append(self.var_x[h, i, k1])
                            lhs.addTerms(lhs_coe, lhs_var)

                            con_name = '1st_and_2nd-' + str(k2) + '_' + str(j) + '_' + str(k1) + '_' + str(i)
                            self.binding_cons[con_name] = self.model.addConstr(
                                self.varzeta_c_k2[j, k2] >= self.varzeta_s_k1[i, k1] +
                                self.graph.second_echelon_graph.arc_dict[
                                    (i, j)].distance + self.grb_params.p - self.grb_params.big_m * (
                                        2 - self.var_y[i, j, k2] - lhs),
                                name=con_name
                            )

    def add_first_variables(self):

        for i in self.graph.first_echelon_list:

            for j in self.graph.first_echelon_list:

                if judge_arc(arc_id=(i, j),
                             graph=self.graph.first_echelon_graph):
                    for k in range(self.ins.vehicle_num_1st):
                        # travel variables
                        var_name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                        self.var_x[i, j, k] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0.0, ub=1.0,
                            name=var_name,
                            column=None,
                            obj=0
                        )

            for k in range(self.ins.vehicle_num_1st):
                # quantity variables
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k1'
                self.w_s_k1[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=self.graph.vertex_dict[i].demand, ub=self.grb_params.vehicle_1_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                # arrive time
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k1'
                self.varzeta_s_k1[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                # service start time
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k1'
                self.tau_s_k1[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

    # ********************************************************************************************************
    #                                               No sate selection
    # ********************************************************************************************************
    # Variables

    def add_second_variables_no_select(self):
        for i in self.graph.second_echelon_list:
            for j in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        # travel
                        var_name = 'y_' + str(i) + '_' + str(j) + '_' + str(k)
                        self.var_y[i, j, k] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0.0, ub=1.0,
                            name=var_name,
                            column=None,
                            obj=0
                        )

            for k in range(self.ins.vehicle_num_2nd):
                # quantity
                demand = self.graph.vertex_dict[i].demand if i in self.graph.customer_list else 0
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k2'
                self.w_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=demand, ub=self.grb_params.vehicle_2_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                # arrive time
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                self.varzeta_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                # service start time
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                self.tau_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    # lb=0.0, ub=1440,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

    # Constraints

    def add_first_cons_no_select(self):

        # start and return
        for k in range(self.ins.vehicle_num_1st):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.graph.sate_list:
                if judge_arc(arc_id=(0, j),
                             graph=self.graph.first_echelon_graph):
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.var_x[0, j, k])

            lhs_start.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = '1st_con_start_' + str(k)
            self.first_cons[con_name_start] = self.model.addConstr(
                lhs_start <= 1,
                name=con_name_start
            )

            # return
            lhs_end = LinExpr()
            lhs_en_coe = []
            lhs_en_var = []

            for i in self.graph.sate_list:
                if judge_arc(arc_id=(i, self.graph.depot_list[-1]),
                             graph=self.graph.first_echelon_graph):
                    lhs_en_coe.append(1)
                    lhs_en_var.append(self.var_x[i, self.graph.depot_list[-1], k])

            lhs_end.addTerms(lhs_en_coe, lhs_en_var)
            con_name_end = '1st_con_return_' + str(k)
            self.first_cons[con_name_end] = self.model.addConstr(
                lhs_end <= 1,
                name=con_name_end
            )

            # start equ return
            con_name = '1st_con_start_equ_return-' + str(k)
            self.first_cons[con_name] = self.model.addConstr(
                lhs_start == lhs_end,
                name=con_name
            )

            # must start from depot
            # lhs_start_from_depot = LinExpr()
            # lhs_start_from_depot_coe = []
            # lhs_start_from_depot_var = []
            for i in self.graph.sate_list:
                for j in self.graph.sate_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        # lhs_start_from_depot_coe.append(1)
                        # lhs_start_from_depot_var.append(self.var_x[i, j, k])
                        con_name = '1st_con_must_start_from_depot-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.first_cons[con_name] = self.model.addConstr(
                            self.var_x[i, j, k] <= lhs_start,
                            name=con_name
                        )

            # lhs_start_from_depot.addTerms(lhs_start_from_depot_coe, lhs_start_from_depot_var)
            # con_name = '1st_con_must_start_from_depot-' + str(k)
            # self.first_cons[con_name] = self.model.addConstr(
            #     lhs_start_from_depot <= self.ins.sate_num * lhs_start,
            #     name=con_name
            # )

        # satellites must service
        for i in self.graph.sate_list:
            lhs_service = LinExpr()
            lhs_service_coe = []
            lhs_service_vars = []

            for k in range(self.ins.vehicle_num_1st):
                for j in self.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        lhs_service_coe.append(1)
                        lhs_service_vars.append(self.var_x[i, j, k])

            lhs_service.addTerms(lhs_service_coe, lhs_service_vars)
            con_name = '1st-con_sate_visit_' + str(i)
            self.first_cons[con_name] = self.model.addConstr(lhs_service == 1, name=con_name)

        # flow balance
        for sate in self.graph.sate_list:
            for k in range(self.ins.vehicle_num_1st):

                lhs_flow = LinExpr()
                lhs_flow_coe = []
                lhs_flow_var = []

                for i in self.graph.first_echelon_list:

                    # in
                    if judge_arc(arc_id=(i, sate),
                                 graph=self.graph.first_echelon_graph):
                        lhs_flow_coe.append(1)
                        lhs_flow_var.append(self.var_x[i, sate, k])

                    # out
                    if judge_arc(arc_id=(sate, i),
                                 graph=self.graph.first_echelon_graph):
                        lhs_flow_coe.append(-1)
                        lhs_flow_var.append(self.var_x[sate, i, k])

                lhs_flow.addTerms(lhs_flow_coe, lhs_flow_var)
                con_flow_balance_name = '1st_con_flow_balance-' + str(sate) + '_' + str(k)
                self.first_cons[con_flow_balance_name] = self.model.addConstr(lhs_flow == 0,
                                                                              name=con_flow_balance_name)

        # capacity
        for i in self.graph.first_echelon_list:
            for j in self.graph.first_echelon_list:
                if judge_arc(arc_id=(i, j),
                             graph=self.graph.first_echelon_graph):

                    for k in range(self.ins.vehicle_num_1st):

                        con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'

                        if con_name_capacity not in self.first_cons.keys():
                            self.first_cons[con_name_capacity] = self.model.addConstr(
                                self.w_s_k1[i, k] - self.w_s_k1[j, k] + (
                                        self.graph.vertex_dict[j].demand + self.grb_params.vehicle_1_capacity) *
                                self.var_x[i, j, k] <= self.grb_params.vehicle_1_capacity,
                                name=con_name_capacity
                            )

        # Time Window
        for k in range(self.ins.vehicle_num_1st):
            for i in self.graph.first_echelon_list:

                lq_ser_after_arr = LinExpr()
                lq_ser_after_arr_coe = [1, -1]
                lq_ser_after_arr_var = [self.varzeta_s_k1[i, k], self.tau_s_k1[i, k]]
                lq_ser_after_arr.addTerms(lq_ser_after_arr_coe, lq_ser_after_arr_var)

                con_ser_after_arr = '1st-ser_after_arr-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_ser_after_arr] = self.model.addConstr(
                    lq_ser_after_arr <= 0,
                    name=con_ser_after_arr
                )

                for j in self.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        con_name_time_window = '1st-time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_s_k1[i, k] + self.graph.arc_dict[i, j].distance + self.grb_params.t_unload - \
                              self.varzeta_s_k1[j, k]

                        rhs = self.grb_params.vehicle_1_capacity * (1 - self.var_x[i, j, k])

                        self.first_cons[con_name_time_window] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name_time_window
                        )

    def add_second_cons_no_select(self):
        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:
                # start
                lhs_start = LinExpr()
                lhs_start_coe = []
                lhs_start_var = []

                # return
                lhs_return = LinExpr()
                lhs_return_coe = []
                lhs_return_var = []

                sate_depot = self.graph.sate_to_depot[s]

                for j in self.graph.sate_serv_cus[s]:
                    if judge_arc(arc_id=(s, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_start_coe.append(1)
                        lhs_start_var.append(self.var_y[s, j, k])

                    if judge_arc(arc_id=(j, sate_depot),
                                 graph=self.graph.second_echelon_graph):
                        lhs_return_coe.append(1)
                        lhs_return_var.append(self.var_y[j, sate_depot, k])

                lhs_start.addTerms(lhs_start_coe, lhs_start_var)
                con_name_start = '2nd_con_start_' + str(s) + '_' + str(k)
                self.second_cons[con_name_start] = self.model.addConstr(
                    lhs_start <= 1,
                    name=con_name_start
                )

                lhs_return.addTerms(lhs_return_coe, lhs_return_var)
                con_start_equ_return = '2nd_con_start_equ_return-' + str(s) + '_' + str(k)
                self.second_cons[con_start_equ_return] = self.model.addConstr(
                    lhs_start == lhs_return,
                    name=con_start_equ_return
                )

                for i in self.graph.sate_serv_cus[s]:
                    for j in self.graph.sate_serv_cus[s]:
                        if judge_arc(arc_id=(i, j),
                                     graph=self.graph.second_echelon_graph):
                            con_lhs_must_start_from_sate = '2nd_con_must_start_from_sate-' + str(i) + '_' + str(
                                j) + '_' + str(k)
                            self.second_cons[con_lhs_must_start_from_sate] = self.model.addConstr(
                                self.var_y[i, j, k] <= lhs_start,
                                name=con_lhs_must_start_from_sate
                            )

        # 每个customer只能被访问一次
        for c in self.graph.customer_list:

            lhs_cus_service = LinExpr()
            lhs_cus_service_coe = []
            lhs_cus_service_var = []

            for i in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, c),
                             graph=self.graph.second_echelon_graph):

                    for k in range(self.ins.vehicle_num_2nd):
                        lhs_cus_service_coe.append(1)
                        lhs_cus_service_var.append(self.var_y[i, c, k])
            lhs_cus_service.addTerms(lhs_cus_service_coe, lhs_cus_service_var)

            con_cus_service = '2nd_customer_visit-' + str(c)
            self.second_cons[con_cus_service] = self.model.addConstr(
                lhs_cus_service == 1,
                name=con_cus_service
            )
            # self.second_cons[con_cus_service] = self.model.addConstr(
            #     lhs_cus_service == 1,
            #     name=con_cus_service
            # )

        # 每个车从只能服务一个sate
        for k in range(self.ins.vehicle_num_2nd):
            lhs_only_one_sate = LinExpr()
            lhs_only_one_sate_coe = []
            lhs_only_one_sate_var = []

            for s in self.graph.sate_list:
                for j in self.graph.sate_serv_cus[s]:
                    if judge_arc(arc_id=(s, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_only_one_sate_coe.append(1)
                        lhs_only_one_sate_var.append(self.var_y[s, j, k])
            lhs_only_one_sate.addTerms(lhs_only_one_sate_coe, lhs_only_one_sate_var)
            con_only_one_sate = '2nd_1service_sate_' + str(k)
            self.second_cons[con_only_one_sate] = self.model.addConstr(
                lhs_only_one_sate <= 1,
                name=con_only_one_sate
            )

        # flow balance
        for l in self.graph.customer_list:

            for k in range(self.ins.vehicle_num_2nd):
                lhs_flow = LinExpr()
                lhs_flow_coe = []
                lhs_flow_var = []

                # in
                visit_list_1 = self.graph.customer_list + [self.graph.cus_belong_sate[l]]
                for i in visit_list_1:
                    if judge_arc(arc_id=(i, l),
                                 graph=self.graph.second_echelon_graph):
                        lhs_flow_coe.append(1)
                        lhs_flow_var.append(self.var_y[i, l, k])

                # out
                visit_list_2 = self.graph.customer_list + [
                    self.graph.sate_to_depot[self.graph.cus_belong_sate[l]]]
                for j in visit_list_2:
                    if judge_arc(arc_id=(l, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_flow_coe.append(-1)
                        lhs_flow_var.append(self.var_y[l, j, k])

                lhs_flow.addTerms(lhs_flow_coe, lhs_flow_var)
                con_name = '2nd-flow_balance-' + str(l) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs_flow == 0,
                    name=con_name
                )

        # Capacity
        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):

                for j in self.graph.second_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs = self.w_c_k2[i, k] - self.w_c_k2[j, k] + (
                                self.graph.vertex_dict[j].demand + self.grb_params.vehicle_2_capacity) * \
                              self.var_y[i, j, k]

                        con_capacity = '2nd-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        self.second_cons[con_capacity] = self.model.addConstr(
                            lhs <= self.grb_params.vehicle_2_capacity,
                            name=con_capacity
                        )

        # Time Window
        for k in range(self.ins.vehicle_num_2nd):
            for i in self.graph.second_echelon_list:
                service_time = self.ins.model_para.service_time if i in self.ins.graph.customer_list else 0
                con_ser_after_arr = '2nd-con_ser_after_arr-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_ser_after_arr] = self.model.addConstr(
                    self.varzeta_c_k2[i, k] <= self.tau_c_k2[i, k],
                    name=con_ser_after_arr
                )

                for j in self.graph.second_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs = self.tau_c_k2[i, k] + service_time + self.graph.arc_dict[
                            i, j].distance - self.varzeta_c_k2[j, k]
                        rhs = (1 - self.var_y[i, j, k]) * self.grb_params.big_m

                        con_time_window = '2nd-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        self.second_cons[con_time_window] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_time_window
                        )

    # ********************************************************************************************************
    #                                                 Sate selection
    # ********************************************************************************************************
    # Variables
    def add_second_variables_sate_select(self):
        for i in self.graph.second_echelon_list:
            for j in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        # travel
                        var_name = 'y_' + str(i) + '_' + str(j) + '_' + str(k)
                        self.var_y[i, j, k] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0.0, ub=1.0,
                            name=var_name,
                            column=None,
                            obj=0
                        )

            for k in range(self.ins.vehicle_num_2nd):
                # quantity
                demand = self.graph.vertex_dict[i].demand if i in self.graph.customer_list else 0
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k2'
                self.w_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=demand, ub=self.grb_params.vehicle_2_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                # arrive time
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                self.varzeta_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                # service start time
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                self.tau_c_k2[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    # lb=0.0, ub=1440,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

        # 1 if customer served by satellite
        for c in self.graph.customer_list:
            for s in self.graph.sate_list:
                var_name = 'zeta_' + str(c) + '_' + str(s)
                self.zeta_c_s[c, s] = self.model.addVar(
                    vtype=GRB.BINARY,
                    lb=0.0, ub=1.0,
                    name=var_name,
                    column=None,
                    obj=0
                )

        vertex_list = self.graph.sate_list + self.graph.depot_list
        for i in vertex_list:
            var_d_name = 'D_' + str(i)
            self.sate_demand[i] = self.model.addVar(
                vtype=GRB.CONTINUOUS,
                lb=0.0, ub=self.grb_params.m_s,
                name=var_d_name,
                column=None,
                obj=0
            )

    # Constraints
    def add_first_cons_sate_select(self):
        """ """
        # start and return
        for k in range(self.ins.vehicle_num_1st):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.graph.sate_list:
                if judge_arc(arc_id=(0, j),
                             graph=self.graph.first_echelon_graph):
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.var_x[0, j, k])

            lhs_start.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = '1st_con_start_' + str(k)
            self.first_cons[con_name_start] = self.model.addConstr(
                lhs_start <= 1,
                name=con_name_start
            )

            # return
            lhs_end = LinExpr()
            lhs_en_coe = []
            lhs_en_var = []

            for i in self.graph.sate_list:
                if judge_arc(arc_id=(i, self.graph.depot_list[-1]),
                             graph=self.graph.first_echelon_graph):
                    lhs_en_coe.append(1)
                    lhs_en_var.append(self.var_x[i, self.graph.depot_list[-1], k])

            lhs_end.addTerms(lhs_en_coe, lhs_en_var)
            con_name_end = '1st_con_return_' + str(k)
            self.first_cons[con_name_end] = self.model.addConstr(
                lhs_end <= 1,
                name=con_name_end
            )

            # start equ return
            con_name = '1st_con_start_equ_return-' + str(k)
            self.first_cons[con_name] = self.model.addConstr(
                lhs_start == lhs_end,
                name=con_name
            )

            # must start from depot
            # lhs_start_from_depot = LinExpr()
            # lhs_start_from_depot_coe = []
            # lhs_start_from_depot_var = []
            for i in self.graph.sate_list:
                for j in self.graph.sate_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        # lhs_start_from_depot_coe.append(1)
                        # lhs_start_from_depot_var.append(self.var_x[i, j, k])
                        con_name = '1st_con_must_start_from_depot-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.first_cons[con_name] = self.model.addConstr(
                            self.var_x[i, j, k] <= lhs_start,
                            name=con_name
                        )

            # lhs_start_from_depot.addTerms(lhs_start_from_depot_coe, lhs_start_from_depot_var)
            # con_name = '1st_con_must_start_from_depot-' + str(k)
            # self.first_cons[con_name] = self.model.addConstr(
            #     lhs_start_from_depot <= self.ins.sate_num * lhs_start,
            #     name=con_name
            # )

        # satellites must service
        for i in self.graph.sate_list:
            lhs_service = LinExpr()
            lhs_service_coe = []
            lhs_service_vars = []

            for k in range(self.ins.vehicle_num_1st):
                for j in self.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        lhs_service_coe.append(1)
                        lhs_service_vars.append(self.var_x[i, j, k])

            lhs_service.addTerms(lhs_service_coe, lhs_service_vars)
            con_name = '1st-con_sate_visit_' + str(i)
            self.first_cons[con_name] = self.model.addConstr(lhs_service == 1, name=con_name)

        # flow balance
        for sate in self.graph.sate_list:
            for k in range(self.ins.vehicle_num_1st):

                lhs_flow = LinExpr()
                lhs_flow_coe = []
                lhs_flow_var = []

                for i in self.graph.first_echelon_list:

                    # in
                    if judge_arc(arc_id=(i, sate),
                                 graph=self.graph.first_echelon_graph):
                        lhs_flow_coe.append(1)
                        lhs_flow_var.append(self.var_x[i, sate, k])

                    # out
                    if judge_arc(arc_id=(sate, i),
                                 graph=self.graph.first_echelon_graph):
                        lhs_flow_coe.append(-1)
                        lhs_flow_var.append(self.var_x[sate, i, k])

                lhs_flow.addTerms(lhs_flow_coe, lhs_flow_var)
                con_flow_balance_name = '1st_con_flow_balance-' + str(sate) + '_' + str(k)
                self.first_cons[con_flow_balance_name] = self.model.addConstr(lhs_flow == 0,
                                                                              name=con_flow_balance_name)

        # Time Window
        for k in range(self.ins.vehicle_num_1st):
            for i in self.graph.first_echelon_list:

                lq_ser_after_arr = LinExpr()
                lq_ser_after_arr_coe = [1, -1]
                lq_ser_after_arr_var = [self.varzeta_s_k1[i, k], self.tau_s_k1[i, k]]
                lq_ser_after_arr.addTerms(lq_ser_after_arr_coe, lq_ser_after_arr_var)

                con_ser_after_arr = '1st-ser_after_arr-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_ser_after_arr] = self.model.addConstr(
                    lq_ser_after_arr <= 0,
                    name=con_ser_after_arr
                )

                for j in self.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.first_echelon_graph):
                        con_name_time_window = '1st-time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_s_k1[i, k] + self.graph.arc_dict[
                            i, j].distance + self.grb_params.t_unload - \
                              self.varzeta_s_k1[j, k]

                        rhs = self.grb_params.vehicle_1_capacity * (1 - self.var_x[i, j, k])

                        self.first_cons[con_name_time_window] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name_time_window
                        )

        # capacity
        for i in self.graph.first_echelon_list:
            for j in self.graph.first_echelon_list:
                if judge_arc(arc_id=(i, j),
                             graph=self.graph.first_echelon_graph):

                    for k in range(self.ins.vehicle_num_1st):
                        con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'

                        if con_name_capacity not in self.first_cons.keys():
                            self.first_cons[con_name_capacity] = self.model.addConstr(
                                self.w_s_k1[i, k] - self.w_s_k1[j, k] + (
                                        self.sate_demand[j] + self.grb_params.vehicle_1_capacity) *
                                self.var_x[i, j, k] <= self.grb_params.vehicle_1_capacity,
                                name=con_name_capacity
                            )

        for sate in self.graph.sate_list:
            demand = LinExpr()
            demand_coe = []
            demand_var = []

            for c in self.graph.customer_list:
                demand_coe.append(self.graph.vertex_dict[c].demand)
                demand_var.append(self.zeta_c_s[c, sate])
            demand.addTerms(demand_coe, demand_var)

            con_name = 'sate_demand-' + str(sate)
            self.first_cons[con_name] = self.model.addConstr(
                demand == self.sate_demand[sate],
                name=con_name
            )

    def add_second_cons_sate_select(self):
        # vehicle 每辆车只能从一个satellite as depot 出发
        for k in range(self.ins.vehicle_num_2nd):
            lhs_only_one_sate = LinExpr()
            lhs_only_one_sate_coe = []
            lhs_only_one_sate_var = []

            for s in self.graph.sate_list:
                for j in self.graph.customer_list:
                    if judge_arc(arc_id=(s, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_only_one_sate_coe.append(1)
                        lhs_only_one_sate_var.append(self.var_y[s, j, k])
            lhs_only_one_sate.addTerms(lhs_only_one_sate_coe, lhs_only_one_sate_var)
            con_only_one_sate = '2nd_service_sate_' + str(k)
            self.second_cons[con_only_one_sate] = self.model.addConstr(
                lhs_only_one_sate <= 1,
                name=con_only_one_sate
            )

        # 每个客户只能分配给一个sate
        for c in self.graph.customer_list:
            customer_assign = LinExpr()
            customer_assign_coe = []
            customer_assign_var = []

            for s in self.graph.sate_list:
                customer_assign_coe.append(1)
                customer_assign_var.append(self.zeta_c_s[c, s])
            customer_assign.addTerms(customer_assign_coe, customer_assign_var)

            con_customer_assign = '2nd-con_customer_assign-' + str(c)
            self.second_cons[con_customer_assign] = self.model.addConstr(
                customer_assign == 1,
                name=con_customer_assign
            )

        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        # 添加约束 sate 出发 和 返回 只能有 分配的 customer， var_y 和 zeta 的关系
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:
                # start
                lhs_start = LinExpr()
                lhs_start_coe = []
                lhs_start_var = []

                # return
                lhs_return = LinExpr()
                lhs_return_coe = []
                lhs_return_var = []

                sate_depot = self.graph.sate_to_depot[s]

                for j in self.graph.customer_list:
                    if judge_arc(arc_id=(s, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_start_coe.append(1)
                        lhs_start_var.append(self.var_y[s, j, k])

                    if judge_arc(arc_id=(j, sate_depot),
                                 graph=self.graph.second_echelon_graph):
                        lhs_return_coe.append(1)
                        lhs_return_var.append(self.var_y[j, sate_depot, k])

                lhs_start.addTerms(lhs_start_coe, lhs_start_var)
                con_name_start = '2nd_con_start-' + str(s) + '_' + str(k)
                self.second_cons[con_name_start] = self.model.addConstr(
                    lhs_start <= 1,
                    name=con_name_start
                )

                lhs_return.addTerms(lhs_return_coe, lhs_return_var)
                con_start_equ_return = '2nd_con_start_equ_return-' + str(s) + '_' + str(k)
                self.second_cons[con_start_equ_return] = self.model.addConstr(
                    lhs_start == lhs_return,
                    name=con_start_equ_return
                )

        # 车可以有多个 satellite 选择，与客户的分配相关
        for k in range(self.ins.vehicle_num_2nd):
            lhs_start_2 = LinExpr()
            lhs_start_2_coe = []
            lhs_start_2_var = []

            for s in self.graph.sate_list:
                for i in self.graph.customer_list:

                    if judge_arc(arc_id=(s, i),
                                 graph=self.graph.second_echelon_graph):
                        lhs_start_2_coe.append(1)
                        lhs_start_2_var.append(self.var_y[s, i, k])
            lhs_start_2.addTerms(lhs_start_2_coe, lhs_start_2_var)

            for i in self.graph.customer_list:
                for j in self.graph.customer_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        con_lhs_must_start_from_sate = '2nd_con_must_start_from_sate-' + str(i) + '_' + str(
                            j) + '_' + str(k)
                        self.second_cons[con_lhs_must_start_from_sate] = self.model.addConstr(
                            self.var_y[i, j, k] <= lhs_start_2,
                            name=con_lhs_must_start_from_sate
                        )

        # travel 限制，与分配联系起来
        for l in self.graph.customer_list:
            for m in self.graph.customer_list:

                if judge_arc(arc_id=(l, m),
                             graph=self.graph.second_echelon_graph):

                    for i in self.graph.sate_list:

                        lq_travel_assign = LinExpr()
                        lq_travel_assign_coe = []
                        lq_travel_assign_var = []

                        sate_list = deepcopy(self.graph.sate_list)
                        for s in sate_list:
                            if s != i:
                                lq_travel_assign_coe.append(1)
                                lq_travel_assign_var.append(self.zeta_c_s[m, s])
                        lq_travel_assign.addTerms(lq_travel_assign_coe, lq_travel_assign_var)

                        lq_travel_assign_vehicle = LinExpr()
                        lq_travel_assign_vehicle_coe = []
                        lq_travel_assign_vehicle_var = []
                        for k in range(self.ins.vehicle_num_2nd):
                            lq_travel_assign_vehicle_coe.append(1)
                            lq_travel_assign_vehicle_var.append(self.var_y[l, m, k])
                        lq_travel_assign_vehicle.addTerms(lq_travel_assign_vehicle_coe, lq_travel_assign_vehicle_var)

                        con_travel_assign = '2nd_con_travel_assign-' + str(l) + '_' + str(m)
                        self.second_cons[con_travel_assign] = self.model.addConstr(
                            lq_travel_assign_vehicle + self.zeta_c_s[l, i] + lq_travel_assign <= 2,
                            name=con_travel_assign
                        )

        # for sate in self.graph.sate_list:
        #     sate_depot = self.graph.sate_to_depot[sate]
        #
        #     for c in self.graph.customer_list:
        #         start_only_assign = LinExpr()
        #         start_only_assign_coe = []
        #         start_only_assign_var = []
        #         if judge_arc(arc_id=(sate, c),
        #                      graph=self.graph.second_echelon_graph):
        #             for k in range(self.ins.vehicle_num_2nd):
        #                 start_only_assign_coe.append(1)
        #                 start_only_assign_var.append(self.var_y[sate, c, k])
        #         start_only_assign.addTerms(start_only_assign_coe, start_only_assign_var)
        #
        #         con_start_only_assign = '2nd_con_start_only_assign-' + str(sate) + '_' + str(c)
        #         self.second_cons[con_start_only_assign] = self.model.addConstr(
        #             start_only_assign <= self.zeta_c_s[c, sate],
        #             name=con_start_only_assign
        #         )
        #
        #         return_only_assign = LinExpr()
        #         return_only_assign_coe = []
        #         return_only_assign_var = []
        #         if judge_arc(arc_id=(c, sate_depot),
        #                      graph=self.graph.second_echelon_graph):
        #             for k in range(self.ins.vehicle_num_2nd):
        #                 return_only_assign_coe.append(1)
        #                 return_only_assign_var.append(self.var_y[c, sate_depot, k])
        #         return_only_assign.addTerms(return_only_assign_coe, return_only_assign_var)
        #         con_return_only_assign = '2nd_con_return_only_assign-' + str(sate) + '_' + str(c)
        #         self.second_cons[con_return_only_assign] = self.model.addConstr(
        #             return_only_assign <= self.zeta_c_s[c, sate],
        #             name=con_return_only_assign
        #         )

        # 每个customer只能被访问一次
        for c in self.graph.customer_list:

            lhs_cus_service = LinExpr()
            lhs_cus_service_coe = []
            lhs_cus_service_var = []

            for i in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, c),
                             graph=self.graph.second_echelon_graph):

                    for k in range(self.ins.vehicle_num_2nd):
                        lhs_cus_service_coe.append(1)
                        lhs_cus_service_var.append(self.var_y[i, c, k])
            lhs_cus_service.addTerms(lhs_cus_service_coe, lhs_cus_service_var)

            con_cus_service = '2nd_customer_visit-' + str(c)
            self.second_cons[con_cus_service] = self.model.addConstr(
                lhs_cus_service  == 1,
                name=con_cus_service
            )
            # self.second_cons[con_cus_service] = self.model.addConstr(
            #     lhs_cus_service == 1,
            #     name=con_cus_service
            # )

        # flow balance
        for l in self.graph.customer_list:
            lhs_in = LinExpr()
            lhs_in_coe = []
            lhs_in_var = []

            lhs_out = LinExpr()
            lhs_out_coe = []
            lhs_out_var = []

            for k in range(self.ins.vehicle_num_2nd):
                lhs_flow = LinExpr()
                lhs_flow_coe = []
                lhs_flow_var = []

                # in
                visit_list_1 = self.graph.customer_list + self.graph.sate_list
                for i in visit_list_1:
                    if judge_arc(arc_id=(i, l),
                                 graph=self.graph.second_echelon_graph):
                        lhs_flow_coe.append(1)
                        lhs_flow_var.append(self.var_y[i, l, k])

                        lhs_in_coe.append(1)
                        lhs_in_var.append(self.var_y[i, l, k])

                # out
                visit_list_2 = self.graph.customer_list + self.graph.sate_depot_list
                for j in visit_list_2:
                    if judge_arc(arc_id=(l, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs_flow_coe.append(-1)
                        lhs_flow_var.append(self.var_y[l, j, k])

                        lhs_out_coe.append(1)
                        lhs_out_var.append(self.var_y[l, j, k])

                lhs_flow.addTerms(lhs_flow_coe, lhs_flow_var)
                con_name = '2nd-flow_balance-' + str(l) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs_flow == 0,
                    name=con_name
                )
            lhs_in.addTerms(lhs_in_coe, lhs_in_var)
            con_name_in = '2nd-only_one_in-' + str(l)
            self.second_cons[con_name_in] = self.model.addConstr(
                lhs_in <= 1,
                name=con_name_in
            )
            lhs_out.addTerms(lhs_out_coe, lhs_out_var)
            con_name_out = '2nd-only_one_out-' + str(l)
            self.second_cons[con_name_out] = self.model.addConstr(
                lhs_out <= 1,
                name=con_name_out
            )

            con_name_in_eq_out = '2nd-in_eq_out-' + str(l)
            self.second_cons[con_name_in_eq_out] = self.model.addConstr(
                lhs_in == lhs_out,
                name=con_name_in_eq_out
            )

        # Capacity
        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):

                for j in self.graph.second_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs = self.w_c_k2[i, k] - self.w_c_k2[j, k] + (
                                self.graph.vertex_dict[j].demand + self.grb_params.vehicle_2_capacity) * \
                              self.var_y[i, j, k]

                        con_capacity = '2nd-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        self.second_cons[con_capacity] = self.model.addConstr(
                            lhs <= self.grb_params.vehicle_2_capacity,
                            name=con_capacity
                        )

        # Time Window
        for k in range(self.ins.vehicle_num_2nd):
            for i in self.graph.second_echelon_list:

                service_time = self.ins.model_para.service_time if i in self.ins.graph.customer_list else 0

                con_ser_after_arr = '2nd-con_ser_after_arr-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_ser_after_arr] = self.model.addConstr(
                    self.varzeta_c_k2[i, k] <= self.tau_c_k2[i, k],
                    name=con_ser_after_arr
                )

                for j in self.graph.second_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs = self.tau_c_k2[i, k] + service_time + self.graph.arc_dict[
                            i, j].distance - self.varzeta_c_k2[j, k]
                        rhs = (1 - self.var_y[i, j, k]) * self.grb_params.big_m

                        con_time_window = '2nd-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        self.second_cons[con_time_window] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_time_window
                        )

    # ********************************************************************************************************
    #                                                 Print Function
    # ********************************************************************************************************

    def get_od_info(self):

        ods_route_vars = {od: list() for od in range(self.ins.od_num)}
        for var_key, var_ in self.var_z.items():
            if var_.x >= 0.5:
                ods_route_vars[var_key[-1]].append([var_key[0], var_key[1]])

        for od_id, route_vars in ods_route_vars.items():
            if len(route_vars) == 1:
                self.od_routes[od_id] = route_vars
                cur_dis = self.graph.arc_dict[route_vars[0][0], route_vars[0][1]].distance
                self.od_info[od_id] = [route_vars, cur_dis]

            else:
                cur_route, cur_dis = self.connect_segments(segments=route_vars)
                self.od_info[od_id] = [cur_route, cur_dis]

    def connect_segments(self, segments):
        # 使用字典存储每个起点对应的终点
        start_map = {seg[0]: seg[1] for seg in segments}
        # 寻找起始点（没有其他段以此为终点）
        all_starts = set(start_map.keys())
        all_ends = set(start_map.values())
        start_point = list(all_starts - all_ends)[0]
        # 初始化结果列表
        result = [start_point]
        # 按照连接顺序构建结果列表
        distance = 0

        while start_point in start_map:
            next_point = start_map[start_point]
            result.append(next_point)

            distance += calc_travel_time(x_1=self.graph.vertex_dict[start_point].x_coord,
                                         y_1=self.graph.vertex_dict[start_point].y_coord,
                                         x_2=self.graph.vertex_dict[next_point].x_coord,
                                         y_2=self.graph.vertex_dict[next_point].y_coord)

            start_point = next_point

        return result, distance

    def get_routes_arcs(self,
                        level):
        routes = defaultdict(list)

        if level == 1:
            start_word = 'x'
        else:
            start_word = 'y'

        for var in self.model.getVars():

            if var.x >= 0.5:
                if var.varName.startswith(start_word):
                    indices = var.varName.split('_')[1:]  # ['1', '7', '2']
                    # 转换为整数并解构
                    start, end, vehicle = map(int, indices)

                    # 判断是否有车辆记录
                    # if vehicle not in routes.keys():
                    routes[vehicle].append((start, end))

        return routes

    def get_route(self,
                  route_arcs,
                  level):
        cur_vertex = None
        depot_return = None

        # 首先确定出发点
        if level == 1:
            cur_vertex = 0
            depot_return = self.graph.depot_list[1]

        else:
            for arc in route_arcs:
                if arc[0] in self.graph.sate_list:
                    cur_vertex = arc[0]
                    depot_return = self.graph.sate_to_depot[cur_vertex]

        route = [cur_vertex]

        while cur_vertex != depot_return:
            for arc in route_arcs:
                if arc[0] == cur_vertex:
                    route.append(arc[1])
                    cur_vertex = arc[1]

        return route

    def print_result(self):

        # 1st
        routes_arc_1st = self.get_routes_arcs(level=1)
        routes_1st = defaultdict(list)

        for key_, arcs in routes_arc_1st.items():
            routes_1st[key_] = self.get_route(route_arcs=arcs,
                                              level=1)

        print(f'Gurobi Solution-1st routes: {routes_1st}')

        # 2nd
        routes_arc_2nd = self.get_routes_arcs(level=2)
        routes_2nd = defaultdict(list)

        for key_, arcs in routes_arc_2nd.items():
            routes_2nd[key_] = self.get_route(route_arcs=arcs,
                                              level=2)

        print(f'Gurobi Solution-2nd routes: {routes_2nd}')

        return routes_1st, routes_2nd