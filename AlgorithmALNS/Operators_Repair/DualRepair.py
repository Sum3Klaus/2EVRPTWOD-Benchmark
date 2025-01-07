# -*- coding: utf-8 -*-
# @Time     : 2024-07-19-11:20
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy
import logging
import numpy as np
import math


class DualRepair(object):
    """  """

    def __init__(self):
        self.no = 4

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """

        def find_min_dual_insert(unassigned,
                                 assigned,
                                 alns):
            opt_insert_vertex = None
            opt_insert_index = None
            opt_insert_cost = - float('inf')

            regret_num = alns_model.params.regret_n

            for vertex in unassigned:
                n_insert_cost = np.zeros((len(assigned), 3))

                for index in range(len(assigned)):
                    new_vertex_sequence_2 = deepcopy(assigned)
                    new_vertex_sequence_2.insert(index, vertex)

                    new_sol = alns_model.split_route(vertex_sequence=new_vertex_sequence_2)
                    new_routes = new_sol.routes
                    cur_dual_value = sum(alns.cg.RMP_duals[str(i)] for i in new_sol.vertex_id_sequence)
                    new_routes_cost = sum(route_.cost for route_ in new_routes) - cur_dual_value

                    n_insert_cost[index, 0] = vertex.id_
                    n_insert_cost[index, 1] = index
                    n_insert_cost[index, 2] = new_routes_cost

                n_insert_cost = n_insert_cost[n_insert_cost[:, 2].argsort()]  # [node_id , insert_obj: ascending ]
                obj_difference = 0

                for index_ in range(1, math.ceil(regret_num)):
                    # calculate current regret value
                    obj_difference = obj_difference + n_insert_cost[index_, 2] - n_insert_cost[0, 2]

                # if new_routes_cost < opt_insert_cost:
                #     opt_insert_vertex = vertex
                #     opt_insert_index = index
                if obj_difference > opt_insert_cost:
                    # only when the current regret value bigger than history
                    opt_insert_vertex = alns_model.ins.graph.vertex_dict[int(n_insert_cost[0, 0])]
                    opt_insert_index = int(n_insert_cost[0, 1])
                    opt_insert_cost = obj_difference

            return opt_insert_vertex, opt_insert_index

        if alns_model.model_builder.RMP is None:
            alns_model.model_builder.build_rmp_and_sp()
            alns_model.cg.set_model(model_builder=alns_model.model_builder)

        for route in alns_model.route_records:
            if route.route_list not in alns_model.model_builder.column_pool.values():
                alns_model.cg.route_index = next(alns_model.cg.next_iter_time)
                cur_column = alns_model.cg.get_column(route_list=route.route_list)
                alns_model.cg.add_column_into_rmp(route=route,
                                                  new_column=cur_column,
                                                  iter_times=alns_model.cg.route_index)

        alns_model.cg.solve_rmp_and_get_duals()

        if len(assigned_list) < 2 or len(unassigned_list) <= 2:
            logging.warning("Cannot do repair!!!")
            return alns_model.best_sol.vertex_sequence

        else:
            repair_vertex_sequence = deepcopy(assigned_list)
            unassigned_list = deepcopy(unassigned_list)

            while len(unassigned_list) > 0:
                best_insert_vertex, best_insert_vertex_id = find_min_dual_insert(unassigned=unassigned_list,
                                                                                 assigned=repair_vertex_sequence,
                                                                                 alns=alns_model)

                repair_vertex_sequence.insert(best_insert_vertex_id, best_insert_vertex)

                # unassigned_list.remove(best_insert_vertex)
                unassigned_list = [vertex for vertex in unassigned_list if vertex.id_ != best_insert_vertex.id_]

        return repair_vertex_sequence
