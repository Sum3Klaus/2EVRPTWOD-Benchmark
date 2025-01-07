# -*- coding: utf-8 -*-
# @Time     : 2024-07-09-16:14
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class HistoricalArriveDestroy(object):
    """
    This removal operator keeps track of the shortest setup time of each job.
    pd jobs with setup times that have larger distance to their best setup times are removed.
    """

    def __init__(self):
        self.no = 6

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        根据和历史最优解的到达时间的gap
        :param sol:
        :param remove_num:
        :param alns_model:
        :return:
        """

        best_record = alns_model.best_cus_arrive_time
        # cur_arrive_time = sol.cus_arriveTime

        differences_dict = dict()

        remove_list = []
        remove_id_list = []
        destroy_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)
        destroy_vertex_sequence = sol_cp.vertex_sequence

        for vertex in sol_cp.vertex_sequence:
            differences_cur = abs(sol_cp.cus_arriveTime[vertex.id_] - best_record[vertex.id_])

            differences_dict[vertex] = differences_cur

        differences_sort = sorted(differences_dict.items(), key=lambda x: x[1], reverse=True)

        for i in range(destroy_num):
            destroy_list.append(differences_sort[i][0])

        for vertex_ in destroy_list:
            remove_list.append(vertex_)
            destroy_vertex_sequence.remove(vertex_)
            remove_id_list.append(vertex_.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence