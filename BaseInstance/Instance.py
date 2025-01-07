# -*- coding: utf-8 -*-
# @Time     : 2024-07-29-22:42
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import math
import random
from copy import deepcopy
from random import *
from ModelPara import ModelParameters
from Common import *
from ODGenerator import GenOD
from ODTask import *
from SateGenerator import GenSate
from Graph import *
import matplotlib.pyplot as plt
import itertools
import ast
from scipy.spatial import distance
from geopy.distance import geodesic


class Instance(object):

    def __init__(self,
                 params: ModelParameters,
                 od_num: int,
                 is_select: bool,
                 benchmark_id: int,
                 initial_value
                 ):
        """

        :param params: gurobi model parameters
        :param od_num: Occasional Drivers num
        :param is_select: is sate selection
        :param benchmark_id: 0: Solomon, 1:Breunig & Papadopoulos, 2: kancharla-ramadurai
        """
        self.model_para = params

        self.od_num = od_num

        self.is_select = is_select
        self.benchmark_id = benchmark_id

        self.sate_num = 0
        self.customer_num = 0
        self.sate_capacity = 0

        self.od_cost = 0
        self.od_travel_compensation = 0  # = iter_hun.ins.od_cost * ins.model_para.c_c
        self.iter_od_use = 0

        self.graph = Graph(ins=self)

        self.vehicle_num_1st = 0
        self.vehicle_num_2nd = 0

        self.gen_od_task = None
        self.gen_sate = None
        self.od_cus_matcher = None

        # self.hungarian_list = [[] * i for i in range(self.map_.customer_num)]
        self.od_cus_matchDict = dict()
        self.customer_list_alns = None
        self.customer_list_od = list()

        self.alns_dict = None
        # self.alns_customers = None

        self.sate_arrive_time = {}

        # alns
        self.span_time_dict_sate = None
        self.span_time_dict_sate_sort = None

        # time windows
        self.sata_distance_sum = 0
        self.max_start_distance = 0

        self.sate_arrive_time_result = None
        self.routes_1st_result = None
        self.routes_2nd_result = None

        self.result_info_1st = None
        self.result_info_2nd = None

        self.initial_value = initial_value

    def __repr__(self):
        return f'Instance info: [sate_num={self.sate_num}],[customer_num={self.customer_num}],[od_num={self.od_num}]'

    def input_info(self):
        """
        将 instance 的信息输入 Graph， 并生成相关的数据
        :return:
        """
        self.graph.input_graph_info()

        self.alns_dict = {0: self.graph.sate_list}

        # alns
        self.span_time_dict_sate = {sate: {} for sate in self.graph.sate_list}
        self.span_time_dict_sate_sort = {sate: None for sate in self.graph.sate_list}

        if self.benchmark_id != 0:
            self.graph.calc_cus_belong_sate()

    def gen_graph(self):
        self.get_ini_sate_arrive_time()
        self.graph.gen_sub_graphs()

    def gen_graph_real_case(self):
        self.get_ini_sate_arrive_time_real_case()
        self.graph.gen_sub_graphs_real_case()

    # Occasional Drivers Generation Programming
    def cluster_sate(self):
        self.gen_sate = GenSate(graph=self.graph)
        self.gen_sate.get_features()
        self.gen_sate.start_cluster()

    def gen_od(self,
               od_extend_time):
        self.gen_od_task = GenOD(graph=self.graph)
        self.gen_od_task.get_customer_square()
        self.gen_od_task.gen_od_task(od_extend_time=od_extend_time)

        capacity = 0
        for cus in self.graph.customer_list:
            capacity += self.graph.vertex_dict[cus].demand

        # self.model_para.vehicle_od_capacity = capacity / self.customer_num * 2.5

    def get_ini_sate_arrive_time(self):
        """  """
        for sate in self.graph.sate_list:
            cur_distance = calc_travel_time(x_1=self.graph.vertex_dict[0].x_coord,
                                            y_1=self.graph.vertex_dict[0].y_coord,
                                            x_2=self.graph.vertex_dict[sate].x_coord,
                                            y_2=self.graph.vertex_dict[sate].y_coord
                                            )
            # self.sate_arrive_time[sate] = self.graph.arc_dict[(0, sate)].distance
            # self.graph.vertex_dict[sate].ready_time = self.graph.arc_dict[(0, sate)].distance

            self.graph.vertex_dict[sate].ready_time = self.sate_arrive_time[sate] = cur_distance

    def get_ini_sate_arrive_time_real_case(self):
        """  """
        for sate in self.graph.sate_list:
            cur_distance = geodesic((self.graph.vertex_dict[0].x_coord, self.graph.vertex_dict[0].y_coord),
                                    (self.graph.vertex_dict[sate].x_coord, self.graph.vertex_dict[sate].y_coord)).meters

            self.graph.vertex_dict[sate].ready_time = self.sate_arrive_time[sate] = cur_distance / 100

    def calc_alns_dict(self):
        """
        计算在 将客户分配给 ODs 后剩余的 客户
        :return:
        """
        for i in self.graph.sate_list:

            cur_list = []

            for cus in self.graph.sate_serv_cus[i]:
                if cus in self.customer_list_alns:
                    cur_list.append(cus)

            self.alns_dict[i] = cur_list

    def read_data(self,
                  *args,
                  **kwargs):
        """ """
        if self.benchmark_id == 0:
            self.read_solomon_data(*args, **kwargs)
            self.input_info()
            self.cluster_sate()

        elif self.benchmark_id == 1:

            self.read_two_echelon_bp_instance(*args)
            self.input_info()

        elif self.benchmark_id == 2:

            self.read_two_echelon_kr_instance(*args)
            self.input_info()

        elif self.benchmark_id == 3:

            self.read_two_echelon_gptv_instance(*args)
            self.input_info()

    def read_solomon_data(self,
                          filepath,
                          sate_num,
                          cus_num,
                          customer_extend_time):
        """

        :param filepath:
        :param sate_num
        :param cus_num
        :param customer_extend_time
        :return:
        """
        self.sate_num = sate_num
        self.graph.customer_num = self.customer_num = cus_num
        self.calc_od_num()
        self.graph.vertex_num = sate_num * 2 + cus_num + self.od_num * 2 + 2
        self.vehicle_num_1st = sate_num
        self.vehicle_num_2nd = cus_num
        f = open(filepath, 'r')
        lines = f.readlines()

        cnt = 0

        for line in lines:
            cnt += 1
            if cnt == 5:
                line = line[:-1].strip()  # '  5                200\n'
                str_arr = re.split(r" +", line)  # ['5', '200']
                # self.vehicle_num_1st = int(str_arr[0])
                # self.params_.vehicle_1_capacity = int(str_arr[RepairOperators])

            elif cnt == 10:

                line = line[:-1].strip()
                str_arr = re.split(r" +",
                                   line)

                # new_vertex.ID = int(str_arr[0])
                # new_vertex.x_coor = int(str_arr[RepairOperators])
                # new_vertex.y_coor = int(str_arr[2])
                # new_vertex.demand = int(str_arr[3])
                # # new_vertex.demand = 30
                # new_vertex.ready_time = int(str_arr[4])
                # new_vertex.due_time = int(str_arr[5])
                # new_vertex.service_time = int(str_arr[6])

                new_vertex = Vertex(id_=int(str_arr[0]),
                                    ready_time=int(str_arr[4]),
                                    due_time=int(str_arr[5]) + 100,
                                    x_coord=int(str_arr[1]),
                                    y_coord=int(str_arr[2]))

                self.graph.add_vertex(vertex=new_vertex)

            # set satellites
            # elif (cnt > 10) and (cnt <= 10 + self.sate_num):
            #     line = line[:-RepairOperators].strip()
            #     str_arr = re.split(r" +",
            #                        line)

            # elif (cnt > 10) and (cnt <= 10 + self.graph.customer_num + self.sate_num)
            elif (cnt > 10) and (cnt <= 10 + self.graph.customer_num):

                line = line[:-1].strip()
                str_arr = re.split(r" +",
                                   line)

                # new_vertex = Vertex(id_=int(str_arr[0]) + self.sate_num,
                #                     ready_time=int(str_arr[4]),
                #                     due_time=int(str_arr[5]),
                #                     x_coord=int(str_arr[RepairOperators]),
                #                     y_coord=int(str_arr[2]),
                #                     demand=int(str_arr[3]))

                new_vertex = Vertex(id_=int(str_arr[0]) + self.sate_num,
                                    ready_time=int(str_arr[4]),
                                    due_time=int(str_arr[5]) + customer_extend_time,
                                    x_coord=int(str_arr[1]),
                                    y_coord=int(str_arr[2]),
                                    demand=int(str_arr[3]))

                # new_vertex = Vertex(id_=int(str_arr[0]) + self.sate_num,
                #                     ready_time=int(0),
                #                     due_time=int(1440),
                #                     x_coord=int(str_arr[RepairOperators]),
                #                     y_coord=int(str_arr[2]),
                #                     demand=int(str_arr[3]))
                self.sate_capacity += new_vertex.demand

                if cnt <= 10 + self.sate_num:
                    # sate 为取货时间
                    new_vertex.service_time = self.model_para.p

                else:
                    # customer 为服务/送货时间
                    new_vertex.service_time = self.model_para.service_time

                self.graph.add_vertex(vertex=new_vertex)

        # add satellite as depot
        """        
        for i in self.map_.sate_list:
            new_vertex = deepcopy(self.map_.vertex_dict[i])

            # 更新 id 和 时间窗
            new_vertex.id = i + self.map_.sate_num + self.map_.customer_num
            new_vertex.ready_time += 100
            new_vertex.due_time += 150

            self.map_.add_vertex(vertex=new_vertex)
        """

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

        if self.is_select is True:
            self.model_para.m_s = round((self.sate_capacity / self.sate_num) * 1.5)

    def read_two_echelon_bp_instance(self,
                                     filepath):
        """  """
        with open(filepath, 'r') as file:
            lines = file.readlines()
            # vertex_num = 0
            mode = None

            for line in lines:
                line = line.strip()

                if line.startswith('!'):
                    # 确定info title
                    if 'Trucks' in line:
                        mode = 'trucks'
                    elif 'CityFreighters' in line:
                        mode = 'city_freighters'
                    elif 'Stores' in line:
                        mode = 'stores'
                    elif 'Customers' in line:
                        mode = 'customers'
                    else:
                        mode = None
                elif mode == 'trucks' and line:
                    trucks_info = [int(x) if i == 0 else float(x) for i, x in enumerate(line.split(','))]

                    self.vehicle_num_1st = trucks_info[0]
                    self.model_para.vehicle_1_capacity = trucks_info[1]
                    # per cost = trucks_info[2]
                    # self.model_para.vehicle_1_cost = trucks_info[3]

                    mode = None
                elif mode == 'city_freighters' and line:
                    city_freighters_info = [int(x) if i < 3 else float(x) for i, x in enumerate(line.split(','))]

                    self.vehicle_num_2nd = city_freighters_info[0]
                    # self.sate_num = city_freighters_info[1]
                    self.model_para.vehicle_2_capacity = city_freighters_info[2]
                    # per_cost = city_freighters_info[3]
                    # self.model_para.vehicle_2_cost = city_freighters_info[4]

                    mode = None
                elif mode == 'stores' and line:
                    stores_info = [tuple(map(int, coord.split(','))) for coord in line.split()]
                    # vertex_num += len(stores_info)

                    self.sate_num = len(stores_info) - 1

                    depot = Vertex(id_=0,
                                   x_coord=stores_info[0][0],
                                   y_coord=stores_info[0][1],
                                   ready_time=0,
                                   due_time=1440)

                    self.graph.add_vertex(vertex=depot)

                    for index_ in range(1, len(stores_info)):
                        sate = Vertex(id_=index_,
                                      x_coord=stores_info[index_][0],
                                      y_coord=stores_info[index_][1],
                                      ready_time=0,
                                      due_time=1440)
                        sate.service_time = self.model_para.p
                        self.graph.add_vertex(vertex=sate)

                    mode = None
                elif mode == 'customers' and line:
                    customers_info = [tuple(map(int, coord.split(','))) for coord in line.split()]
                    # vertex_num += len(customers_info)
                    self.customer_num = len(customers_info)

                    for cus_id in range(len(customers_info)):
                        customer = Vertex(id_=self.sate_num + cus_id + 1,
                                          x_coord=customers_info[cus_id][0],
                                          y_coord=customers_info[cus_id][1],
                                          ready_time=420,
                                          due_time=1080)
                        customer.service_time = self.model_para.service_time
                        customer.demand = customers_info[cus_id][2]
                        self.graph.add_vertex(vertex=customer)

                    mode = None

            # self.graph.vertex_num = sate_num * 2 + cus_num + self.od_num * 2 + 2
            self.calc_od_num()
            self.graph.vertex_num = (len(stores_info) - 1) * 2 + len(customers_info) + self.od_num * 2 + 2

            depot2 = deepcopy(self.graph.vertex_dict[0])
            depot2.id_ = self.graph.vertex_num - 1
            self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

            for index_ in range(self.sate_num):
                # add satellite as depot
                new_sate_depot = deepcopy(sate)

                # 更新 id 和 时间窗
                new_sate_depot.id_ = index_ + self.graph.vertex_num - (self.od_num * 2) - self.sate_num - 1
                # new_vertex_depot.due_time = 1440

                self.graph.add_vertex(vertex=new_sate_depot)

    def read_two_echelon_kr_instance(self,
                                     filepath):
        """  """
        f = open(filepath, 'r')
        lines = f.readlines()

        cnt = 0

        for line in lines:
            cnt += 1

            if cnt == 4:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.graph.vertex_num = int(str_arr[1])

            elif cnt == 5:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.sate_num = int(str_arr[1])

            elif cnt == 6:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.customer_num = int(str_arr[1])

            elif cnt == 9:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.model_para.vehicle_1_capacity = float(str_arr[1])

            elif cnt == 10:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.model_para.vehicle_2_capacity = float(str_arr[1])

            elif cnt == 11:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.vehicle_num_1st = int(str_arr[1])

            elif cnt == 12:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                self.vehicle_num_2nd = int(str_arr[1])

            elif 14 <= cnt <= 14 + self.customer_num:
                # depot and customer
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)

                if int(str_arr[0]) == 0:
                    depot = Vertex(id_=0,
                                   x_coord=float(str_arr[1]),
                                   y_coord=float(str_arr[2]),
                                   ready_time=0,
                                   due_time=1440)
                    self.graph.add_vertex(vertex=depot)

                else:
                    cus_id = self.sate_num + int(str_arr[0])

                    cus = Vertex(id_=cus_id,
                                 x_coord=float(str_arr[1]),
                                 y_coord=float(str_arr[2]),
                                 ready_time=420,
                                 due_time=1080)
                    cus.service_time = self.model_para.service_time
                    self.graph.add_vertex(vertex=cus)

            elif 15 + self.customer_num < cnt <= 15 + self.customer_num + self.sate_num:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)

                sate = Vertex(id_=int(str_arr[0]),
                              x_coord=float(str_arr[1]),
                              y_coord=float(str_arr[2]),
                              ready_time=0,
                              due_time=1440)
                sate.service_time = self.model_para.t_unload
                self.graph.add_vertex(vertex=sate)

                # add satellite as depot
                new_sate_depot = deepcopy(sate)

                # 更新 id 和 时间窗
                new_sate_depot.id_ = int(str_arr[0]) + self.graph.vertex_num - 1

                self.graph.add_vertex(vertex=new_sate_depot)

            elif 16 + self.customer_num + self.sate_num < cnt < 18 + self.customer_num * 2 + self.sate_num:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)

                if int(str_arr[0]) != 0:
                    cus_id = self.sate_num + int(str_arr[0])
                    self.graph.vertex_dict[cus_id].demand = float(str_arr[1])

        # self.graph.vertex_num = sate_num * 2 + cus_num + self.od_num * 2 + 2
        self.calc_od_num()
        self.graph.vertex_num = self.sate_num * 2 + self.customer_num + self.od_num * 2 + 2

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

    def read_two_echelon_gptv_instance(self,
                                       filepath):
        """  """
        with open(filepath, 'r') as file:
            data = dict()

            lines = file.readlines()

            current_section = None

            for line in lines:
                line = line.strip()
                # 判断信息类型
                if line.startswith('!'):
                    if 'Trucks' in line:
                        current_section = 'trucks'
                    elif 'CityFreighters' in line:
                        current_section = 'city_freighters'
                    elif 'Stores' in line:
                        current_section = 'stores'
                    elif 'Customers' in line:
                        current_section = 'customers'

                # 记录数据
                else:
                    if current_section == 'trucks':
                        parts = line.split(',')
                        self.vehicle_num_1st = int(parts[0])
                        self.model_para.vehicle_1_capacity = int(parts[1])
                        self.model_para.cost_per_distance_1st = int(parts[2])

                    elif current_section == 'city_freighters':
                        parts = line.split(',')
                        self.model_para.vehicle_max_ser_sate_num = int(parts[0])
                        self.vehicle_num_2nd = int(parts[1])
                        self.model_para.vehicle_2_capacity = int(parts[2])
                        self.model_para.cost_per_distance_2nd = int(parts[3])

                    elif current_section == 'stores':
                        data['stores'] = [
                            tuple(map(int, store.split(',')))
                            for store in line.split()
                        ]

                    elif current_section == 'customers':
                        if line == '':
                            pass
                        else:
                            data['customers'] = [
                                list(map(int, customer.split(',')))
                                for customer in line.split()
                            ]
            #
            # print()

        # 添加vertex

        # Depot and Satellites
        self.sate_num = len(data['stores']) - 1
        for i in range(len(data['stores'])):
            vertex = Vertex(id_=i,
                            x_coord=float(data['stores'][i][0]),
                            y_coord=float(data['stores'][i][1]),
                            # x_coord=float(data['stores'][i][0]) / 100,
                            # y_coord=float(data['stores'][i][1]) / 100,
                            ready_time=0,
                            due_time=self.initial_value)
            vertex.service_time = 0 if i == 0 else self.model_para.t_unload
            vertex.demand = 0
            self.graph.add_vertex(vertex=vertex)

            if i > 0:
                # add satellite as depot
                new_sate_depot = deepcopy(vertex)

                # 更新 id 和 时间窗
                new_sate_depot.id_ = i + len(data['stores']) + len(data['customers']) - 1

                self.graph.add_vertex(vertex=new_sate_depot)

        # customers
        self.customer_num = len(data['customers'])
        for i in range(len(data['customers'])):
            cus = Vertex(id_=int(len(data['stores']) + i),
                         x_coord=float(data['customers'][i][0]),
                         y_coord=float(data['customers'][i][1]),
                         # x_coord=float(data['customers'][i][0]) / 100,
                         # y_coord=float(data['customers'][i][1]) / 100,
                         ready_time=420,
                         due_time=self.initial_value)
            cus.service_time = self.model_para.service_time
            cus.demand = int(data['customers'][i][2])

            self.graph.add_vertex(vertex=cus)

        self.calc_od_num()
        self.graph.vertex_num = self.sate_num * 2 + self.customer_num + self.od_num * 2 + 2

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

    def read_two_echelon_gptv_instance_benchmark_file(self,
                                                      filepath):
        """  """
        f = open(filepath, 'r')
        lines = f.readlines()

        cnt = 0

        for line in lines:
            cnt += 1
            line = line.strip()

            if cnt >= 4:

                str_info = line.split(';')
                if str_info[-1] == 'depot':
                    # depot_dict[0] = [[str_info[1], str_info[2]], str_info[3]]
                    depot = Vertex(id_=0,
                                   x_coord=float(str_info[1]),
                                   y_coord=float(str_info[2]),
                                   ready_time=0,
                                   due_time=1440)
                    depot.demand = str_info[3]
                    depot.service_time = 0

                    self.graph.add_vertex(vertex=depot)

                elif str_info[-1] == 'satellite':
                    sate_id = cnt - 4
                    self.sate_num += 1
                    sate = Vertex(id_=sate_id,
                                  x_coord=float(str_info[1]),
                                  y_coord=float(str_info[2]),
                                  ready_time=0,
                                  due_time=1440)
                    sate.demand = int(str_info[3])
                    sate.service_time = 0

                    self.graph.add_vertex(vertex=sate)

                elif str_info[-1] == 'customer':
                    cus_id = cnt - 4
                    self.customer_num += 1
                    cus = Vertex(id_=cus_id,
                                 x_coord=float(str_info[1]),
                                 y_coord=float(str_info[2]),
                                 ready_time=420,
                                 due_time=1080)
                    cus.demand = int(str_info[3])
                    cus.service_time = self.model_para.service_time

                    self.graph.add_vertex(vertex=cus)

        if self.is_select is True:
            self.model_para.m_s = round((self.sate_capacity / self.sate_num) * 1.5)

        self.calc_od_num()
        self.graph.vertex_num = self.sate_num * 2 + self.customer_num + self.od_num * 2 + 2

        for sate_id in range(1, self.sate_num + 1):
            # add satellite as depot
            new_sate_depot = deepcopy(self.graph.vertex_dict[sate_id])

            # 更新 id 和 时间窗
            new_sate_depot.id_ = sate_id + self.sate_num + self.customer_num

            self.graph.add_vertex(vertex=new_sate_depot)

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

    def plot_vertices(self):
        """
        绘制原始的坐标图
        :return:
        """
        plt.figure(figsize=(10, 8))

        # 绘制 depot
        plt.scatter(x=self.graph.vertex_dict[0].x_coord,
                    y=self.graph.vertex_dict[0].y_coord,
                    color='red', label='Depot', marker='s', s=100)
        plt.text(self.graph.vertex_dict[0].x_coord,
                 self.graph.vertex_dict[0].y_coord,
                 'depot', fontsize=9, ha='right')

        # 绘制 satellites
        for satellite in self.graph.sate_list:
            cur_sate = self.graph.vertex_dict[satellite]
            plt.scatter(x=cur_sate.x_coord,
                        y=cur_sate.y_coord,
                        color='blue', label='Satellite', marker='^', s=100)
            plt.text(cur_sate.x_coord,
                     cur_sate.y_coord,
                     f'sate-{satellite}', fontsize=9, ha='right')

        # 绘制 customers
        for customer in self.graph.customer_list:
            cur_cus = self.graph.vertex_dict[customer]
            plt.scatter(x=cur_cus.x_coord,
                        y=cur_cus.y_coord,
                        color='green', label='Customer', marker='o', s=100)
            plt.text(cur_cus.x_coord,
                     cur_cus.y_coord,
                     f'{customer}', fontsize=9, ha='right')

        # 绘制 ODs
        for od in self.graph.od_o_list:
            cur_o = self.graph.vertex_dict[od]
            cur_d = self.graph.vertex_dict[self.graph.o_to_d[od]]

            plt.scatter(x=cur_o.x_coord,
                        y=cur_o.y_coord,
                        color='yellow', label='Customer', marker='o', s=100)
            plt.text(cur_o.x_coord,
                     cur_o.y_coord,
                     f'{od}', fontsize=9, ha='right')

            plt.scatter(x=cur_d.x_coord,
                        y=cur_d.y_coord,
                        color='yellow', label='Customer', marker='o', s=100)
            plt.text(cur_d.x_coord,
                     cur_d.y_coord,
                     f'{cur_d.id_}', fontsize=9, ha='right')

        # 防止重复标签
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Depot, Satellites, and Customers')
        plt.grid(True)
        plt.show()

    def plot_routes(self,
                    routes_1st,
                    routes_2nd,
                    routes_od):
        # 绘制坐标点
        # 绘制 depot
        plt.scatter(x=self.graph.vertex_dict[0].x_coord,
                    y=self.graph.vertex_dict[0].y_coord,
                    color='red', label='Depot', marker='s', s=100)
        plt.text(self.graph.vertex_dict[0].x_coord,
                 self.graph.vertex_dict[0].y_coord,
                 'depot', fontsize=9, ha='right')

        # 绘制 satellites
        for satellite in self.graph.sate_list:
            cur_sate = self.graph.vertex_dict[satellite]
            plt.scatter(x=cur_sate.x_coord,
                        y=cur_sate.y_coord,
                        color='blue', label='Satellite', marker='^', s=100)
            plt.text(cur_sate.x_coord,
                     cur_sate.y_coord,
                     f'sate-{satellite}', fontsize=9, ha='right')

        # 绘制 customers
        for customer in self.graph.customer_list:
            cur_cus = self.graph.vertex_dict[customer]
            plt.scatter(x=cur_cus.x_coord,
                        y=cur_cus.y_coord,
                        color='green', label='Customer', marker='o', s=100)
            plt.text(cur_cus.x_coord,
                     cur_cus.y_coord,
                     f'{customer}', fontsize=9, ha='right')

        # 绘制 ODs
        for od in self.graph.od_o_list:
            cur_o = self.graph.vertex_dict[od]
            cur_d = self.graph.vertex_dict[self.graph.o_to_d[od]]

            plt.scatter(x=cur_o.x_coord,
                        y=cur_o.y_coord,
                        color='yellow', label='Customer', marker='o', s=100)
            plt.text(cur_o.x_coord,
                     cur_o.y_coord,
                     f'{od}', fontsize=9, ha='right')

            plt.scatter(x=cur_d.x_coord,
                        y=cur_d.y_coord,
                        color='yellow', label='Customer', marker='o', s=100)
            plt.text(cur_d.x_coord,
                     cur_d.y_coord,
                     f'{cur_d.id_}', fontsize=9, ha='right')

        # 绘制一级路径
        for route in routes_1st:
            route1_coords = [(self.graph.vertex_dict[v].x_coord, self.graph.vertex_dict[v].y_coord) for v in route]
            x1, y1 = zip(*route1_coords)
            plt.plot(x1, y1, color='orange', linewidth=2, label='Level 1 Path')

        # 绘制二级路径
        for route in routes_2nd:
            route2_coords = [(self.graph.vertex_dict[v].x_coord, self.graph.vertex_dict[v].y_coord) for v in route]
            x2, y2 = zip(*route2_coords)
            plt.plot(x2, y2, color='purple', linewidth=2, label='Level 2 Path')

        # 绘制OD路径
        for route in routes_od:
            route2_coords = [(self.graph.vertex_dict[v].x_coord, self.graph.vertex_dict[v].y_coord) for v in route]
            x2, y2 = zip(*route2_coords)
            plt.plot(x2, y2, color='cyan', linewidth=2, label='OD Path')

        # 防止重复标签
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Depot, Satellites, Customers, and Routes')
        plt.grid(True)
        plt.show()

    @staticmethod
    def read_benchmark_result(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        # 初始化变量
        sate_info = {}
        # layer1_info = []
        # layer2_routes = []
        in_layer1 = False
        in_layer2 = False
        sate_ser_weight = 0
        sate_routes = []
        routes = []

        # 解析文件内容
        for line in lines:
            line = line.strip()

            # 识别 Layer 1 的开始和结束
            if "Layer1" in line:
                in_layer1 = True
                in_layer2 = False
                continue
            elif "Layer2" in line:
                in_layer1 = False
                in_layer2 = True
                continue

            # 提取 Layer 1 的信息
            if in_layer1 and "Weight" in line:
                parts = line.split('Weight(')[1].split(')')
                weight = float(parts[0])

                # 判断是否有空置的sate
                cur_str = line.split('Cust(1) ')

                if len(cur_str) == 1:
                    start_node = 9999
                else:
                    start_node = int(line.split('Cust(1) ')[1])
                # layer1_info.append((weight, start_node))

                # 需要判断是否有多次车辆从depot 驶入 同一个 sate
                if start_node in sate_info.keys():
                    sate_info[start_node][0] += weight
                elif start_node not in sate_info.keys():
                    sate_info[start_node] = [weight, []]

            # 提取 Layer 2 的路径信息
            if in_layer2 and 'Vehicles' in line:
                sate_ser_weight = 0
                sate_routes.append([])
            if in_layer2 and "Cust" in line:
                parts = line.split('Weight(')[1].split(')')
                weight = float(parts[0])
                sate_ser_weight += weight
                customers = list(map(int, line.split('Cust(')[1].split(')')[1].strip().split()))
                # layer2_routes.append((weight, customers))
                sate_routes[-1].append((weight, customers))

        # 将 Layer 1 的载重信息和 Layer 2 的路径进行匹配，生成完整的路径
        full_routes = []

        # 判断 layer2 的路径的起始点
        for sate_route in sate_routes:
            cur_weight = 0
            cur_sate = None

            for route_info in sate_route:
                cur_weight += route_info[0]

            for key, value in sate_info.items():
                if cur_weight == value[0]:
                    cur_sate = key

            for route_info in sate_route:
                sate_info[cur_sate][1].append(route_info[1])
                full_routes.append([cur_sate] + route_info[1] + [cur_sate])

        return sate_info, full_routes

    @staticmethod
    def turn_instance(sate_num,
                      routes):
        for route in routes:
            for id_ in range(1, len(route) - 1):
                route[id_] += sate_num

    def get_benchmark_result1_pre(self,
                                  result_path):
        arrive_time_dict = dict()

        sate_info, full_routes = self.read_benchmark_result(filename=result_path)
        self.turn_instance(sate_num=self.sate_num,
                           routes=full_routes)

        sate_combinations = list(itertools.combinations(self.graph.sate_list, 2))
        # self.sata_distance_sum = sum(self.graph.arc_dict[combination].distance for combination in sate_combinations)
        for combination in sate_combinations:
            cur_distance = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            self.sata_distance_sum += cur_distance

        sate_depot_combinations = list(itertools.product([0], self.graph.sate_list))
        # self.max_start_distance = max(
        #     self.graph.arc_dict[combination].distance for combination in sate_depot_combinations)
        for combination in sate_depot_combinations:
            cur_distance_depot = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            if cur_distance_depot > self.max_start_distance:
                self.max_start_distance = cur_distance_depot

        for route in full_routes:
            cur_sate = route[0]

            id_ = 1
            # cur_arrive_time = self.graph.arc_dict[0, cur_sate].distance + self.model_para.t_unload
            cur_arrive_time = (self.sata_distance_sum + self.max_start_distance * 2 +
                               self.model_para.t_unload * self.sate_num)

            while id_ < (len(route) - 1):
                cur_distance = round(calc_travel_time(
                    x_1=self.graph.vertex_dict[route[id_ - 1]].x_coord,
                    x_2=self.graph.vertex_dict[route[id_]].x_coord,
                    y_1=self.graph.vertex_dict[route[id_ - 1]].y_coord,
                    y_2=self.graph.vertex_dict[route[id_]].y_coord
                ), 2)

                # cur_arrive_time += self.graph.arc_dict[route[id_ - 1], route[id_]].distance
                cur_arrive_time += cur_distance
                arrive_time_dict[route[id_]] = cur_arrive_time

                cur_arrive_time += self.model_para.service_time
                id_ += 1

        return arrive_time_dict

    def get_benchmark_result1(self,
                              result_path):
        self.result_info_1st = []
        self.result_info_2nd = []

        self.routes_1st_result = dict()
        self.routes_2nd_result = dict()

        self.sate_arrive_time_result = {sate: 0 for sate in self.graph.sate_list}

        arrive_time_dict = dict()
        sate_demand = dict()

        with open(result_path, 'r') as file:
            lines = file.readlines()
            cnt = 0
            # 分割为行

            # 读取 Layer1 数据
            layer1_section = False
            layer2_section = False

            for line in lines:
                # 检测段落
                if "Layer1" in line:
                    layer1_section = True
                    continue
                elif "Layer2" in line:
                    layer1_section = False
                    layer2_section = True
                    continue

                if layer1_section and line.strip():
                    # 提取 Layer1 的信息
                    match = re.search(r'Cost\(([\d.]+)\),Weight\(([\d.]+)\),Cust\((\d+)\)', line)
                    if match:
                        cost = float(match.group(1))
                        weight = float(match.group(2))
                        cust_count = int(match.group(3))
                        # 提取路径
                        path_data = line.split('Cust(')[-1].split(')')[-1].strip().split()
                        # 检查路径长度是否与客户数量一致
                        if len(path_data) == cust_count:
                            self.result_info_1st.append({
                                'cost': cost,
                                'weight': weight,
                                'cust_count': cust_count,
                                'path': path_data
                            })

                elif layer2_section and line.strip():
                    # 提取 Layer2 的信息

                    if 'Vehicles' in line:
                        sate_demand[len(self.result_info_2nd) + 1] = 0
                        start_sate = len(self.result_info_2nd) + 1
                        self.routes_2nd_result[len(self.result_info_2nd) + 1] = []
                        self.result_info_2nd.append(list())

                    match = re.search(r'Cost\(([\d.]+)\),Weight\(([\d.]+)\),Cust\((\d+)\)', line)
                    if match:
                        cust_count = int(match.group(3))
                        path_data = line.split('Cust(')[-1].split(')')[1].strip().split()
                        self.result_info_2nd[-1].append({
                            'start_sate': int(start_sate),
                            'cost': float(match.group(1)),
                            'weight': float(match.group(2)),
                            'cust_count': cust_count,
                            'path': path_data
                        })
                        # self.result_info_2nd[-1][-1]['path'].insert(0, start_sate)
                        # self.result_info_2nd[-1][-1]['path'].append(start_sate)

            # print()

        for id_ in range(len(self.result_info_1st)):
            cur_info = self.result_info_1st[id_]

            for id2_ in range(len(cur_info['path'])):
                cur_ver = cur_info['path'][id2_]
                cur_info['path'][id2_] = int(cur_ver)

            self.routes_1st_result[id_] = cur_info['path']
            self.routes_1st_result[id_].insert(0, 0)
            self.routes_1st_result[id_].append(0)

        for id_ in range(len(self.result_info_2nd)):
            sate_info = self.result_info_2nd[id_]

            for cur_info in sate_info:
                for id2_ in range(len(cur_info['path'])):
                    cur_ver = cur_info['path'][id2_]

                    cur_info['path'][id2_] = int(cur_ver) + self.sate_num

                    sate_demand[id_ + 1] += cur_info['weight']

                cur_info['path'].insert(0, cur_info['start_sate'])
                cur_info['path'].append(cur_info['start_sate'])

                self.routes_2nd_result[id_ + 1].append(cur_info['path'])

        for route in list(self.routes_1st_result.values()):
            cur_arrive_time = 0
            for id_ in range(1, len(route)):
                #
                cur_distance = round(calc_travel_time(
                    x_1=self.graph.vertex_dict[route[id_ - 1]].x_coord,
                    x_2=self.graph.vertex_dict[route[id_]].x_coord,
                    y_1=self.graph.vertex_dict[route[id_ - 1]].y_coord,
                    y_2=self.graph.vertex_dict[route[id_]].y_coord
                ), 2)
                # sate_arrive_time[route[id_]] = cur_arrive_time + cur_distance
                cur_arrive_time += cur_distance
                if route[id_] in self.graph.sate_list:
                    self.sate_arrive_time_result[route[id_]] = cur_arrive_time

        # 计算 sate 距离信息
        sate_combinations = list(itertools.combinations(self.graph.sate_list, 2))
        # self.sata_distance_sum = sum(self.graph.arc_dict[combination].distance for combination in sate_combinations)
        for combination in sate_combinations:
            cur_distance = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            self.sata_distance_sum += cur_distance

        sate_depot_combinations = list(itertools.product([0], self.graph.sate_list))
        # self.max_start_distance = max(
        #     self.graph.arc_dict[combination].distance for combination in sate_depot_combinations)
        for combination in sate_depot_combinations:
            cur_distance_depot = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            if cur_distance_depot > self.max_start_distance:
                self.max_start_distance = cur_distance_depot

        for start_sate, routes in self.routes_2nd_result.items():
            for route in routes:
                cur_arrive_time = (self.sata_distance_sum + self.max_start_distance * 2 +
                                   self.model_para.t_unload * self.sate_num)

                # cur_arrive_time = self.sate_arrive_time_result[route[0]]
                # cur_arrive_time = 0

                id_ = 1

                while id_ < len(route) - 1:
                    # if id_ - 1 == 0:
                    #     pre_ver_id = route[id_ - 1]
                    #     cur_ver_id = route[id_ - 1] + self.sate_num
                    # else:
                    #     pre_ver_id = route[id_ - 1] + self.sate_num
                    #     cur_ver_id = route[id_ - 1] + self.sate_num

                    cur_distance = round(calc_travel_time(
                        x_1=self.graph.vertex_dict[route[id_ - 1]].x_coord,
                        x_2=self.graph.vertex_dict[route[id_]].x_coord,
                        y_1=self.graph.vertex_dict[route[id_ - 1]].y_coord,
                        y_2=self.graph.vertex_dict[route[id_]].y_coord
                    ), 2)

                    cur_arrive_time += cur_distance
                    arrive_time_dict[route[id_]] = cur_arrive_time

                    cur_arrive_time += self.model_para.service_time
                    id_ += 1

                # print()

        return arrive_time_dict

    def get_benchmark_result2(self,
                              result_path):
        """  """
        arrive_time_dict = dict()

        """ 读取result """
        self.routes_1st_result = dict()
        self.routes_2nd_result = dict()

        self.sate_arrive_time_result = {sate: 0 for sate in self.graph.sate_list}

        # 计算 sate 距离信息
        sate_combinations = list(itertools.combinations(self.graph.sate_list, 2))
        for combination in sate_combinations:
            cur_distance = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            self.sata_distance_sum += cur_distance

        sate_depot_combinations = list(itertools.product([0], self.graph.sate_list))
        for combination in sate_depot_combinations:
            cur_distance_depot = round(calc_travel_time(
                x_1=self.graph.vertex_dict[combination[0]].x_coord,
                x_2=self.graph.vertex_dict[combination[1]].x_coord,
                y_1=self.graph.vertex_dict[combination[0]].y_coord,
                y_2=self.graph.vertex_dict[combination[1]].y_coord
            ), 2)
            if cur_distance_depot > self.max_start_distance:
                self.max_start_distance = cur_distance_depot

        with open(result_path, 'r') as file:
            lines = file.readlines()
            cnt = 0
            vehicle_1st = 0
            vehicle_2nd = 0

            for line in lines:
                cnt += 1

                if cnt >= 7:
                    line = line.strip()

                    str_info = line.split(';')

                    if str_info[-1] == 'Truck':
                        self.routes_1st_result[vehicle_1st] = ast.literal_eval(str_info[1])
                        vehicle_1st += 1

                    elif str_info[-1] == 'CityFreighter':
                        self.routes_2nd_result[vehicle_2nd] = ast.literal_eval(str_info[1])
                        vehicle_2nd += 1

        # 确定 1st route
        for route in list(self.routes_1st_result.values()):
            cur_arrive_time = 0
            for id_ in range(1, len(route)):
                #
                cur_distance = round(calc_travel_time(
                    x_1=self.graph.vertex_dict[route[id_ - 1]].x_coord,
                    x_2=self.graph.vertex_dict[route[id_]].x_coord,
                    y_1=self.graph.vertex_dict[route[id_ - 1]].y_coord,
                    y_2=self.graph.vertex_dict[route[id_]].y_coord
                ), 2)
                # sate_arrive_time[route[id_]] = cur_arrive_time + cur_distance
                cur_arrive_time += cur_distance
                if route[id_] in self.graph.sate_list:
                    self.sate_arrive_time_result[route[id_]] = cur_arrive_time

        for route in list(self.routes_2nd_result.values()):
            cur_arrive_time = (self.sata_distance_sum + self.max_start_distance * 2 +
                               self.model_para.t_unload * self.sate_num)

            # cur_arrive_time = self.sate_arrive_time_result[route[0]]
            # cur_arrive_time = 0

            id_ = 1

            while id_ < (len(route) - 1):
                cur_distance = round(calc_travel_time(
                    x_1=self.graph.vertex_dict[route[id_ - 1]].x_coord,
                    x_2=self.graph.vertex_dict[route[id_]].x_coord,
                    y_1=self.graph.vertex_dict[route[id_ - 1]].y_coord,
                    y_2=self.graph.vertex_dict[route[id_]].y_coord
                ), 2)

                cur_arrive_time += cur_distance
                arrive_time_dict[route[id_]] = cur_arrive_time

                cur_arrive_time += self.model_para.service_time
                id_ += 1

        return arrive_time_dict

    def set_time_window(self,
                        arrive_time_dict,
                        random_seed,
                        customer_extend_time=0):
        np.random.seed(random_seed)
        cur_arrive_time = (self.sata_distance_sum + self.max_start_distance * 2 +
                           self.model_para.t_unload * self.sate_num)

        """ set2-3 """
        for cus, arrive_time in arrive_time_dict.items():
            # r = np.random.uniform(0, (arrive_time - cur_arrive_time) - 10)
            r = np.random.uniform(1, min(35, round(arrive_time - cur_arrive_time)))

            # print(r)
            # ready ti            # self.graph.vertex_dict[cus].ready_time = (arrive_time - r)
            self.graph.vertex_dict[cus].ready_time = math.floor(arrive_time - r)
            # due time
            # self.graph.vertex_dict[cus].due_time = (arrive_time + r)
            self.graph.vertex_dict[cus].due_time = math.ceil(arrive_time + r) + customer_extend_time

        """ set4 """
        # per_d = self.calc_per_cus_dis()
        # for cus, arrive_time in arrive_time_dict.items():
        #     # r = np.random.uniform(0, per_d)
        #     r = np.random.uniform(0, arrive_time)
        #
        #     # print(r)
        #     # ready time
        #     # self.graph.vertex_dict[cus].ready_time = (arrive_time - r)
        #     self.graph.vertex_dict[cus].ready_time = math.floor(arrive_time - r)
        #     # due time
        #     # self.graph.vertex_dict[cus].due_time = (arrive_time + r)
        #     self.graph.vertex_dict[cus].due_time = math.ceil(arrive_time + r) + customer_extend_time

        for sate in self.graph.sate_list:
            # self.graph.vertex_dict[sate].ready_time += cur_arrive_time
            self.graph.vertex_dict[sate].due_time += cur_arrive_time + max(arrive_time_dict.values())
            # sate_depot_id = sate + self.sate_num + self.customer_num - 1
            sate_depot_id = self.graph.sate_to_depot[sate]
            self.graph.vertex_dict[sate_depot_id].due_time += cur_arrive_time + max(arrive_time_dict.values()) * 2

    def calc_capacity_assignment(self):
        # capacity_assignment = {sate: [] for sate in self.graph.sate_list}
        sate_od_demand = {sate: 0 for sate in self.graph.sate_list}

        for sate in self.graph.sate_list:

            for cus in self.customer_list_od:
                if cus in self.graph.sate_serv_cus[sate]:
                    # capacity_assignment[sate].append(cus)
                    sate_od_demand[sate] += self.graph.vertex_dict[cus].demand

        return sate_od_demand

    def calc_od_num(self):
        """ """
        self.od_num = math.ceil(
            math.log(self.customer_num) * 2 + ((self.customer_num - 20) / 5)
        )

    def calc_per_cus_dis(self):

        dis_dic = {}
        for cus1 in self.graph.customer_list:
            for cus2 in self.graph.customer_list:
                if cus2 != cus1:
                    if (cus1, cus2) not in dis_dic.keys() and (cus2, cus1) not in dis_dic.keys():
                        dis_dic[(cus1, cus2)] = calc_travel_time(self.graph.vertex_dict[cus1].x_coord,
                                                                 self.graph.vertex_dict[cus1].y_coord,
                                                                 self.graph.vertex_dict[cus2].x_coord,
                                                                 self.graph.vertex_dict[cus2].y_coord)

        return round(sum(dis_dic.values()) / len(dis_dic))

    def read_self_ins(self,
                      filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = dict()

            lines = file.readlines()

            current_section = None

            for line in lines:
                line = line.strip()
                # 判断信息类型
                if line.startswith('!'):
                    if 'Trucks' in line:
                        current_section = 'trucks'
                    elif 'CityFreighters' in line:
                        current_section = 'city_freighters'
                    elif 'Stores' in line:
                        current_section = 'stores'
                    elif 'Customers' in line:
                        current_section = 'customers'
                    elif 'Customer id' in line:
                        current_section = 'customer TW'
                    elif 'OD capacity' in line:
                        data['OD capacity'] = line.split()[-1]
                    elif 'Task id' in line:
                        current_section = 'Occasional Drivers'

                # 记录数据
                else:
                    if current_section == 'trucks':
                        parts = line.split(',')
                        self.vehicle_num_1st = int(parts[0])
                        self.model_para.vehicle_1_capacity = int(parts[1])
                        self.model_para.cost_per_distance_1st = int(parts[2])

                    elif current_section == 'city_freighters':
                        parts = line.split(',')
                        self.model_para.vehicle_max_ser_sate_num = int(parts[0])
                        self.vehicle_num_2nd = int(parts[1])
                        self.model_para.vehicle_2_capacity = int(parts[2])
                        self.model_para.cost_per_distance_2nd = int(parts[3])

                    elif current_section == 'stores':
                        data['stores'] = [
                            tuple(map(int, store.split(',')))
                            for store in line.split()
                        ]

                    elif current_section == 'customers':
                        if line == '':
                            pass
                        else:
                            data['customers'] = [
                                list(map(int, customer.split(',')))
                                for customer in line.split()
                            ]
                    elif current_section == 'customer TW':
                        if line == '':
                            pass
                        else:
                            data['customer TW'] = [
                                tuple(map(float, item.split(','))) for item in
                                re.findall(r"\((.*?)\)", line)
                            ]

                    elif current_section == 'Occasional Drivers':
                        data['Occasional Drivers'] = [tuple(map(float, item.split(','))) for item in
                                                      re.findall(r"\((.*?)\)", line)]

        # Depot and Satellites
        self.sate_num = len(data['stores']) - 1
        for i in range(len(data['stores'])):
            vertex = Vertex(id_=i,
                            x_coord=float(data['stores'][i][0]),
                            y_coord=float(data['stores'][i][1]),
                            # x_coord=float(data['stores'][i][0]) / 100,
                            # y_coord=float(data['stores'][i][1]) / 100,
                            ready_time=0,
                            due_time=self.initial_value)
            vertex.service_time = 0 if i == 0 else self.model_para.t_unload
            vertex.demand = 0
            self.graph.add_vertex(vertex=vertex)

            if i > 0:
                # add satellite as depot
                new_sate_depot = deepcopy(vertex)

                # 更新 id 和 时间窗
                new_sate_depot.id_ = i + len(data['stores']) + len(data['customers']) - 1

                self.graph.add_vertex(vertex=new_sate_depot)

        # customers
        self.customer_num = len(data['customers'])
        for i in range(len(data['customers'])):
            cus = Vertex(id_=int(len(data['stores']) + i),
                         x_coord=float(data['customers'][i][0]),
                         y_coord=float(data['customers'][i][1]),
                         # x_coord=float(data['customers'][i][0]) / 100,
                         # y_coord=float(data['customers'][i][1]) / 100,
                         ready_time=420,
                         due_time=self.initial_value)
            cus.service_time = self.model_para.service_time
            cus.demand = int(data['customers'][i][2])

            self.graph.add_vertex(vertex=cus)

        # customers time windows
        for i in range(len(data['customer TW'])):
            cus_id = int(data['customer TW'][i][0])
            self.graph.vertex_dict[cus_id].ready_time = data['customer TW'][i][1]
            self.graph.vertex_dict[cus_id].due_time = data['customer TW'][i][2]

        # ODs
        self.od_num = len(data['Occasional Drivers'])
        self.graph.ins.model_para.vehicle_od_capacity = float(data['OD capacity'])
        for i in range(len(data['Occasional Drivers'])):
            od_o = Vertex(id_=int(data['Occasional Drivers'][i][1]),
                          x_coord=float(data['Occasional Drivers'][i][2]),
                          y_coord=float(data['Occasional Drivers'][i][3]),
                          ready_time=float(data['Occasional Drivers'][i][4]),
                          due_time=float(data['Occasional Drivers'][i][5]))
            self.graph.add_vertex(vertex=od_o)

            od_d = Vertex(id_=int(data['Occasional Drivers'][i][6]),
                          x_coord=float(data['Occasional Drivers'][i][7]),
                          y_coord=float(data['Occasional Drivers'][i][8]),
                          ready_time=float(data['Occasional Drivers'][i][9]),
                          due_time=float(data['Occasional Drivers'][i][10]))
            self.graph.add_vertex(vertex=od_d)

            cur_distance = calc_travel_time(
                x_1=od_o.x_coord,
                x_2=od_d.x_coord,
                y_1=od_o.y_coord,
                y_2=od_d.y_coord
            )

            new_arc = Arc(
                head_vertex=od_o.id_, tail_vertex=od_d.id_,
                distance=cur_distance,
                adj=1
            )

            od_task = ODTask(_id=int(data['Occasional Drivers'][i][0]),
                             origin_node=od_o,
                             terminate_node=od_d,
                             arc=new_arc,
                             dis=cur_distance)

            self.graph.od_task_dict[i] = od_task

        self.graph.vertex_num = self.sate_num * 2 + self.customer_num + self.od_num * 2 + 2

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

        self.input_info()
        self.gen_od_task = GenOD(graph=self.graph)
        self.gen_od_task.get_customer_square()

    def read_real_case(self,
                       filepath):
        self.initial_value = 2400
        ini_sate_due_time = 1800
        self.model_para.service_time = 5
        self.model_para.t_unload = 10

        with open(filepath, 'r') as file:
            data = dict()

            lines = file.readlines()

            current_section = None

            for line in lines:
                line = line.strip()
                # 判断信息类型
                if line.startswith('!'):
                    if 'Depot' in line:
                        current_section = 'Depot'
                    elif 'Vehicle Capacity' in line:
                        current_section = 'Vehicle Capacity'
                    elif 'Satellites' in line:
                        current_section = 'Satellites'
                    elif 'Customers' in line:
                        current_section = 'Customers'
                    elif 'OD capacity' in line:
                        data['OD capacity'] = line.split()[-1]
                    elif 'Task id' in line:
                        current_section = 'Occasional Drivers'

                # 记录数据
                else:
                    if current_section == 'Depot':
                        parts = line.split(',')
                        data['depot'] = parts

                    elif current_section == 'Vehicle Capacity':
                        parts = line.split(',')
                        self.model_para.vehicle_1_capacity = int(float(parts[0]))
                        self.model_para.vehicle_2_capacity = int(float(parts[1]))

                    elif current_section == 'Satellites':
                        matches = re.findall(r'\((.*?)\)', line)
                        data['Satellites'] = [list(map(float, match.split(','))) for match in matches]
                        self.sate_num = len(data['Satellites'])
                        self.model_para.vehicle_max_ser_sate_num = int(len(data['Satellites']))
                        self.vehicle_num_1st = self.sate_num * 2

                    elif current_section == 'Customers':
                        # 使用正则表达式提取每个括号中的内容
                        matches = re.findall(r'\((.*?)\)', line)

                        # 将结果转换为列表，每个括号内的内容对应一个列表
                        data['customers'] = [list(map(float, match.split(','))) for match in matches]
                        self.customer_num = len(data['customers'])
                        self.vehicle_num_2nd = int(len(data['customers']) / 3)

                    elif current_section == 'Occasional Drivers':
                        data['Occasional Drivers'] = [tuple(map(float, item.split(','))) for item in
                                                      re.findall(r"\((.*?)\)", line)]

        # Depot
        depot = Vertex(id_=0,
                       x_coord=float(data['depot'][0]),
                       y_coord=float(data['depot'][1]),
                       ready_time=0,
                       due_time=self.initial_value)
        self.graph.add_vertex(vertex=depot)

        # Satellites
        for i in range(1, 1 + len(data['Satellites'])):
            sate = Vertex(id_=i,
                          x_coord=float(data['Satellites'][i - 1][0]),
                          y_coord=float(data['Satellites'][i - 1][1]),
                          ready_time=0,
                          due_time=ini_sate_due_time)

            sate.service_time = 0 if i == 0 else self.model_para.t_unload
            sate.demand = 0
            self.graph.add_vertex(vertex=sate)

            # add satellite as depot
            new_sate_depot = deepcopy(sate)

            # 更新 id 和 时间窗
            new_sate_depot.id_ = i + self.sate_num + self.customer_num

            self.graph.add_vertex(vertex=new_sate_depot)

        # Customers
        for i in range(len(data['customers'])):
            cus = Vertex(id_=self.sate_num + 1 + i,
                         x_coord=float(data['customers'][i][0]),
                         y_coord=float(data['customers'][i][1]),
                         # x_coord=float(data['customers'][i][0]) / 100,
                         # y_coord=float(data['customers'][i][1]) / 100,
                         ready_time=float(data['customers'][i][2]),
                         due_time=float(data['customers'][i][3]),
                         demand=float(data['customers'][i][4]))
            cus.service_time = self.model_para.service_time

            self.graph.add_vertex(vertex=cus)

        # ODs
        self.od_num = len(data['Occasional Drivers'])
        self.graph.ins.model_para.vehicle_od_capacity = float(data['OD capacity'])

        for i in range(len(data['Occasional Drivers'])):
            od_o = Vertex(id_=int(data['Occasional Drivers'][i][1]),
                          x_coord=float(data['Occasional Drivers'][i][2]),
                          y_coord=float(data['Occasional Drivers'][i][3]),
                          ready_time=float(data['Occasional Drivers'][i][4]),
                          due_time=float(data['Occasional Drivers'][i][5]))
            self.graph.add_vertex(vertex=od_o)

            od_d = Vertex(id_=int(data['Occasional Drivers'][i][6]),
                          x_coord=float(data['Occasional Drivers'][i][7]),
                          y_coord=float(data['Occasional Drivers'][i][8]),
                          ready_time=float(data['Occasional Drivers'][i][9]),
                          due_time=float(data['Occasional Drivers'][i][10]))
            self.graph.add_vertex(vertex=od_d)

            cur_distance = geodesic((od_o.x_coord, od_o.y_coord),
                                    (od_d.x_coord, od_d.y_coord)).meters / 100

            new_arc = Arc(
                head_vertex=od_o.id_, tail_vertex=od_d.id_,
                distance=cur_distance,
                adj=1
            )

            od_task = ODTask(_id=int(data['Occasional Drivers'][i][0]),
                             origin_node=od_o,
                             terminate_node=od_d,
                             arc=new_arc,
                             dis=cur_distance)

            self.graph.od_task_dict[i] = od_task

        self.graph.vertex_num = self.sate_num * 2 + self.customer_num + self.od_num * 2 + 2

        depot2 = deepcopy(self.graph.vertex_dict[0])
        depot2.id_ = self.graph.vertex_num - 1
        self.graph.vertex_dict[self.graph.vertex_num - 1] = depot2

        self.input_info()
        self.gen_od_task = GenOD(graph=self.graph)
        self.gen_od_task.get_customer_square_real_case()