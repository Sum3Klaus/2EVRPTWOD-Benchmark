# -*- coding: utf-8 -*-
# @Time     : 2024-08-02-17:26
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Solution import *
from Common import *
from copy import deepcopy


class GreedyAlgorithm(object):

    @staticmethod
    def find_min_suc(ins,
                     level,
                     vertex,
                     lst: list):
        """  """
        min_vertex = -1
        min_dis = np.inf

        if level == 1:
            successors = vertex.successors_1st
        else:
            successors = vertex.successors_2nd

        if not successors:
            print('-' * 20 + 'no successors' + '-' * 20)

        cur_successors = [i for i in successors if i in lst]

        if len(cur_successors) == 0:

            return -1

        else:
            for suc in cur_successors:
                cur_arc = (vertex.id_, suc)
                if ins.graph.arc_dict[cur_arc].adj == 1:
                    if ins.graph.arc_dict[cur_arc].distance < min_dis:
                        min_dis = ins.graph.arc_dict[cur_arc].distance
                        min_vertex = suc
        if min_vertex == -1:
            return -1

        return ins.graph.vertex_dict[min_vertex]

    @staticmethod
    def gen_new_route(vertex):
        new_route = Route()
        new_route.insert_vertex(0, vertex=vertex)
        new_route.timeTable[0] = vertex.ready_time
        new_route.arriveTime[0] = vertex.ready_time

        return new_route

    def find_greedy_sol_depot_select(self,
                                     ins,
                                     depots_dict,
                                     level,
                                     vertex_list):
        greedy_sol = Sol(ins=ins)
        fixed_cost = ins.model_para.vehicle_1_cost if level == 1 else ins.model_para.vehicle_2_cost
        service_time = ins.model_para.service_time if level == 2 else ins.model_para.t_unload
        cur_graph = ins.graph.first_echelon_graph if level == 1 else ins.graph.second_echelon_graph
        vertex_list = deepcopy(vertex_list)

        new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[vertex_list[0]])
        vertex_list.remove(vertex_list[0])

        while len(vertex_list) > 0:
            last_vertex = new_route.route[-1]

            min_vertex = self.find_min_suc(ins=ins,
                                           level=level,
                                           vertex=last_vertex,
                                           lst=vertex_list)
            # 当前点没有后继点
            if min_vertex == -1:
                cur_best_depot = select_depot(ins=ins,
                                              route=new_route.route_list,
                                              depots_dict=depots_dict)

                new_route.input_start_and_return(ins=ins,
                                                 vertex_start=ins.graph.vertex_dict[cur_best_depot],
                                                 vertex_return=ins.graph.vertex_dict[depots_dict[cur_best_depot]]
                                                 )
                new_route.cost += fixed_cost
                greedy_sol.add_route_into_sol(route=new_route)

                new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[vertex_list[0]])
                vertex_list.remove(vertex_list[0])

            # 找到了贪心距离的点
            else:
                # 符合时间窗和容量约束
                if check_time_and_capacity(route=new_route,
                                           vertex=min_vertex,
                                           level=level,
                                           ins=ins):
                    new_route.add_vertex_into_route(vertex=min_vertex,
                                                    distance=cur_graph.arc_dict[
                                                        (last_vertex.id_, min_vertex.id_)].distance,
                                                    service_time=service_time)

                    vertex_list.remove(min_vertex.id_)

                # 不符合容量约束
                else:
                    cur_best_depot = select_depot(ins=ins,
                                                  route=new_route.route_list,
                                                  depots_dict=depots_dict)

                    new_route.input_start_and_return(ins=ins,
                                                     vertex_start=ins.graph.vertex_dict[cur_best_depot],
                                                     vertex_return=ins.graph.vertex_dict[depots_dict[cur_best_depot]]
                                                     )
                    new_route.cost += fixed_cost
                    greedy_sol.add_route_into_sol(route=new_route)

                    new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[vertex_list[0]])
                    vertex_list.remove(vertex_list[0])

        if level == 1:
            depots_list = ins.graph.depot_list
        else:
            depots_list = ins.graph.sate_depot_list

        if len(vertex_list) == 0 and new_route.route_list[-1] not in depots_list:
            cur_best_depot = select_depot(ins=ins,
                                          route=new_route.route_list,
                                          depots_dict=depots_dict)

            new_route.input_start_and_return(ins=ins,
                                             vertex_start=ins.graph.vertex_dict[cur_best_depot],
                                             vertex_return=ins.graph.vertex_dict[depots_dict[cur_best_depot]]
                                             )
            new_route.cost += fixed_cost
            greedy_sol.add_route_into_sol(route=new_route)

        return greedy_sol

    def find_greedy_sol_no_select(self,
                                  ins,
                                  depots_dict,
                                  level,
                                  vertex_list):
        # greedy_sol = Sol(ins=ins)
        cur_routes = []
        fixed_cost = ins.model_para.vehicle_1_cost if level == 1 else ins.model_para.vehicle_2_cost
        service_time = ins.model_para.service_time if level == 2 else ins.model_para.t_unload
        cur_graph = ins.graph.first_echelon_graph if level == 1 else ins.graph.second_echelon_graph
        vertex_list = deepcopy(vertex_list)

        depot_start = list(depots_dict.keys())[0]
        depot_return = depots_dict[depot_start]
        start_time = ins.graph.vertex_dict[depot_start].ready_time

        new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[depot_start])
        new_route.cost += fixed_cost

        while len(vertex_list) > 0:
            if len(vertex_list) == 0:
                break

            last_vertex = new_route.route[-1]
            min_vertex = self.find_min_suc(ins=ins,
                                           level=level,
                                           vertex=last_vertex,
                                           lst=vertex_list)

            if min_vertex == -1:
                new_route.add_vertex_into_route(vertex=ins.graph.vertex_dict[depot_return],
                                                distance=ins.graph.arc_dict[
                                                    (last_vertex.id_, depot_return)].distance,
                                                service_time=0)
                new_route.cost += fixed_cost
                # greedy_sol.add_route_into_sol(route=new_route)
                cur_routes.append(new_route)

                new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[depot_start])

            else:

                if check_time_and_capacity(route=new_route,
                                           vertex=min_vertex,
                                           level=level,
                                           ins=ins):
                    new_route.add_vertex_into_route(vertex=min_vertex,
                                                    distance=cur_graph.arc_dict[
                                                        (last_vertex.id_, min_vertex.id_)].distance,
                                                    service_time=service_time)
                    if min_vertex.id_ in vertex_list:
                        vertex_list.remove(min_vertex.id_)

                else:
                    new_route.add_vertex_into_route(vertex=ins.graph.vertex_dict[depot_return],
                                                    distance=cur_graph.arc_dict[
                                                        (last_vertex.id_, depot_return)].distance,
                                                    service_time=0)
                    new_route.cost += fixed_cost
                    # greedy_sol.add_route_into_sol(route=new_route)
                    cur_routes.append(new_route)

                    new_route = self.gen_new_route(vertex=ins.graph.vertex_dict[depot_start])

        if len(vertex_list) == 0 and new_route.route_list[-1] != depot_return:
            new_route.add_vertex_into_route(vertex=ins.graph.vertex_dict[depot_return],
                                            distance=cur_graph.arc_dict[
                                                (new_route.route[-1].id_, depot_return)].distance,
                                            service_time=0)

            # greedy_sol.add_route_into_sol(route=new_route)
            cur_routes.append(new_route)

        return cur_routes

    def find_greedy_sol(self,
                        ins,
                        is_select,
                        level,
                        target=None):
        """
        使用时需要注意 1st 只有一个depot 所以 is_select 需要设置成为 False
        """

        if is_select is True:

            depots_dict = {sate: ins.graph.sate_to_depot[sate] for sate in ins.graph.sate_list}
            # vertex_list = ins.alns_customers
            vertex_list = ins.customer_list_alns

            greedy_sol = self.find_greedy_sol_depot_select(ins=ins,
                                                           depots_dict=depots_dict,
                                                           level=level,
                                                           vertex_list=vertex_list)

        else:
            greedy_sol = Sol(ins=ins)
            if level == 1:
                depots_dict = {ins.graph.depot_list[0]: ins.graph.depot_list[1]}

                routes = self.find_greedy_sol_no_select(ins=ins,
                                                        depots_dict=depots_dict,
                                                        level=level,
                                                        vertex_list=ins.graph.sate_list)

            else:
                # 2nd
                depots_dict = {target: ins.graph.sate_to_depot[target]}
                vertex_list = ins.alns_dict[target]

                routes = self.find_greedy_sol_no_select(ins=ins,
                                                        depots_dict=depots_dict,
                                                        level=level,
                                                        vertex_list=vertex_list)

            for route in routes:
                greedy_sol.add_route_into_sol(route=route)

        return greedy_sol
