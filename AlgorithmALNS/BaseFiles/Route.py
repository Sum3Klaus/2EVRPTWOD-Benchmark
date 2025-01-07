# -*- coding: utf-8 -*-
# @Time     : 2024-04-14-21:49
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import Common
from geopy.distance import geodesic


class Route(object):
    """ 没有等级分别，1st用gurobi求解 """

    def __init__(self):
        self.id_ = 0

        self.cost = 0.0
        self.distance = 0.0
        self.route = []  # vertex
        self.route_list = []  # vertex_id

        self.timeTable = [0]
        self.arriveTime = [0]
        self.capacityTable = [0]

    def print_route(self):
        formatted_route = ', '.join(str(item) for item in self.route)
        return print('route-{:<5d}=[{:<25s}]   | {:<5f}'.format(self.id_, formatted_route, self.cost))

    def __repr__(self):
        return f'route-{self.id_}={self.route} | cost={self.cost}'

    def add_vertex_into_route(self,
                              vertex,
                              distance,
                              service_time):
        self.route.append(vertex)
        self.route_list.append(vertex.id_)

        self.cost += distance
        self.distance += distance

        if self.timeTable[-1] == 0:
            next_start_time = self.timeTable[-1] + distance
        else:
            next_start_time = self.timeTable[-1] + distance + service_time
        self.arriveTime.append(next_start_time)
        self.timeTable.append(next_start_time if next_start_time >= vertex.ready_time else vertex.ready_time)
        self.capacityTable.append(vertex.demand)

    def remove_vertex(self, vertex):
        self.route.remove(vertex)
        self.route_list.remove(vertex.id_)

    def insert_vertex(self, index, vertex):
        self.route.insert(index, vertex)
        self.route_list.insert(index, vertex.id_)

    def ini_route(self):
        self.cost = 0.0
        self.distance = 0.0

        self.timeTable = [0]
        self.arriveTime = [0]
        self.capacityTable = [0]

    def update_route(self):
        """ 求解过程中生成路径 """
        pre_id = 0
        for vertex in range(len(self.route) - 1):
            next_id = pre_id + 1

            cur_distance = Common.calc_travel_time(x_1=self.route[pre_id].x_coord, y_1=self.route[pre_id].y_coord,
                                                   x_2=self.route[next_id].x_coord, y_2=self.route[next_id].y_coord)

            # cur_distance = geodesic((self.route[pre_id].x_coord, self.route[pre_id].y_coord),
            #                         (self.route[next_id].x_coord, self.route[next_id].y_coord)).meters / 100

            self.cost += cur_distance
            self.distance += cur_distance

            service_time = self.route[next_id].service_time if pre_id >= 1 else 0

            next_start_time = self.timeTable[-1] + cur_distance + service_time
            self.timeTable.append(next_start_time if next_start_time >= self.route[next_id].ready_time else self.route[
                next_id].ready_time)
            self.arriveTime.append(next_start_time)
            self.capacityTable.append(self.route[next_id].demand)

            pre_id += 1

    def set_sate_route(self,
                       sate):
        # self.timeTable[0] = sate_start
        self.route.append(sate)
        self.route_list.append(sate.id_)

    def set_start_time(self,
                       ins,
                       sate):
        self.timeTable[0] = ins.sate_arrive_time[sate]
        self.arriveTime[0] = ins.sate_arrive_time[sate]

    def input_start_and_return(self,
                               ins,
                               vertex_start,
                               vertex_return
                               ):

        self.insert_vertex(0, vertex_start)
        self.insert_vertex(len(self.route), vertex_return)
        self.ini_route()

        self.set_start_time(ins=ins,
                            sate=vertex_start.id_)

        self.update_route()

    def turn_route_list_into_route(self,
                                   route_list,
                                   level,
                                   ins):
        self.ini_route()
        self.route_list = list()
        self.route = list()

        if level == 1:
            self.cost += ins.model_para.vehicle_1_cost
            service_time = ins.model_para.t_unload
        else:
            self.cost += ins.model_para.vehicle_2_cost
            service_time = ins.model_para.service_time

            self.set_start_time(ins=ins,
                                sate=route_list[0])

        self.route.append(ins.graph.vertex_dict[route_list[0]])
        self.route_list.append(route_list[0])

        for vertex_id in route_list[1:]:
            cur_distance = ins.graph.arc_dict[self.route_list[-1], vertex_id].distance
            self.add_vertex_into_route(vertex=ins.graph.vertex_dict[vertex_id],
                                       distance=cur_distance,
                                       service_time=service_time)