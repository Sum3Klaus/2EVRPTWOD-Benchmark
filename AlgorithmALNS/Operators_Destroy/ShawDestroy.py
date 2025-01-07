# -*- coding: utf-8 -*-
# @Time     : 2024-04-15-18:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
from copy import deepcopy
import numpy as np


class ShawDestroy(object):

    def __init__(self):
        self.no = 1

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """  """
        remove_list = []
        remove_id_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)
        destroy_vertex_sequence = sol_cp.vertex_sequence
        routes = sol_cp.routes

        # destroy_rate = random.uniform(alns_model.params.worst_destroy_min, alns_model.params.worst_destroy_max)
        # destroy_num = math.floor(destroy_rate * len(sol.vertex_sequence))
        if destroy_num == len(sol.vertex_sequence):
            destroy_num -= 2
        destroy_num = destroy_num if destroy_num >= 1 else 1

        relation_list = []

        route = random.choice(routes)
        vertex = random.choice(route.route[1: -1])

        for ver in destroy_vertex_sequence:

            if ver.id_ != vertex.id_:
                cur_dis = alns_model.ins.graph.arc_dict[(vertex.id_, ver.id_)].distance if \
                    alns_model.ins.graph.arc_dict[(
                        vertex.id_, ver.id_)].adj == 1 else 1000

                cur_fitness = 0.75 * cur_dis + .015 * abs(
                    (vertex.ready_time - ver.ready_time) + (vertex.due_time - ver.due_time)) + 0.1 * abs(
                    vertex.demand - ver.demand)

                relation_list.append(cur_fitness)

        sorted_index = sorted(range(len(relation_list)), key=lambda k: relation_list[k], reverse=False)

        remove_index_list = sorted_index[:destroy_num - 1]

        for i in remove_index_list:
            remove_list.append(destroy_vertex_sequence[i])

        for vertex in remove_list:
            destroy_vertex_sequence.remove(vertex)
            remove_id_list.append(vertex.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence