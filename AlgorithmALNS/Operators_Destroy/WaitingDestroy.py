# -*- coding: utf-8 -*-
# @Time     : 2024-07-08-22:17
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class WaitingDestroy(object):

    def __init__(self):
        self.no = 3

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        根据每个车访问客户的等待时间进行排序

        :param sol:
        :param remove_num
        :param alns_model:
        :return:
        """

        def calc_waiting_time(sol_pre):
            """

            :return: customer_list
            """
            customer_list = []

            for route in sol_pre.routes:
                for vertex in route.route[1: -1]:
                    cur_id = route.route.index(vertex)
                    pre_start_time = route.timeTable[cur_id - 1]
                    cur_arc = (route.route[cur_id - 1].id_, route.route[cur_id].id_)

                    vertex.waiting_time = max(0, (
                                vertex.ready_time - pre_start_time - sol_pre.ins.model_para.service_time -
                                sol_pre.ins.graph.arc_dict[cur_arc].distance))
                    customer_list.append(vertex)

            cus_list_sort = sorted(customer_list, key=lambda x: x.waiting_time, reverse=True)

            return cus_list_sort

        remove_list = []
        remove_id_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)

        destroy_vertex_sequence = sol_cp.vertex_sequence

        cus_list_sort = calc_waiting_time(sol_pre=sol_cp)
        destroy_list = cus_list_sort[: destroy_num]

        for vertex_ in destroy_list:
            remove_list.append(vertex_)
            destroy_vertex_sequence.remove(vertex_)
            remove_id_list.append(vertex_.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence
