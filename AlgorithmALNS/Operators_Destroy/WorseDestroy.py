# -*- coding: utf-8 -*-
# @Time     : 2024-04-15-18:39
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy
import random
import math


class WorseDestroy(object):

    def __init__(self):
        self.no = 2

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """  """
        remove_list = []
        remove_id_list = []
        obj_difference_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)

        vertex_sequence = sol_cp.vertex_sequence
        total_cost_pre = sol_cp.totalCost

        for ver_index in range(len(vertex_sequence)):

            # cur_ver = sol.vertex_sequence[ver_index]

            destroy_vertex_sequence = deepcopy(vertex_sequence)

            destroy_vertex_sequence.pop(ver_index)
            new_sol = alns_model.split_route(vertex_sequence=destroy_vertex_sequence)
            routes_remove = new_sol.routes

            routes_remove_total_cost = sum(route.cost for route in routes_remove)

            obj_difference_list.append(total_cost_pre - routes_remove_total_cost)

        sorted_index = sorted(range(len(obj_difference_list)), key=lambda k: obj_difference_list[k], reverse=True)

        # destroy_rate = random.uniform(alns_model.params.worst_destroy_min, alns_model.params.worst_destroy_max)
        destroy_vertex_sequence = sol_cp.vertex_sequence
        # destroy_num = math.ceil(destroy_rate * len(destroy_vertex_sequence))
        # destroy_num = destroy_num if destroy_num >= 1 else 1
        if destroy_num == len(sol.vertex_sequence):
            destroy_num -= 2

        remove_index_list = sorted_index[:destroy_num]

        for i in remove_index_list:
            remove_list.append(destroy_vertex_sequence[i])

        for vertex in remove_list:
            destroy_vertex_sequence.remove(vertex)
            remove_id_list.append(vertex.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence