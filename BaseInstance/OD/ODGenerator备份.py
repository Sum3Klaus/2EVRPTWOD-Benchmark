# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-15:35
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from ODTask import ODTask
from Arc import Arc
from Common import *


class GenOD(object):
    np.random.seed(0)

    def __init__(self,
                 graph):
        self.graph_ = graph
        # self.time_period = [100 * i for i in range(12)]
        # self.time_period = self.graph_.customer_list
        self.time_period = [660, 1020]   # 0: 中午 1: 下午，为了更加贴近真实情况 {0: 660, 1: 1020}
        # self.gen_od_task()

    def gen_od_task(self,
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

            origin_due_time = origin_ready_time + np.random.randint(10, 30)

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
