# -*- coding: utf-8 -*-
# @Time     : 2024-07-12-14:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
from copy import deepcopy
import logging


class DistanceRepair(object):

    def __init__(self):
        self.no = 3

    @staticmethod
    def do_repair1(unassigned_list,
                   assigned_list,
                   alns_model):
        """  """
        sate_no = alns_model.target

        def find_min_dis_insert(ass_list,
                                una_list,
                                alns):
            """ """
            best_insert_vertex_id_ = None
            best_insert_vertex_ = None
            best_insert_cost = float('inf')

            # insert sate and sate_as_depot
            cur_assigned_list = deepcopy(ass_list)
            cur_assigned_list.insert(0, alns.ins.graph.vertex_dict[sate_no])
            sate_depot = alns.ins.graph.sate_to_depot[sate_no]
            cur_assigned_list.append(alns.ins.graph.vertex_dict[sate_depot])

            for vertex in una_list:
                for index_ in range(1, len(cur_assigned_list) - 1):
                    arc_1 = (sate_no, vertex.id_)
                    arc_2 = (vertex.id_, cur_assigned_list[index_].id_)
                    cur_distance = alns.ins.graph.arc_dict[arc_1].distance + alns.ins.graph.arc_dict[arc_2].distance

                    if cur_distance < best_insert_cost:
                        best_insert_vertex_id_ = index_
                        best_insert_vertex_ = vertex

            return best_insert_vertex_, best_insert_vertex_id_

        assigned_list = deepcopy(assigned_list)
        unassigned_list = deepcopy(unassigned_list)

        while len(unassigned_list) > 0:
            best_insert_vertex, best_insert_vertex_id = find_min_dis_insert(ass_list=assigned_list,
                                                                            una_list=unassigned_list,
                                                                            alns=alns_model)

            assigned_list.insert(best_insert_vertex_id, best_insert_vertex)

            unassigned_list.remove(best_insert_vertex)

        return assigned_list

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """
        根据插入的前后距离 distance_{pre_vertex, insert_vertex} + distance_{insert_vertex, next_vertex}
        """

        def find_min_dis_insert(ass_list,
                                una_list,
                                alns):
            """ """
            # 确定起始点
            best_depot = None
            for start, end in alns_model.depots_dict.items():
                best_depot_distance = float('inf')

                vertex_first = assigned_list[0]
                vertex_last = assigned_list[-1]

                cus_distance = alns_model.ins.graph.arc_dict[start, vertex_first.id_].distance + \
                               alns_model.ins.graph.arc_dict[vertex_last.id_, end].distance

                if cus_distance < best_depot_distance:
                    best_depot = start
                    best_depot_distance = cus_distance

            # 遍历，确定距离最短的插入位置和vertex
            best_insert_vertex_id_ = None
            best_insert_vertex_ = None
            best_insert_cost = float('inf')

            # insert sate and sate_as_depot
            cur_assigned_list = deepcopy(ass_list)
            cur_assigned_list.insert(0, alns.ins.graph.vertex_dict[best_depot])
            sate_depot = alns.ins.graph.sate_to_depot[best_depot]
            cur_assigned_list.append(alns.ins.graph.vertex_dict[sate_depot])

            for vertex in una_list:
                for index_ in range(1, len(cur_assigned_list) - 1):
                    arc_1 = (cur_assigned_list[index_ - 1].id_, vertex.id_)
                    arc_2 = (vertex.id_, cur_assigned_list[index_].id_)
                    cur_distance = alns.ins.graph.arc_dict[arc_1].distance + alns.ins.graph.arc_dict[arc_2].distance

                    if cur_distance < best_insert_cost:
                        best_insert_vertex_id_ = index_
                        best_insert_vertex_ = vertex

            return best_insert_vertex_, best_insert_vertex_id_

        while len(unassigned_list) > 0:
            best_insert_vertex, best_insert_vertex_id = find_min_dis_insert(ass_list=assigned_list,
                                                                            una_list=unassigned_list,
                                                                            alns=alns_model)

            assigned_list.insert(best_insert_vertex_id, best_insert_vertex)

            unassigned_list.remove(best_insert_vertex)

        return assigned_list