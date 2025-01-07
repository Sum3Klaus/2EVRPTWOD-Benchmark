# -*- coding: utf-8 -*-
# @Time     : 2024-08-05-16:12
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import pandas as pd
import numpy as np
from Solution import *
from copy import deepcopy
from Route import *


class SavingAlgorithm(object):
    """
    设计 sate selection 的 Saving Algorithm
    https://github.com/zuzhaoye/vehicle-routing-problem-vrp-Clarke-Wright-Savings-Method/blob/master/cw_algorithm.ipynb
    """

    @staticmethod
    def calc_saving(ins,
                    depot_start_id,
                    vertex_id_list):
        savings = dict()

        for cus_id_1 in range(len(vertex_id_list)):
            cus_1 = vertex_id_list[cus_id_1]

            for cus_id_2 in range(cus_id_1 + 1, len(vertex_id_list)):
                if cus_id_1 != cus_id_2:
                    cus_2 = vertex_id_list[cus_id_2]

                    savings[str(cus_1) + ',' + str(cus_2)] = ins.graph.arc_dict[depot_start_id, cus_1].distance + \
                                                             ins.graph.arc_dict[depot_start_id, cus_2].distance - \
                                                             ins.graph.arc_dict[cus_1, cus_2].distance
        saving_pd = pd.DataFrame.from_dict(savings, orient='index')

        saving_pd.rename(columns={0: 'saving'}, inplace=True)
        saving_pd.sort_values(by=['saving'], ascending=False, inplace=True)

        return saving_pd

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

    @staticmethod
    def calc_route_cap(ins,
                       route_list):
        cap_sum = 0

        for vertex_id in route_list:
            cap_sum += ins.graph.vertex_dict[vertex_id].demand

        return cap_sum

    @staticmethod
    def which_route(routes_id_list,
                    link):
        """  determine 4 things:
        1. if the link in any route in routes -> determined by if count_in > 0
        2. if yes, which node is in the route -> returned to node_sel
        3. if yes, which route is the node belongs to -> returned to route id: i_route
        4. are both of the nodes in the same route? -> overlap = 1, yes; otherwise, no"""

        # assume nodes are not in any route
        node_sel = list()
        i_route = [-1, -1]
        count_in = 0

        for route in routes_id_list:
            for node in link:
                try:
                    route.index(node)
                    i_route[count_in] = routes_id_list.index(route)
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
    def check_time_window_feasible(ins,
                                   level,
                                   route_list):

        service_time = ins.model_para.service_time if level == 2 else ins.model_para.t_unload

        cur_index = 0
        cur_finish_time = ins.graph.vertex_dict[
                              route_list[cur_index]].ready_time + service_time

        while cur_index != len(route_list):
            distance = ins.graph.arc_dict[cur_index, cur_index + 1].distance

            if cur_finish_time + distance <= ins.graph.vertex_dict[cur_index + 1].due_time:
                cur_finish_time += distance

                if cur_finish_time < ins.graph.vertex_dict[cur_index + 1].ready_time:
                    cur_finish_time = ins.graph.vertex_dict[cur_index + 1].ready_time

                cur_finish_time += service_time

                cur_index += 1

            else:
                return False

        return True

    @staticmethod
    def input_start_and_return(ins,
                               routes_id_list,
                               deport_start,
                               deport_return,
                               fixed_cost,
                               service_time):
        """ """
        routes = []
        for route in routes_id_list:
            new_route = Route()
            new_route.set_sate_route(sate=ins.graph.vertex_dict[deport_start])
            new_route.set_start_time(ins=ins,
                                     sate=deport_start)
            new_route.cost += fixed_cost

            route.append(deport_return)
            for vertex_id in route:
                new_route.add_vertex_into_route(vertex=ins.graph.vertex_dict[vertex_id],
                                                distance=ins.graph.arc_dict[
                                                    new_route.route_list[-1], vertex_id].distance,
                                                service_time=service_time)
            routes.append(new_route)
        return routes

    def run(self,
            ins,
            deport_start,
            deport_return,
            vertex_id_list,
            level):

        # calc saving
        savings_pd = self.calc_saving(ins=ins,
                                      depot_start_id=deport_start,
                                      vertex_id_list=vertex_id_list)

        # create empty routes
        routes_id_list = list()

        # if there is any remaining customer to be served
        remaining = True

        # define capacity of the vehicle
        cap = ins.model_para.vehicle_1_capacity if level == 1 else ins.model_para.vehicle_2_capacity
        service_time = ins.model_para.t_unload if level == 1 else ins.model_para.service_time
        fixed_cost = ins.model_para.vehicle_1_cost if level == 1 else ins.model_para.vehicle_2_cost

        # record steps
        step = 0

        customer_list = deepcopy(vertex_id_list)

        for link in savings_pd.index:
            step += 1
            if remaining:

                link = self.get_vertex(link=link)

                vertex_pre = ins.graph.vertex_dict[link[0]]
                vertex_next = ins.graph.vertex_dict[link[1]]

                # node_sel: vertex which in route
                # num_in: unm of vertex in link which in route
                # i_route: route index in routes
                # overlap: are both of the nodes in the same route? -> overlap = 1
                node_sel, num_in, i_route, overlap = self.which_route(link=link,
                                                                      routes_id_list=routes_id_list)

                """ 
                    condition a. Either, neither i nor j have already been assigned to a route,
                    ...in which case a new route is initiated including both i and j.
                 """
                if num_in == 0:
                    if self.calc_route_cap(ins=ins,
                                           route_list=link) <= cap and vertex_pre.ready_time + service_time + \
                            ins.graph.arc_dict[vertex_pre.id_, vertex_next.id_].distance <= vertex_next.due_time:

                        routes_id_list.append(link)
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
                    position = routes_id_list[i_rt].index(n_sel)
                    link_temp = link.copy()
                    link_temp.remove(n_sel)
                    vertex = link_temp[0]

                    cond1 = (not self.interior(n_sel, routes_id_list[i_rt]))
                    cond2 = (self.calc_route_cap(ins=ins,
                                                 route_list=routes_id_list[i_rt] + [vertex]) <= cap)
                    cond3 = (self.check_time_window_feasible(ins=ins,
                                                             route_list=routes_id_list[i_rt] + [vertex],
                                                             level=level))

                    if cond1:
                        if cond2 and cond3:
                            print('\t', 'Link ', link, ' fulfills criteria b), so a new node is added to route ',
                                  routes_id_list[i_rt], '.')
                            if position == 0:
                                routes_id_list[i_rt].insert(0, vertex)
                            else:
                                routes_id_list[i_rt].append(vertex)
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
                        cond1 = (not self.interior(node_sel[0], routes_id_list[i_route[0]]))
                        cond2 = (not self.interior(node_sel[1], routes_id_list[i_route[1]]))
                        cond3 = (self.calc_route_cap(ins=ins,
                                                     route_list=routes_id_list[i_route[0]] + routes_id_list[
                                                         i_route[1]]) <= cap)

                        if cond1 and cond2:
                            if cond3:
                                route_temp = self.merge(route0=routes_id_list[i_route[0]],
                                                        route1=routes_id_list[i_route[1]],
                                                        link=node_sel)
                                cond4 = (self.check_time_window_feasible(ins=ins,
                                                                         level=level,
                                                                         route_list=route_temp))

                                if cond4:
                                    temp1 = routes_id_list[i_route[0]]
                                    temp2 = routes_id_list[i_route[1]]
                                    routes_id_list.remove(temp1)
                                    routes_id_list.remove(temp2)
                                    routes_id_list.append(route_temp)

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

        if len(customer_list) > 0:
            for c in customer_list:
                routes_id_list.append([c])

        routes = self.input_start_and_return(ins=ins,
                                             routes_id_list=routes_id_list,
                                             deport_start=deport_start,
                                             deport_return=deport_return,
                                             fixed_cost=fixed_cost,
                                             service_time=service_time
                                             )
        return routes

    def gen_saving_sol(self,
                       ins,
                       deport_start,
                       deport_return,
                       vertex_id_list,
                       level):

        saving_sol = Sol(ins=ins)

        routes = self.run(ins=ins,
                          deport_start=deport_start,
                          deport_return=deport_return,
                          vertex_id_list=vertex_id_list,
                          level=level)

        for route in routes:
            saving_sol.add_route_into_sol(route=route)

        return saving_sol