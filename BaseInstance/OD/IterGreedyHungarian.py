# -*- coding: utf-8 -*-
# @Time     : 2024-04-23-14:27
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from OdCustomerMatch import OdCustomerMatch
from copy import deepcopy
import numpy as np
import pandas as pd
from gurobipy import *
import time


class IterGreedyHungarian(object):

    def __init__(self,
                 ins,
                 initial_value):
        """
        RepairOperators: Input Instance,
        2: Output OD-Customers match result
        3: Initialization: feasible=True
        4: gen Matrix
        5: if Matrix all inf.:
        6:      feasible=False
        7: while feasible:
        8:      do Hungarian Algorithm match
        9:      add OD-Customer match result
        10:     Update Matrix
        11:     if Matrix all inf.:
        12:         feasible=False
        """
        self.ins = ins

        self.matcher = OdCustomerMatch(ins=self.ins)
        self.rest_customer = deepcopy(ins.graph.customer_list)

        # self.matrix = np.full(shape=(len(self.rest_customer), self.ins.od_num), fill_value=1000.0)
        rows, cols = len(self.rest_customer), self.ins.od_num

        """ set2-3 """
        self.initial_value = 1000.0
        """ set4 """
        # self.initial_value = initial_value

        data = np.full((rows, cols), self.initial_value)
        self.matrix = pd.DataFrame(data, columns=[od for od in self.ins.graph.od_o_list],
                                   index=[c for c in self.rest_customer])

        self.od_start_time = {od: self.ins.graph.vertex_dict[od].ready_time for od in self.ins.graph.od_o_list}
        self.od_ser_cus = {od: [[], set(), 0., 0, 0.] for od in
                           self.ins.graph.od_o_list}
        # RepairOperators: cus_id, 2: sate, 3: cost, 4: serviced time, 5: demand
        self.serv_timeTable = {od: [] for od in self.ins.graph.od_o_list}
        self.od_routes = {od: [od] for od in self.ins.graph.od_o_list}

        self.feasible = True

        """ tsp pdp """
        self.model = Model('Tsp_pdp')
        self.model.setParam('TimeLimit', 120)
        self.var_x = {}  # travel variables
        self.var_w = {}  # capacity variables
        self.var_t = {}  # arrive time
        self.var_s = {}  # service time
        self.cons = {}
        self.obj = LinExpr()

    def gen_od_cus_matrix(self):
        """
        被服务后，rest_customer会移除
        """
        count_true = 0

        pre_matrix = deepcopy(self.matrix)

        rows, cols = len(self.rest_customer), self.ins.od_num

        data = np.full((rows, cols), self.initial_value)
        self.matrix = pd.DataFrame(data, columns=[od for od in self.ins.graph.od_o_list],
                                   index=[c for c in self.rest_customer])

        for od in range(len(self.ins.graph.od_o_list)):
            o = self.ins.graph.od_o_list[od]
            d = self.ins.graph.od_d_list[od]

            for c in range(len(self.rest_customer)):
                cur_cus = self.rest_customer[c]
                cur_sate = self.ins.graph.cus_belong_sate[cur_cus]

                if self.ins.graph.vertex_dict[cur_cus].demand > self.ins.model_para.vehicle_od_capacity or \
                        self.od_ser_cus[o][4] + self.ins.graph.vertex_dict[
                    cur_cus].demand > self.ins.model_para.vehicle_od_capacity:
                    self.matrix.loc[cur_cus, o] = self.initial_value

                else:
                    if len(self.od_ser_cus[o][0]) == 0:
                        # 还没服务cus
                        arc_1 = (o, cur_sate)
                        arc_2 = (cur_sate, cur_cus)
                        arc_3 = (cur_cus, d)

                        # cur_od_cost = round(
                        #     (self.ins.graph.od_graph.arc_dict[arc_1].distance + self.ins.graph.od_graph.arc_dict[
                        #         arc_2].distance + self.ins.graph.od_graph.arc_dict[arc_3].distance -
                        #      self.ins.graph.od_graph.arc_dict[(o, d)].distance), 2)
                        cur_od_cost = round(
                            (self.ins.graph.od_graph.arc_dict[arc_1].distance + self.ins.graph.od_graph.arc_dict[
                                arc_2].distance + self.ins.graph.od_graph.arc_dict[arc_3].distance), 2)

                        # 判定条件
                        # RepairOperators. arc
                        cond_1 = (self.ins.graph.od_graph.arc_dict[arc_1].adj == 1) and (
                                self.ins.graph.od_graph.arc_dict[
                                    arc_2].adj == 1) and (
                                         self.ins.graph.od_graph.arc_dict[arc_3].adj == 1)
                        # 2. 满足取货的时间窗
                        cur_arrive_sate_time = self.ins.graph.vertex_dict[o].ready_time + \
                                               self.ins.graph.od_graph.arc_dict[
                                                   arc_1].distance
                        if cur_arrive_sate_time < self.ins.graph.vertex_dict[cur_sate].ready_time:
                            cur_arrive_sate_time = self.ins.graph.vertex_dict[cur_sate].ready_time
                        cond_2 = (cur_arrive_sate_time <= self.ins.graph.vertex_dict[cur_sate].due_time)

                        # 3. 满足送货的时间窗
                        cur_arrive_cus_time = cur_arrive_sate_time + self.ins.model_para.p + \
                                              self.ins.graph.od_graph.arc_dict[arc_2].distance
                        if cur_arrive_cus_time < self.ins.graph.vertex_dict[cur_cus].ready_time:
                            cur_arrive_cus_time = self.ins.graph.vertex_dict[cur_cus].ready_time
                        cond_3 = (cur_arrive_cus_time <= self.ins.graph.vertex_dict[cur_cus].due_time)

                        # 4. 满足od任务的时间窗
                        cur_arrive_d_time = cur_arrive_cus_time + self.ins.model_para.service_time + \
                                            self.ins.graph.od_graph.arc_dict[arc_3].distance
                        cond_4 = (cur_arrive_d_time <= self.ins.graph.vertex_dict[d].due_time)

                        if cond_1 and cond_2 and cond_3 and cond_4:
                            # matrix index 坐标
                            self.matrix.loc[cur_cus, o] = cur_od_cost if pre_matrix.loc[cur_cus, o] > cur_od_cost else \
                                self.matrix.loc[cur_cus, o]
                            # self.serv_timeTable[o].append((cur_cus, cur_arrive_cus_time))

                    else:
                        # 服务了cus，需要判断
                        if pre_matrix.loc[cur_cus, o] == self.initial_value:
                            # 这个cus不能被服务
                            continue

                        else:
                            if cur_sate in self.od_ser_cus[o][1]:
                                # 属于同一个sate
                                pre_cus = self.od_ser_cus[o][0][-1]

                                arc_4 = (pre_cus, cur_cus)
                                arc_5 = (cur_cus, d)

                                cur_travel = self.ins.graph.od_graph.arc_dict[arc_4].distance

                                cur_arrive_time = self.od_ser_cus[o][3] + cur_travel

                                # 判定条件
                                # arc
                                cond_5 = (self.ins.graph.od_graph.arc_dict[arc_4].adj == 1 and
                                          self.ins.graph.od_graph.arc_dict[arc_5].adj == 1)
                                # 6. 满足customer的时间窗
                                cond_6 = (cur_arrive_time <= self.ins.graph.vertex_dict[cur_cus].due_time)
                                if cur_arrive_time < self.ins.graph.vertex_dict[cur_cus].ready_time:
                                    cur_arrive_time = self.ins.graph.vertex_dict[cur_cus].ready_time

                                # 7. 满足od配送时间窗
                                con_7 = (
                                        cur_arrive_time + self.ins.model_para.service_time +
                                        self.ins.graph.od_graph.arc_dict[arc_5].distance <= self.ins.graph.vertex_dict[
                                            d].due_time
                                )

                                cur_od_cost = self.od_ser_cus[o][2] - self.ins.graph.od_graph.arc_dict[
                                    (pre_cus, d)].distance + self.ins.graph.od_graph.arc_dict[arc_4].distance + \
                                              self.ins.graph.arc_dict[arc_5].distance

                                if cond_5 and cond_6 and con_7:
                                    self.matrix.loc[cur_cus, o] = cur_od_cost

                                """     """
                                if (cond_5 and cond_6) and (not con_7):
                                    lst = deepcopy(self.od_ser_cus[o][0])
                                    lst.append(cur_cus)

                                    feasible, route, cost, service_time = self.calc_shortest_path(customer_list=lst,
                                                                                                  od_o=o)

                                    if feasible:
                                        self.matrix.loc[cur_cus, o] = cost
                                        # #######################################################
                                        # #######################################################
                                        self.od_ser_cus[o][3] = service_time
                                        # self.serv_timeTable[o].append((cur_cus, cur_arrive_time))

                            else:
                                # 不属于同一个sate，需要再去一次sate取货
                                pre_cus = self.od_ser_cus[o][0][-1]

                                arc_6 = (pre_cus, cur_sate)
                                arc_7 = (cur_sate, cur_cus)
                                arc_8 = (cur_cus, d)

                                # 满足sate时间窗
                                cur_arrive_sate_time = self.od_ser_cus[o][3] + self.ins.graph.arc_dict[arc_6].distance
                                if cur_arrive_sate_time < self.ins.graph.vertex_dict[cur_sate].ready_time:
                                    cur_arrive_sate_time = self.ins.graph.vertex_dict[cur_sate].ready_time

                                # 判定条件
                                # arc
                                con_8 = (self.ins.graph.od_graph.arc_dict[arc_6].adj == 1 and
                                         self.ins.graph.od_graph.arc_dict[arc_7].adj == 1 and
                                         self.ins.graph.od_graph.arc_dict[arc_8].adj == 1)

                                # 9. 满足sate取货时间窗
                                con_9 = (cur_arrive_sate_time <= self.ins.graph.vertex_dict[cur_sate].due_time)

                                # 满足cus时间窗
                                # 10. 满足cus时间窗
                                cur_arrive_cus_time = cur_arrive_sate_time + self.ins.model_para.p + \
                                                      self.ins.graph.od_graph.arc_dict[arc_7].distance
                                if cur_arrive_cus_time < self.ins.graph.vertex_dict[cur_cus].ready_time:
                                    cur_arrive_cus_time = self.ins.graph.vertex_dict[cur_cus].ready_time

                                con_10 = (
                                        cur_arrive_cus_time <= self.ins.graph.vertex_dict[cur_cus].due_time
                                )

                                # 11. 满足od时间窗
                                con_11 = (
                                        cur_arrive_cus_time + self.ins.model_para.service_time +
                                        self.ins.graph.arc_dict[
                                            arc_8].distance <= self.ins.graph.vertex_dict[d].due_time
                                )

                                if con_8 and con_9 and con_10 and con_11:
                                    cur_od_cost = self.od_ser_cus[o][2] - self.ins.graph.od_graph.arc_dict[
                                        (pre_cus, d)].distance + self.ins.graph.od_graph.arc_dict[
                                                      (pre_cus, cur_sate)].distance + self.ins.graph.od_graph.arc_dict[
                                                      (cur_sate, cur_cus)].distance + self.ins.graph.od_graph.arc_dict[
                                                      (cur_cus, d)].distance
                                    self.matrix.loc[cur_cus, o] = cur_od_cost
                                    # self.serv_timeTable[o].append((cur_cus, cur_arrive_cus_time))

    def gen_hungarian_dict(self):
        """  """
        hungarian_dict = {}
        feasible_cus_list = []

        for i in range(self.rest_customer):
            cur_cus = 'C_' + str(self.rest_customer[i])
            hungarian_dict[cur_cus] = {}

            for j in self.ins.graph.od_o_list:
                cur_od = 'OD_' + str(self.ins.graph.od_o_list[j])

                if self.matrix.loc[i, j] != np.inf:
                    hungarian_dict[cur_cus][cur_od] = -self.matrix.loc[i, j]

                    feasible_cus_list.append(cur_od)

                else:
                    # pass
                    hungarian_dict[cur_cus][cur_od] = -500

        hungarian_dict_cp = deepcopy(hungarian_dict)

        for cus in hungarian_dict_cp.keys():

            if not hungarian_dict_cp[cus].values():
                hungarian_dict.pop(cus)

        return hungarian_dict

    def ini_tsp_pdp(self):
        """
        lst = [6, 10]

        :return:
        """
        self.model = Model('Tsp_pdp')
        self.model.setParam('OutputFlag', 0)
        self.model.setParam('TimeLimit', 120)

        self.var_x = {}  # travel variables
        self.var_w = {}  # capacity variables
        self.var_t = {}  # arrive time
        self.var_s = {}  # service time
        self.cons = {}
        self.obj = LinExpr()

    def get_route(self, o):
        """  """
        route = [o]

        # feasible = True
        while route[-1] != self.ins.graph.o_to_d[o]:
            # length = len(route)

            for key in self.var_x:
                if self.var_x[key].x >= 0.5:
                    if key[0] == route[-1]:
                        route.append(key[1])

            # if length == len(route):
            #     feasible = False
        return route

    def calc_shortest_path(self,
                           customer_list,
                           od_o):
        """"  """

        self.build_shortest_path_model(customer_list=customer_list,
                                       od_o=od_o)

        self.model.optimize()

        if self.model.Status == 2:
            # optimal
            feasible = True

            route = self.get_route(o=od_o)
            cost = self.model.ObjVal
            service_time = self.var_s[route[-3]].x

            self.od_ser_cus[od_o][2] = cost

        else:
            route = None
            cost = self.initial_value
            service_time = None
            feasible = False

        return feasible, route, cost, service_time

    def build_shortest_path_model(self,
                                  customer_list,
                                  od_o):
        """"  """
        self.ini_tsp_pdp()

        # pick_up_list = [self.ins.graph.pdp_dict.inverse[c] for c in customer_list]
        pick_up_list = []

        # 判断离客户最近的sate
        for c in customer_list:
            sate = self.ins.graph.cus_belong_sate[c]
            sate_index = self.ins.graph.sate_list.index(sate)
            pick_up_list.append(self.ins.graph.pdp_dict.inverse[c][sate_index])

        """ 添加变量 """
        visit_list = pick_up_list + customer_list + [od_o, self.ins.graph.o_to_d[od_o]]

        for i in visit_list:
            self.var_w[i] = self.model.addVar(vtype=GRB.CONTINUOUS,
                                              lb=0, ub=self.ins.model_para.vehicle_od_capacity,
                                              name='c_' + str(i),
                                              column=None,
                                              obj=0
                                              )

            self.var_t[i] = self.model.addVar(vtype=GRB.CONTINUOUS,
                                              lb=0, ub=1440,
                                              name='a_' + str(i),
                                              column=None,
                                              obj=0
                                              )

            self.var_s[i] = self.model.addVar(vtype=GRB.CONTINUOUS,
                                              lb=self.ins.graph.vertex_dict[i].ready_time,
                                              ub=self.ins.graph.vertex_dict[i].due_time,
                                              name='s_' + str(i),
                                              column=None,
                                              obj=0
                                              )

            for j in visit_list:
                if i != j:
                    if self.ins.graph.pdp_graph.arc_dict[(i, j)].adj == 1:
                        self.var_x[i, j] = self.model.addVar(
                            vtype=GRB.BINARY,
                            lb=0, ub=1,
                            name='x_' + str(i) + '_' + str(j),
                            column=None,
                            obj=self.ins.graph.pdp_graph.arc_dict[(i, j)].distance
                        )

        """ 添加约束 """
        """start and return"""
        visit_start = pick_up_list + customer_list  # note that: 不能直接回到destination

        lhs = LinExpr()
        lhs_coe = []
        lhs_var = []
        for j in visit_start:
            if self.ins.graph.pdp_graph.arc_dict[(od_o, j)].adj == 1:
                lhs_coe.append(1)
                lhs_var.append(self.var_x[od_o, j])

        lhs.addTerms(lhs_coe, lhs_var)
        con_name = 'start_1-' + str(od_o)
        # self.cons[con_name] = self.model.addConstr(
        #     lhs >= 0.999,
        #     name=con_name
        # )
        # con_name = 'start_2-' + str(od_o)
        # self.cons[con_name] = self.model.addConstr(
        #     lhs <= RepairOperators,
        #     name=con_name
        # )
        self.cons[con_name] = self.model.addConstr(
            lhs == 1,
            name=con_name
        )

        visit_return = pick_up_list + customer_list  # note that: 不能直接由origin → destination

        lhs = LinExpr()
        lhs_coe = []
        lhs_var = []
        for i in visit_return:
            if self.ins.graph.pdp_graph.arc_dict[(i, self.ins.graph.o_to_d[od_o])].adj == 1:
                lhs_coe.append(1)
                lhs_var.append(self.var_x[i, self.ins.graph.o_to_d[od_o]])

        lhs.addTerms(lhs_coe, lhs_var)
        con_name = 'return_1-' + str(self.ins.graph.o_to_d[od_o])
        # self.cons[con_name] = self.model.addConstr(
        #     lhs >= 0.999,
        #     name=con_name
        # )
        # con_name = 'return_2-' + str(self.ins.graph.o_to_d[od_o])
        # self.cons[con_name] = self.model.addConstr(
        #     lhs <= RepairOperators,
        #     name=con_name
        # )
        self.cons[con_name] = self.model.addConstr(
            lhs == 1,
            name=con_name
        )

        """每个cus需要被访问"""
        visit_list = pick_up_list + customer_list
        for c in customer_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []

            for i in visit_list:
                if c != i:
                    if self.ins.graph.pdp_graph.arc_dict[(i, c)].adj == 1:
                        lhs_coe.append(1)
                        lhs_var.append(self.var_x[i, c])

            lhs.addTerms(lhs_coe, lhs_var)
            con_name = 'customer_1-' + str(c)
            self.cons[con_name] = self.model.addConstr(lhs >= 0.99, name=con_name)
            con_name = 'customer_2-' + str(c)
            self.cons[con_name] = self.model.addConstr(lhs <= 1, name=con_name)

        """flow balance"""
        visit_list = pick_up_list + customer_list
        visit_list_in = visit_list + [od_o]
        visit_list_out = visit_list + [self.ins.graph.o_to_d[od_o]]

        for l in visit_list:
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []
            for i in visit_list_in:
                if i != l:
                    if self.ins.graph.pdp_graph.arc_dict[(i, l)].adj == 1:
                        lhs_coe.append(1)
                        lhs_var.append(self.var_x[i, l])

            for j in visit_list_out:
                if j != l:
                    if self.ins.graph.pdp_graph.arc_dict[(l, j)].adj == 1:
                        lhs_coe.append(-1)
                        lhs_var.append(self.var_x[l, j])

            lhs.addTerms(lhs_coe, lhs_var)
            con_name = 'flow_balance-' + str(l)

            self.cons[con_name] = self.model.addConstr(
                lhs <= 0,
                name=con_name
            )

        """capacity"""
        # 起始点
        lq = LinExpr()
        lq.addTerms([1], [self.var_w[od_o]])

        con_name = 'capacity_start-' + str(od_o)
        self.cons[con_name] = self.model.addConstr(
            lq <= 0,
            name=con_name
        )

        visit_list = customer_list + pick_up_list + [od_o, self.ins.graph.o_to_d[od_o]]
        for i in visit_list:
            for j in visit_list:
                if i != j:
                    if i == od_o and j == self.ins.graph.o_to_d[od_o]:
                        pass
                    else:
                        if self.ins.graph.pdp_graph.arc_dict[(i, j)].adj == 1:
                            if j in pick_up_list:
                                demand = self.ins.graph.vertex_dict[j].demand
                            elif j in customer_list:
                                demand = -self.ins.graph.vertex_dict[j].demand
                            else:
                                demand = 0

                            lq = LinExpr()
                            lq.addTerms([1, -1, self.ins.model_para.vehicle_od_capacity],
                                        [self.var_w[i], self.var_w[j], self.var_x[i, j]])
                            con_name = 'capacity_travel-' + str(i) + '_' + str(j)
                            self.cons[con_name] = self.model.addConstr(
                                lq <= self.ins.model_para.vehicle_od_capacity - demand,
                                name=con_name
                            )

            if i in pick_up_list:
                demand = self.ins.graph.vertex_dict[i].demand
            elif i in customer_list:
                demand = -self.ins.graph.vertex_dict[i].demand
            else:
                demand = 0

            lq = LinExpr()
            lq.addTerms([1], [self.var_w[i]])

            con_name_1 = 'capacity_lb-' + str(i)
            self.cons[con_name_1] = self.model.addConstr(
                demand <= lq,
                name=con_name_1
            )

            con_name_2 = 'od_capacity_ub-' + str(i)
            self.cons[con_name_2] = self.model.addConstr(
                lq <= self.ins.model_para.vehicle_od_capacity,
                name=con_name_2
            )

        """time window"""
        # RepairOperators. 服务时间 ≥ 到达时间
        visit_list = customer_list + pick_up_list + [od_o, self.ins.graph.o_to_d[od_o]]
        for i in visit_list:
            arrive = self.var_t[i]
            service = self.var_s[i]

            lhs = LinExpr()
            lhs.addTerms([1, -1], [arrive, service])

            con_name = 'service_after_arrive-' + str(i)
            self.cons[con_name] = self.model.addConstr(
                lhs <= 0,
                name=con_name
            )

        # 2.首先到达pickup，then delivery
        for i in pick_up_list:
            p = i
            d = self.ins.graph.pdp_dict_corr[i]

            arrive_p = self.var_t[p]
            arrive_d = self.var_t[d]

            lhs = LinExpr()
            lhs.addTerms(
                [1, -1], [arrive_p, arrive_d],
            )

            con_name = 'od_service_after_arrive-' + str(p)
            self.cons[con_name] = self.model.addConstr(
                lhs <= 0,
                name=con_name
            )

            visit_list = pick_up_list + customer_list + [od_o]
            lhs = LinExpr()
            lhs_coe = []
            lhs_var = []

            for l in visit_list:
                if p != l:
                    if self.ins.graph.pdp_graph.arc_dict[(l, p)].adj == 1:
                        lhs_coe.append(1)
                        lhs_var.append(self.var_x[l, p])
                if d != l:
                    if self.ins.graph.pdp_graph.arc_dict[(l, d)].adj == 1:
                        lhs_coe.append(-1)
                        lhs_var.append(self.var_x[l, d])

            lhs.addTerms(lhs_coe, lhs_var)
            con_name = 'od_p_before_d-' + str(p)
            self.cons[con_name] = self.model.addConstr(
                lhs >= 0,
                name=con_name
            )

        # 3.连续性
        visit_list = customer_list + pick_up_list + [od_o, self.ins.graph.o_to_d[od_o]]
        for i in visit_list:
            for j in visit_list:
                if i != j:
                    if i == od_o and j == self.ins.graph.o_to_d[od_o]:
                        pass
                    else:
                        if self.ins.graph.pdp_graph.arc_dict[(i, j)].adj == 1:
                            if i in self.ins.graph.customer_list:
                                service_time = self.ins.model_para.service_time
                            elif i in self.ins.graph.pickup_id_list:
                                service_time = self.ins.model_para.p
                            else:
                                service_time = 0

                            arrive = self.var_t[j]
                            service = self.var_s[i]
                            travel = self.var_x[i, j]

                            lhs = LinExpr()
                            lhs.addTerms([1, -1, self.ins.model_para.big_m],
                                         [service, arrive, travel])
                            con_name_travel = 'd_travel_p-' + str(i) + '_' + str(j)

                            self.cons[con_name_travel] = self.model.addConstr(
                                lhs <= self.ins.model_para.big_m - self.ins.graph.pdp_graph.arc_dict[
                                    i, j].distance - service_time,
                                name=con_name_travel
                            )

    def do_match(self):
        dis_matrix = deepcopy(self.matrix.to_numpy())
        od_cus_match, customer_list_od, customer_list_alns = self.matcher.start_match(
            distance_matrix=dis_matrix,
            rest_cus_list=self.rest_customer)

        # for key, value in od_cus_match.items():
        #     self.ins.od_cus_matchDict[key] = value
        #
        #     self.ins.od_cost += value

        self.ins.customer_list_od += customer_list_od

        self.ins.customer_list_alns = customer_list_alns

        self.matcher.update_od_time(match_list=od_cus_match,
                                    iter_hun=self)

        for match in od_cus_match.keys():
            cus = list(match)[0]
            # od_o = self.ins.graph.od_o_list[list(match)[RepairOperators]]

            self.rest_customer.remove(cus)

        if len(od_cus_match) == 0:
            self.feasible = False

    def remove_cus(self):

        for match in self.ins.od_cus_matchDict.keys():
            cus = list(match)[0]
            # od_o = self.ins.graph.od_o_list[list(match)[RepairOperators]]

            self.rest_customer.remove(cus)

    def iterative_hungarian(self):

        strat_time = time.time()
        time_using = 0

        while self.feasible and time_using < 60:
            self.gen_od_cus_matrix()
            matrix = self.matrix.to_numpy()
            self.matcher.dis_matrix = matrix

            self.do_match()

            cur_time = time.time()
            time_using = cur_time - strat_time

        o_to_d_list = [i for i in self.ins.graph.od_o_list if len(self.od_ser_cus[i][0]) == 0]

        for key, value in self.od_ser_cus.items():
            # self.ins.od_cus_matchDict[key] = value

            self.ins.od_cost += value[2]

        for o in o_to_d_list:
            d = self.ins.graph.o_to_d[o]

            self.ins.od_cost += self.ins.graph.arc_dict[o, d].distance

        # self.ins.od_travel_compensation = self.ins.od_cost * self.ins.model_para.c_c
        self.get_ih_result()

    def get_od_use(self):
        order_num = 0

        for key_ in self.od_ser_cus.keys():
            order_num += len(self.od_ser_cus[key_][0])

        return order_num

    def get_ih_result(self):
        self.ins.od_travel_compensation = self.ins.od_cost * self.ins.model_para.c_c
        self.ins.iter_od_use = self.get_od_use()

    def get_od_routes(self):

        sorted_data = dict(sorted(self.serv_timeTable.items(),
                                  key=lambda item: item[1][0][1] if item[1] else float('inf')))

        for od in self.ins.graph.od_o_list:

            # 如果没有服务，直接前往自己的目的地
            if len(self.serv_timeTable[od]) == 0:
                pass

            else:
                for v in sorted_data[od]:
                    self.od_routes[od].append(v[0])

            self.od_routes[od].append(self.ins.graph.o_to_d[od])
