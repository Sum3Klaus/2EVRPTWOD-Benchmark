# -*- coding: utf-8 -*-
# @Time     : 2024-07-31-13:52
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from gurobipy import *
from Common import *
from Instance import *
from collections import defaultdict
from Solution import *


class GurobiModelBuilder(object):

    def __init__(self,
                 ins: Instance):

        self.ins = ins
        self.graph = ins.graph
        self.grb_params = ins.model_para

        # build GRB model
        self.model = Model('gurobi_model')

        # objectives
        self.objs = {
            '1st travel cost': 0,
            '1st carbon cost': 0,
            '1st vehicle cost': 0,
            '2nd travel cost': 0,
            '2nd carbon cost': 0,
            '2nd vehicle cost': 0,
            'od travel cost': 0,
            'od compensation cost': 0,
        }

        # travel cost
        # self.travel_cost_1 = 0
        # self.travel_cost_2 = 0
        # self.travel_cost_od = 0

        # fuel cost
        self.fuel_consumption = 0

        # sets
        # build ODs PDP model
        self.pd_task = {cus: [self.graph.cus_belong_sate[cus], cus] for cus in
                        self.ins.graph.customer_list}  # cus: [origin, destination]

        # occasional drivers 对于 od vehicle id
        self.od_lists = {
            k: [self.graph.od_o_list[k]] + [self.graph.od_d_list[k]] + self.graph.sate_list + self.graph.customer_list
            for k in range(len(self.graph.od_o_list))}

        self.od_list = self.graph.od_o_list + self.graph.od_d_list + self.graph.sate_list + self.graph.customer_list
        self.pdp_list = self.graph.sate_list + self.graph.customer_list

        """ first echelon """
        self.var_x = {}  # 路径
        self.w_s_k1 = {}  # capacity
        self.varzeta_s_k1 = {}  # arrive time
        self.tau_s_k1 = {}  # service start time

        self.first_cons = {}  # {cons_1: {} }

        """ second echelon """
        self.var_y = {}
        self.zeta_c_s = {}
        self.w_c_k2 = {}
        self.varzeta_c_k2 = {}  # 数学模型需要修改 #########################################################
        self.tau_c_k2 = {}
        self.sate_demand = {}

        self.second_cons = {}

        self.sate_demand = {}

        """ od """
        self.var_z = {}
        self.var_r = {}
        self.varzeta_c_k_od = {}
        self.tau_c_k_od = {}
        self.w_c_k_od = {}
        self.w_s_k_od = {}

        self.od_cons = {}

        self.od_travel_vars = {}
        self.od_routes = {}  # od id: []
        self.od_info = {}  # od_id: [route, cost]

        """ binding_cons """
        self.binding_cons = {}
        """ valid inequalities """
        self.valid_inequalities = {}
        self.valid_inequalities_1 = {}
        self.valid_inequalities_2 = {}
        self.valid_vars = {}

        """ set2-3 """
        self.initial_value = 1200.0
        """ set4 """
        # self.initial_value = 100000.0

    def build_model(self):
        self.add_variables()
        self.set_objs()
        self.add_cons()
        # self.add_valid_inequalities1()
        self.add_valid_inequalities2()
        self.add_valid_inequalities3()

    def add_variables(self):
        self.add_first_variables()

        if self.ins.is_select is True:
            # 1st
            # self.add_first_variables_sate_select()
            # 2nd
            self.add_second_variables_sate_select()
            # ODs
            self.add_od_variables_pdp()

        else:
            # 1st
            # self.add_first_variables_no_select()
            # 2nd
            self.add_second_variables_no_select()
            # ODs
            self.add_od_variables_pdp()

    def set_objs(self):
        self.set_first_obj()
        self.set_second_obj()

        self.model.setObjective(
            self.objs['1st travel cost'] + self.objs['1st carbon cost'] + self.objs['1st vehicle cost'] +
            self.objs['2nd travel cost'] + self.objs['2nd carbon cost'] + self.objs['2nd vehicle cost'] +
            self.objs['od travel cost'] + self.objs['od compensation cost'],
            sense=GRB.MINIMIZE
        )
        # self.model.setObjective(self.objs[1] + self.objs[2] + self.objs[3], sense=GRB.MINIMIZE)
        # self.model.setObjective(self.objs[1] + self.objs[2], sense=GRB.MINIMIZE)
        # self.model.setObjective(self.objs[1], sense=GRB.MINIMIZE)

    def add_cons(self):
        self.add_binding_cons()

        if self.ins.is_select is True:
            # 1st
            self.add_first_cons_sate_select()
            # 2nd
            self.add_second_cons_sate_select()
            # ODs
            self.add_od_cons_pdp_sate_select()

        else:
            # 1st
            self.add_first_cons_no_select()
            # 2nd
            self.add_second_cons_no_select()
            # ODs
            self.add_od_cons_pdp_no_select()

    def set_first_obj(self):
        """travel cost"""
        # self.objs[1] = 0
        # self.objs[3] = 0  # carbon cost

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

                    # coe_3_1.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)
                    coe_3_1.append(arc.distance * self.grb_params.rho_1 * self.grb_params.c_r)

        obj_1_1.addTerms(coe_1_1, vars_1_1)
        # self.travel_cost_1 = obj_1_1
        # self.objs[1] += obj_1_1
        self.objs['1st travel cost'] += obj_1_1

        obj_3_1.addTerms(coe_3_1, vars_1_1)
        # self.objs[3] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_1 - self.grb_params.Q_q_1))
        self.objs['1st carbon cost'] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_1 - self.grb_params.Q_q_1))

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

                    # coe_3_2.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)
                    coe_3_2.append(arc.distance * self.grb_params.rho_2 * self.grb_params.c_r)

        obj_1_2.addTerms(coe_1_2, vars_1_2)
        # self.travel_cost_2 = obj_1_2
        # self.objs[1] += obj_1_2
        self.objs['2nd travel cost'] += obj_1_2

        obj_3_2.addTerms(coe_3_2, vars_1_2)
        # self.objs[3] += (obj_3_2 - self.grb_params.Q_q_2)
        # self.objs[3] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_2 - self.grb_params.Q_q_2))
        self.objs['2nd carbon cost'] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_2 - self.grb_params.Q_q_2))

        """occasional driver"""
        # travel cost
        obj_1_3_1 = QuadExpr()  # order travel
        obj_1_3_2 = LinExpr()
        coe_1_3_1 = []
        coe_1_3_2 = []
        vars_1_3_1 = []
        vars_1_3_2 = []

        # carbon cost
        # obj_3_3 = LinExpr()
        # coe_3_3 = []

        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            for arc_id, arc in self.graph.pdp_graph.arc_dict.items():
                if arc.adj == 1:
                    if (arc_id[0] in self.graph.od_o_list and arc_id[0] != o) or (
                            arc_id[1] in self.graph.od_d_list and arc_id[1] != d):
                        pass
                    else:
                        from_id = arc_id[0]
                        to_id = arc_id[1]

                        # quantity
                        # var_name = 'z_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                        # coe_1_3_1.append(arc.distance)
                        coe_1_3_1.append(arc.distance * self.grb_params.c_c)
                        vars_1_3_1.append(self.var_z[from_id, to_id, k])

                        # coe_3_3.append(arc.distance * carbon_coe)

        obj_1_3_1.addTerms(coe_1_3_1, vars_1_3_1)
        # self.objs[1] += obj_1_3_1
        self.objs['od travel cost'] += obj_1_3_1

        # obj_3_3.addTerms(coe_3_3, vars_1_3_1)
        # self.objs[3] += obj_3_3

        # compensation cost
        for c in self.graph.customer_list:
            for k in range(len(self.graph.od_o_list)):
                # var_r_name = 'r_' + str(c) + '_' + str(k)

                coe_1_3_2.append(self.grb_params.compensation)
                vars_1_3_2.append(self.var_r[c, k])
        obj_1_3_2.addTerms(coe_1_3_2, vars_1_3_2)
        # self.objs[1] += obj_1_3_2
        self.objs['od compensation cost'] += obj_1_3_2
        # self.travel_cost_od = obj_1_3_1

    def set_second_obj(self):
        """ vehicle usage cost """
        # self.objs[2] = 0

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
        # self.objs[2] += lhs_1
        self.objs['1st vehicle cost'] += lhs_1

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
        # self.objs[2] += lhs_2
        self.objs['2nd vehicle cost'] += lhs_2

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
                            # self.binding_cons[con_name] = self.model.addConstr(
                            #     self.varzeta_c_k2[j, k2] >= self.varzeta_s_k1[i, k1] +
                            #     self.graph.second_echelon_graph.arc_dict[
                            #         (i, j)].distance + self.grb_params.p - self.grb_params.big_m * (
                            #             2 - self.var_y[i, j, k2] - lhs),
                            #     name=con_name
                            # )
                            self.binding_cons[con_name] = self.model.addConstr(
                                self.tau_c_k2[j, k2] >= self.tau_s_k1[i, k1] +
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
                    # lb=self.graph.vertex_dict[i].demand, ub=self.grb_params.vehicle_1_capacity,
                    lb=0, ub=self.grb_params.vehicle_1_capacity,
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

    def add_valid_inequalities1(self):
        """ 添加有效不等式 """

        # 1
        # The Two-Echelon Capacitated Vehicle Routing  Problem: Models and Math-Based Heuristics
        # 对应 eq 27
        valid_lq = LinExpr()
        valid_lq_coe = []
        valid_lq_var = []
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:
                for j in self.graph.customer_list:
                    if judge_arc(arc_id=(s, j),
                                 graph=self.graph.second_echelon_graph):
                        valid_lq_coe.append(1)
                        valid_lq_var.append(self.var_y[s, j, k])

        total_demand = sum([self.graph.vertex_dict[c].demand for c in self.graph.customer_list])
        valid_lq.addTerms(valid_lq_coe, valid_lq_var)
        self.valid_inequalities['valid inequalities 1'] = self.model.addConstr(
            valid_lq >= total_demand / self.grb_params.vehicle_2_capacity,
            name='valid inequalities-1'
        )
        self.model.update()

    def add_valid_inequalities2(self):
        """"""
        # 2
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

                        con_travel_assign = '2nd_con_travel_assign-' + str(l) + '_' + str(i) + '_' + str(m)
                        self.valid_inequalities_2[con_travel_assign] = self.model.addConstr(
                            lq_travel_assign_vehicle + self.zeta_c_s[l, i] + lq_travel_assign <= 2,
                            name=con_travel_assign
                        )
        self.model.update()

    def add_valid_inequalities3(self):
        """ """
        # 3
        var_chi = dict()
        valid_cons1 = dict()
        var_upsilon = dict()
        valid_cons2 = dict()
        var_eta = dict()
        valid_cons3 = dict()
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:

                start_lq = LinExpr()
                start_lq_coe = []
                start_lq_var = []

                for c in self.graph.customer_list:
                    if judge_arc(arc_id=(s, c),
                                 graph=self.graph.second_echelon_graph):
                        start_lq_coe.append(1)
                        start_lq_var.append(self.var_y[s, c, k])
                start_lq.addTerms(start_lq_coe, start_lq_var)

                var_chi[s, k] = self.model.addVar(name=f'chi_{s}_{k}')
                valid_cons1[s, k] = self.model.addConstr(
                    var_chi[s, k] == start_lq,
                    name=f'chi_{s}_{k}'
                )

                for i in self.graph.customer_list:
                    for j in self.graph.customer_list:
                        if judge_arc(arc_id=(i, j),
                                     graph=self.graph.second_echelon_graph) and judge_arc(arc_id=(j, i),
                                                                                          graph=self.graph.second_echelon_graph):
                            var_upsilon[i, j, k, s] = self.model.addVar(name=f'upsilon{i}_{j}_{k}_{s}')
                            valid_cons2[i, j, k, s] = self.model.addConstr(
                                var_upsilon[i, j, k, s] == self.var_y[i, j, k] + self.var_y[j, i, k],
                                name=f'upsilon{i}_{j}_{k}_{s}'
                            )

                            var_eta[i, j, k, s] = self.model.addVar(name=f'eta{i}_{j}_{k}_{s}')
                            valid_cons2[i, j, k, s, 1] = self.model.addConstr(
                                var_eta[i, j, k, s] <= var_chi[s, k],
                                name=f'eta-1-{i}_{j}_{k}_{s}'
                            )
                            valid_cons3[i, j, k, s, 2] = self.model.addConstr(
                                var_eta[i, j, k, s] <= var_upsilon[i, j, k, s],
                                name=f'eta-2-{i}_{j}_{k}_{s}'
                            )
                            valid_cons3[i, j, k, s, 3] = self.model.addConstr(
                                var_eta[i, j, k, s] >= var_chi[s, k] + var_upsilon[i, j, k, s] - 1,
                                name=f'eta-3-{i}_{j}_{k}_{s}'
                            )
                            valid_cons3[i, j, k, s, 4] = self.model.addConstr(
                                var_eta[i, j, k, s] <= self.zeta_c_s[i, s],
                                name=f'eta-4-{i}_{j}_{k}_{s}'
                            )
        self.model.update()

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

    def add_od_variables_pdp(self):

        for c in self.graph.customer_list:
            for k in range(len(self.graph.od_o_list)):
                # task assignment
                var_r_name = 'r_' + str(c) + '_' + str(k)
                self.var_r[c, k] = self.model.addVar(
                    vtype=GRB.BINARY,
                    lb=0.0, ub=1.0,
                    name=var_r_name,
                    column=None,
                    obj=0
                )
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            for arc_id, arc in self.graph.pdp_graph.arc_dict.items():
                if judge_arc(arc_id=arc_id,
                             graph=self.graph.pdp_graph):
                    if (arc_id[0] in self.graph.od_o_list and arc_id[0] != o) or (
                            arc_id[1] in self.graph.od_d_list and arc_id[1] != d):
                        pass

                    else:
                        # travel
                        from_id = arc_id[0]
                        to_id = arc_id[1]

                        var_name = 'z_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                        self.var_z[from_id, to_id, k] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0.0, ub=1.0,
                            name=var_name,
                            column=None,
                            obj=0
                        )

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [o, d]
            for i in visit_list:
                # arrive
                var_zeta_name = 'varzeta_' + str(i) + '_' + str(k)

                self.varzeta_c_k_od[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                # service
                var_tau_name = 'tau_' + str(i) + '_' + str(k)

                self.tau_c_k_od[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    # lb=self.graph.vertex_dict[i].ready_time, ub=1440,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

                # quantity
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k_od'

                self.w_c_k_od[i, k] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0, ub=self.grb_params.vehicle_od_capacity,
                    name=var_w_name,
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
                            # self.first_cons[con_name_capacity] = self.model.addConstr(
                            #     self.w_s_k1[i, k] - self.w_s_k1[j, k] + (
                            #             self.graph.vertex_dict[j].demand + self.grb_params.vehicle_1_capacity) *
                            #     self.var_x[i, j, k] <= self.grb_params.vehicle_1_capacity,
                            #     name=con_name_capacity
                            # )
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

            lhs_cus_assign_od = LinExpr()
            lhs_cus_assign_od_coe = []
            lhs_cus_assign_od_var = []

            for k_od in range(len(self.graph.od_o_list)):
                lhs_cus_assign_od_coe.append(1)
                lhs_cus_assign_od_var.append(self.var_r[c, k_od])
            lhs_cus_assign_od.addTerms(lhs_cus_assign_od_coe, lhs_cus_assign_od_var)

            for i in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, c),
                             graph=self.graph.second_echelon_graph):

                    for k in range(self.ins.vehicle_num_2nd):
                        lhs_cus_service_coe.append(1)
                        lhs_cus_service_var.append(self.var_y[i, c, k])
            lhs_cus_service.addTerms(lhs_cus_service_coe, lhs_cus_service_var)

            con_cus_service = '2nd_customer_visit-' + str(c)
            self.second_cons[con_cus_service] = self.model.addConstr(
                lhs_cus_service + lhs_cus_assign_od == 1,
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

        # vehicle max serve sate num con
        for sate in self.graph.sate_list:
            max_ser_lq = LinExpr()
            max_ser_lq_coe = []
            max_ser_lq_var = []

            for j in self.graph.second_echelon_list:
                if judge_arc(arc_id=(sate, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        max_ser_lq_coe.append(1)
                        max_ser_lq_var.append(self.var_y[sate, j, k])

            max_ser_lq.addTerms(max_ser_lq_coe, max_ser_lq_var)

            con_max_serve_name = '2nd-con_max_serve-' + f'{sate}'
            self.second_cons[con_max_serve_name] = self.model.addConstr(
                max_ser_lq <= self.ins.model_para.vehicle_max_ser_sate_num,
                name=con_max_serve_name
            )

    def add_od_cons_pdp_no_select(self):
        # 每个customer 都需要被访问
        for c in self.graph.customer_list:
            lq_assign = LinExpr()
            lq_assign_coe = []
            lq_assign_var = []

            for k in range(len(self.graph.od_o_list)):
                lq_assign_coe.append(1)
                lq_assign_var.append(self.var_r[c, k])

            lq_assign.addTerms(lq_assign_coe, lq_assign_var)
            con_assign = 'od-customer_assign-' + str(c)
            self.od_cons[con_assign] = self.model.addConstr(
                lq_assign <= 1,
                name=con_assign
            )

        # 每个车都应该由起始点出发（各自的origin），和回到destination
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            od_start = LinExpr()
            od_start_coe = []
            od_start_var = []

            # start
            # 出发只能去 pickup 或者 直接去 d
            visit_list_start = self.graph.pickup_id_list + self.graph.customer_list + [d]

            for j in visit_list_start:
                if judge_arc(arc_id=(o, j),
                             graph=self.graph.pdp_graph):
                    od_start_coe.append(1)
                    od_start_var.append(self.var_z[o, j, k])
            od_start.addTerms(od_start_coe, od_start_var)

            od_return = LinExpr()
            od_return_coe = []
            od_return_var = []

            # return
            # return只能去 delivery 或者 直接由 o
            visit_list_return = self.graph.pickup_id_list + self.graph.customer_list + [o]

            for i in visit_list_return:
                if judge_arc(arc_id=(i, d),
                             graph=self.graph.pdp_graph):
                    od_return_coe.append(1)
                    od_return_var.append(self.var_z[i, d, k])
            od_return.addTerms(od_return_coe, od_return_var)

            con_name_start = 'od-start-' + str(k)
            self.od_cons[con_name_start] = self.model.addConstr(
                od_start == 1,
                name=con_name_start
            )

            con_name_return = 'od-return-' + str(k)
            self.od_cons[con_name_return] = self.model.addConstr(
                od_return == 1,
                name=con_name_return
            )

        # 只有分配到任务的车辆才会访问客户点
        for c in self.graph.customer_list:
            p = self.graph.pdp_dict.inverse[c]  # pickup vertex
            d = c  # delivery vertex

            for k in range(len(self.graph.od_o_list)):

                lhs_assign_visit_1 = LinExpr()
                lhs_assign_visit_coe_1 = []
                lhs_assign_visit_var_1 = []

                visit_list = self.graph.pickup_id_list + self.graph.customer_list + [self.graph.od_o_list[k]]

                # pickup
                for l in visit_list:
                    if judge_arc(arc_id=(l, p),
                                 graph=self.graph.pdp_graph):
                        lhs_assign_visit_coe_1.append(1)
                        lhs_assign_visit_var_1.append(self.var_z[l, p, k])
                lhs_assign_visit_1.addTerms(lhs_assign_visit_coe_1, lhs_assign_visit_var_1)

                # delivery
                lhs_assign_visit_2 = LinExpr()
                lhs_assign_visit_coe_2 = []
                lhs_assign_visit_var_2 = []
                for i in visit_list:
                    if judge_arc(arc_id=(i, d),
                                 graph=self.graph.pdp_graph):
                        lhs_assign_visit_coe_2.append(1)
                        lhs_assign_visit_var_2.append(self.var_z[i, d, k])
                lhs_assign_visit_2.addTerms(lhs_assign_visit_coe_2, lhs_assign_visit_var_2)

                con_assign_visit_1 = 'od-assign_visit_1-' + str(c) + '_' + str(k)
                self.od_cons[con_assign_visit_1] = self.model.addConstr(
                    lhs_assign_visit_1 == lhs_assign_visit_2,
                    name=con_assign_visit_1
                )

                con_assign_visit_2 = 'od-assign_visit_2-' + str(c) + '_' + str(k)
                self.od_cons[con_assign_visit_2] = self.model.addConstr(
                    self.var_r[c, k] == lhs_assign_visit_2,
                    name=con_assign_visit_2
                )

        # flow balance
        # 对于每个p和d进去的等于流出的
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list

            for l in visit_list:
                flow_in = LinExpr()
                flow_in_coe = []
                flow_in_var = []

                flow_out = LinExpr()
                flow_out_coe = []
                flow_out_var = []

                set_v = self.graph.pickup_id_list + self.graph.customer_list + [o, d]

                # in
                for i in set_v:
                    if judge_arc(arc_id=(i, l),
                                 graph=self.graph.pdp_graph):
                        flow_in_coe.append(1)
                        flow_in_var.append(self.var_z[i, l, k])
                flow_in.addTerms(flow_in_coe, flow_in_var)

                # out
                for j in set_v:
                    if judge_arc(arc_id=(l, j),
                                 graph=self.graph.pdp_graph):
                        flow_out_coe.append(1)
                        flow_out_var.append(self.var_z[l, j, k])
                flow_out.addTerms(flow_out_coe, flow_out_var)

                con_flow_balance_in = 'od_flow_balance_in-' + str(l) + '_' + str(k)
                self.od_cons[con_flow_balance_in] = self.model.addConstr(
                    flow_in <= 1,
                    name=con_flow_balance_in
                )

                con_flow_balance = 'od_flow_balance-' + str(l) + '_' + str(k)
                self.od_cons[con_flow_balance] = self.model.addConstr(
                    flow_in == flow_out,
                    name=con_flow_balance
                )

        # capacity
        # note that, demand at sate + and customer -
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            for c in self.graph.customer_list:
                con_customer_capacity = 'od-customer_capacity-' + str(c) + '_' + str(k)

                lq = LinExpr()
                lq.addTerms([1], [self.var_r[c, k]])

                self.od_cons[con_customer_capacity] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_od_capacity / self.graph.vertex_dict[c].demand,
                    name=con_customer_capacity
                )

            con_capacity_start = 'od_capacity_start-' + str(k)
            self.od_cons[con_capacity_start] = self.model.addConstr(
                self.w_c_k_od[o, k] <= 0,
                name=con_capacity_start
            )

            visit_list = self.graph.customer_list + self.graph.pickup_id_list + [o, d]
            for i in visit_list:
                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):

                        if j in self.graph.pickup_id_list:
                            demand = self.graph.vertex_dict[j].demand
                        elif j in self.graph.customer_list:
                            demand = -self.graph.vertex_dict[j].demand
                        else:
                            demand = 0

                        lhs = self.w_c_k_od[i, k] - self.w_c_k_od[j, k] + self.var_z[i, j, k] * (
                                demand + self.grb_params.vehicle_od_capacity)
                        con_capacity_travel = 'od_capacity_travel-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.od_cons[con_capacity_travel] = self.model.addConstr(
                            lhs <= self.grb_params.vehicle_od_capacity,
                            name=con_capacity_travel
                        )

                if i in self.graph.pickup_id_list:
                    demand = self.graph.vertex_dict[i].demand
                elif i in self.graph.customer_list:
                    demand = -self.graph.vertex_dict[i].demand
                else:
                    demand = 0

                lq_pickup = LinExpr()
                lq_pickup_var = []
                lq_pickup_coe = []

                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):
                        lq_pickup_coe.append(1)
                        lq_pickup_var.append(self.var_z[i, j, k])
                lq_pickup.addTerms(lq_pickup_coe, lq_pickup_var)

                con_name_1 = 'od_capacity_lb-' + str(i) + '_' + str(k)
                self.od_cons[con_name_1] = self.model.addConstr(
                    demand * lq_pickup <= self.w_c_k_od[i, k],
                    name=con_name_1
                )

                con_name_2 = 'od_capacity_ub-' + str(i) + '_' + str(k)
                self.od_cons[con_name_2] = self.model.addConstr(
                    lq_pickup <= self.grb_params.vehicle_od_capacity,
                    name=con_name_2
                )

        # Time Window
        for k in range(len(self.graph.od_o_list)):
            origin = self.graph.od_o_list[k]
            destination = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [origin, destination]

            for i in visit_list:
                con_ser_after_arr = 'od_service_after_arrive-' + str(i) + '_' + str(k)
                self.od_cons[con_ser_after_arr] = self.model.addConstr(
                    self.varzeta_c_k_od[i, k] <= self.tau_c_k_od[i, k],
                    name=con_ser_after_arr
                )

            # 2.首先到达pickup，then delivery
            for i in self.graph.pickup_id_list:
                p = i
                d = self.graph.pdp_dict[i]

                con_delivery_after_pickup = 'od_delivery_after_pickup-' + str(p) + '_' + str(k)
                self.od_cons[con_delivery_after_pickup] = self.model.addConstr(
                    self.varzeta_c_k_od[p, k] <= self.varzeta_c_k_od[d, k],
                    name=con_delivery_after_pickup
                )

            # 3.连续性
            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [origin, destination]
            for i in visit_list:
                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):

                        if i in self.graph.customer_list:
                            service_time = self.grb_params.service_time
                        elif i in self.graph.pickup_id_list:
                            service_time = self.grb_params.p
                        else:
                            service_time = 0

                        lhs = LinExpr()
                        lhs.addTerms([1, -1, self.grb_params.big_m],
                                     [self.tau_c_k_od[i, k], self.varzeta_c_k_od[j, k], self.var_z[i, j, k]])

                        con_d_travel_p = 'od_d_travel_p-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.od_cons[con_d_travel_p] = self.model.addConstr(
                            lhs <= self.grb_params.big_m - self.graph.pdp_graph.arc_dict[
                                i, j].distance - service_time,
                            name=con_d_travel_p
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
            self.first_cons[con_name] = self.model.addConstr(lhs_service >= 1, name=con_name)

        for k in range(self.ins.vehicle_num_1st):
            lhs_first_vehicle_once = LinExpr()
            lhs_first_vehicle_once_coe = []
            lhs_first_vehicle_once_vars = []

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
        # for j in self.graph.first_echelon_list:
        # for j in self.graph.first_echelon_list:
        #     if judge_arc(arc_id=(i, j),
        #                  graph=self.graph.first_echelon_graph):
        #
        #         for k in range(self.ins.vehicle_num_1st):
        #             con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #
        #             if con_name_capacity not in self.first_cons.keys():
        #                 self.first_cons[con_name_capacity] = self.model.addConstr(
        #                     self.w_s_k1[i, k] - self.w_s_k1[j, k] + (
        #                             self.sate_demand[j] + self.grb_params.vehicle_1_capacity) *
        #                     self.var_x[i, j, k] <= self.grb_params.vehicle_1_capacity,
        #                     name=con_name_capacity
        #                 )

        for j in self.ins.graph.sate_list:
            for k in range(self.ins.vehicle_num_1st):
                # capacity_service_lq = QuadExpr()
                capacity_service_lq = LinExpr()
                capacity_service_lq_coe = []
                capacity_service_lq_var = []
                # capacity_service_lq_var2 = []

                for i in self.ins.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.ins.graph.first_echelon_graph):
                        capacity_service_lq_coe.append(1)
                        capacity_service_lq_var.append(self.var_x[i, j, k])
                        # capacity_service_lq_var2.append(self.sate_demand[j])

                # capacity_service_lq.addTerms(capacity_service_lq_coe,
                #                              capacity_service_lq_var1,
                #                              capacity_service_lq_var2)
                capacity_service_lq.addTerms(capacity_service_lq_coe, capacity_service_lq_var)

                con_name_capacity = '1st-3-con_capacity_service_-' + f'{j}' + '_' + f'{k}'
                self.first_cons[con_name_capacity] = self.model.addConstr(
                    capacity_service_lq * self.ins.model_para.vehicle_1_capacity >= self.w_s_k1[j, k],
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

        for i in self.ins.graph.sate_list:
            sate_service_lq = LinExpr()
            sate_service_coe = []
            sate_service_var = []

            con_name_capacity = '1st-3-con_capacity_sate-' + f'{i}'
            for k in range(self.ins.vehicle_num_1st):
                sate_service_coe.append(1)
                sate_service_var.append(self.w_s_k1[i, k])

            sate_service_lq.addTerms(sate_service_coe, sate_service_var)
            self.first_cons[con_name_capacity] = self.model.addConstr(
                sate_service_lq >= self.sate_demand[i],
                name=con_name_capacity
            )

        for k in range(self.ins.vehicle_num_1st):
            vehicle_service_lq = LinExpr()
            vehicle_service_coe = []
            vehicle_service_var = []

            con_name_capacity = '1st-3-con_capacity_vehicle-' + f'{k}'

            for i in self.ins.graph.sate_list:
                vehicle_service_coe.append(1)
                vehicle_service_var.append(self.w_s_k1[i, k])
            vehicle_service_lq.addTerms(vehicle_service_coe, vehicle_service_var)

            self.first_cons[con_name_capacity] = self.model.addConstr(
                vehicle_service_lq <= self.grb_params.vehicle_1_capacity,
                name=con_name_capacity
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
        # for l in self.graph.customer_list:
        #     for m in self.graph.customer_list:
        #
        #         if judge_arc(arc_id=(l, m),
        #                      graph=self.graph.second_echelon_graph):
        #
        #             for i in self.graph.sate_list:
        #
        #                 lq_travel_assign = LinExpr()
        #                 lq_travel_assign_coe = []
        #                 lq_travel_assign_var = []
        #
        #                 sate_list = deepcopy(self.graph.sate_list)
        #                 for s in sate_list:
        #                     if s != i:
        #                         lq_travel_assign_coe.append(1)
        #                         lq_travel_assign_var.append(self.zeta_c_s[m, s])
        #                 lq_travel_assign.addTerms(lq_travel_assign_coe, lq_travel_assign_var)
        #
        #                 lq_travel_assign_vehicle = LinExpr()
        #                 lq_travel_assign_vehicle_coe = []
        #                 lq_travel_assign_vehicle_var = []
        #                 for k in range(self.ins.vehicle_num_2nd):
        #                     lq_travel_assign_vehicle_coe.append(1)
        #                     lq_travel_assign_vehicle_var.append(self.var_y[l, m, k])
        #                 lq_travel_assign_vehicle.addTerms(lq_travel_assign_vehicle_coe, lq_travel_assign_vehicle_var)
        #
        #                 con_travel_assign = '2nd_con_travel_assign-' + str(l) + '_' + str(i) + '_' + str(m)
        #                 self.second_cons[con_travel_assign] = self.model.addConstr(
        #                     lq_travel_assign_vehicle + self.zeta_c_s[l, i] + lq_travel_assign <= 2,
        #                     name=con_travel_assign
        #                 )

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

            lhs_cus_assign_od = LinExpr()
            lhs_cus_assign_od_coe = []
            lhs_cus_assign_od_var = []

            for k_od in range(len(self.graph.od_o_list)):
                lhs_cus_assign_od_coe.append(1)
                lhs_cus_assign_od_var.append(self.var_r[c, k_od])
            lhs_cus_assign_od.addTerms(lhs_cus_assign_od_coe, lhs_cus_assign_od_var)

            for i in self.graph.second_echelon_list:

                if judge_arc(arc_id=(i, c),
                             graph=self.graph.second_echelon_graph):

                    for k in range(self.ins.vehicle_num_2nd):
                        lhs_cus_service_coe.append(1)
                        lhs_cus_service_var.append(self.var_y[i, c, k])
            lhs_cus_service.addTerms(lhs_cus_service_coe, lhs_cus_service_var)

            con_cus_service = '2nd_customer_visit-' + str(c)
            self.second_cons[con_cus_service] = self.model.addConstr(
                lhs_cus_service + lhs_cus_assign_od == 1,
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

        # vehicle max serve sate num con
        for sate in self.graph.sate_list:
            max_ser_lq = LinExpr()
            max_ser_lq_coe = []
            max_ser_lq_var = []

            for j in self.graph.second_echelon_list:
                if judge_arc(arc_id=(sate, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        max_ser_lq_coe.append(1)
                        max_ser_lq_var.append(self.var_y[sate, j, k])

            max_ser_lq.addTerms(max_ser_lq_coe, max_ser_lq_var)

            con_max_serve_name = '2nd-con_max_serve-' + f'{sate}'
            self.second_cons[con_max_serve_name] = self.model.addConstr(
                max_ser_lq <= self.ins.model_para.vehicle_max_ser_sate_num,
                name=con_max_serve_name
            )

    def add_od_cons_pdp_sate_select(self):
        # 每个customer 都需要被访问
        for c in self.graph.customer_list:
            lq_assign = LinExpr()
            lq_assign_coe = []
            lq_assign_var = []

            for k in range(len(self.graph.od_o_list)):
                lq_assign_coe.append(1)
                lq_assign_var.append(self.var_r[c, k])

            lq_assign.addTerms(lq_assign_coe, lq_assign_var)
            con_assign = 'od-customer_assign-' + str(c)
            self.od_cons[con_assign] = self.model.addConstr(
                lq_assign <= 1,
                name=con_assign
            )

        # 每个车都应该由起始点出发（各自的origin），和回到destination
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            od_start = LinExpr()
            od_start_coe = []
            od_start_var = []

            # start
            # 出发只能去 pickup 或者 直接去 d
            visit_list_start = self.graph.pickup_id_list + self.graph.customer_list + [d]

            for j in visit_list_start:
                if judge_arc(arc_id=(o, j),
                             graph=self.graph.pdp_graph):
                    od_start_coe.append(1)
                    od_start_var.append(self.var_z[o, j, k])
            od_start.addTerms(od_start_coe, od_start_var)

            od_return = LinExpr()
            od_return_coe = []
            od_return_var = []

            # return
            # return只能去 delivery 或者 直接由 o
            visit_list_return = self.graph.pickup_id_list + self.graph.customer_list + [o]

            for i in visit_list_return:
                if judge_arc(arc_id=(i, d),
                             graph=self.graph.pdp_graph):
                    od_return_coe.append(1)
                    od_return_var.append(self.var_z[i, d, k])
            od_return.addTerms(od_return_coe, od_return_var)

            con_name_start = 'od-start-' + str(k)
            self.od_cons[con_name_start] = self.model.addConstr(
                od_start == 1,
                name=con_name_start
            )

            con_name_return = 'od-return-' + str(k)
            self.od_cons[con_name_return] = self.model.addConstr(
                od_return == 1,
                name=con_name_return
            )

        # 只有分配到任务的车辆才会访问客户点
        # 每个 customer 都 sate_num 个取货点
        for c in self.graph.customer_list:
            p_list = self.graph.pdp_dict.inverse[c]  # pickup vertex
            d = c  # delivery vertex

            for k in range(len(self.graph.od_o_list)):
                o = self.graph.od_o_list[k]
                # d = self.graph.od_d_list[k]

                lhs_assign_visit_1 = LinExpr()
                lhs_assign_visit_coe_1 = []
                lhs_assign_visit_var_1 = []

                visit_list = self.graph.pickup_id_list + self.graph.customer_list + [self.graph.od_o_list[k]]

                # pickup
                for l in visit_list:
                    for p in p_list:
                        if judge_arc(arc_id=(l, p),
                                     graph=self.graph.pdp_graph):
                            lhs_assign_visit_coe_1.append(1)
                            lhs_assign_visit_var_1.append(self.var_z[l, p, k])

                lhs_assign_visit_1.addTerms(lhs_assign_visit_coe_1, lhs_assign_visit_var_1)

                # delivery
                lhs_assign_visit_2 = LinExpr()
                lhs_assign_visit_coe_2 = []
                lhs_assign_visit_var_2 = []

                for i in visit_list:
                    if judge_arc(arc_id=(i, d),
                                 graph=self.graph.pdp_graph):
                        lhs_assign_visit_coe_2.append(1)
                        lhs_assign_visit_var_2.append(self.var_z[i, d, k])
                lhs_assign_visit_2.addTerms(lhs_assign_visit_coe_2, lhs_assign_visit_var_2)

                con_assign_visit_1 = 'od-assign_visit_1-' + str(c) + '_' + str(k)
                self.od_cons[con_assign_visit_1] = self.model.addConstr(
                    lhs_assign_visit_1 == lhs_assign_visit_2,
                    name=con_assign_visit_1
                )

                con_assign_visit_2 = 'od-assign_visit_2-' + str(c) + '_' + str(k)
                self.od_cons[con_assign_visit_2] = self.model.addConstr(
                    self.var_r[c, k] == lhs_assign_visit_2,
                    name=con_assign_visit_2
                )

                # 只有一个取货点
                con_assign_visit_3 = 'od-assign_visit_3-' + str(c) + '_' + str(k)
                self.od_cons[con_assign_visit_3] = self.model.addConstr(
                    lhs_assign_visit_1 <= self.var_r[c, k],
                    name=con_assign_visit_3
                )

                visit_list_pickup = self.graph.pickup_id_list + self.graph.customer_list + [o]
                for p in p_list:
                    sate = self.graph.sate_list[p_list.index(p)]

                    lq_pickup = LinExpr()
                    lq_pickup_coe = []
                    lq_pickup_var = []

                    for i in visit_list_pickup:
                        if judge_arc(arc_id=(i, p),
                                     graph=self.graph.pdp_graph):
                            lq_pickup_coe.append(1)
                            lq_pickup_var.append(self.var_z[i, p, k])
                    lq_pickup.addTerms(lq_pickup_coe, lq_pickup_var)

                    con_assign_pick_sate = 'od-assign_assign_pick_sate-' + str(p) + '_' + str(k)
                    self.od_cons[con_assign_pick_sate] = self.model.addConstr(
                        lq_pickup == self.zeta_c_s[c, sate] * self.var_r[c, k],
                        name=con_assign_pick_sate
                    )

        # flow balance
        # 对于每个p和d进去的等于流出的
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list

            for l in visit_list:
                flow_in = LinExpr()
                flow_in_coe = []
                flow_in_var = []

                flow_out = LinExpr()
                flow_out_coe = []
                flow_out_var = []

                set_v = self.graph.pickup_id_list + self.graph.customer_list + [o, d]

                # in
                for i in set_v:
                    if judge_arc(arc_id=(i, l),
                                 graph=self.graph.pdp_graph):
                        flow_in_coe.append(1)
                        flow_in_var.append(self.var_z[i, l, k])
                flow_in.addTerms(flow_in_coe, flow_in_var)

                # out
                for j in set_v:
                    if judge_arc(arc_id=(l, j),
                                 graph=self.graph.pdp_graph):
                        flow_out_coe.append(1)
                        flow_out_var.append(self.var_z[l, j, k])
                flow_out.addTerms(flow_out_coe, flow_out_var)

                con_flow_balance_in = 'od_flow_balance_in-' + str(l) + '_' + str(k)
                self.od_cons[con_flow_balance_in] = self.model.addConstr(
                    flow_in <= 1,
                    name=con_flow_balance_in
                )

                con_flow_balance = 'od_flow_balance-' + str(l) + '_' + str(k)
                self.od_cons[con_flow_balance] = self.model.addConstr(
                    flow_in == flow_out,
                    name=con_flow_balance
                )

        # capacity
        # note that, demand at sate + and customer -
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            for c in self.graph.customer_list:
                con_customer_capacity = 'od-customer_capacity-' + str(c) + '_' + str(k)

                lq = LinExpr()
                lq.addTerms([1], [self.var_r[c, k]])

                self.od_cons[con_customer_capacity] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_od_capacity / self.graph.vertex_dict[c].demand,
                    name=con_customer_capacity
                )

            con_capacity_start = 'od_capacity_start-' + str(k)
            self.od_cons[con_capacity_start] = self.model.addConstr(
                self.w_c_k_od[o, k] <= 0,
                name=con_capacity_start
            )

            visit_list = self.graph.customer_list + self.graph.pickup_id_list + [o, d]
            for i in visit_list:
                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):

                        if j in self.graph.pickup_id_list:
                            demand = self.graph.vertex_dict[j].demand
                        elif j in self.graph.customer_list:
                            demand = -self.graph.vertex_dict[j].demand
                        else:
                            demand = 0

                        lhs = self.w_c_k_od[i, k] - self.w_c_k_od[j, k] + self.var_z[i, j, k] * (
                                demand + self.grb_params.vehicle_od_capacity)
                        con_capacity_travel = 'od_capacity_travel-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.od_cons[con_capacity_travel] = self.model.addConstr(
                            lhs <= self.grb_params.vehicle_od_capacity,
                            name=con_capacity_travel
                        )

                if i in self.graph.pickup_id_list:
                    demand = self.graph.vertex_dict[i].demand
                elif i in self.graph.customer_list:
                    demand = -self.graph.vertex_dict[i].demand
                else:
                    demand = 0

                lq_pickup = LinExpr()
                lq_pickup_var = []
                lq_pickup_coe = []

                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):
                        lq_pickup_coe.append(1)
                        lq_pickup_var.append(self.var_z[i, j, k])
                lq_pickup.addTerms(lq_pickup_coe, lq_pickup_var)

                con_name_1 = 'od_capacity_lb-' + str(i) + '_' + str(k)
                self.od_cons[con_name_1] = self.model.addConstr(
                    demand * lq_pickup <= self.w_c_k_od[i, k],
                    name=con_name_1
                )

                con_name_2 = 'od_capacity_ub-' + str(i) + '_' + str(k)
                self.od_cons[con_name_2] = self.model.addConstr(
                    lq_pickup <= self.grb_params.vehicle_od_capacity,
                    name=con_name_2
                )

        # Time Window
        for k in range(len(self.graph.od_o_list)):
            origin = self.graph.od_o_list[k]
            destination = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [origin, destination]

            for i in visit_list:
                con_ser_after_arr = 'od_service_after_arrive-' + str(i) + '_' + str(k)
                self.od_cons[con_ser_after_arr] = self.model.addConstr(
                    self.varzeta_c_k_od[i, k] <= self.tau_c_k_od[i, k],
                    name=con_ser_after_arr
                )

            # 2.首先到达pickup，then delivery
            for i in self.graph.pickup_id_list:
                p = i
                result = [pair for pair in self.graph.pdp_dict.keys() if p in pair]
                d = self.graph.pdp_dict[result[0]]

                con_delivery_after_pickup = 'od_delivery_after_pickup-' + str(p) + '_' + str(k)
                self.od_cons[con_delivery_after_pickup] = self.model.addConstr(
                    self.varzeta_c_k_od[p, k] <= self.varzeta_c_k_od[d, k],
                    name=con_delivery_after_pickup
                )

            # 3.连续性
            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [origin, destination]
            for i in visit_list:
                for j in visit_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.pdp_graph):

                        if i in self.graph.customer_list:
                            service_time = self.grb_params.service_time
                        elif i in self.graph.pickup_id_list:
                            service_time = self.grb_params.p
                        else:
                            service_time = 0

                        lhs = LinExpr()
                        lhs.addTerms([1, -1, self.grb_params.big_m],
                                     [self.tau_c_k_od[i, k], self.varzeta_c_k_od[j, k], self.var_z[i, j, k]])

                        con_d_travel_p = 'od_d_travel_p-' + str(i) + '_' + str(j) + '_' + str(k)
                        self.od_cons[con_d_travel_p] = self.model.addConstr(
                            lhs <= self.grb_params.big_m - self.graph.pdp_graph.arc_dict[
                                i, j].distance - service_time,
                            name=con_d_travel_p
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

        # ODs
        self.get_od_info()
        print(f'Gurobi Solution-od routes: {self.od_info}')

        self.print_cost()

        return routes_1st, routes_2nd

    def print_cost(self):
        for k, v in self.objs.items():
            print(k, '=', v.getValue())


class GrbFirstEchelon(object):

    def __init__(self,
                 ins,
                 sate_last_arrive_time,
                 sate_od_demand):
        """  """
        self.ins = ins
        self.para = ins.model_para
        self.sate_last_arrive_time = sate_last_arrive_time

        self.model = Model('First Echelon Model')
        self.grb_sol = Sol(ins=self.ins)

        self.objs = {
            '1st travel cost': 0,
            '1st vehicle cost': 0,
            '1st carbon cost': 0
        }
        # self.obj_1_1 = LinExpr()

        self.x = dict()  # 路径
        self.w_s = dict()  # capacity 车辆 为 sate 服务的需求量

        self.var_zeta_s = dict()  # arrive time
        self.tau_s = dict()  # service start time

        self.cons = dict()

        self.travel_x = {i: [] for i in range(self.ins.vehicle_num_1st)}
        self.routes = [[] * i for i in range(self.ins.vehicle_num_1st)]
        self.sate_od_demand = sate_od_demand

        """ set2-3 """
        self.initial_value = 1200.0
        """ set4 """
        # self.initial_value = 100000.0

    def build_grb_model(self):

        self.add_variables()
        self.add_cons()
        self.set_obj()

    def add_variables(self):
        """  """

        for arc_id, arc in self.ins.graph.first_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_1st):
                    from_id = arc_id[0]
                    to_id = arc_id[1]

                    # quantity
                    var_name = 'x_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                    self.x[(from_id, to_id, k)] = self.model.addVar(
                        vtype=GRB.BINARY,
                        lb=0.0, ub=1.0,
                        name=var_name,
                        column=None,
                        obj=0
                    )

        for i in self.ins.graph.first_echelon_list:
            for k in range(self.ins.vehicle_num_1st):
                """quantity"""
                var_w_name = 'w_' + str(i) + '_' + str(k)
                self.w_s[(i, k)] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.ins.model_para.vehicle_1_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                # arrive time
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k)
                self.var_zeta_s[(i, k)] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.ins.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                # service start time
                var_tau_name = 'tau_' + str(i) + '_' + str(k)
                self.tau_s[(i, k)] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.ins.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

    def add_cons(self):
        """  """
        # start and return
        for k in range(self.ins.vehicle_num_1st):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.ins.graph.sate_list:
                if judge_arc(arc_id=(0, j),
                             graph=self.ins.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(0) + '_' + str(j) + '_' + str(k)
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.x[(0, j, k)])
            lhs_start.addTerms(lhs_start_coe, lhs_start_var)
            con_name_start = '1st_con_start_' + str(k)
            self.cons[con_name_start] = self.model.addConstr(
                lhs_start <= 1,
                # lhs_start <= self.ins.vehicle_num_1st,
                name=con_name_start
            )
            # return
            lhs_end = LinExpr()
            lhs_en_coe = []
            lhs_en_var = []

            for i in self.ins.graph.sate_list:
                if judge_arc(arc_id=(i, self.ins.graph.depot_list[-1]),
                             graph=self.ins.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(self.ins.graph.depot_list[-1]) + '_' + str(k)
                    lhs_en_coe.append(1)
                    lhs_en_var.append(self.x[(i, self.ins.graph.depot_list[-1], k)])
            lhs_end.addTerms(lhs_en_coe, lhs_en_var)
            con_name_end = '1st_con_return_' + str(k)
            self.cons[con_name_end] = self.model.addConstr(
                lhs_end <= 1,
                # lhs_end <= self.ins.vehicle_num_1st,
                name=con_name_end
            )
            # start equ return
            con_name = '1st_con_start_equ_return-' + str(k)
            self.cons[con_name] = self.model.addConstr(
                lhs_start == lhs_end,
                name=con_name
            )
        # flow balance
        for l in self.ins.graph.sate_list:

            for k in range(self.ins.vehicle_num_1st):

                lhs = LinExpr()
                lhs_coe = []
                lhs_vars = []
                for j in self.ins.graph.first_echelon_list:
                    arc_id_1 = (j, l)
                    if judge_arc(arc_id=arc_id_1, graph=self.ins.graph.first_echelon_graph):
                        var_x_name_1 = 'x_' + str(j) + '_' + str(l) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.x[(j, l, k)])

                    arc_id_2 = (l, j)
                    if judge_arc(arc_id=arc_id_2, graph=self.ins.graph.first_echelon_graph):
                        var_x_name_2 = 'x_' + str(l) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(-1)
                        lhs_vars.append(self.x[(l, j, k)])

                lhs.addTerms(lhs_coe, lhs_vars)
                con_flow_balance_name = '1st_con_flow_balance-' + str(l) + '_' + str(k)
                self.cons[con_flow_balance_name] = self.model.addConstr(lhs <= 0, name=con_flow_balance_name)

        # must visit
        # first_visit_list = self._map.satellite_id_list
        # first_visit_list.append(self._map.vertex_sum)
        for i in self.ins.graph.sate_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_vars = []

            for k in range(self.ins.vehicle_num_1st):
                for j in self.ins.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.ins.graph.first_echelon_graph):
                        var_x_name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.x[(i, j, k)])

            lhs.addTerms(lhs_coe, lhs_vars)
            con_name = '1st-con_sate_visit_' + str(i)
            self.cons[con_name] = self.model.addConstr(
                lhs >= 0,
                name=con_name
            )

        # Capacity
        # for i in self.ins.graph.first_echelon_list:
        #     for k in range(self.ins.vehicle_num_1st):
        #         # con_name_capacity_1 = '1st-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
        #         var_w_1 = 'w_' + str(i) + '_' + str(k)
        #
        #         for j in self.ins.graph.first_echelon_list:
        #             if judge_arc(arc_id=(i, j),
        #                          graph=self.ins.graph.first_echelon_graph):
        #                 var_w_2 = 'w_' + str(j) + '_' + str(k)
        #                 var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #                 con_name = '1st-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #
        #                 self.cons[con_name] = self.model.addConstr(
        #                     self.w_s[(j, k)] - self.w_s[(i, k)] <= self.ins.graph.vertex_dict[
        #                         j].demand + self.ins.model_para.vehicle_1_capacity * (1 - self.x[(i, j, k)]),
        #                     name=con_name
        #                 )

        # Time Window
        # for k in range(self.ins.vehicle_num_1st):
        #     for i in self.ins.graph.first_echelon_list:
        #
        #         lq_ser_after_arr = LinExpr()
        #         lq_ser_after_arr_coe = [1, -1]
        #         lq_ser_after_arr_var = [self.var_zeta_s[i, k], self.tau_s[i, k]]
        #         lq_ser_after_arr.addTerms(lq_ser_after_arr_coe, lq_ser_after_arr_var)
        #
        #         con_ser_after_arr = '1st-ser_after_arr-' + f'{i}' + '_' + f'{k}'
        #         self.cons[con_ser_after_arr] = self.model.addConstr(
        #             lq_ser_after_arr <= 0,
        #             name=con_ser_after_arr
        #         )
        #
        #         for j in self.ins.graph.first_echelon_list:
        #             if judge_arc(arc_id=(i, j),
        #                          graph=self.ins.graph.first_echelon_graph):
        #                 con_name_time_window = '1st-time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #                 lhs = self.tau_s[i, k] + self.ins.graph.arc_dict[
        #                     i, j].distance + self.ins.model_para.t_unload - \
        #                       self.var_zeta_s[j, k]
        #
        #                 rhs = self.ins.model_para.vehicle_1_capacity * (1 - self.x[i, j, k])
        #
        #                 self.cons[con_name_time_window] = self.model.addConstr(
        #                     lhs <= rhs,
        #                     name=con_name_time_window
        #                 )

        # capacity
        # for j in self.ins.graph.first_echelon_list:
        # for j in self.ins.graph.first_echelon_list:
        #     if judge_arc(arc_id=(i, j),
        #                  graph=self.ins.graph.first_echelon_graph):
        #
        #         for k in range(self.ins.vehicle_num_1st):
        #             con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #
        #             self.cons[con_name_capacity] = self.model.addConstr(
        #                 self.w_s[i, k] - self.w_s[j, k] + (
        #                         self.ins.graph.vertex_dict[j].demand + self.ins.model_para.vehicle_1_capacity) *
        #                 self.x[i, j, k] <= self.ins.model_para.vehicle_1_capacity,
        #                 name=con_name_capacity
        #             )

        # for j in self.ins.graph.sate_list:
        #     for k in range(self.ins.vehicle_num_1st):
        #         capacity_service_lq = LinExpr()
        #         capacity_service_lq_coe = []
        #         capacity_service_lq_var = []
        #         # capacity_service_lq_var2 = []
        #
        #         for i in self.ins.graph.first_echelon_list:
        #             if judge_arc(arc_id=(i, j),
        #                          graph=self.ins.graph.first_echelon_graph):
        #                 capacity_service_lq_coe.append(1)
        #                 capacity_service_lq_var.append(self.x[i, j, k])
        #
        #         capacity_service_lq.addTerms(capacity_service_lq_coe,
        #                                      capacity_service_lq_var)
        #         con_name_capacity = '1st-3-con_capacity_service_-' + f'{j}' + '_' + f'{k}'
        #         self.cons[con_name_capacity] = self.model.addConstr(
        #             capacity_service_lq * self.ins.model_para.vehicle_1_capacity >= self.w_s[j, k],
        #             name=con_name_capacity
        #         )
        visit_list = self.ins.graph.sate_list + [self.ins.graph.depot_list[-1]]
        for i in self.ins.graph.sate_list:

            for k in range(self.ins.vehicle_num_1st):
                capacity_service_lq = LinExpr()
                capacity_service_lq_coe = []
                capacity_service_lq_var = []

                for j in visit_list:
                    if i != j:
                        capacity_service_lq_coe.append(1)
                        capacity_service_lq_var.append(self.x[i, j, k])

                capacity_service_lq.addTerms(capacity_service_lq_coe, capacity_service_lq_var)
                con_name_capacity = '1st-3-con_capacity_service_-' + f'{i}' + '_' + f'{k}'
                self.cons[con_name_capacity] = self.model.addConstr(
                    capacity_service_lq * self.ins.graph.vertex_dict[i].demand >= self.w_s[i, k],
                    name=con_name_capacity
                )

        for i in self.ins.graph.sate_list:
            sate_service_lq = LinExpr()
            sate_service_coe = []
            sate_service_var = []

            con_name_capacity = '1st-3-con_capacity_sate-' + f'{i}'
            for k in range(self.ins.vehicle_num_1st):
                sate_service_coe.append(1)
                sate_service_var.append(self.w_s[i, k])

            sate_service_lq.addTerms(sate_service_coe, sate_service_var)
            self.cons[con_name_capacity] = self.model.addConstr(
                sate_service_lq >= self.ins.graph.vertex_dict[i].demand,
                name=con_name_capacity
            )

        for k in range(self.ins.vehicle_num_1st):
            vehicle_service_lq = LinExpr()
            vehicle_service_coe = []
            vehicle_service_var = []

            con_name_capacity = '1st-3-con_capacity_vehicle-' + f'{k}'

            for i in self.ins.graph.sate_list:
                vehicle_service_coe.append(1)
                vehicle_service_var.append(self.w_s[i, k])
            vehicle_service_lq.addTerms(vehicle_service_coe, vehicle_service_var)

            self.cons[con_name_capacity] = self.model.addConstr(
                vehicle_service_lq <= self.para.vehicle_1_capacity,
                name=con_name_capacity
            )

        """
        2024.10.03
        vertex.demand 应该 修改
        """

        # time windows
        for k in range(self.ins.vehicle_num_1st):
            for i in self.ins.graph.first_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k)
                var_tau_name = 'tau_' + str(i) + '_' + str(k)
                con_name_time_1 = '1st-4-con_time_window_0-' + f'{i}' + '_' + f'{k}'

                self.cons[con_name_time_1] = self.model.addConstr(
                    self.var_zeta_s[(i, k)] <= self.tau_s[(i, k)],
                    # + unload time
                    name=con_name_time_1
                )

                con_name_time_2 = '1st-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.cons[con_name_time_2] = self.model.addConstr(
                    self.ins.graph.vertex_dict[i].ready_time <= self.tau_s[(i, k)],
                    name=con_name_time_2
                )

                con_name_time_3 = '1st-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.cons[con_name_time_3] = self.model.addConstr(
                    # self.tau_s[(i, k)] <= self.ins.graph.vertex_dict[i].due_time,
                    self.tau_s[(i, k)] <= self.sate_last_arrive_time[i],
                    name=con_name_time_3
                )

                for j in self.ins.graph.first_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.ins.graph.first_echelon_graph.arc_dict and \
                            self.ins.graph.first_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k)
                        con_name = '1st-4-con_time_window_3-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_s[(i, k)] + self.ins.graph.first_echelon_graph.arc_dict[arc_id].distance - \
                              self.var_zeta_s[(j, k)] + self.ins.model_para.t_unload
                        rhs = (1 - self.x[(i, j, k)]) * self.ins.model_para.big_m

                        self.cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def set_obj(self):
        """ """
        # self.objs[1] = 0
        # self.objs[2] = 0  # vehicle usage

        travel_cost = LinExpr()
        coe_1_1 = []
        vars_1_1 = []

        carbon_cost = LinExpr()
        coe_3_1 = []

        for arc_id, arc in self.ins.graph.first_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_1st):
                    from_id = arc_id[0]
                    to_id = arc_id[1]
                    var_name = 'x_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                    coe_1_1.append(arc.distance)
                    vars_1_1.append(self.x[(from_id, to_id, k)])

                    coe_3_1.append(arc.distance * self.para.rho_1 * self.para.c_r)

        travel_cost.addTerms(coe_1_1, vars_1_1)
        self.objs['1st travel cost'] += travel_cost

        carbon_cost.addTerms(coe_3_1, vars_1_1)
        self.objs['1st carbon cost'] += (self.para.c_p * (self.para.phi * carbon_cost - self.para.Q_q_1))

        lhs_1 = LinExpr()
        lhs_1_coe = []
        lhs_1_var = []
        for s in self.ins.graph.sate_list:
            if judge_arc(arc_id=(0, s),
                         graph=self.ins.graph.first_echelon_graph):
                for k in range(self.ins.vehicle_num_1st):
                    var_x_name = 'x_' + str(0) + '_' + str(s) + '_' + str(k)
                    lhs_1_coe.append(self.ins.model_para.vehicle_1_cost)
                    lhs_1_var.append(self.x[(0, s, k)])
        lhs_1.addTerms(lhs_1_coe, lhs_1_var)
        # self.objs[2] += lhs_1
        self.objs['1st vehicle cost'] += lhs_1

        self.model.setObjective(
            self.objs['1st travel cost'] + self.objs['1st carbon cost'] + self.objs['1st vehicle cost']
            , sense=GRB.MINIMIZE)

    def solve_and_print_result(self):
        self.model.optimize()

        # if self.model.status == 2:
        if self.model.SolCount > 0:
            print(" ---------  The solution ---------  ")
            print("obj: {}".format(self.model.ObjVal))

            for var in self.model.getVars():
                var_name = var.varName
                # if (var.x > 0.RepairOperators and var_name.startswith('x')):
                #     print("{} = {}".format(var_name, var.x))

                if var.x > 0.5:
                    if var_name.startswith('x'):
                        # if var_name.startswith('x'):
                        print("{} = {}".format(var_name, var.x))
                        # self.travel_x[var_name] = var.x

        else:
            print('Cannot find a feasible solution!!!')

    def _get_travel_x(self):
        for key, var in self.x.items():
            if var.x >= 0.5:
                self.travel_x[key[-1]].append(key)

    def get_routes(self):
        """  """
        vehicle_used = []
        # self._get_travel_x()

        for vehicle_id, travel_x in self.travel_x.items():
            if len(travel_x) != 0:
                # not empty
                cur_route, self.routes[vehicle_id] = self._get_route(travel_x_list=travel_x)

    def gen_new_route(self):
        """  """
        new_route = Route()
        new_route.route.append(self.ins.graph.vertex_dict[0])
        new_route.route_list.append(0)
        new_route.cost += self.ins.model_para.vehicle_1_cost

        return new_route

    def _get_route(self,
                   travel_x_list: list):
        """  """

        def find_start_x(lst):
            for x in lst:
                if x[0] == 0:
                    return x
                else:
                    pass

        if len(travel_x_list) == 0:
            return []

        route = self.gen_new_route()

        start_x = find_start_x(lst=travel_x_list)
        assigned = [start_x]

        from_id = 0
        next_id = start_x[1]

        # route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[next_id],
        #                             distance=self.ins.graph.arc_dict[(from_id, next_id)].distance,
        #                             service_time=self.ins.model_para.t_unload)

        route_list = [from_id, next_id]

        while len(assigned) != len(travel_x_list):
            for x in travel_x_list:
                if x[0] == next_id:
                    route_list.append(x[1])
                    assigned.append(x)

                    route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[next_id],
                                                distance=self.ins.graph.arc_dict[(from_id, next_id)].distance,
                                                service_time=self.ins.model_para.t_unload)

                    from_id = x[0]
                    next_id = x[1]

        route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[next_id],
                                    distance=self.ins.graph.arc_dict[(from_id, next_id)].distance,
                                    service_time=0)

        return route_list, route

    def gen_grb_sol(self):
        """ """
        # build model
        self.build_grb_model()

        # compute
        # self.model.computeIIS()
        # self.model.write('1st_compute.ilp')
        self.model.update()
        # self.model.write('1ST.LP')
        # self.model.optimize()

        # solve
        self.solve_and_print_result()

        # get vars
        if self.model.status == GRB.OPTIMAL:
            self._get_travel_x()

            for vehicle_id, travel_x in self.travel_x.items():
                if len(travel_x) != 0:
                    # not empty
                    cur_route_list, cur_route = self._get_route(travel_x_list=travel_x)
                    # cur_route = self.print_result()
                    self.routes[vehicle_id] = cur_route
                    self.grb_sol.add_route_into_sol(route=cur_route)

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
            depot_return = self.ins.graph.depot_list[1]

        else:
            for arc in route_arcs:
                if arc[0] in self.ins.graph.sate_list:
                    cur_vertex = arc[0]
                    depot_return = self.ins.graph.sate_to_depot[cur_vertex]

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

        return routes_1st


