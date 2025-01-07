# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-22:59
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import numpy as np
from copy import deepcopy


class OdCustomerMatch(object):

    def __init__(self,
                 ins):
        """ """
        self.ins = ins
        self.od_cost = 0
        self.dis_matrix = np.full(shape=(self.ins.customer_num, self.ins.od_num), fill_value=1000.0)

    def calc_od_cus_matrix(self):

        for od in range(self.ins.od_num):
            for cus in range(self.ins.customer_num):

                for sate in self.ins.graph.sate_list:
                    cur_cus = self.ins.graph.customer_list[cus]
                    cur_sate = sate
                    cur_od_o = self.ins.graph.od_o_list[od]
                    cur_od_d = self.ins.graph.o_to_d[cur_od_o]

                    arc_1 = (cur_od_o, cur_sate)
                    arc_2 = (cur_sate, cur_cus)
                    arc_3 = (cur_cus, cur_od_d)

                    cur_od_cost = round(
                        (self.ins.graph.od_graph.arc_dict[arc_1].distance + self.ins.graph.od_graph.arc_dict[
                            arc_2].distance + self.ins.graph.od_graph.arc_dict[arc_3].distance -
                         self.ins.graph.od_graph.arc_dict[(cur_od_o, cur_od_d)].distance), 2)

                    cond_1 = (self.ins.graph.vertex_dict[cur_od_o].ready_time + self.ins.graph.od_graph.arc_dict[
                        arc_1].distance <= self.ins.graph.vertex_dict[cur_sate].due_time)
                    cond_2 = (self.ins.graph.vertex_dict[cur_od_o].ready_time + self.ins.graph.od_graph.arc_dict[
                        arc_1].distance + self.ins.model_para.p + self.ins.graph.od_graph.arc_dict[arc_2].distance <=
                              self.ins.graph.vertex_dict[cur_cus].due_time)
                    cond_3 = (self.ins.graph.vertex_dict[cur_od_o].ready_time + self.ins.graph.od_graph.arc_dict[
                        arc_1].distance + self.ins.model_para.p + self.ins.graph.od_graph.arc_dict[
                                  arc_2].distance + self.ins.model_para.p +
                              self.ins.graph.od_graph.arc_dict[arc_3].distance <= self.ins.graph.vertex_dict[
                                  cur_od_d].due_time)

                    if self.ins.graph.od_graph.arc_dict[arc_1].adj == 1 and self.ins.graph.od_graph.arc_dict[
                        arc_2].adj == 1 and \
                            self.ins.graph.od_graph.arc_dict[arc_3].adj == 1:
                        if cond_1 and cond_2 and cond_3:
                            self.dis_matrix[cus, od] = cur_od_cost if self.dis_matrix[cus, od] > cur_od_cost else \
                                self.dis_matrix[cus, od]

                        # else:
                        #     # self.dis_matrix[cus, od] += np.inf
                        #     self.dis_matrix[cus, od] += 1000

                    # else:
                    #     self.dis_matrix[cus, od] += 1000

    def gen_hungarian_dict(self):
        """  """
        hungarian_dict = {}
        feasible_cus_list = []

        for i in range(self.ins.customer_num):
            cur_cus = 'C_' + str(self.ins.graph.customer_list[i])
            hungarian_dict[cur_cus] = {}
            for j in range(self.ins.od_num):
                cur_od = 'OD_' + str(self.ins.graph.od_o_list[j])

                if self.dis_matrix[i, j] != np.inf:
                    hungarian_dict[cur_cus][cur_od] = -self.dis_matrix[i, j]

                    feasible_cus_list.append(cur_od)

                else:
                    # pass
                    hungarian_dict[cur_cus][cur_od] = -500

        hungarian_dict_cp = deepcopy(hungarian_dict)
        # for od in hungarian_dict_cp.keys():
        #
        #     for cus in feasible_cus_list:
        #
        #         if cus not in hungarian_dict_cp[od].keys():
        #             hungarian_dict[od][cus] = 10000

        for cus in hungarian_dict_cp.keys():

            if not hungarian_dict_cp[cus].values():
                hungarian_dict.pop(cus)

        return hungarian_dict

    def gen_hungarian_tuple(self):

        data = []

        for i in range(self.ins.customer_num):
            cur_cus = self.ins.graph.customer_list[i]

            for j in range(self.ins.od_num):
                cur_od = self.ins.graph.od_o_list[j]

                cur_dis = self.dis_matrix[i, j] if self.dis_matrix[i, j] != np.inf else 1000

                data.append(
                    (cur_cus, cur_od, cur_dis)
                )

        return data

    def start_match(self,
                    distance_matrix,
                    rest_cus_list):
        """
        匈牙利算法计算 od 服务的订单
        :param distance_matrix:
        :param rest_cus_list
        :return:
        """
        from Hungarian import Hungarian

        """ set2-3 """
        initial_value = 1000.0
        """ set4 """
        # initial_value = 100000.0

        def check_breaking_match(matched_dict: dict,
                                 matched_list: list,
                                 cust_alns: list):
            matched_dict_cp = deepcopy(matched_dict)

            for match_key, cost in matched_dict_cp.items():
                if cost >= initial_value:
                    matched_dict.pop(match_key)
                    matched_list.remove(match_key[0])
                    cust_alns.append(match_key[0])

                    self.od_cost -= initial_value

        match_dict = {}
        rest_customer_list = deepcopy(rest_cus_list)
        cus_od_list = []

        hungarian = Hungarian(distance_matrix)
        print('calculating...')
        hungarian.calculate()
        self.od_cost = hungarian.get_total_potential()
        print("Calculated value:\t", self.od_cost)  # = 12
        match_list = hungarian.get_results()
        print("Results:\n\t", match_list)

        # 检查是否有不能服务的订单
        for match in match_list:
            customer_id = rest_cus_list[match[0]]
            od_id = list(self.ins.graph.od_task_dict.keys())[match[1]]

            cus_od_list.append(rest_cus_list[match[0]])

            rest_customer_list.remove(customer_id)
            match_dict[(customer_id, od_id)] = self.dis_matrix[match[0], match[1]]

        print(f'customer-od: {match_dict}')

        check_breaking_match(matched_dict=match_dict,
                             matched_list=cus_od_list,
                             cust_alns=rest_customer_list)

        return match_dict, cus_od_list, rest_customer_list

    def update_od_time2(self,
                        match_list,
                        iter_hun):

        """ update info """
        for match in match_list:
            customer_id = list(match)[0]
            od_id = self.ins.graph.od_o_list[list(self.ins.graph.od_task_dict.keys())[match[1]]]
            cur_sate = self.ins.graph.cus_belong_sate[customer_id]

            if len(iter_hun.od_ser_cus[od_id][0]) == 0:
                arc_1 = (od_id, cur_sate)
                arc_2 = (cur_sate, customer_id)
                arc_3 = (customer_id, self.ins.graph.o_to_d[od_id])
                cur_od_cost = round(
                    (self.ins.graph.od_graph.arc_dict[arc_1].distance + self.ins.graph.od_graph.arc_dict[
                        arc_2].distance + self.ins.graph.od_graph.arc_dict[arc_3].distance -
                     self.ins.graph.od_graph.arc_dict[(od_id, self.ins.graph.o_to_d[od_id])].distance), 2)

                iter_hun.od_ser_cus[od_id][0].append(customer_id)
                iter_hun.od_ser_cus[od_id][1].add(cur_sate)
                iter_hun.od_ser_cus[od_id][2] = cur_od_cost
                arrive_sate_time = self.ins.graph.vertex_dict[od_id].ready_time + \
                                   self.ins.graph.od_graph.arc_dict[arc_1].distance
                if arrive_sate_time < self.ins.graph.vertex_dict[cur_sate].ready_time:
                    arrive_sate_time = self.ins.graph.vertex_dict[cur_sate].ready_time

                cur_ser_cus = arrive_sate_time + self.ins.model_para.p + self.ins.graph.od_graph.arc_dict[
                    arc_2].distance
                if cur_ser_cus < self.ins.graph.vertex_dict[customer_id].ready_time:
                    cur_ser_cus = self.ins.graph.vertex_dict[customer_id].ready_time

                iter_hun.od_ser_cus[od_id][3] = cur_ser_cus + self.ins.model_para.service_time

            else:
                pre_cus = iter_hun.od_ser_cus[od_id][0][-1]

                if cur_sate in iter_hun.od_ser_cus[od_id][1]:

                    arc_4 = (pre_cus, customer_id)
                    arc_5 = (customer_id, self.ins.graph.o_to_d[od_id])
                    cur_od_cost = iter_hun.od_ser_cus[od_id][2] - self.ins.graph.arc_dict[
                        (pre_cus, od_id)].distance + self.ins.graph.arc_dict[arc_4].distance + \
                                  self.ins.graph.arc_dict[arc_5].distance

                    iter_hun.od_ser_cus[od_id][0].append(customer_id)
                    # self.od_ser_cus[cur_od_o][RepairOperators].add(cur_sate)
                    iter_hun.od_ser_cus[od_id][2] = cur_od_cost
                    arrive_cus_time = iter_hun.od_ser_cus[od_id][3] + self.ins.graph.arc_dict[arc_4].distance
                    if arrive_cus_time < self.ins.graph.vertex_dict[customer_id].ready_time:
                        arrive_cus_time = self.ins.graph.vertex_dict[customer_id].ready_time

                    iter_hun.od_ser_cus[od_id][3] = arrive_cus_time + self.ins.model_para.service_time

                else:
                    # 不属于同一个sate，需要再去一次sate取货
                    pre_cus = iter_hun.od_ser_cus[od_id][0][-1]
                    cur_ser_sate = iter_hun.od_ser_cus[od_id][3] + self.ins.graph.arc_dict[(pre_cus, cur_sate)].distance
                    cur_ser_cus = cur_ser_sate + self.ins.model_para.p + self.ins.graph.arc_dict[
                        (cur_sate, customer_id)].distance

                    cur_od_cost = iter_hun.od_ser_cus[od_id][2] - self.ins.graph.arc_dict[
                        (pre_cus, self.ins.graph.o_to_d[od_id])].distance + self.ins.graph.arc_dict[
                                      (pre_cus, cur_sate)].distance + self.ins.graph.arc_dict[
                                      (cur_sate, customer_id)].distance + self.ins.graph.arc_dict[
                                      (customer_id, self.ins.graph.o_to_d[od_id])].distance

                    iter_hun.od_ser_cus[od_id][0].append(customer_id)
                    iter_hun.od_ser_cus[od_id][1].add(cur_sate)
                    iter_hun.od_ser_cus[od_id][2] = cur_od_cost
                    iter_hun.od_ser_cus[od_id][3] = cur_ser_cus + self.ins.model_para.service_time

    def update_od_time(self,
                       match_list,
                       iter_hun):

        """ update info """

        for match in match_list:
            customer_id = list(match)[0]
            od_id = self.ins.graph.od_o_list[list(self.ins.graph.od_task_dict.keys())[match[1]]]
            cur_sate = self.ins.graph.cus_belong_sate[customer_id]

            cur_cus_index = iter_hun.rest_customer.index(customer_id)

            # capacity
            iter_hun.od_ser_cus[od_id][4] += self.ins.graph.vertex_dict[customer_id].demand

            if len(iter_hun.od_ser_cus[od_id][0]) == 0:
                arc_1 = (od_id, cur_sate)
                arc_2 = (cur_sate, customer_id)
                arc_3 = (customer_id, self.ins.graph.o_to_d[od_id])

                iter_hun.od_ser_cus[od_id][0].append(customer_id)
                iter_hun.od_ser_cus[od_id][1].add(cur_sate)
                # iter_hun.od_ser_cus[od_id][2] = iter_hun.matrix[cur_cus_index, list(match)[RepairOperators]]
                iter_hun.od_ser_cus[od_id][2] = iter_hun.matrix.loc[customer_id, od_id]
                arrive_sate_time = self.ins.graph.vertex_dict[od_id].ready_time + \
                                   self.ins.graph.od_graph.arc_dict[arc_1].distance
                if arrive_sate_time < self.ins.graph.vertex_dict[cur_sate].ready_time:
                    arrive_sate_time = self.ins.graph.vertex_dict[cur_sate].ready_time

                cur_ser_cus = arrive_sate_time + self.ins.model_para.p + self.ins.graph.od_graph.arc_dict[
                    arc_2].distance
                if cur_ser_cus < self.ins.graph.vertex_dict[customer_id].ready_time:
                    cur_ser_cus = self.ins.graph.vertex_dict[customer_id].ready_time

                iter_hun.od_ser_cus[od_id][3] = cur_ser_cus + self.ins.model_para.service_time

                iter_hun.serv_timeTable[od_id].append((cur_sate, arrive_sate_time))
                iter_hun.serv_timeTable[od_id].append((customer_id, cur_ser_cus + self.ins.model_para.service_time))

            else:
                pre_cus = iter_hun.od_ser_cus[od_id][0][-1]

                if cur_sate in iter_hun.od_ser_cus[od_id][1]:

                    arc_4 = (pre_cus, customer_id)
                    arc_5 = (customer_id, self.ins.graph.o_to_d[od_id])
                    # cur_od_cost = iter_hun.od_ser_cus[od_id][2] - self.ins.graph.arc_dict[
                    #     (pre_cus, od_id)].distance + self.ins.graph.arc_dict[arc_4].distance + \
                    #               self.ins.graph.arc_dict[arc_5].distance

                    if customer_id not in iter_hun.od_ser_cus[od_id][0]:
                        iter_hun.od_ser_cus[od_id][0].append(customer_id)
                        # self.od_ser_cus[cur_od_o][RepairOperators].add(cur_sate)
                        iter_hun.od_ser_cus[od_id][2] = iter_hun.matrix.loc[customer_id, od_id]
                        arrive_cus_time = iter_hun.od_ser_cus[od_id][3] + self.ins.graph.arc_dict[arc_4].distance
                        # #######################################################
                        # #######################################################
                        if arrive_cus_time < self.ins.graph.vertex_dict[customer_id].ready_time:
                            arrive_cus_time = self.ins.graph.vertex_dict[customer_id].ready_time

                        iter_hun.od_ser_cus[od_id][3] = arrive_cus_time + self.ins.model_para.service_time

                        # iter_hun.serv_timeTable[od_id].append((cur_sate, cur_ser_sate))
                        iter_hun.serv_timeTable[od_id].append(
                            (customer_id, arrive_cus_time + self.ins.model_para.service_time))

                    else:
                        pass

                else:
                    # 不属于同一个sate，需要再去一次sate取货
                    pre_cus = iter_hun.od_ser_cus[od_id][0][-1]
                    cur_ser_sate = iter_hun.od_ser_cus[od_id][3] + self.ins.graph.arc_dict[(pre_cus, cur_sate)].distance
                    cur_ser_cus = cur_ser_sate + self.ins.model_para.p + self.ins.graph.arc_dict[
                        (cur_sate, customer_id)].distance

                    # cur_od_cost = iter_hun.od_ser_cus[od_id][2] - self.ins.graph.arc_dict[
                    #     (pre_cus, self.ins.graph.o_to_d[od_id])].distance + self.ins.graph.arc_dict[
                    #                   (pre_cus, cur_sate)].distance + self.ins.graph.arc_dict[
                    #                   (cur_sate, customer_id)].distance + self.ins.graph.arc_dict[
                    #                   (customer_id, self.ins.graph.o_to_d[od_id])].distance

                    iter_hun.od_ser_cus[od_id][0].append(customer_id)
                    iter_hun.od_ser_cus[od_id][1].add(cur_sate)
                    iter_hun.od_ser_cus[od_id][2] = iter_hun.matrix.loc[customer_id, od_id]
                    iter_hun.od_ser_cus[od_id][3] = cur_ser_cus + self.ins.model_para.service_time

                    iter_hun.serv_timeTable[od_id].append((cur_sate, cur_ser_sate))
                    iter_hun.serv_timeTable[od_id].append((customer_id, cur_ser_cus + self.ins.model_para.service_time))
