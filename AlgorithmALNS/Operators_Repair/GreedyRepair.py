# -*- coding: utf-8 -*-
# @Time     : 2024-04-15-22:23
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
from copy import deepcopy
import logging


class GreedyRepair(object):

    def __init__(self):
        self.no = 1

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """

        def find_greedy_insert(unassigned_list,
                               assigned_list,
                               alns_model):
            """  """
            best_insert_vertex_id = None
            best_insert_vertex = None
            best_insert_cost = float('inf')

            cur_sol = alns_model.split_route(vertex_sequence=assigned_list)

            for vertex in unassigned_list:

                for i in range(len(assigned_list)):

                    new_vertex_sequence_2 = deepcopy(assigned_list)

                    new_vertex_sequence_2.insert(i, vertex)

                    new_sol = alns_model.split_route(new_vertex_sequence_2)

                    obj_difference = cur_sol.totalCost - new_sol.totalCost

                    if obj_difference < best_insert_cost:
                        best_insert_vertex_id = i
                        best_insert_vertex = vertex
                        best_insert_cost = obj_difference
            return best_insert_vertex, best_insert_vertex_id

        logging.debug(f"assigned list type: {type(assigned_list)}")

        if len(assigned_list) <= 2:
            logging.warning("Cannot do repair!!!")
            return alns_model.best_sol.vertex_sequence

        assigned_list = deepcopy(assigned_list)
        unassigned_list = deepcopy(unassigned_list)

        while len(unassigned_list) > 0:

            best_insert_vertex, best_insert_vertex_id = find_greedy_insert(unassigned_list=unassigned_list,
                                                                           assigned_list=assigned_list,
                                                                           alns_model=alns_model)

            assigned_list.insert(best_insert_vertex_id, best_insert_vertex)

            unassigned_list.remove(best_insert_vertex)

        return assigned_list
