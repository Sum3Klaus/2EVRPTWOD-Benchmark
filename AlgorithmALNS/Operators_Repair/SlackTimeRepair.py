# -*- coding: utf-8 -*-
# @Time     : 2024-07-22-14:17
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy
import numpy as np


class SlackTimeRepair(object):

    def __init__(self):
        self.no = 5

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """

        def calc_slack_time(alns,
                            route):
            slack_time = 0
            slack_time_list = alns.calc_latest_time_table(route=route)
            for index_ in range(1, len(route.route_list)):
                slack_time += (slack_time_list[index_] - route.timeTable[index_])

            return slack_time

        def find_min_slack_insert(unassigned,
                                  assigned,
                                  alns):
            opt_insert_vertex = None
            opt_insert_index = None
            opt_slack_time = float('inf')

            for vertex in unassigned:
                for index in range(len(assigned)):
                    new_vertex_sequence_2 = deepcopy(assigned_list)
                    new_vertex_sequence_2.insert(index, vertex)

                    new_sol = alns_model.split_route(vertex_sequence=new_vertex_sequence_2)
                    cur_slack_time = 0

                    for route in new_sol.routes:
                        cur_slack_time += calc_slack_time(alns=alns,
                                                          route=route)

                    if cur_slack_time < opt_slack_time:
                        opt_slack_time = cur_slack_time
                        opt_insert_vertex = vertex
                        opt_insert_index = index

            return opt_insert_vertex, opt_insert_index

        repair_vertex_sequence = deepcopy(assigned_list)
        unassigned_list = deepcopy(unassigned_list)

        while len(unassigned_list) > 0:
            best_insert_vertex, best_insert_vertex_id = find_min_slack_insert(unassigned=unassigned_list,
                                                                              assigned=repair_vertex_sequence,
                                                                              alns=alns_model)

            repair_vertex_sequence.insert(best_insert_vertex_id, best_insert_vertex)

            # unassigned_list.remove(best_insert_vertex)
            unassigned_list = [vertex for vertex in unassigned_list if vertex.id_ != best_insert_vertex.id_]

        return repair_vertex_sequence
