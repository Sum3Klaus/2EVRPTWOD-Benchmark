# -*- coding: utf-8 -*-
# @Time     : 2024-07-08-23:07
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class DistanceDestroy(object):
    """
    cur_distance = arc[prc, cur].distance + arc[cur, next].distance
    """

    def __init__(self):
        self.no = 4

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        根据访问的距离
        :param sol:
        :param remove_num:
        :param alns_model:
        :return:
        """
        remove_list = []
        remove_id_list = []
        destroy_list = []
        destroy_num = remove_num
        distance_dict = dict()

        sol_cp = deepcopy(sol)

        destroy_vertex_sequence = sol_cp.vertex_sequence

        # calculate distance
        for route in sol_cp.routes:

            for index_ in range(1, len(route.route) - 1):
                pre_arc = (route.route[index_ - 1].id_, route.route[index_].id_)
                next_arc = (route.route[index_].id_, route.route[index_ + 1].id_)

                distance_dict[route.route[index_]] = sol_cp.ins.graph.arc_dict[pre_arc].distance + \
                                                     sol_cp.ins.graph.arc_dict[next_arc].distance

        distance_dict_sort = sorted(distance_dict.items(), key=lambda x: x[1], reverse=True)
        # destroy_list = distance_dict_sort[: destroy_num]
        for i in range(destroy_num):
            destroy_list.append(distance_dict_sort[i][0])

        for vertex_ in destroy_list:
            remove_list.append(vertex_)
            destroy_vertex_sequence.remove(vertex_)
            remove_id_list.append(vertex_.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence
