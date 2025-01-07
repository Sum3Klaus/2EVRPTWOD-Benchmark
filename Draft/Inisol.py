# -*- coding: utf-8 -*-
# @Time     : 2024-04-14-18:15
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy
from Common import *
from Solution import Sol
from Route import Route
import numpy as np
import pandas as pd


class IniSol(object):
    """  """

    def __init__(self,
                 ins):
        self.ins = ins

        self.sates_sol = {self.ins.graph.sate_list[i]: Sol(ins=ins) for i in
                          range(self.ins.sate_num)}

        self.first_sol = Sol(ins=ins)

        """
        The carbon quota used in the experiment is the carbon emissions value of the initial solution in the algorithm
        """
        self.travel_1 = 0
        self.Q_q_1 = 0
        self.travel_2 = 0
        self.Q_q_2 = 0

    def find_min_suc(self,
                     vertex,
                     lst: list):
        """  """
        min_vertex = 0
        min_dis = np.inf

        successors = vertex.successors_2nd

        if not successors:
            print('-' * 20 + 'no successors' + '-' * 20)

        cur_successors = [i for i in successors if i in lst]

        if len(cur_successors) == 0:

            if vertex.id_ in self.ins.graph.customer_list:
                min_vertex = self.ins.graph.sate_to_depot[self.ins.graph.cus_belong_sate[vertex.id_]]

        else:
            for suc in cur_successors:
                cur_arc = (vertex.id_, suc)
                if self.ins.graph.arc_dict[cur_arc].adj == 1:
                    if self.ins.graph.arc_dict[cur_arc].distance < min_dis:
                        min_dis = self.ins.graph.arc_dict[cur_arc].distance
                        min_vertex = suc

        return self.ins.graph.vertex_dict[min_vertex]

    def gen_greedy_sol(self):
        """  """
        for target in self.ins.graph.sate_list:
            print(target)
            # if target == 2:
            #     print()
            self.find_solo_greedy_sol(target=target)

    def find_solo_greedy_sol(self,
                             target):
        """  """

        fixed_cost = self.ins.model_para.vehicle_2_cost
        depot_start = self.ins.graph.vertex_dict[target]
        depot_end = self.ins.graph.vertex_dict[self.ins.graph.sate_to_depot[target]]
        sate_start_time = self.ins.graph.vertex_dict[target].ready_time

        cur_graph = self.ins.graph.second_echelon_graph

        vertex_list = deepcopy(self.ins.alns_dict[target])

        # new_route = Route()
        # new_route.cost += fixed_cost
        # new_route.route.append(depot_start)
        # new_route.timeTable[0] = sate_start_time
        new_route = self.gen_new_route(fixed_cost=fixed_cost,
                                       depot_start=depot_start,
                                       route_start_time=sate_start_time)

        while True:

            if len(vertex_list) == 0:
                break

            last_vertex = new_route.route[-1]
            min_vertex = self.find_min_suc(vertex=last_vertex,
                                           lst=vertex_list)

            if min_vertex.id_ in self.ins.graph.depot_list or min_vertex.id_ in self.ins.graph.sate_depot_list:
                # min = depot
                new_route.add_vertex_into_route(vertex=depot_end,
                                                distance=cur_graph.arc_dict[
                                                    (last_vertex.id_, depot_end.id_)].distance,
                                                service_time=0)

                self.sates_sol[target].add_route_into_sol(route=new_route)

                # new_route = Route()
                # new_route.cost += fixed_cost
                # new_route.route.append(depot_start)
                # new_route.timeTable[0] = sate_start_time
                # new_route.arriveTime[0] = sate_start_time
                new_route = self.gen_new_route(fixed_cost=fixed_cost,
                                               depot_start=depot_start,
                                               route_start_time=sate_start_time)

            else:

                if check_time_and_capacity(route=new_route,
                                           vertex=min_vertex,
                                           ins=self.ins):
                    new_route.add_vertex_into_route(vertex=min_vertex,
                                                    distance=cur_graph.arc_dict[
                                                        (last_vertex.id_, min_vertex.id_)].distance,
                                                    service_time=self.ins.model_para.service_time)

                    if min_vertex.id_ in vertex_list:
                        vertex_list.remove(min_vertex.id_)

                    else:
                        if min_vertex.id_ in self.ins.graph.sate_depot_list:
                            self.sates_sol[target].add_route_into_sol(route=new_route)

                            new_route = Route()
                            new_route.cost += fixed_cost
                            new_route.route.append(depot_start)
                            new_route.timeTable[0] = sate_start_time

                else:
                    new_route.add_vertex_into_route(vertex=depot_end,
                                                    distance=cur_graph.arc_dict[
                                                        (last_vertex.id_, depot_end.id_)].distance,
                                                    service_time=0)

                    self.sates_sol[target].add_route_into_sol(route=new_route)

                    # new_route = Route()
                    # new_route.cost += fixed_cost
                    # new_route.route.append(depot_start)
                    # new_route.timeTable[0] = sate_start_time
                    new_route = self.gen_new_route(fixed_cost=fixed_cost,
                                                   depot_start=depot_start,
                                                   route_start_time=sate_start_time)

        # add depot
        if len(vertex_list) == 0:
            new_route.add_vertex_into_route(vertex=depot_end,
                                            distance=cur_graph.arc_dict[
                                                (new_route.route[-1].id_, depot_end.id_)].distance,
                                            service_time=self.ins.model_para.service_time)

            self.sates_sol[target].add_route_into_sol(route=new_route)

    def gen_ini_first_sol(self):

        for sate in self.ins.graph.sate_list:
            new_route = Route()
            new_route.cost += self.ins.model_para.vehicle_1_cost
            new_route.route.append(self.ins.graph.vertex_dict[0])

            cur_distance = self.ins.graph.arc_dict[(0, sate)].distance

            new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[sate],
                                            distance=cur_distance,
                                            service_time=self.ins.model_para.t_unload)

            new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[self.ins.graph.depot_list[-1]],
                                            distance=cur_distance,
                                            service_time=0)

            self.first_sol.add_route_into_sol(route=new_route)

    @staticmethod
    def gen_new_route(fixed_cost,
                      depot_start,
                      route_start_time):
        new_route = Route()
        new_route.cost += fixed_cost
        new_route.set_sate_route(sate=depot_start)
        new_route.timeTable[0] = route_start_time
        new_route.arriveTime[0] = route_start_time

        return new_route

    def get_init_q_q(self):

        # 1st
        for route in self.first_sol.routes:
            self.travel_1 += (route.cost - self.ins.model_para.vehicle_1_cost)

        self.Q_q_1 = self.travel_1 * self.ins.model_para.rho_1

        # 2nd
        for sate in self.ins.graph.sate_list:
            cur_sol = self.sates_sol[sate]

            for route in cur_sol.routes:
                self.travel_2 += (route.cost - self.ins.model_para.vehicle_2_cost)

        self.Q_q_2 = self.travel_2 * self.ins.model_para.rho_2

        self.ins.model_para.Q_q_1 = self.Q_q_1
        self.ins.model_para.Q_q_2 = self.Q_q_2

    @staticmethod
    def gen_new_route_no_start(fixed_cost,
                               vertex):
        new_route = Route()
        new_route.cost += fixed_cost
        new_route.timeTable[0] = vertex.ready_time
        new_route.arriveTime[0] = vertex.ready_time

        return new_route

    def gen_saving_with_sate_select_sol(self):
        """

        :return:
        """