class GrbModelWithoutOD(object):

    def __init__(self,
                 ins,
                 od_list,
                 sate_od_demand):
        """  """
        self.ins = deepcopy(ins)
        self.graph = self.ins.graph
        self.grb_params = self.ins.model_para
        self.od_list = od_list

        self.model = Model('gurobi_model')
        self.objs = {'1st travel cost': 0,
                     '1st carbon cost': 0,
                     '1st vehicle cost': 0,
                     '2nd travel cost': 0,
                     '2nd carbon cost': 0,
                     '2nd vehicle cost': 0}

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

        self.sate_od_demand = sate_od_demand

        """ set2-3 """
        self.initial_value = 1200.0
        """ set4 """
        # self.initial_value = 100000.0

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

        self.model.setObjective(
            self.objs['1st travel cost'] + self.objs['1st carbon cost'] + self.objs['1st vehicle cost'] + self.objs[
                '2nd travel cost'] + self.objs['2nd carbon cost'] + self.objs['2nd vehicle cost'],
            sense=GRB.MINIMIZE)
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
        # self.objs[1] = 0
        # self.objs[3] = 0  # carbon cost

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

                    coe_3_1.append(arc.distance * self.grb_params.rho_1 * self.grb_params.c_r)

        obj_1_1.addTerms(coe_1_1, vars_1_1)
        # #self.travel_cost_1 = obj_1_1
        self.objs['1st travel cost'] += obj_1_1

        obj_3_1.addTerms(coe_3_1, vars_1_1)
        self.objs['1st carbon cost'] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_1 - self.grb_params.Q_q_1))

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

                    coe_3_2.append(arc.distance * self.grb_params.rho_2 * self.grb_params.c_r)

        obj_1_2.addTerms(coe_1_2, vars_1_2)
        # self.travel_cost_2 = obj_1_2
        self.objs['2nd travel cost'] += obj_1_2

        obj_3_2.addTerms(coe_3_2, vars_1_2)
        # self.objs[3] += (obj_3_2 - self.grb_params.Q_q_2)
        self.objs['2nd carbon cost'] += (self.grb_params.c_p * (self.grb_params.phi * obj_3_2 - self.grb_params.Q_q_2))

    def set_second_obj(self):
        """ vehicle usage cost """
        # self.objs[2] = 0

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
        self.objs['1st vehicle cost'] += lhs_1

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
        self.objs['2nd vehicle cost'] += lhs_2

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
                            # self.binding_cons[con_name] = self.model.addConstr(
                            #     self.varzeta_c_k2[j, k2] >= self.varzeta_s_k1[i, k1] +
                            #     self.graph.second_echelon_graph.arc_dict[
                            #         (i, j)].distance + self.grb_params.p - self.grb_params.big_m * (
                            #             2 - self.var_y[i, j, k2] - lhs),
                            #     name=con_name
                            # )
                            self.binding_cons[con_name] = self.model.addConstr(
                                self.tau_c_k2[j, k2] >= self.tau_s_k1[i, k1] +
                                self.graph.second_echelon_graph.arc_dict[
                                    (i, j)].distance + self.grb_params.p - self.grb_params.big_m * (
                                        2 - self.var_y[i, j, k2] - lhs),
                                name=con_name
                            )

    def add_first_variables(self):
        """ set2-3 """
        self.initial_value = 1200.0
        """ set4 """
        # self.initial_value = 100000.0

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
                    lb=0, ub=self.grb_params.vehicle_1_capacity,
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

        # vehicle max serve sate num con
        for sate in self.graph.sate_list:
            max_ser_lq = LinExpr()
            max_ser_lq_coe = []
            max_ser_lq_var = []

            for j in self.graph.second_echelon_list:
                if judge_arc(arc_id=(sate, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        max_ser_lq_coe.append(1)
                        max_ser_lq_var.append(self.var_y[sate, j, k])

            max_ser_lq.addTerms(max_ser_lq_coe, max_ser_lq_var)

            con_max_serve_name = '2nd-con_max_serve-' + f'{sate}'
            self.second_cons[con_max_serve_name] = self.model.addConstr(
                max_ser_lq <= self.ins.model_para.vehicle_max_ser_sate_num,
                name=con_max_serve_name
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
        # for j in self.graph.first_echelon_list:
        # for j in self.graph.first_echelon_list:
        #     if judge_arc(arc_id=(i, j),
        #                  graph=self.graph.first_echelon_graph):
        #
        #         for k in range(self.ins.vehicle_num_1st):
        #             con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
        #
        #             if con_name_capacity not in self.first_cons.keys():
        #                 self.first_cons[con_name_capacity] = self.model.addConstr(
        #                     self.w_s_k1[i, k] - self.w_s_k1[j, k] + (
        #                             self.sate_demand[j] + self.grb_params.vehicle_1_capacity) *
        #                     self.var_x[i, j, k] <= self.grb_params.vehicle_1_capacity,
        #                     name=con_name_capacity
        #                 )

        for j in self.ins.graph.sate_list:
            for k in range(self.ins.vehicle_num_1st):
                capacity_service_lq = LinExpr()
                capacity_service_lq_coe = []
                capacity_service_lq_var = []

                for i in self.ins.graph.first_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.ins.graph.first_echelon_graph):
                        capacity_service_lq_coe.append(1)
                        capacity_service_lq_var.append(self.var_x[i, j, k])

                capacity_service_lq.addTerms(capacity_service_lq_coe,
                                             capacity_service_lq_var)
                con_name_capacity = '1st-3-con_capacity_service_-' + f'{j}' + '_' + f'{k}'
                self.first_cons[con_name_capacity] = self.model.addConstr(
                    capacity_service_lq * self.ins.model_para.vehicle_1_capacity >= self.w_s_k1[j, k],
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

        for i in self.ins.graph.sate_list:
            sate_service_lq = LinExpr()
            sate_service_coe = []
            sate_service_var = []

            con_name_capacity = '1st-3-con_capacity_sate-' + f'{i}'
            for k in range(self.ins.vehicle_num_1st):
                sate_service_coe.append(1)
                sate_service_var.append(self.w_s_k1[i, k])

            sate_service_lq.addTerms(sate_service_coe, sate_service_var)
            self.first_cons[con_name_capacity] = self.model.addConstr(
                sate_service_lq == self.sate_demand[i] + self.sate_od_demand[i],
                name=con_name_capacity
            )

        for k in range(self.ins.vehicle_num_1st):
            vehicle_service_lq = LinExpr()
            vehicle_service_coe = []
            vehicle_service_var = []

            con_name_capacity = '1st-3-con_capacity_vehicle-' + f'{k}'

            for i in self.ins.graph.sate_list:
                vehicle_service_coe.append(1)
                vehicle_service_var.append(self.w_s_k1[i, k])
            vehicle_service_lq.addTerms(vehicle_service_coe, vehicle_service_var)

            self.first_cons[con_name_capacity] = self.model.addConstr(
                vehicle_service_lq <= self.grb_params.vehicle_1_capacity,
                name=con_name_capacity
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
                lhs_cus_service == 1,
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

        # vehicle max serve sate num con
        for sate in self.graph.sate_list:
            max_ser_lq = LinExpr()
            max_ser_lq_coe = []
            max_ser_lq_var = []

            for j in self.graph.second_echelon_list:
                if judge_arc(arc_id=(sate, j),
                             graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        max_ser_lq_coe.append(1)
                        max_ser_lq_var.append(self.var_y[sate, j, k])

            max_ser_lq.addTerms(max_ser_lq_coe, max_ser_lq_var)

            con_max_serve_name = '2nd-con_max_serve-' + f'{sate}'
            self.second_cons[con_max_serve_name] = self.model.addConstr(
                max_ser_lq <= self.ins.model_para.vehicle_max_ser_sate_num,
                name=con_max_serve_name
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
