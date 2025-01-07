# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-17:46
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import math
import logging
import re
import numpy as np
import gurobipy
from Vertex import Vertex
from Route import *


def operator_out_of_bound(assigned_list,
                          alns_model):
    logging.basicConfig(level=logging.DEBUG)

    """ 在关键步骤添加调试信息和日志记录，帮助识别数据在哪个环节出错。 """
    logging.debug(f"输入点数: {len(assigned_list)}")
    if len(assigned_list) < 2:
        logging.warning("Cannot do repair!!!")
        return alns_model.best_sol.vertex_sequence


def calc_travel_time(x_1, y_1,
                     x_2, y_2):
    distance = round(math.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2), 2)

    return distance


def judge_arc(arc_id,
              graph):
    if arc_id in graph.arc_dict and graph.arc_dict[arc_id].adj == 1:
        return True

    else:
        return False


def check_capacity(route,
                   vertex: Vertex,
                   ins):
    """  """
    vehicle_capacity = ins.model_para.vehicle_2_capacity
    feasible = True if sum(route.capacityTable) + vertex.demand <= vehicle_capacity else False

    return feasible


def check_time(route,
               vertex: Vertex,
               level,
               ins):
    """
    """
    cur_graph = ins.graph.second_echelon_graph if level == 2 else ins.graph.first_echelon_graph
    arc = (route.route[-1].id_, vertex.id_)

    if cur_graph.arc_dict[arc].adj == 0:
        return False

    service_time = ins.model_para.service_time
    # sub_graph = ins.graph.second_echelon_graph

    if cur_graph.arc_dict[arc].adj == 0:
        return False

    last_time = route.timeTable[-1] + service_time
    trav_dis = cur_graph.arc_dict[arc].distance

    feasible = True if (last_time + trav_dis <= vertex.due_time) else False

    return feasible


def check_time_and_capacity(route,
                            vertex: Vertex,
                            ins,
                            level):
    feasible = True if (check_time(route=route, vertex=vertex, ins=ins, level=level) and check_capacity(route, vertex,
                                                                                                        ins)) else False

    return feasible


def update_sate_start_time(ins,
                           sol):
    """  """
    for route in sol.routes:
        for sate in route.route:

            if sate.id_ in ins.graph_.sate_list:
                sate_index = route.route.index(sate)

                start_time = route.timeTable[sate_index]

                ins.sate_arrive_time[sate.id_] = start_time


def check_cannot_situation(ins,
                           sate_id,
                           sate_last_arrive_time):
    feasible = True

    last = sate_last_arrive_time[sate_id]
    for vertex_id in ins.graph.alns_dict[sate_id]:

        if last + ins.graph.arc_dict[(sate_id, vertex_id)].distance <= ins.graph.vertex_dict[vertex_id].due_time:
            return feasible

        else:
            feasible = False
            return feasible


def get_var_index(model: gurobipy.Model,
                  start_word):
    var_dict = {}
    var_list_str = []

    for var in model.getVars():

        if var.x >= 0.5:
            if var.varName.startswith(start_word):
                var_list_str.append(var.varName)

    for var_str in var_list_str:
        matches = re.findall(r'_(\d+)', var_str)

        subscripts = [int(match) for match in matches]

        if subscripts[-1] not in var_dict:
            var_dict[subscripts[-1]] = [subscripts]

        else:
            var_dict[subscripts[-1]].append(subscripts)

    return var_dict


def get_od_routes(var_dict, ins):
    routes = {}

    for i in var_dict.keys():
        var_ = var_dict[i]

        o = ins.graph.od_o_list[i]
        d = ins.graph.od_d_list[i]

        routes[i] = [o]

        while routes[i][-1] != d:

            for var in var_:

                if routes[i][-1] == var[0]:
                    routes[i].append(var[1])

    return routes


def calc_od_route_cost(route,
                       ins):
    """
    var_dict = get_var_index(grb.model, 'z')
    routes = get_od_routes(var_dict, ins)
    cost = calc_od_route_cost(routes[0], ins)
    :param route:
    :param ins:
    :return:
    """
    cost = 0

    for i in range(len(route) - 1):
        # cost += calc_travel_time(x_1=ins.graph.vertex_dict[route[i]].x_coord,
        #                          y_1=ins.graph.vertex_dict[route[i]].y_coord,
        #                          x_2=ins.graph.vertex_dict[route[i + RepairOperators]].x_coord,
        #                          y_2=ins.graph.vertex_dict[route[i + RepairOperators]].y_coord)

        cost += ins.graph.pdp_graph.arc_dict[route[i], route[i + 1]].distance

    return cost


def get_od_info(model,
                start_word,
                ins):
    var_dict = get_var_index(model, start_word)

    routes = get_od_routes(var_dict, ins)


def select_depot(ins,
                 depots_dict,
                 route):
    """ """
    head_vertex_id = route[0]
    tail_vertex_id = route[-1]

    best_depot = None
    best_distance = float('inf')

    for depot_start in depots_dict.keys():
        depot_return = depots_dict[depot_start]

        cur_distance = ins.graph.arc_dict[depot_start, head_vertex_id].distance + ins.graph.arc_dict[
            tail_vertex_id, depot_return].distance

        if cur_distance < best_distance:
            best_depot = depot_start
            best_distance = cur_distance

    return best_depot

