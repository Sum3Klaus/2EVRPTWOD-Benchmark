# -*- coding: utf-8 -*-
# @Time     : 2024-04-16-14:44
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
import numpy as np
from copy import deepcopy
import logging


class RegretRepair(object):

    def __init__(self):
        self.no = 2

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """

        def find_regret_insert(unassigned_list,
                               assigned_list,
                               alns_model):
            """  """

            # regret_rate = random.uniform(alns_model.params.regret_min, alns_model.params.regret_max)
            # regret_num = math.ceil(regret_rate * len(assigned_list))
            # regret_num = regret_num if regret_num >= 2 else 2
            regret_num = alns_model.params.regret_n

            opt_insert_vertex = None
            opt_insert_index = None
            opt_insert_cost = - float('inf')

            for vertex in unassigned_list:
                n_insert_cost = np.zeros((len(assigned_list), 3))

                for index in range(len(assigned_list)):
                    new_vertex_sequence_2 = deepcopy(assigned_list)
                    new_vertex_sequence_2.insert(index, vertex)

                    new_sol = alns_model.split_route(vertex_sequence=new_vertex_sequence_2)
                    new_routes = new_sol.routes
                    new_routes_cost = sum(route.cost for route in new_routes)

                    n_insert_cost[index, 0] = vertex.id_
                    n_insert_cost[index, 1] = index
                    n_insert_cost[index, 2] = new_routes_cost

                n_insert_cost = n_insert_cost[n_insert_cost[:, 2].argsort()]  # [node_id , insert_obj: ascending ]
                obj_difference = 0

                for index in range(1, math.ceil(regret_num)):
                    # calculate current regret value
                    obj_difference = obj_difference + n_insert_cost[index, 2] - n_insert_cost[0, 2]

                if obj_difference > opt_insert_cost:
                    # only when the current regret value bigger than history
                    opt_insert_vertex = alns_model.ins.graph.vertex_dict[int(n_insert_cost[0, 0])]
                    opt_insert_index = int(n_insert_cost[0, 1])
                    opt_insert_cost = obj_difference

            return opt_insert_vertex, opt_insert_index

        logging.debug(f"assigned numbers: {len(assigned_list)}")

        if len(assigned_list) < 2 or len(unassigned_list) <= 2:
            logging.warning("Cannot do repair!!!")
            return alns_model.best_sol.vertex_sequence

        # if len(assigned_list) <= 2:
        #     assigned_list1 = deepcopy(unassigned_list)
        #     unassigned_list1 = deepcopy(assigned_list)
        #
        #     assigned_list = assigned_list1
        #     unassigned_list = unassigned_list1

        else:
            repair_vertex_sequence = deepcopy(assigned_list)
            unassigned_list = deepcopy(unassigned_list)

            while len(unassigned_list) > 0:

                best_insert_vertex, best_insert_vertex_id = find_regret_insert(unassigned_list=unassigned_list,
                                                                               assigned_list=repair_vertex_sequence,
                                                                               alns_model=alns_model)

                repair_vertex_sequence.insert(best_insert_vertex_id, best_insert_vertex)

                # unassigned_list.remove(best_insert_vertex)
                unassigned_list = [vertex for vertex in unassigned_list if vertex.id_ != best_insert_vertex.id_]

        return repair_vertex_sequence