class SavingAlgorithm(object):
    """
    设计 sate selection 的 Saving Algorithm
    https://github.com/zuzhaoye/vehicle-routing-problem-vrp-Clarke-Wright-Savings-Method/blob/master/cw_algorithm.ipynb
    """

    def __init__(self,
                 ins):

        self.ins = ins

        self.saving_dict = dict()
        self.saving_pd = dict()

        self.routes_list = {sate_id: list() for sate_id in ins.graph.sate_list}  # vertex_id
        self.routes = {sate_id: list() for sate_id in ins.graph.sate_list}  # vertex

        # if there is any remaining customer to be served
        self.remaining = True

        # define capacity of the vehicle
        self.cap = self.ins.model_para.vehicle_2_capacity

        # record steps
        self.step = 0

    def calc_saving(self,
                    sate_id):
        savings = dict()

        for cus_id_1 in range(len(self.ins.graph.sate_serv_cus[sate_id])):
            cus_1 = self.ins.graph.sate_serv_cus[sate_id][cus_id_1]

            for cus_id_2 in range(cus_id_1 + 1, len(self.ins.graph.sate_serv_cus[sate_id])):
                if cus_id_1 != cus_id_2:
                    cus_2 = self.ins.graph.sate_serv_cus[sate_id][cus_id_2]

                    savings[str(cus_1) + ',' + str(cus_2)] = self.ins.graph.arc_dict[sate_id, cus_1].distance + \
                                                             self.ins.graph.arc_dict[sate_id, cus_2].distance - \
                                                             self.ins.graph.arc_dict[cus_1, cus_2].distance

        return savings

    def calc_sates_savings(self):

        for sate_id in self.ins.graph.sate_list:
            self.saving_dict[sate_id] = self.calc_saving(sate_id=sate_id)

            self.saving_pd[sate_id] = pd.DataFrame.from_dict(self.saving_dict[sate_id], orient='index')

            self.saving_pd[sate_id].rename(columns={0: f'Sate_{sate_id}'}, inplace=True)
            self.saving_pd[sate_id].sort_values(by=[f'Sate_{sate_id}'], ascending=False, inplace=True)

    @staticmethod
    def get_vertex(link):
        # convert link string to link list to handle saving's key, i.e. str(10, 6) to (10, 6)
        vertices = link.split(',')

        return [int(vertices[0]), int(vertices[1])]

    @staticmethod
    def interior(node, route):
        # determine if a node is interior to a route
        try:
            i = route.index(node)
            # adjacent to depot, not interior
            if i == 0 or i == (len(route) - 1):
                label = False
            else:
                label = True
        except:
            label = False

        return label

    @staticmethod
    def merge(route0, route1, link):
        # merge two routes with a connection link
        if route0.index(link[0]) != (len(route0) - 1):
            route0.reverse()

        if route1.index(link[1]) != 0:
            route1.reverse()

        return route0 + route1

    def calc_route_cap(self,
                       route_list):
        cap_sum = 0

        for vertex_id in route_list:
            cap_sum += self.ins.graph.vertex_dict[vertex_id].demand

        return cap_sum

    def which_route(self,
                    link,
                    sate_id):
        """  determine 4 things:
        1. if the link in any route in routes -> determined by if count_in > 0
        2. if yes, which node is in the route -> returned to node_sel
        3. if yes, which route is the node belongs to -> returned to route id: i_route
        4. are both of the nodes in the same route? -> overlap = 1, yes; otherwise, no"""

        # assume nodes are not in any route
        node_sel = list()
        i_route = [-1, -1]
        count_in = 0

        for route in self.routes_list[sate_id]:
            for node in link:
                try:
                    route.index(node)
                    i_route[count_in] = self.routes_list[sate_id].index(route)
                    node_sel.append(node)
                    count_in += 1
                except:
                    pass

        if i_route[0] == i_route[1]:
            overlap = 1
        else:
            overlap = 0

        return node_sel, count_in, i_route, overlap

    @staticmethod
    def gen_new_route(vertex_pre,
                      vertex_next):
        new_route = Route()

        new_route.route.append(vertex_pre)
        new_route.route_list.append(vertex_pre.id_)

        new_route.route.append(vertex_next)
        new_route.route_list.append(vertex_next.id_)

        return new_route

    def check_time_window_feasible(self,
                                   route_list):

        cur_index = 0
        cur_finish_time = self.ins.graph.vertex_dict[
                              route_list[cur_index]].ready_time + self.ins.model_para.service_time

        while cur_index != len(route_list):
            distance = self.ins.graph.arc_dict[cur_index, cur_index + 1].distance

            if cur_finish_time + distance <= self.ins.graph.vertex_dict[cur_index + 1].due_time:
                cur_finish_time += distance

                if cur_finish_time < self.ins.graph.vertex_dict[cur_index + 1].ready_time:
                    cur_finish_time = self.ins.graph.vertex_dict[cur_index + 1].ready_time

                cur_finish_time += self.ins.model_para.service_time

                cur_index += 1

            else:
                return False

        return True

    def gen_routes(self,
                   sate_id):
        """ """
        for route_list in self.routes_list[sate_id]:
            new_route = Route()
            new_route.set_sate_route(sate=self.ins.graph.vertex_dict[sate_id])
            new_route.set_start_time(sate=sate_id,
                                     ins=self.ins)
            new_route.cost += self.ins.model_para.vehicle_2_cost

            route_list.append(self.ins.graph.sate_to_depot[sate_id])
            for vertex_id in route_list:
                vertex_pre = new_route.route[-1]
                vertex_cur = self.ins.graph.vertex_dict[vertex_id]
                distance = self.ins.graph.arc_dict[vertex_pre.id_, vertex_cur.id_].distance

                new_route.add_vertex_into_route(vertex=vertex_cur,
                                                distance=distance,
                                                service_time=self.ins.model_para.service_time)

            self.routes[sate_id].append(new_route)

    def gen_all_sate_routes(self):
        for sate_id in self.ins.graph.sate_list:
            self.gen_routes(sate_id=sate_id)

    def turn_routes_into_sol(self,
                             routes):
        sol = Sol(ins=self.ins)

        for route in routes:
            sol.add_route_into_sol(route=route)

        return sol

    def run(self,
            sate_id):
        """ """
        customer_list = deepcopy(self.ins.graph.sate_serv_cus[sate_id])
        serv_time = self.ins.model_para.service_time
        remaining = True

        for link in self.saving_pd[sate_id].index:
            # link = '3, 7'
            self.step += 1

            if remaining:

                link = self.get_vertex(link=link)  # link = [3, 7]
                vertex_pre = self.ins.graph.vertex_dict[link[0]]
                vertex_next = self.ins.graph.vertex_dict[link[1]]

                # node_sel: vertex which in route
                # num_in: unm of vertex in link which in route
                # i_route: route index in routes
                # overlap: are both of the nodes in the same route? -> overlap = 1
                node_sel, num_in, i_route, overlap = self.which_route(link=link,
                                                                      sate_id=sate_id)

                """ 
                    condition a. Either, neither i nor j have already been assigned to a route,
                    ...in which case a new route is initiated including both i and j.
                 """
                if num_in == 0:
                    if self.calc_route_cap(link) <= self.cap and vertex_pre.ready_time + serv_time + \
                            self.ins.graph.arc_dict[vertex_pre.id_, vertex_next.id_].distance <= vertex_next.due_time:

                        self.routes_list[sate_id].append(link)
                        # new_route = self.gen_new_route(vertex_pre=vertex_pre,
                        #                                vertex_next=vertex_next)

                        customer_list.remove(link[0])
                        customer_list.remove(link[1])
                        print('\t', 'Link ', link, ' fulfills criteria a), so it is created as a new route')
                    else:
                        print('\t', 'Though Link ', link,
                              ' fulfills criteria a), it exceeds maximum load, so skip this link.')

                elif num_in == 1:
                    """                    
                    # condition b. Or, exactly one of the two nodes (i or j) has already been included
                    # ...in an existing route and that point is not interior to that route
                    # ...(a point is interior to a route if it is not adjacent to the depot D in the order of 
                    traversal of nodes),
                    # ...in which case the link (i, j) is added to that same route.
                    """

                    n_sel = node_sel[0]
                    i_rt = i_route[0]
                    position = self.routes_list[sate_id][i_rt].index(n_sel)
                    link_temp = link.copy()
                    link_temp.remove(n_sel)
                    vertex = link_temp[0]
                    # if 19 in link:
                    #     print()

                    cond1 = (not self.interior(n_sel, self.routes_list[sate_id][i_rt]))
                    cond2 = (self.calc_route_cap(route_list=self.routes_list[sate_id][i_rt] + [vertex]) <= self.cap)
                    cond3 = (self.check_time_window_feasible(route_list=self.routes_list[sate_id][i_rt] + [vertex]))

                    if cond1:
                        if cond2 and cond3:
                            print('\t', 'Link ', link, ' fulfills criteria b), so a new node is added to route ',
                                  self.routes_list[sate_id][i_rt], '.')
                            if position == 0:
                                self.routes_list[sate_id][i_rt].insert(0, vertex)
                            else:
                                self.routes_list[sate_id][i_rt].append(vertex)
                            customer_list.remove(vertex)
                        else:
                            print('\t', 'Though Link ', link,
                                  ' fulfills criteria b), it exceeds maximum load, so skip this link.')
                            continue
                    else:
                        continue

                else:
                    """
                    # condition c. Or, both i and j have already been included in two different existing routes
                    # ...and neither point is interior to its route, in which case the two routes are merged.
                    """
                    if overlap == 0:
                        cond1 = (not self.interior(node_sel[0], self.routes_list[sate_id][i_route[0]]))
                        cond2 = (not self.interior(node_sel[1], self.routes_list[sate_id][i_route[1]]))
                        cond3 = (self.calc_route_cap(
                            route_list=self.routes_list[sate_id][i_route[0]] + self.routes_list[sate_id][
                                i_route[1]]) <= self.cap)

                        if cond1 and cond2:
                            if cond3:
                                route_temp = self.merge(route0=self.routes_list[sate_id][i_route[0]],
                                                        route1=self.routes_list[sate_id][i_route[1]],
                                                        link=node_sel)
                                cond4 = (self.check_time_window_feasible(route_list=route_temp))

                                if cond4:
                                    temp1 = self.routes_list[sate_id][i_route[0]]
                                    temp2 = self.routes_list[sate_id][i_route[1]]
                                    self.routes_list[sate_id].remove(temp1)
                                    self.routes_list[sate_id].remove(temp2)
                                    self.routes_list[sate_id].append(route_temp)

                                    try:
                                        customer_list.remove(link[0])
                                        customer_list.remove(link[1])
                                    except:
                                        # print('\t', f"Node {link[0]} or {link[1]} has been
                                        # removed in a previous step.")
                                        pass

                                        print('\t', 'Link ', link, ' fulfills criteria c), so route ', temp1,
                                              ' and route ', temp2, ' are merged')
                                else:
                                    print('\t', 'Though Link ', link,
                                          ' fulfills criteria c), it exceeds maximum load, so skip this link.')
                                    continue
                        else:
                            print('\t', 'For link ', link,
                                  ', Two nodes are found in two different routes, but not all the nodes'
                                  ' fulfill interior requirement, so skip this link')
                            continue
                    else:
                        print('\t', 'Link ', link, ' is already included in the routes')
                        continue
            else:
                print('-------')
                print('All nodes are included in the routes, algorithm closed')
                break

            remaining = bool(len(customer_list) > 0)

        if remaining:
            for cus in customer_list:
                self.routes_list[sate_id].append([cus])

        self.gen_routes(sate_id=sate_id)
        print(self.routes_list)
