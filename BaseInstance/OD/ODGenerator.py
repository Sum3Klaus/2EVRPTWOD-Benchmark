# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-15:35
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import math
import random

import numpy as np
from scipy.spatial import distance
from geopy.distance import geodesic
from ODTask import ODTask
from Arc import Arc
from Common import *


class GenOD(object):
    # np.random.seed(0)

    def __init__(self,
                 graph):
        self.graph_ = graph
        # self.time_period = [100 * i for i in range(12)]
        # self.time_period = self.graph_.customer_list
        self.time_period = [660, 1020]  # 0: 中午 1: 下午，为了更加贴近真实情况 {0: 660, 1: 1020}
        # self.gen_od_task()
        self.square_customer_coord = [[+float('inf'), -float('inf')],
                                      [+float('inf'), -float('inf')]]  # [[x_min, x_max], [y_min, y_max]]
        self.diagonal = 0
        self.average_ready_time = 0
        self.average_due_time = 0
        self.average_demand = sum([self.graph_.vertex_dict[cus].demand for cus in self.graph_.customer_list]) / len(
            self.graph_.customer_list)

    def get_customer_square(self):
        """  """
        for cus in self.graph_.customer_list:
            # x
            if self.graph_.vertex_dict[cus].x_coord < self.square_customer_coord[0][0]:
                self.square_customer_coord[0][0] = self.graph_.vertex_dict[cus].x_coord

            if self.graph_.vertex_dict[cus].x_coord > self.square_customer_coord[0][1]:
                self.square_customer_coord[0][1] = self.graph_.vertex_dict[cus].x_coord

            # y
            if self.graph_.vertex_dict[cus].y_coord < self.square_customer_coord[1][0]:
                self.square_customer_coord[1][0] = self.graph_.vertex_dict[cus].y_coord

            if self.graph_.vertex_dict[cus].y_coord > self.square_customer_coord[1][1]:
                self.square_customer_coord[1][1] = self.graph_.vertex_dict[cus].y_coord

            # time
            self.average_ready_time += self.graph_.vertex_dict[cus].ready_time
            self.average_due_time += self.graph_.vertex_dict[cus].due_time

        # d = max([
        #     self.square_customer_coord[0][1], self.square_customer_coord[1][0]
        # ])

        d = max(
            self.square_customer_coord[0][1] - self.square_customer_coord[0][0],
            self.square_customer_coord[1][1] - self.square_customer_coord[1][0]
        )

        self.diagonal = math.sqrt(
            d ** 2 + d ** 2
        )

        self.average_ready_time /= len(self.graph_.customer_list)
        self.average_due_time /= len(self.graph_.customer_list)

    def get_customer_square_real_case(self):
        for cus in self.graph_.customer_list:
            # x
            if self.graph_.vertex_dict[cus].x_coord < self.square_customer_coord[0][0]:
                self.square_customer_coord[0][0] = self.graph_.vertex_dict[cus].x_coord

            if self.graph_.vertex_dict[cus].x_coord > self.square_customer_coord[0][1]:
                self.square_customer_coord[0][1] = self.graph_.vertex_dict[cus].x_coord

            # y
            if self.graph_.vertex_dict[cus].y_coord < self.square_customer_coord[1][0]:
                self.square_customer_coord[1][0] = self.graph_.vertex_dict[cus].y_coord

            if self.graph_.vertex_dict[cus].y_coord > self.square_customer_coord[1][1]:
                self.square_customer_coord[1][1] = self.graph_.vertex_dict[cus].y_coord

            # time
            self.average_ready_time += self.graph_.vertex_dict[cus].ready_time
            self.average_due_time += self.graph_.vertex_dict[cus].due_time

        # 构建最小正方形
        d = max(
            round(self.square_customer_coord[0][1], 4) - round(self.square_customer_coord[0][0], 4),
            round(self.square_customer_coord[1][1], 4) - round(self.square_customer_coord[1][0], 4)
        )

        # 纬度范围
        lat_min = (round(self.square_customer_coord[0][1], 4) - round(self.square_customer_coord[0][0], 4) - d) / 2
        lat_max = (round(self.square_customer_coord[0][1], 4) - round(self.square_customer_coord[0][0], 4) + d) / 2
        # 经度范围
        lng_min = (round(self.square_customer_coord[1][1], 4) - round(self.square_customer_coord[1][0], 4) - d) / 2
        lng_max = (round(self.square_customer_coord[1][1], 4) - round(self.square_customer_coord[1][0], 4) + d) / 2
        # 计算对角线距离（米）
        self.diagonal = geodesic((lat_min, lng_min), (lat_max, lng_max)).meters
        self.average_ready_time /= len(self.graph_.customer_list)
        self.average_due_time /= len(self.graph_.customer_list)
        # print()

    def _gen_od_origin(self):
        sate_select = np.random.choice(self.graph_.sate_list)
        # 随机角度
        theta = np.random.uniform(0, 2 * math.pi)
        # cur_dis = np.random.randint(0, math.floor(self.diagonal))
        cur_dis_times = np.random.uniform(0.2, 0.35)
        cur_dis = int(cur_dis_times * self.diagonal)

        # 计算随机点的坐标
        x = self.graph_.vertex_dict[sate_select].x_coord + cur_dis * math.cos(theta)
        y = self.graph_.vertex_dict[sate_select].y_coord + cur_dis * math.sin(theta)

        return sate_select, int(x), int(y)

    def _gen_od_origin_base_cus(self,
                                cus):
        sate_select = self.graph_.cus_belong_sate[cus]
        # 随机角度
        theta = np.random.uniform(0, 2 * math.pi)
        # cur_dis = np.random.randint(0, math.floor(self.diagonal))
        cur_dis_times = np.random.uniform(0.05, 0.25)
        cur_dis = int(cur_dis_times * self.diagonal)

        # 计算随机点的坐标
        x = self.graph_.vertex_dict[sate_select].x_coord + cur_dis * math.cos(theta)
        y = self.graph_.vertex_dict[sate_select].y_coord + cur_dis * math.sin(theta)

        return sate_select, int(x), int(y)

    def _gen_od_destination(self):
        customer_select = np.random.choice(self.graph_.customer_list)
        # 随机角度
        theta = np.random.uniform(0, 2 * math.pi)
        cur_dis_times = np.random.uniform(0.05, 0.15)
        # cur_dis = np.random.randint(0, math.floor(self.diagonal))
        cur_dis = int(cur_dis_times * self.diagonal)

        # 计算随机点的坐标
        x = self.graph_.vertex_dict[customer_select].x_coord + cur_dis * math.cos(theta)
        y = self.graph_.vertex_dict[customer_select].y_coord + cur_dis * math.sin(theta)

        return customer_select, int(x), int(y)

    def gen_od_origin_and_destination(self):
        # capacity_times = np.random.uniform(1.0, 3.0,)
        # capacity_times = 1
        capacity_times = 1 + np.random.randint(1, 11) / 10.0
        self.graph_.ins.model_para.vehicle_od_capacity = int(self.average_demand * capacity_times)

        # sate_select, origin_x, origin_y = self._gen_od_origin()
        # customer_select, destination_x, destination_y = self._gen_od_destination()

        customer_select, destination_x, destination_y = self._gen_od_destination()
        sate_select, origin_x, origin_y = self._gen_od_origin_base_cus(cus=customer_select)

        return [origin_x, origin_y], [destination_x, destination_y], [sate_select, customer_select]

    def gen_od_task2(self,
                     od_extend_time):
        for i in range(self.graph_.ins.od_num):
            time_period_select = np.random.choice(self.time_period)

            id_ = 1 + self.graph_.ins.sate_num * 2 + self.graph_.ins.customer_num + i

            coord_x = [self.graph_.vertex_dict[c].x_coord for c in self.graph_.customer_list]
            coord_y = [self.graph_.vertex_dict[c].y_coord for c in self.graph_.customer_list]

            # origin node
            origin_x = np.random.randint(low=(max(coord_x) - 20), high=(max(coord_x) + 10))
            origin_y = np.random.randint(low=(max(coord_y) - 20), high=(max(coord_y) + 10))
            origin_ready_time = time_period_select - np.random.randint(0, 30) - od_extend_time
            if origin_ready_time <= 0:
                origin_ready_time = 0

            origin_due_time = origin_ready_time + np.random.randint(0, 15)

            origin_vertex = Vertex(id_=id_,
                                   ready_time=origin_ready_time,
                                   due_time=origin_due_time,
                                   x_coord=origin_x,
                                   y_coord=origin_y)

            # terminate node
            terminate_x = np.random.randint(low=(max(coord_x) - 30), high=(max(coord_x) + 15))
            terminate_y = np.random.randint(low=(max(coord_y) - 30), high=(max(coord_y) + 15))

            cur_distance = round(calc_travel_time(
                x_1=origin_x,
                x_2=terminate_x,
                y_1=origin_y,
                y_2=terminate_y
            ), 2)

            terminate_ready_time = origin_due_time + cur_distance
            # terminate_due_time = terminate_ready_time + np.random.randint(150, 200)
            # terminate_due_time = terminate_ready_time + od_extend_time + cur_distance
            terminate_due_time = terminate_ready_time + od_extend_time + np.random.randint(0, 5)

            terminate_vertex = Vertex(
                id_=1 + self.graph_.ins.sate_num * 2 + self.graph_.ins.customer_num + i + self.graph_.ins.od_num,
                ready_time=terminate_ready_time,
                due_time=terminate_due_time,
                x_coord=terminate_x,
                y_coord=terminate_y)

            self.graph_.vertex_dict[origin_vertex.id_] = origin_vertex
            self.graph_.vertex_dict[terminate_vertex.id_] = terminate_vertex
            origin_vertex.successors_2nd.append(terminate_vertex)
            terminate_vertex.predecessors_2nd.append(origin_vertex)

            new_arc = Arc(
                head_vertex=origin_vertex.id_, tail_vertex=terminate_vertex.id_,
                distance=cur_distance,
                adj=1
            )

            # add task
            new_task = ODTask(_id=i,
                              origin_node=origin_vertex,
                              terminate_node=terminate_vertex,
                              dis=cur_distance,
                              arc=new_arc)

            self.graph_.od_task_dict[i] = new_task

    def gen_od_task(self,
                    od_extend_time):
        """ """
        # od_coord_dict = dict()
        # od_time_dict = dict()
        for i in range(self.graph_.ins.od_num):
            id_ = 1 + self.graph_.ins.sate_num * 2 + self.graph_.ins.customer_num + i

            origin_coord, destination_coord, sate_cus_select = self.gen_od_origin_and_destination()
            # od_coord_dict[id_] = [origin_coord, destination_coord]

            cur_distance = round(calc_travel_time(
                x_1=origin_coord[0],
                x_2=destination_coord[0],
                y_1=origin_coord[1],
                y_2=destination_coord[1]
            ), 2)

            # origin_ready_times = np.random.uniform(0.1, 0.5)
            # origin_ready_time = int(origin_ready_times * self.average_ready_time)

            # origin_due_times = np.random.uniform(0.5, 1)
            # origin_due_time = int(origin_due_times * self.average_ready_time)

            """ 小距离算例 """
            # origin vertex
            delta_time1 = np.random.randint(20, 31)
            origin_ready_time = self.average_ready_time - delta_time1
            origin_due_time = self.average_ready_time + delta_time1

            """ 大距离算例 """
            # o_ready_times = np.random.randint(1, 5) / 10.0  # diagonal
            # origin_ready_time = self.average_ready_time - o_ready_times*self.diagonal
            # origin_due_time = self.average_ready_time + o_ready_times*self.diagonal

            # r = np.random.randint(0, int(self.average_ready_time / 2))
            # origin_ready_time = int(self.graph_.vertex_dict[sate_cus_select[1]].ready_time - r)
            # origin_due_time = int(self.graph_.vertex_dict[sate_cus_select[1]].ready_time + r)

            origin_vertex = Vertex(id_=id_,
                                   ready_time=origin_ready_time,
                                   due_time=origin_due_time,
                                   x_coord=origin_coord[0],
                                   y_coord=origin_coord[1])

            # destination_ready_times = np.random.uniform(0.1, 0.5)
            # destination_due_times = np.random.uniform(0.5, 1)

            # destination_ready_time = int(destination_ready_times * self.average_due_time)
            # destination_due_time = destination_due_times * (self.average_due_time + cur_distance) + od_extend_time
            """ 小距离算例 """
            # destination vertex
            delta_time2 = np.random.randint(15, 31)
            destination_ready_time = self.average_due_time - delta_time2
            destination_due_time = self.average_due_time + delta_time2 + od_extend_time

            # destination_ready_time = origin_ready_time + cur_distance - delta_time2
            # destination_due_time = origin_ready_time + cur_distance + delta_time2
            # destination_due_time = origin_due_time + cur_distance + delta_time2

            """ 大距离算例 """
            # d_due_times = np.random.randint(1, 5) / 10.0  # diagonal
            # destination_ready_time = self.average_due_time - d_due_times * self.diagonal
            # destination_due_time = self.average_due_time + od_extend_time + d_due_times * self.diagonal

            if destination_due_time - origin_ready_time < cur_distance:
                destination_due_time = origin_due_time + cur_distance

            # destination_ready_time = int(0.5 * self.average_due_time)
            # destination_due_time = int(1.0 * self.average_due_time + cur_distance)

            # r = np.random.randint(0, int(self.average_due_time / 2))
            # destination_ready_time = int(self.graph_.vertex_dict[sate_cus_select[1]].due_time - r)
            # destination_due_time = int(self.graph_.vertex_dict[sate_cus_select[1]].due_time + r) + od_extend_time

            destination_vertex = Vertex(
                id_=1 + self.graph_.ins.sate_num * 2 + self.graph_.ins.customer_num + i + self.graph_.ins.od_num,
                ready_time=destination_ready_time,
                due_time=destination_due_time,
                x_coord=destination_coord[0],
                y_coord=destination_coord[1])
            # destination_vertex = Vertex(
            #     id_=1 + self.graph_.ins.sate_num * 2 + self.graph_.ins.customer_num + i + self.graph_.ins.od_num,
            #     ready_time=origin_due_time + delta_time_lb,
            #     due_time=origin_due_time + cur_distance + delta_time_ub + od_extend_time,
            #     x_coord=destination_coord[0],
            #     y_coord=destination_coord[1])

            self.graph_.vertex_dict[origin_vertex.id_] = origin_vertex
            self.graph_.vertex_dict[destination_vertex.id_] = destination_vertex
            origin_vertex.successors_2nd.append(destination_vertex)
            destination_vertex.predecessors_2nd.append(origin_vertex)

            new_arc = Arc(
                head_vertex=origin_vertex.id_, tail_vertex=destination_vertex.id_,
                distance=cur_distance,
                adj=1
            )

            # od_time_dict[id_] = [[origin_ready_time, origin_due_time],
            #                      [destination_ready_time, destination_due_time]]
            # add task
            new_task = ODTask(_id=i,
                              origin_node=origin_vertex,
                              terminate_node=destination_vertex,
                              dis=cur_distance,
                              arc=new_arc)

            self.graph_.od_task_dict[i] = new_task
        print()
