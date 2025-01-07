# -*- coding: utf-8 -*-
# @Time     : 2024-07-30-15:51
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Common import *
from gurobipy import *


class GurobiModelBuilder(object):

    def __init__(self,
                 ins):

        self.ins = ins
        self.graph = ins.graph
        self.grb_params = ins.model_para

        # build GRB model
        self.model = Model('gurobi_model')

        # objectives
        self.objs = {}

        # travel cost
        self.travel_cost_1 = 0
        self.travel_cost_2 = 0
        self.travel_cost_od = 0

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

    @staticmethod
    def judge_arc(arc_id,
                  graph):
        if arc_id in graph.arc_dict and graph.arc_dict[arc_id].adj == 1:
            return True

        else:
            return False

    def add_variables(self):
        self.add_first_variables()

        if self.ins.is_select is True:
            self.add_second_variables_sate_select()
        else:
            self.add_second_variables_no_selection()
        self.add_od_variables_pdp()

    def add_cons(self):
        self.add_first_cons()

        if self.ins.is_select is True:
            self.add_second_cons_sate_select()
        else:
            self.add_second_cons_no_select()

        self.add_od_cons_pdp()
        self.add_binding_cons()

    def set_objs(self):
        self.set_first_obj()
        self.set_second_obj()

        self.model.setObjective(self.objs[1] + self.objs[2] + self.objs[3] * self.grb_params.c_p, sense=GRB.MINIMIZE)

    def add_first_variables(self):
        """ first echelon """
        for arc_id, arc in self.graph.first_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_1st):
                    """quantity"""
                    from_id = arc_id[0]
                    to_id = arc_id[1]

                    var_name = 'x_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                    self.var_x[var_name] = self.model.addVar(
                        vtype=GRB.BINARY,
                        lb=0.0, ub=1.0,
                        name=var_name,
                        column=None,
                        obj=0
                    )

        for i in self.graph.first_echelon_list:
            for k in range(self.ins.vehicle_num_1st):
                """quantity"""
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k1'
                self.w_s_k1[var_w_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.grb_params.vehicle_1_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                """arrive time"""
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k1'
                self.varzeta_s_k1[var_zeta_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=1440,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                """service start time"""
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k1'
                self.tau_s_k1[var_tau_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=1440,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

    def add_second_variables_sate_select(self):
        """ """
        for arc_id, arc in self.graph.second_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_2nd):
                    from_id = arc_id[0]
                    to_id = arc_id[1]

                    """travel"""
                    var_name = 'y_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                    self.var_y[var_name] = self.model.addVar(
                        vtype=GRB.BINARY,
                        lb=0.0, ub=1.0,
                        name=var_name,
                        column=None,
                        obj=0
                    )

        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):
                """quantity"""
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k2'
                self.w_c_k2[var_w_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.grb_params.vehicle_2_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                """arrive time"""
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                self.varzeta_c_k2[var_zeta_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                """service start time"""
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                self.tau_c_k2[var_tau_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    # lb=0.0, ub=1440,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

        for sate in self.graph.sate_list:
            var_d_name = 'D_' + str(sate)
            self.sate_demand[var_d_name] = self.model.addVar(
                vtype=GRB.CONTINUOUS,
                lb=0.0, ub=self.ins.model_para.m_s,
                name=var_d_name,
                column=None,
                obj=0
            )

            sate_depot = self.graph.sate_to_depot[sate]
            var_d_name = 'D_' + str(sate_depot)
            self.sate_demand[var_d_name] = self.model.addVar(
                vtype=GRB.CONTINUOUS,
                lb=0.0, ub=self.ins.model_para.m_s,
                name=var_d_name,
                column=None,
                obj=0
            )

        for c in self.ins.graph.customer_list:
            for s in self.ins.graph.sate_list:
                var_name = 'zeta_' + str(c) + '_' + str(s)
                self.zeta_c_s[var_name] = self.model.addVar(
                    vtype=GRB.BINARY,
                    lb=0.0, ub=1.0,
                    name=var_name,
                    column=None,
                    obj=0
                )

    def add_second_variables_no_selection(self):
        """ second echelon """
        for arc_id, arc in self.graph.second_echelon_graph.arc_dict.items():
            if arc.adj == 1:
                for k in range(self.ins.vehicle_num_2nd):
                    from_id = arc_id[0]
                    to_id = arc_id[1]

                    """travel"""
                    var_name = 'y_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                    self.var_y[var_name] = self.model.addVar(
                        vtype=GRB.BINARY,
                        lb=0.0, ub=1.0,
                        name=var_name,
                        column=None,
                        obj=0
                    )

        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):
                """quantity"""
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k2'
                self.w_c_k2[var_w_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.grb_params.vehicle_2_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

                """arrive time"""
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                self.varzeta_c_k2[var_zeta_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.graph.vertex_dict[i].due_time,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                """service start time"""
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                self.tau_c_k2[var_tau_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    # lb=0.0, ub=1440,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

    def add_od_variables_pdp(self):
        """  """
        for c in self.graph.customer_list:
            for k in range(len(self.graph.od_o_list)):
                """task assignment"""
                var_r_name = 'r_' + str(c) + '_' + str(k)
                self.var_r[var_r_name] = self.model.addVar(
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
                # if arc_id == (6, 8):
                #     print()
                if arc.adj == 1:
                    if (arc_id[0] in self.graph.od_o_list and arc_id[0] != o) or (
                            arc_id[1] in self.graph.od_d_list and arc_id[1] != d):
                        pass
                    else:

                        """travel"""
                        from_id = arc_id[0]
                        to_id = arc_id[1]

                        var_name = 'z_' + str(from_id) + '_' + str(to_id) + '_' + str(k)
                        self.var_z[var_name] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0.0, ub=1.0,
                            name=var_name,
                            column=None,
                            obj=0
                        )

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [o, d]
            for i in visit_list:
                """arrive"""
                var_zeta_name = 'varzeta_' + str(i) + '_' + str(k)

                self.varzeta_c_k_od[var_zeta_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=1440,
                    name=var_zeta_name,
                    column=None,
                    obj=0
                )

                """service"""
                var_tau_name = 'tau_' + str(i) + '_' + str(k)

                self.tau_c_k_od[var_tau_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=self.graph.vertex_dict[i].ready_time, ub=self.graph.vertex_dict[i].due_time,
                    # lb=self.graph.vertex_dict[i].ready_time, ub=1440,
                    name=var_tau_name,
                    column=None,
                    obj=0
                )

                """quantity"""
                var_w_name = 'w_' + str(i) + '_' + str(k) + '_k_od'

                self.w_c_k_od[var_w_name] = self.model.addVar(
                    vtype=GRB.CONTINUOUS,
                    lb=0.0, ub=self.grb_params.vehicle_od_capacity,
                    name=var_w_name,
                    column=None,
                    obj=0
                )

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
                    var_name = 'x_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                    # coe_1_1.append(arc.distance * 3)
                    coe_1_1.append(arc.distance)
                    vars_1_1.append(self.var_x[var_name])

                    coe_3_1.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)

        obj_1_1.addTerms(coe_1_1, vars_1_1)
        self.travel_cost_1 = obj_1_1
        self.objs[1] += obj_1_1

        obj_3_1.addTerms(coe_3_1, vars_1_1)
        self.objs[3] += (obj_3_1 - self.grb_params.Q_q_1)

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
                    var_name = 'y_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                    # coe_1_2.append(arc.distance * 2)
                    coe_1_2.append(arc.distance)
                    vars_1_2.append(self.var_y[var_name])

                    coe_3_2.append(arc.distance * self.grb_params.rho_1 * self.grb_params.phi)

        obj_1_2.addTerms(coe_1_2, vars_1_2)
        self.travel_cost_2 = obj_1_2
        self.objs[1] += obj_1_2

        obj_3_2.addTerms(coe_3_2, vars_1_2)
        self.objs[3] += (obj_3_2 - self.grb_params.Q_q_2)

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
                        var_name = 'z_' + str(from_id) + '_' + str(to_id) + '_' + str(k)

                        # coe_1_3_1.append(arc.distance)
                        coe_1_3_1.append(arc.distance * self.grb_params.c_c)
                        vars_1_3_1.append(self.var_z[var_name])

                        # coe_3_3.append(arc.distance * carbon_coe)

        obj_1_3_1.addTerms(coe_1_3_1, vars_1_3_1)
        self.objs[1] += obj_1_3_1

        # obj_3_3.addTerms(coe_3_3, vars_1_3_1)
        # self.objs[3] += obj_3_3

        # compensation cost
        for c in self.graph.customer_list:
            for k in range(len(self.graph.od_o_list)):
                var_r_name = 'r_' + str(c) + '_' + str(k)

                coe_1_3_2.append(self.grb_params.compensation)
                vars_1_3_2.append(self.var_r[var_r_name])
        obj_1_3_2.addTerms(coe_1_3_2, vars_1_3_2)
        self.objs[1] += obj_1_3_2

        self.travel_cost_od = obj_1_3_1

    def set_second_obj(self):
        """ vehicle usage cost """
        self.objs[2] = 0

        """1st echelon"""
        lhs_1 = LinExpr()
        lhs_1_coe = []
        lhs_1_var = []
        for s in self.graph.sate_list:
            if self.judge_arc(arc_id=(0, s),
                              graph=self.graph.first_echelon_graph):
                for k in range(self.ins.vehicle_num_1st):
                    var_x_name = 'x_' + str(0) + '_' + str(s) + '_' + str(k)
                    lhs_1_coe.append(self.grb_params.vehicle_1_cost)
                    lhs_1_var.append(self.var_x[var_x_name])
        lhs_1.addTerms(lhs_1_coe, lhs_1_var)
        self.objs[2] += lhs_1

        # 2nd
        lhs_2 = LinExpr()
        lhs_2_coe = []
        lhs_2_var = []
        for c in self.graph.customer_list:
            for s in self.graph.sate_list:
                for k in range(self.ins.vehicle_num_2nd):
                    if self.judge_arc(arc_id=(s, c),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(s) + '_' + str(c) + '_' + str(k)
                        lhs_2_coe.append(self.grb_params.vehicle_2_cost)
                        lhs_2_var.append(self.var_y[var_y_name])
        lhs_2.addTerms(lhs_2_coe, lhs_2_var)
        self.objs[2] += lhs_2

    def add_first_cons(self):
        """ 1st echelon """
        # start and return
        for k in range(self.ins.vehicle_num_1st):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.graph.sate_list:
                if self.judge_arc(arc_id=(0, j),
                                  graph=self.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(0) + '_' + str(j) + '_' + str(k)
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.var_x[var_x_name])
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
                if self.judge_arc(arc_id=(i, self.graph.depot_list[-1]),
                                  graph=self.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(self.graph.depot_list[-1]) + '_' + str(k)
                    lhs_en_coe.append(1)
                    lhs_en_var.append(self.var_x[var_x_name])
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

        # flow balance
        for l in self.graph.sate_list:

            for k in range(self.ins.vehicle_num_1st):

                lhs = LinExpr()
                lhs_coe = []
                lhs_vars = []
                for j in self.graph.first_echelon_list:
                    arc_id_1 = (j, l)
                    if self.judge_arc(arc_id=arc_id_1, graph=self.graph.first_echelon_graph):
                        var_x_name_1 = 'x_' + str(j) + '_' + str(l) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.var_x[var_x_name_1])

                    arc_id_2 = (l, j)
                    if self.judge_arc(arc_id=arc_id_2, graph=self.graph.first_echelon_graph):
                        var_x_name_2 = 'x_' + str(l) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(-1)
                        lhs_vars.append(self.var_x[var_x_name_2])

                lhs.addTerms(lhs_coe, lhs_vars)
                con_flow_balance_name = '1st_con_flow_balance-' + str(l) + '_' + str(k)
                self.first_cons[con_flow_balance_name] = self.model.addConstr(lhs <= 0,
                                                                              name=con_flow_balance_name)

        # must visit
        # first_visit_list = self._map.satellite_id_list
        # first_visit_list.append(self._map.vertex_sum)
        for i in self.graph.sate_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_vars = []

            for k in range(self.ins.vehicle_num_1st):
                for j in self.graph.first_echelon_list:
                    if self.judge_arc(arc_id=(i, j), graph=self.graph.first_echelon_graph):
                        var_x_name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.var_x[var_x_name])

            lhs.addTerms(lhs_coe, lhs_vars)
            con_name = '1st-con_sate_visit_' + str(i)
            self.first_cons[con_name] = self.model.addConstr(lhs == 1, name=con_name)
            # self.model.addConstr(lhs <= RepairOperators.RepairOperators, name=con_name)

        # Capacity
        for i in self.graph.first_echelon_list:
            for k in range(self.ins.vehicle_num_1st):
                con_name_capacity_1 = '1st-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
                con_name_capacity_2 = '1st-3-con_capacity-2_' + f'{i}' + '_' + f'{k}'
                var_w_1 = 'w_' + str(i) + '_' + str(k) + '_k1'
                lq = LinExpr()
                lq.addTerms([1], [self.w_s_k1[var_w_1]])
                self.first_cons[con_name_capacity_1] = self.model.addConstr(
                    self.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )
                self.first_cons[con_name_capacity_2] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_1_capacity,
                    name=con_name_capacity_2
                )

                for j in self.graph.first_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.first_echelon_graph.arc_dict and \
                            self.graph.first_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_demand_name = 'D_' + str(j)
                        con_name = '1st-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_w_2 = 'w_' + str(j) + '_' + str(k) + '_k1'

                        if con_name not in self.first_cons.keys():
                            self.first_cons[con_name] = self.model.addConstr(
                                self.w_s_k1[var_w_2] - self.w_s_k1[var_w_1] <= self.graph.vertex_dict[
                                    j].demand + self.grb_params.vehicle_1_capacity * (1 - self.var_x[var_name]),
                                name=con_name
                            )

        # time windows
        for k in range(self.ins.vehicle_num_1st):
            for i in self.graph.first_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k1'
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k1'
                con_name_time_1 = '1st-4-con_time_window-' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                lq.addTerms([1], [self.tau_s_k1[var_tau_name]])
                self.first_cons[con_name_time_1] = self.model.addConstr(
                    self.varzeta_s_k1[var_zeta_name] <= lq + self.grb_params.t_unload,  # + unload time
                    name=con_name_time_1
                )

                con_name_time_2 = '1st-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_name_time_2] = self.model.addConstr(
                    self.graph.vertex_dict[i].ready_time <= lq,
                    name=con_name_time_2
                )
                con_name_time_3 = '1st-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_name_time_3] = self.model.addConstr(
                    lq <= self.graph.vertex_dict[i].due_time,
                    name=con_name_time_3
                )

                for j in self.graph.first_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.arc_dict and \
                            self.graph.first_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k) + '_k1'
                        con_name = '1st-4-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_s_k1[var_tau_name] + self.graph.first_echelon_graph.arc_dict[arc_id].distance - \
                              self.varzeta_s_k1[var_zeta_name_2]
                        rhs = (1 - self.var_x[var_name]) * self.grb_params.big_m

                        self.first_cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def add_first_cons_sate_select(self):
        """ 1st echelon """
        # start and return
        for k in range(self.ins.vehicle_num_1st):
            # start
            lhs_start = LinExpr()
            lhs_start_coe = []
            lhs_start_var = []

            for j in self.graph.sate_list:
                if self.judge_arc(arc_id=(0, j),
                                  graph=self.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(0) + '_' + str(j) + '_' + str(k)
                    lhs_start_coe.append(1)
                    lhs_start_var.append(self.var_x[var_x_name])
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
                if self.judge_arc(arc_id=(i, self.graph.depot_list[-1]),
                                  graph=self.graph.first_echelon_graph):
                    var_x_name = 'x_' + str(i) + '_' + str(self.graph.depot_list[-1]) + '_' + str(k)
                    lhs_en_coe.append(1)
                    lhs_en_var.append(self.var_x[var_x_name])
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

        # flow balance
        for l in self.graph.sate_list:

            for k in range(self.ins.vehicle_num_1st):

                lhs = LinExpr()
                lhs_coe = []
                lhs_vars = []
                for j in self.graph.first_echelon_list:
                    arc_id_1 = (j, l)
                    if self.judge_arc(arc_id=arc_id_1, graph=self.graph.first_echelon_graph):
                        var_x_name_1 = 'x_' + str(j) + '_' + str(l) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.var_x[var_x_name_1])

                    arc_id_2 = (l, j)
                    if self.judge_arc(arc_id=arc_id_2, graph=self.graph.first_echelon_graph):
                        var_x_name_2 = 'x_' + str(l) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(-1)
                        lhs_vars.append(self.var_x[var_x_name_2])

                lhs.addTerms(lhs_coe, lhs_vars)
                con_flow_balance_name = '1st_con_flow_balance-' + str(l) + '_' + str(k)
                self.first_cons[con_flow_balance_name] = self.model.addConstr(lhs <= 0,
                                                                              name=con_flow_balance_name)

        # must visit
        # first_visit_list = self._map.satellite_id_list
        # first_visit_list.append(self._map.vertex_sum)
        for i in self.graph.sate_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_vars = []

            for k in range(self.ins.vehicle_num_1st):
                for j in self.graph.first_echelon_list:
                    if self.judge_arc(arc_id=(i, j), graph=self.graph.first_echelon_graph):
                        var_x_name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_vars.append(self.var_x[var_x_name])

            lhs.addTerms(lhs_coe, lhs_vars)
            con_name = '1st-con_sate_visit_' + str(i)
            self.first_cons[con_name] = self.model.addConstr(lhs == 1, name=con_name)
            # self.model.addConstr(lhs <= RepairOperators.RepairOperators, name=con_name)

        # Capacity
        for i in self.graph.first_echelon_list:
            for k in range(self.ins.vehicle_num_1st):
                con_name_capacity_1 = '1st-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
                con_name_capacity_2 = '1st-3-con_capacity-2_' + f'{i}' + '_' + f'{k}'
                var_w_1 = 'w_' + str(i) + '_' + str(k) + '_k1'
                lq = LinExpr()
                lq.addTerms([1], [self.w_s_k1[var_w_1]])
                self.first_cons[con_name_capacity_1] = self.model.addConstr(
                    self.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )
                self.first_cons[con_name_capacity_2] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_1_capacity,
                    name=con_name_capacity_2
                )

                for j in self.graph.first_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.first_echelon_graph.arc_dict and \
                            self.graph.first_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_demand_name = 'D_' + str(j)
                        con_name = '1st-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_w_2 = 'w_' + str(j) + '_' + str(k) + '_k1'

                        if con_name not in self.first_cons.keys():
                            self.first_cons[con_name] = self.model.addConstr(
                                self.w_s_k1[var_w_2] - self.w_s_k1[var_w_1] <= self.graph.vertex_dict[
                                    j].demand + self.grb_params.vehicle_1_capacity * (1 - self.var_x[var_name]),
                                name=con_name
                            )

        # time windows
        for k in range(self.ins.vehicle_num_1st):
            for i in self.graph.first_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k1'
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k1'
                con_name_time_1 = '1st-4-con_time_window-' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                lq.addTerms([1], [self.tau_s_k1[var_tau_name]])
                self.first_cons[con_name_time_1] = self.model.addConstr(
                    self.varzeta_s_k1[var_zeta_name] <= lq + self.grb_params.t_unload,  # + unload time
                    name=con_name_time_1
                )

                con_name_time_2 = '1st-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_name_time_2] = self.model.addConstr(
                    self.graph.vertex_dict[i].ready_time <= lq,
                    name=con_name_time_2
                )
                con_name_time_3 = '1st-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.first_cons[con_name_time_3] = self.model.addConstr(
                    lq <= self.graph.vertex_dict[i].due_time,
                    name=con_name_time_3
                )

                for j in self.graph.first_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.arc_dict and \
                            self.graph.first_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'x_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k) + '_k1'
                        con_name = '1st-4-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_s_k1[var_tau_name] + self.graph.first_echelon_graph.arc_dict[arc_id].distance - \
                              self.varzeta_s_k1[var_zeta_name_2]
                        rhs = (1 - self.var_x[var_name]) * self.grb_params.big_m

                        self.first_cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def add_second_cons_sate_select_draft(self):
        """ second echelon """
        # start
        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:
                # start
                lhs_start = LinExpr()
                lhs_start_coe = []
                lhs_start_var = []

                for j in self.graph.customer_list:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_start_coe.append(1)
                        lhs_start_var.append(self.var_y[var_y_name])
                lhs_start.addTerms(lhs_start_coe, lhs_start_var)
                con_name_start = '2nd_con_start_' + str(s) + '_' + str(k)
                self.second_cons[con_name_start] = self.model.addConstr(
                    lhs_start <= 1,
                    name=con_name_start
                )

                # return
                lhs_end = LinExpr()
                lhs_en_coe = []
                lhs_en_var = []

                for i in self.graph.customer_list:
                    if self.judge_arc(arc_id=(i, self.graph.sate_to_depot[s]),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(i) + '_' + str(self.graph.sate_to_depot[s]) + '_' + str(k)
                        lhs_en_coe.append(1)
                        lhs_en_var.append(self.var_y[var_y_name])
                lhs_end.addTerms(lhs_en_coe, lhs_en_var)
                con_name_end = '2nd_con_return_' + str(k)
                self.second_cons[con_name_end] = self.model.addConstr(
                    lhs_end <= 1,
                    name=con_name_end
                )

                # start equ return
                con_name = '2nd_con_start_equ_return-' + str(s) + '_' + str(k)
                self.first_cons[con_name] = self.model.addConstr(
                    lhs_start == lhs_end,
                    name=con_name
                )

        # 每个customer只能被访问一次
        for c in self.graph.customer_list:

            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            for k_od in range(len(self.graph.od_o_list)):
                var_r_name = 'r_' + str(c) + '_' + str(k_od)
                lhs_coe_1.append(1)
                lhs_var_1.append(self.var_r[var_r_name])
            lhs_1.addTerms(lhs_coe_1, lhs_var_1)

            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in self.graph.second_echelon_list:
                if self.judge_arc(arc_id=(i, c),
                                  graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        var_y_name = 'y_' + str(i) + '_' + str(c) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_y[var_y_name])
            lhs_2.addTerms(lhs_coe_2, lhs_var_2)

            con_name = '2nd_customer_visit-' + str(c)
            self.second_cons[con_name] = self.model.addConstr(
                1 == lhs_1 + lhs_2,
                name=con_name
            )

        # 每个车从只能服务一个sate
        for k in range(self.ins.vehicle_num_2nd):
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []

            for s in self.graph.sate_list:
                for j in self.graph.customer_list:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_var.append(self.var_y[var_y_name])
            lhs.addTerms(lhs_coe, lhs_var)
            con_name = '2nd_1service_sate_' + str(k)
            self.second_cons[con_name] = self.model.addConstr(
                lhs <= 1,
                name=con_name
            )

        # flow balance
        # 流平衡应该是对于每个车的
        for l in self.graph.customer_list:

            for k in range(self.ins.vehicle_num_2nd):
                lhs = LinExpr()
                lhs_coe = []
                lhs_var = []

                # in
                # visit_list_1 = self.graph.customer_list + [self.graph.cus_belong_sate[l]]
                visit_list_1 = self.graph.customer_list + self.graph.sate_list
                for i in visit_list_1:
                    # if self.judge_arc(arc_id=(i, l),
                    #                   graph=self.graph.second_echelon_graph):
                    if i != l:
                        if self.graph.second_echelon_graph.arc_dict[i, l].adj == 1:
                            var_y_name_1 = 'y_' + str(i) + '_' + str(l) + '_' + str(k)
                            lhs_coe.append(1)
                            lhs_var.append(self.var_y[var_y_name_1])

                # out
                # visit_list_2 = self.graph.customer_list + [self.graph.sate_to_depot[self.graph.cus_belong_sate[l]]]
                visit_list_2 = self.graph.customer_list + self.graph.sate_depot_list
                for j in visit_list_2:
                    # if self.judge_arc(arc_id=(l, j),
                    #                   graph=self.graph.second_echelon_graph):
                    if j != l:
                        if self.graph.second_echelon_graph.arc_dict[l, j].adj == 1:
                            var_y_name_2 = 'y_' + str(l) + '_' + str(j) + '_' + str(k)
                            lhs_coe.append(-1)
                            lhs_var.append(self.var_y[var_y_name_2])

                lhs.addTerms(lhs_coe, lhs_var)
                con_name = '2nd-flow_balance-' + str(l) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs == 0,
                    name=con_name
                )

        # 对于每个从sate出发的车，都需要回到相应的sate_to_depot
        for s in self.graph.sate_list:
            sate_depot = self.graph.sate_to_depot[s]

            for k in range(self.ins.vehicle_num_2nd):

                # start
                lhs_1 = LinExpr()
                lhs_coe_1 = []
                lhs_var_1 = []

                # for j in self.graph.sate_serv_cus[s]:
                for j in self.graph.customer_list:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name_1 = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_coe_1.append(1)
                        lhs_var_1.append(self.var_y[var_y_name_1])
                lhs_1.addTerms(lhs_coe_1, lhs_var_1)

                # return
                lhs_2 = LinExpr()
                lhs_coe_2 = []
                lhs_var_2 = []

                # for i in self.graph.sate_serv_cus[s]:
                for i in self.graph.customer_list:
                    if self.judge_arc(arc_id=(i, sate_depot),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name_2 = 'y_' + str(i) + '_' + str(sate_depot) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_y[var_y_name_2])
                lhs_2.addTerms(lhs_coe_2, lhs_var_2)

                con_name = '2nd-sate_balance-' + str(s) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs_1 == lhs_2,
                    name=con_name
                )

        # capacity
        # customers to satellites
        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):
                con_name_capacity_1 = '2nd-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                var_w_1 = 'w_' + str(i) + '_' + str(k) + '_k2'
                lq.addTerms([1], [self.w_c_k2[var_w_1]])
                self.second_cons[con_name_capacity_1] = self.model.addConstr(
                    self.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )

                for j in self.graph.second_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.second_echelon_graph.arc_dict and \
                            self.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        con_name = '2nd-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_w_2 = 'w_' + str(j) + '_' + str(k) + '_k2'

                        if con_name not in self.second_cons.keys():
                            self.second_cons[con_name] = self.model.addConstr(
                                self.w_c_k2[var_w_2] - self.w_c_k2[var_w_1] <= self.graph.vertex_dict[
                                    j].demand + self.grb_params.vehicle_2_capacity * (1 - self.var_y[var_name]),
                                name=con_name
                            )

        # time windows
        for k in range(self.ins.vehicle_num_2nd):
            for i in self.graph.second_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                con_name_time_1 = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{k}'

                lq = LinExpr()
                lq.addTerms([1, -1], [self.varzeta_c_k2[var_zeta_name], self.tau_c_k2[var_tau_name]])
                self.second_cons[con_name_time_1] = self.model.addConstr(
                    lq <= 0,
                    name=con_name_time_1
                )

                lq = LinExpr()
                lq.addTerms([1], [self.tau_c_k2[var_tau_name]])
                con_name_time_2 = '2nd-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_2] = self.model.addConstr(
                    self.graph.vertex_dict[i].ready_time <= lq,
                    name=con_name_time_2
                )

                con_name_time_3 = '2nd-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_3] = self.model.addConstr(
                    lq <= self.graph.vertex_dict[i].due_time,
                    name=con_name_time_3
                )

                for j in self.graph.second_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.second_echelon_graph.arc_dict and \
                            self.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k) + '_k2'
                        con_name = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_c_k2[var_tau_name] + self.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - \
                              self.varzeta_c_k2[var_zeta_name_2]
                        rhs = (1 - self.var_y[var_name]) * self.grb_params.big_m

                        self.second_cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def add_second_cons_sate_select(self):
        """ 2nd echelon sate select """
        # 车辆数目的限制
        lhs_vehicle_con = LinExpr()
        lhs_vehicle_con_var = []
        lhs_vehicle_con_coe = []
        for k in range(self.ins.vehicle_num_2nd):
            for sate in self.graph.sate_list:
                for cus in self.graph.customer_list:
                    var_y_1 = 'y_' + str(sate) + '_' + str(cus) + '_' + str(k)

                    lhs_vehicle_con_var.append(self.var_y[var_y_1])
                    lhs_vehicle_con_coe.append(1)

        lhs_vehicle_con.addTerms(lhs_vehicle_con_coe, lhs_vehicle_con_var)
        con_vehicle_name = 'vehicle_con'

        self.second_cons[con_vehicle_name] = self.model.addConstr(
            lhs_vehicle_con <= self.ins.vehicle_num_2nd,
            name=con_vehicle_name
        )

        # satellite 每个从satellite 出发的车都需要回到对应的satellite as depot
        # vehicle 每辆车只能从一个satellite as depot 出发
        for k in range(self.ins.vehicle_num_2nd):
            lhs_vehicle_start = LinExpr()
            lhs_vehicle_start_var = []
            lhs_vehicle_start_coe = []

            for sate in self.graph.sate_list:
                lhs_start = LinExpr()
                lhs_start_var = []
                lhs_start_coe = []

                lhs_return = LinExpr()
                lhs_return_var = []
                lhs_return_coe = []

                sate_depot = self.graph.sate_to_depot[sate]

                for cus in self.graph.customer_list:
                    if self.judge_arc(arc_id=(sate, cus),
                                      graph=self.graph.second_echelon_graph):
                        var_y_2 = 'y_' + str(sate) + '_' + str(cus) + '_' + str(k)

                        lhs_start_var.append(self.var_y[var_y_2])
                        lhs_start_coe.append(1)

                        lhs_vehicle_start_var.append(self.var_y[var_y_2])
                        lhs_vehicle_start_coe.append(1)

                    if self.judge_arc(arc_id=(cus, sate_depot),
                                      graph=self.graph.second_echelon_graph):
                        var_y_3 = 'y_' + str(cus) + '_' + str(sate_depot) + '_' + str(k)

                        lhs_return_var.append(self.var_y[var_y_3])
                        lhs_return_coe.append(1)

                lhs_start.addTerms(lhs_start_coe, lhs_start_var)
                lhs_return.addTerms(lhs_return_coe, lhs_return_var)

                con_start_return = 'con_start_return_' + str(sate) + '_' + str(k)
                self.model.addConstr(
                    lhs_start == lhs_return,
                    name=con_start_return
                )

            lhs_vehicle_start.addTerms(lhs_vehicle_start_coe, lhs_vehicle_start_var)
            con_vehicle_start = 'con_vehicle_start_' + str(k)
            self.second_cons[con_vehicle_start] = self.model.addConstr(
                lhs_vehicle_start <= 1,
                name=con_vehicle_start
            )

        # 每个customer只能被访问一次
        for cus in self.graph.customer_list:

            lhs_od_assign = LinExpr()
            lhs_od_assign_var = []
            lhs_od_assign_coe = []

            for k_od in range(len(self.graph.od_o_list)):
                var_r_name = 'r_' + str(cus) + '_' + str(k_od)
                lhs_od_assign_coe.append(1)
                lhs_od_assign_var.append(self.var_r[var_r_name])
            lhs_od_assign.addTerms(lhs_od_assign_coe, lhs_od_assign_var)

            lhs_cus_serve = LinExpr()
            lhs_cus_serve_var = []
            lhs_cus_serve_coe = []

            for i in self.graph.second_echelon_list:
                if self.judge_arc(arc_id=(i, cus),
                                  graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        var_y_4 = 'y_' + str(i) + '_' + str(cus) + '_' + str(k)
                        lhs_cus_serve_coe.append(1)
                        lhs_cus_serve_var.append(self.var_y[var_y_4])
            lhs_cus_serve.addTerms(lhs_cus_serve_coe, lhs_cus_serve_var)

            con_name = '2nd_customer_visit-' + str(cus)
            self.second_cons[con_name] = self.model.addConstr(
                1 == lhs_od_assign + lhs_cus_serve,
                name=con_name
            )

            lhs_cus_to_sate = LinExpr()
            lhs_cus_to_sate_coe = []
            lhs_cus_to_sate_var = []
            for s in self.ins.graph.sate_list:
                var_zeta_name = 'zeta_' + str(cus) + '_' + str(s)
                lhs_cus_to_sate_coe.append(1)
                lhs_cus_to_sate_var.append(self.zeta_c_s[var_zeta_name])
            lhs_cus_to_sate.addTerms(lhs_cus_to_sate_coe, lhs_cus_to_sate_var)

        # flow balance
        # 流平衡应该是对于每个车的
        for l in self.graph.customer_list:

            for k in range(self.ins.vehicle_num_2nd):
                lhs_flow_balance = LinExpr()
                lhs_flow_balance_coe = []
                lhs_flow_balance_var = []

                # in
                visit_list_1 = self.graph.customer_list + [self.graph.cus_belong_sate[l]]
                for i in visit_list_1:
                    # if self.judge_arc(arc_id=(i, l),
                    #                   graph=self.graph.second_echelon_graph):
                    if i != l:
                        if self.graph.second_echelon_graph.arc_dict[i, l].adj == 1:
                            var_y_5 = 'y_' + str(i) + '_' + str(l) + '_' + str(k)
                            lhs_flow_balance_coe.append(1)
                            lhs_flow_balance_var.append(self.var_y[var_y_5])

                # out
                visit_list_2 = self.graph.customer_list + [self.graph.sate_to_depot[self.graph.cus_belong_sate[l]]]
                for j in visit_list_2:
                    # if self.judge_arc(arc_id=(l, j),
                    #                   graph=self.graph.second_echelon_graph):
                    if j != l:
                        if self.graph.second_echelon_graph.arc_dict[l, j].adj == 1:
                            var_y_6 = 'y_' + str(l) + '_' + str(j) + '_' + str(k)
                            lhs_flow_balance_coe.append(-1)
                            lhs_flow_balance_var.append(self.var_y[var_y_6])

                lhs_flow_balance.addTerms(lhs_flow_balance_coe, lhs_flow_balance_var)
                con_name = '2nd-flow_balance-' + str(l) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs_flow_balance == 0,
                    name=con_name
                )

        # capacity
        # customers to satellites
        for s in self.ins.graph.sate_list:
            lhs_zeta = LinExpr()
            lhs_zeta_coe = []
            lhs_zeta_var = []

            for c in self.ins.graph.customer_list:
                var_zeta_1 = 'zeta_' + str(c) + '_' + str(s)
                lhs_zeta_coe.append(self.ins.graph.vertex_dict[c].demand)
                lhs_zeta_var.append(self.zeta_c_s[var_zeta_1])
            lhs_zeta.addTerms(lhs_zeta_coe, lhs_zeta_var)

            con_name = '2nd-sate_demand-' + str(s)
            self.second_cons[con_name] = self.model.addConstr(
                lhs_zeta == self.sate_demand[f'D_{s}'],
                name=con_name
            )

        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):
                con_name_capacity_1 = '2nd-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                var_w_1 = 'w_' + str(i) + '_' + str(k) + '_k2'
                lq.addTerms([1], [self.w_c_k2[var_w_1]])
                self.second_cons[con_name_capacity_1] = self.model.addConstr(
                    self.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )

                for j in self.graph.second_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.second_echelon_graph.arc_dict and \
                            self.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        con_name = '2nd-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_w_2 = 'w_' + str(j) + '_' + str(k) + '_k2'

                        if con_name not in self.second_cons.keys():
                            self.second_cons[con_name] = self.model.addConstr(
                                self.w_c_k2[var_w_2] - self.w_c_k2[var_w_1] <= self.graph.vertex_dict[
                                    j].demand + self.grb_params.vehicle_2_capacity * (1 - self.var_y[var_name]),
                                name=con_name
                            )

        # time windows
        for k in range(self.ins.vehicle_num_2nd):
            for i in self.graph.second_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                con_name_time_1 = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{k}'

                lq = LinExpr()
                lq.addTerms([1, -1], [self.varzeta_c_k2[var_zeta_name], self.tau_c_k2[var_tau_name]])
                self.second_cons[con_name_time_1] = self.model.addConstr(
                    lq <= 0,
                    name=con_name_time_1
                )

                lq = LinExpr()
                lq.addTerms([1], [self.tau_c_k2[var_tau_name]])
                con_name_time_2 = '2nd-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_2] = self.model.addConstr(
                    self.graph.vertex_dict[i].ready_time <= lq,
                    name=con_name_time_2
                )

                con_name_time_3 = '2nd-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_3] = self.model.addConstr(
                    lq <= self.graph.vertex_dict[i].due_time,
                    name=con_name_time_3
                )

                for j in self.graph.second_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.second_echelon_graph.arc_dict and \
                            self.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k) + '_k2'
                        con_name = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_c_k2[var_tau_name] + self.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - \
                              self.varzeta_c_k2[var_zeta_name_2]
                        rhs = (1 - self.var_y[var_name]) * self.grb_params.big_m

                        self.second_cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def add_second_cons_no_select(self):
        """ second echelon """
        # start
        # satellite 每个从satellite as depot 出发的车都需要回到对应的satellite as depot
        for k in range(self.ins.vehicle_num_2nd):
            for s in self.graph.sate_list:
                # start
                lhs_start = LinExpr()
                lhs_start_coe = []
                lhs_start_var = []

                for j in self.graph.sate_serv_cus[s]:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_start_coe.append(1)
                        lhs_start_var.append(self.var_y[var_y_name])
                lhs_start.addTerms(lhs_start_coe, lhs_start_var)
                con_name_start = '2nd_con_start_' + str(s) + '_' + str(k)
                self.second_cons[con_name_start] = self.model.addConstr(
                    lhs_start <= 1,
                    name=con_name_start
                )

                # # return
                # lhs_end = LinExpr()
                # lhs_en_coe = []
                # lhs_en_var = []
                #
                # for i in self.graph.sate_serv_cus[s]:
                #     if self.judge_arc(arc_id=(i, self.graph.sate_to_depot[s]),
                #                       graph=self.graph.second_echelon_graph):
                #         var_y_name = 'y_' + str(i) + '_' + str(self.graph.sate_to_depot[s]) + '_' + str(k)
                #         lhs_en_coe.append(RepairOperators)
                #         lhs_en_var.append(self.var_y[var_y_name])
                # lhs_end.addTerms(lhs_en_coe, lhs_en_var)
                # con_name_end = '2nd_con_return_' + str(k)
                # self.second_cons[con_name_end] = self.model.addConstr(
                #     lhs_end <= RepairOperators,
                #     name=con_name_end
                # )
                #
                # # start equ return
                # con_name = '2nd_con_start_equ_return-' + str(s) + '_' + str(k)
                # self.first_cons[con_name] = self.model.addConstr(
                #     lhs_start == lhs_end,
                #     name=con_name
                # )

        # 每个customer只能被访问一次
        for c in self.graph.customer_list:

            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            for k_od in range(len(self.graph.od_o_list)):
                var_r_name = 'r_' + str(c) + '_' + str(k_od)
                lhs_coe_1.append(1)
                lhs_var_1.append(self.var_r[var_r_name])
            lhs_1.addTerms(lhs_coe_1, lhs_var_1)

            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            for i in self.graph.second_echelon_list:

                if self.judge_arc(arc_id=(i, c),
                                  graph=self.graph.second_echelon_graph):
                    for k in range(self.ins.vehicle_num_2nd):
                        var_y_name = 'y_' + str(i) + '_' + str(c) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_y[var_y_name])
            lhs_2.addTerms(lhs_coe_2, lhs_var_2)

            con_name = '2nd_customer_visit-' + str(c)
            self.second_cons[con_name] = self.model.addConstr(
                1 == lhs_1 + lhs_2,
                name=con_name
            )
            # self.second_cons[con_name] = self.model.addConstr(
            #     RepairOperators == lhs_2,
            #     name=con_name
            # )

            # con_name = '2nd_customer_visit-2-' + str(c)
            # self.second_cons[con_name] = self.model.addConstr(
            #     lhs_1 + lhs_2 <= RepairOperators.RepairOperators,
            #     name=con_name
            # )

        # 每个车从只能服务一个sate
        for k in range(self.ins.vehicle_num_2nd):
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []

            for s in self.graph.sate_list:
                for j in self.graph.sate_serv_cus[s]:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_coe.append(1)
                        lhs_var.append(self.var_y[var_y_name])
            lhs.addTerms(lhs_coe, lhs_var)
            con_name = '2nd_1service_sate_' + str(k)
            self.second_cons[con_name] = self.model.addConstr(
                lhs <= 1,
                name=con_name
            )

        # flow balance
        # 流平衡应该是对于每个车的
        for l in self.graph.customer_list:

            for k in range(self.ins.vehicle_num_2nd):
                lhs = LinExpr()
                lhs_coe = []
                lhs_var = []

                # in
                visit_list_1 = self.graph.customer_list + [self.graph.cus_belong_sate[l]]
                for i in visit_list_1:
                    # if self.judge_arc(arc_id=(i, l),
                    #                   graph=self.graph.second_echelon_graph):
                    if i != l:
                        if self.graph.second_echelon_graph.arc_dict[i, l].adj == 1:
                            var_y_name_1 = 'y_' + str(i) + '_' + str(l) + '_' + str(k)
                            lhs_coe.append(1)
                            lhs_var.append(self.var_y[var_y_name_1])

                # out
                visit_list_2 = self.graph.customer_list + [self.graph.sate_to_depot[self.graph.cus_belong_sate[l]]]
                for j in visit_list_2:
                    # if self.judge_arc(arc_id=(l, j),
                    #                   graph=self.graph.second_echelon_graph):
                    if j != l:
                        if self.graph.second_echelon_graph.arc_dict[l, j].adj == 1:
                            var_y_name_2 = 'y_' + str(l) + '_' + str(j) + '_' + str(k)
                            lhs_coe.append(-1)
                            lhs_var.append(self.var_y[var_y_name_2])

                lhs.addTerms(lhs_coe, lhs_var)
                con_name = '2nd-flow_balance-' + str(l) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs == 0,
                    name=con_name
                )

        # 对于每个从sate出发的车，都需要回到相应的sate_to_depot
        for s in self.graph.sate_list:
            sate_depot = self.graph.sate_to_depot[s]

            for k in range(self.ins.vehicle_num_2nd):

                # start
                lhs_1 = LinExpr()
                lhs_coe_1 = []
                lhs_var_1 = []

                for j in self.graph.sate_serv_cus[s]:
                    if self.judge_arc(arc_id=(s, j),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name_1 = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                        lhs_coe_1.append(1)
                        lhs_var_1.append(self.var_y[var_y_name_1])
                lhs_1.addTerms(lhs_coe_1, lhs_var_1)

                # return
                lhs_2 = LinExpr()
                lhs_coe_2 = []
                lhs_var_2 = []

                for i in self.graph.sate_serv_cus[s]:
                    if self.judge_arc(arc_id=(i, sate_depot),
                                      graph=self.graph.second_echelon_graph):
                        var_y_name_2 = 'y_' + str(i) + '_' + str(sate_depot) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_y[var_y_name_2])
                lhs_2.addTerms(lhs_coe_2, lhs_var_2)

                con_name = '2nd-sate_balance-' + str(s) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs_1 == lhs_2,
                    name=con_name
                )

        # vehicle balance
        for k in range(self.ins.vehicle_num_2nd):

            # start
            for s in self.ins.graph.sate_list:
                lhs = LinExpr()
                lhs_coe = []
                lhs_var = []

                rhs = LinExpr()
                rhs_coe = []
                rhs_var = []

                for j in self.ins.graph.second_echelon_graph.vertex_id_list:
                    if s != j:
                        if self.ins.graph.second_echelon_graph.arc_dict[(s, j)].adj == 1:
                            var_y_name_1 = 'y_' + str(s) + '_' + str(j) + '_' + str(k)
                            lhs_coe.append(1)
                            lhs_var.append(self.var_y[var_y_name_1])

                for i in self.ins.graph.second_echelon_graph.vertex_id_list:
                    if i != self.ins.graph.sate_to_depot[s]:
                        if self.ins.graph.second_echelon_graph.arc_dict[
                            (i, self.ins.graph.sate_to_depot[s])].adj == 1:
                            var_y_name_2 = 'y_' + str(i) + '_' + str(self.ins.graph.sate_to_depot[s]) + '_' + str(k)
                            rhs_coe.append(1)
                            rhs_var.append(self.var_y[var_y_name_2])

                lhs.addTerms(lhs_coe, lhs_var)
                rhs.addTerms(rhs_coe, rhs_var)

                con_name = '2nd-con_vehicle_balance-' + str(self.ins.graph.sate_to_depot[s]) + '_' + str(k)
                self.second_cons[con_name] = self.model.addConstr(
                    lhs == rhs,
                    name=con_name
                )

        for k in range(self.ins.vehicle_num_2nd):

            for i in self.ins.graph.customer_list:
                for j in self.ins.graph.customer_list:
                    if i != j:
                        if self.ins.graph.second_echelon_graph.arc_dict[(i, j)].adj == 1:
                            var_y_name = 'y_' + str(i) + '_' + str(j) + '_' + str(k)

                            lhs = LinExpr()
                            lhs_coe = []
                            lhs_var = []

                            for s in self.ins.graph.sate_list:
                                for l in self.ins.graph.second_echelon_graph.vertex_id_list:
                                    if s != l:
                                        if self.ins.graph.second_echelon_graph.arc_dict[(s, l)].adj == 1:
                                            var_y_name_start = 'y_' + str(s) + '_' + str(l) + '_' + str(k)
                                            lhs_coe.append(1)
                                            lhs_var.append(self.var_y[var_y_name_start])
                            lhs.addTerms(lhs_coe, lhs_var)

                            con_name = '2nd_must_start_from_sate-' + str(i) + '_' + str(j) + '_' + str(k)
                            self.second_cons[con_name] = self.model.addConstr(
                                self.var_y[var_y_name] <= lhs,
                                name=con_name
                            )

        # capacity
        # customers to satellites
        for i in self.graph.second_echelon_list:
            for k in range(self.ins.vehicle_num_2nd):
                con_name_capacity_1 = '2nd-3-con_capacity-1_' + f'{i}' + '_' + f'{k}'
                lq = LinExpr()
                var_w_1 = 'w_' + str(i) + '_' + str(k) + '_k2'
                lq.addTerms([1], [self.w_c_k2[var_w_1]])
                self.second_cons[con_name_capacity_1] = self.model.addConstr(
                    self.graph.vertex_dict[i].demand <= lq,
                    name=con_name_capacity_1
                )

                for j in self.graph.second_echelon_list:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.graph.second_echelon_graph):
                        capacity_lq = LinExpr()

                        var_w_2 = 'w_' + str(j) + '_' + str(k) + '_k2'
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        con_name = '2nd-3-con_capacity_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'

                        capacity_lq_coe = [1, -1,
                                           self.graph.vertex_dict[j].demand + self.ins.model_para.vehicle_2_capacity]
                        capacity_lq_var = [self.w_c_k2[var_w_1], self.w_c_k2[var_w_2], self.var_y[var_name]]
                        capacity_lq.addTerms(capacity_lq_coe, capacity_lq_var)

                        self.second_cons[con_name] = self.model.addConstr(
                            capacity_lq <= self.ins.model_para.vehicle_2_capacity,
                            name=con_name
                        )

        # time windows
        for k in range(self.ins.vehicle_num_2nd):
            for i in self.graph.second_echelon_list:
                var_zeta_name = 'var_zeta_' + str(i) + '_' + str(k) + '_k2'
                var_tau_name = 'tau_' + str(i) + '_' + str(k) + '_k2'
                con_name_time_1 = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{k}'

                lq = LinExpr()
                lq.addTerms([1, -1], [self.varzeta_c_k2[var_zeta_name], self.tau_c_k2[var_tau_name]])
                self.second_cons[con_name_time_1] = self.model.addConstr(
                    lq <= 0,
                    name=con_name_time_1
                )

                lq = LinExpr()
                lq.addTerms([1], [self.tau_c_k2[var_tau_name]])
                con_name_time_2 = '2nd-4-con_time_window_1-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_2] = self.model.addConstr(
                    self.graph.vertex_dict[i].ready_time <= lq,
                    name=con_name_time_2
                )

                con_name_time_3 = '2nd-4-con_time_window_2-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_name_time_3] = self.model.addConstr(
                    lq <= self.graph.vertex_dict[i].due_time,
                    name=con_name_time_3
                )

                for j in self.graph.second_echelon_list:
                    arc_id = (i, j)
                    if arc_id in self.graph.second_echelon_graph.arc_dict and \
                            self.graph.second_echelon_graph.arc_dict[arc_id].adj == 1:
                        var_name = 'y_' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        var_zeta_name_2 = 'var_zeta_' + str(j) + '_' + str(k) + '_k2'
                        con_name = '2nd-4-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        lhs = self.tau_c_k2[var_tau_name] + self.graph.second_echelon_graph.arc_dict[
                            arc_id].distance - \
                              self.varzeta_c_k2[var_zeta_name_2]
                        rhs = (1 - self.var_y[var_name]) * self.grb_params.big_m

                        self.second_cons[con_name] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_name
                        )

    def add_binding_cons(self):
        """
        \varzeta_j^{k2} >= \tau_i^{k1} + c_{ij} + ServiveTime_i + M(2 - y_{ijk2} - \sum_{(hi)\in Arc1}x_{hik1} )
        :return:
        """
        for k2 in range(self.ins.vehicle_num_2nd):
            for j in self.graph.customer_list:
                var_zeta_name2 = 'var_zeta_' + str(j) + '_' + str(k2) + '_k2'

                for k1 in range(self.ins.vehicle_num_1st):
                    for i in self.graph.sate_list:
                        if self.judge_arc(arc_id=(i, j),
                                          graph=self.graph.second_echelon_graph):
                            var_zeta_name1 = 'var_zeta_' + str(i) + '_' + str(k1) + '_k1'

                            lhs = LinExpr()
                            lhs_coe = []
                            lhs_var = []

                            for h in self.graph.first_echelon_list:
                                if self.judge_arc(arc_id=(h, i),
                                                  graph=self.graph.first_echelon_graph):
                                    var_x_name = 'x_' + str(h) + '_' + str(i) + '_' + str(k1)
                                    lhs_coe.append(1)
                                    lhs_var.append(self.var_x[var_x_name])
                            lhs.addTerms(lhs_coe, lhs_var)

                            var_y_name = 'y_' + str(i) + '_' + str(j) + '_' + str(k2)
                            con_name = '1st_and_2nd-' + str(k2) + '_' + str(j) + '_' + str(k1) + '_' + str(i)
                            self.binding_cons[con_name] = self.model.addConstr(
                                self.varzeta_c_k2[var_zeta_name2] >= self.varzeta_s_k1[var_zeta_name1] +
                                self.graph.second_echelon_graph.arc_dict[
                                    (i, j)].distance + self.grb_params.p - self.grb_params.big_m * (
                                        2 - self.var_y[var_y_name] - lhs),
                                name=con_name
                            )

    def add_od_cons_pdp(self):
        """ pdp model """
        # 每个customer 都需要被访问
        for c in self.graph.customer_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []

            for k in range(len(self.graph.od_o_list)):
                var_name = 'r_' + str(c) + '_' + str(k)

                lhs_coe.append(1)
                lhs_var.append(self.var_r[var_name])

            lhs.addTerms(lhs_coe, lhs_var)
            con_name = 'od-customer_assign-' + str(c)
            self.od_cons[con_name] = self.model.addConstr(
                lhs <= 1,
                name=con_name
            )

        # 每个车都应该由起始点出发（各自的origin），和回到destination
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            lhs_1 = LinExpr()
            lhs_coe_1 = []
            lhs_var_1 = []

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [d]
            for j in visit_list:
                if (o, j) in self.graph.pdp_graph.arc_dict and self.judge_arc(arc_id=(o, j),
                                                                              graph=self.graph.pdp_graph):
                    var_name_1 = 'z_' + str(o) + '_' + str(j) + '_' + str(k)
                    lhs_coe_1.append(1)
                    lhs_var_1.append(self.var_z[var_name_1])
            lhs_1.addTerms(lhs_coe_1, lhs_var_1)

            lhs_2 = LinExpr()
            lhs_coe_2 = []
            lhs_var_2 = []

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [o]
            for i in visit_list:

                if (i, d) in self.graph.pdp_graph.arc_dict and self.judge_arc(arc_id=(i, d),
                                                                              graph=self.graph.pdp_graph):
                    var_name_2 = 'z_' + str(i) + '_' + str(d) + '_' + str(k)
                    lhs_coe_2.append(1)
                    lhs_var_2.append(self.var_z[var_name_2])
            lhs_2.addTerms(lhs_coe_2, lhs_var_2)
            # lhs_2.addTerms(lhs_coe_2, lhs_var_2)

            con_name_1 = 'od-start-' + str(k)
            self.od_cons[con_name_1] = self.model.addConstr(
                lhs_1 == 1,
                name=con_name_1
            )

            con_name_2 = 'od-return-' + str(k)
            self.od_cons[con_name_2] = self.model.addConstr(
                lhs_2 == 1,
                name=con_name_2
            )

        # 只有分配到任务的车辆才会访问客户点
        for c in self.graph.customer_list:
            p = self.graph.pdp_dict.inverse[c]
            d = c

            for k in range(len(self.graph.od_o_list)):
                var_name = 'r_' + str(c) + '_' + str(k)

                lhs_1 = LinExpr()
                lhs_coe_1 = []
                lhs_var_1 = []

                visit_list = self.graph.pickup_id_list + self.graph.customer_list + [self.graph.od_o_list[k]]
                for l in visit_list:
                    if (l, p) in self.graph.pdp_graph.arc_dict and self.judge_arc(arc_id=(l, p),
                                                                                  graph=self.graph.pdp_graph):
                        var_name_1 = 'z_' + str(l) + '_' + str(p) + '_' + str(k)
                        lhs_coe_1.append(1)
                        lhs_var_1.append(self.var_z[var_name_1])
                lhs_1.addTerms(lhs_coe_1, lhs_var_1)

                lhs_2 = LinExpr()
                lhs_coe_2 = []
                lhs_var_2 = []

                for i in visit_list:
                    if (i, d) in self.graph.pdp_graph.arc_dict and self.judge_arc(arc_id=(i, d),
                                                                                  graph=self.graph.pdp_graph):
                        var_name_2 = 'z_' + str(i) + '_' + str(d) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_z[var_name_2])
                lhs_2.addTerms(lhs_coe_2, lhs_var_2)

                con_name_1 = 'od-assign_visit_1-' + str(c) + '_' + str(k)
                self.od_cons[con_name_1] = self.model.addConstr(
                    lhs_1 == lhs_2,
                    name=con_name_1
                )

                con_name_2 = 'od-assign_visit_2-' + str(c) + '_' + str(k)
                self.od_cons[con_name_2] = self.model.addConstr(
                    self.var_r[var_name] == lhs_2,
                    name=con_name_2
                )

        # capacity
        # note that, demand at sate + and customer -
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            for c in self.graph.customer_list:
                var_r_name = 'r_' + str(c) + '_' + str(k)
                con_name = 'od-customer_capacity-' + str(c) + '_' + str(k)

                lq = LinExpr()
                lq.addTerms([1], [self.var_r[var_r_name]])

                self.od_cons[con_name] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_od_capacity / self.graph.vertex_dict[c].demand,
                    name=con_name
                )

            var_name = 'w_' + str(o) + '_' + str(k) + '_k_od'
            lq = LinExpr()
            lq.addTerms([1], [self.w_c_k_od[var_name]])

            con_name = 'od_capacity_start-' + str(k)
            self.od_cons[con_name] = self.model.addConstr(
                lq <= 0,
                name=con_name
            )

            visit_list = self.graph.customer_list + self.graph.pickup_id_list + [o, d]

            for i in visit_list:
                for j in visit_list:
                    if i != j:
                        if self.judge_arc(arc_id=(i, j),
                                          graph=self.graph.pdp_graph):
                            if j in self.graph.pickup_id_list:
                                demand = self.graph.vertex_dict[j].demand
                            elif j in self.graph.customer_list:
                                demand = -self.graph.vertex_dict[j].demand
                            else:
                                demand = 0

                            var_name_1 = 'w_' + str(i) + '_' + str(k) + '_k_od'
                            var_name_2 = 'w_' + str(j) + '_' + str(k) + '_k_od'
                            var_name_3 = 'z_' + str(i) + '_' + str(j) + '_' + str(k)

                            lq = LinExpr()
                            lq.addTerms([1, -1, self.grb_params.vehicle_od_capacity],
                                        [self.w_c_k_od[var_name_1], self.w_c_k_od[var_name_2], self.var_z[var_name_3]])

                            con_name = 'od_capacity_travel-' + str(i) + '_' + str(j) + '_' + str(k)
                            self.od_cons[con_name] = self.model.addConstr(
                                lq <= self.grb_params.vehicle_od_capacity - demand,
                                name=con_name
                            )

            for i in visit_list:

                if i in self.graph.pickup_id_list:
                    demand = self.graph.vertex_dict[i].demand
                elif i in self.graph.customer_list:
                    demand = -self.graph.vertex_dict[i].demand
                else:
                    demand = 0

                lq_2 = LinExpr()
                lq_2_var = []
                lq_2_coe = []

                for j in visit_list:
                    if self.judge_arc(arc_id=(i, j),
                                      graph=self.graph.pdp_graph):
                        lq_2_coe.append(1)

                        var_name = 'z_' + str(i) + '_' + str(j) + '_' + str(k)
                        lq_2_var.append(self.var_z[var_name])
                lq_2.addTerms(lq_2_coe, lq_2_var)

                var_name = 'w_' + str(i) + '_' + str(k) + '_k_od'

                lq = LinExpr()
                lq.addTerms([1], [self.w_c_k_od[var_name]])

                con_name_1 = 'od_capacity_lb-' + str(i) + '_' + str(k)
                self.od_cons[con_name_1] = self.model.addConstr(
                    demand * lq_2 <= lq,
                    name=con_name_1
                )

                con_name_2 = 'od_capacity_ub-' + str(i) + '_' + str(k)
                self.od_cons[con_name_2] = self.model.addConstr(
                    lq <= self.grb_params.vehicle_od_capacity,
                    name=con_name_2
                )

        # time window
        # RepairOperators. 服务时间 ≥ 到达时间
        for k in range(len(self.graph.od_o_list)):
            origin = self.graph.od_o_list[k]
            destination = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [origin, destination]

            for i in visit_list:
                arrive = 'varzeta_' + str(i) + '_' + str(k)
                service = 'tau_' + str(i) + '_' + str(k)

                lhs = LinExpr()
                lhs.addTerms([1, -1], [self.varzeta_c_k_od[arrive], self.tau_c_k_od[service]])

                con_name = 'od_service_after_arrive-' + str(i) + '_' + str(k)
                self.od_cons[con_name] = self.model.addConstr(
                    lhs <= 0,
                    name=con_name
                )

            # 2.首先到达pickup，then delivery
            for i in self.graph.pickup_id_list:
                p = i
                d = self.graph.pdp_dict[i]

                arrive_p = 'varzeta_' + str(p) + '_' + str(k)
                arrive_d = 'varzeta_' + str(d) + '_' + str(k)

                lhs = LinExpr()
                lhs.addTerms(
                    [1, -1], [self.varzeta_c_k_od[arrive_p], self.varzeta_c_k_od[arrive_d]],
                )

                con_name = 'od_delivery_after_pickup-' + str(p) + '_' + str(k)
                self.od_cons[con_name] = self.model.addConstr(
                    lhs <= 0,
                    name=con_name
                )

        # 3.连续性
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list + [o, d]

            for i in visit_list:
                for j in visit_list:
                    if i != j:
                        if self.judge_arc(arc_id=(i, j),
                                          graph=self.graph.pdp_graph):
                            if i in self.graph.customer_list:
                                service_time = self.grb_params.service_time
                            elif i in self.graph.pickup_id_list:
                                service_time = self.grb_params.p
                            else:
                                service_time = 0

                            arrive = 'varzeta_' + str(j) + '_' + str(k)
                            service = 'tau_' + str(i) + '_' + str(k)
                            travel = 'z_' + str(i) + '_' + str(j) + '_' + str(k)

                            lhs = LinExpr()
                            lhs.addTerms([1, -1, self.grb_params.big_m],
                                         [self.tau_c_k_od[service], self.varzeta_c_k_od[arrive], self.var_z[travel]])
                            con_name_travel = 'od_d_travel_p-' + str(i) + '_' + str(j) + '_' + str(k)

                            self.od_cons[con_name_travel] = self.model.addConstr(
                                lhs <= self.grb_params.big_m - self.graph.pdp_graph.arc_dict[
                                    i, j].distance - service_time,
                                name=con_name_travel
                            )

        # flow balance
        # 对于每个p和d进去的等于流出的
        for k in range(len(self.graph.od_o_list)):
            o = self.graph.od_o_list[k]
            d = self.graph.od_d_list[k]

            visit_list = self.graph.pickup_id_list + self.graph.customer_list

            for l in visit_list:
                lhs_1 = LinExpr()
                lhs_coe_1 = []
                lhs_var_1 = []

                lhs_2 = LinExpr()
                lhs_coe_2 = []
                lhs_var_2 = []

                set_v = self.graph.pickup_id_list + self.graph.customer_list + [o, d]

                # out
                for j in set_v:
                    if self.judge_arc(arc_id=(l, j),
                                      graph=self.graph.pdp_graph):
                        var_name_1 = 'z_' + str(l) + '_' + str(j) + '_' + str(k)
                        lhs_coe_1.append(1)
                        lhs_var_1.append(self.var_z[var_name_1])

                # in
                for i in set_v:
                    if self.judge_arc(arc_id=(i, l),
                                      graph=self.graph.pdp_graph):
                        var_name_2 = 'z_' + str(i) + '_' + str(l) + '_' + str(k)
                        lhs_coe_2.append(1)
                        lhs_var_2.append(self.var_z[var_name_2])

                lhs_1.addTerms(lhs_coe_1, lhs_var_1)
                con_name_1 = 'od_flow_balance_1-' + str(l) + '_' + str(k)
                self.od_cons[con_name_1] = self.model.addConstr(
                    lhs_1 <= 1,
                    name=con_name_1
                )

                lhs_2.addTerms(lhs_coe_2, lhs_var_2)
                con_name_2 = 'od_flow_balance_2-' + str(l) + '_' + str(k)
                self.od_cons[con_name_2] = self.model.addConstr(
                    lhs_2 <= 1,
                    name=con_name_2
                )

                con_name_3 = 'od_flow_balance_3-' + str(l) + '_' + str(k)
                self.od_cons[con_name_3] = self.model.addConstr(
                    lhs_1 == lhs_2,
                    name=con_name_3
                )

    def get_var_index(self):
        var_list_str = []

        for var in self.model.getVars():

            if var.x >= 0.5:
                if var.varName.startswith('z'):
                    var_list_str.append(var.varName)

        for var_str in var_list_str:
            matches = re.findall(r'_(\d+)', var_str)

            subscripts = [int(match) for match in matches]

            if subscripts[-1] not in self.od_travel_vars:
                self.od_travel_vars[subscripts[-1]] = [subscripts]

            else:
                self.od_travel_vars[subscripts[-1]].append(subscripts)

    def get_od_routes(self):

        for i in self.od_travel_vars.keys():
            var_ = self.od_travel_vars[i]

            o = self.ins.graph.od_o_list[i]
            d = self.ins.graph.od_d_list[i]

            self.od_routes[i] = [o]

            while self.od_routes[i][-1] != d:

                for var in var_:

                    if self.od_routes[i][-1] == var[0]:
                        self.od_routes[i].append(var[1])

    def get_od_info(self):

        self.get_var_index()
        self.get_od_routes()

        for od_id in self.od_routes.keys():
            self.od_info[od_id] = []
            self.od_info[od_id].append(self.od_routes[od_id])
            self.od_info[od_id].append(calc_od_route_cost(route=self.od_routes[od_id],
                                                          ins=self.ins))

    # *********************************************************************************************************
    #                                                    NEW
    # *********************************************************************************************************
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

    def add_second_cons_no_select_new(self):
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

                con_ser_after_arr = '2nd-con_ser_after_arr-' + f'{i}' + '_' + f'{k}'
                self.second_cons[con_ser_after_arr] = self.model.addConstr(
                    self.varzeta_c_k2[i, k] <= self.tau_c_k2[i, k],
                    name=con_ser_after_arr
                )

                for j in self.graph.second_echelon_list:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        lhs = self.tau_c_k2[i, k] + self.grb_params.service_time + self.graph.arc_dict[
                            i, j].distance - self.varzeta_c_k2[j, k]
                        rhs = (1 - self.var_y[i, j, k]) * self.grb_params.big_m

                        con_time_window = '2nd-con_time_window-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'
                        self.second_cons[con_time_window] = self.model.addConstr(
                            lhs <= rhs,
                            name=con_time_window
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