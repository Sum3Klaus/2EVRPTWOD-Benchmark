# -*- coding: utf-8 -*-
# @Time     : 2024-07-29-22:49
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from bidict import bidict
from copy import deepcopy
from Common import *
from SubGraph import *
from Arc import *
from geopy.distance import geodesic


class Graph(object):

    def __init__(self,
                 ins):

        self.ins = ins

        # 1st
        self.first_echelon_graph = None
        self.first_echelon_list = []

        # 2nd
        self.second_echelon_graph = None
        self.second_echelon_list = []

        # od
        self.od_graph = None
        self.od_task_dict = {}
        self.od_customer_adj = {}  # {(od_task_id, customer): 0-cannot, RepairOperators-can

        # pdp
        self.pdp_graph = None
        self.pickup_id_list = None
        self.pick_dict = {}
        self.pd_list = []
        self.pdp_dict = None
        self.pd_list_corr = []
        self.pdp_dict_corr = None

        self.sate_list = None
        self.sate_depot_list = None
        self.sate_to_depot = None

        self.customer_num = ins.customer_num
        self.customer_list = None
        self.vertex_num = 0
        self.depot_list = None

        self.od_o_list = None
        self.od_d_list = None
        self.o_to_d = None

        self.vertex_dict = dict()
        self.arc_dict = {}

        self.sate_serv_cus = None  # sate: [customer_id]
        self.cus_belong_sate = {}

        self.vehicle_speed = 100

    def input_graph_info(self):
        self.sate_list = [i for i in range(1, self.ins.sate_num + 1)]
        self.sate_depot_list = [i for i in
                                range(self.ins.sate_num + self.ins.customer_num + 1,
                                      2 * self.ins.sate_num + self.ins.customer_num + 1)]
        self.sate_to_depot = {self.sate_list[i]: self.sate_depot_list[i] for i in range(len(self.sate_list))}

        self.customer_num = self.ins.customer_num
        self.ins.customer_list_alns = self.customer_list = [i for i in range(self.ins.sate_num + 1,
                                                                             self.ins.sate_num + self.ins.customer_num + 1)]
        self.vertex_num = self.ins.customer_num + self.ins.sate_num * 2 + self.ins.od_num * 2 + 2
        self.depot_list = [0, self.vertex_num - 1]

        self.od_o_list = [i for i in range(1 + self.ins.sate_num * 2 + self.customer_num,
                                           1 + self.ins.sate_num * 2 + self.customer_num + self.ins.od_num)]
        self.od_d_list = [i for i in range(1 + self.ins.sate_num * 2 + self.customer_num + self.ins.od_num,
                                           1 + self.ins.sate_num * 2 + self.customer_num + self.ins.od_num * 2)]
        self.o_to_d = {self.od_o_list[i]: self.od_d_list[i] for i in range(self.ins.od_num)}

        self.calc_echelons_list()

        self.sate_serv_cus = {self.sate_list[i]: [] for i in range(self.ins.sate_num)}  # sate: [customer_id]

    def gen_sub_graphs(self):
        """ """
        # 2nd
        if self.ins.is_select is True:
            self.gen_second_graph_sate_select()
            # 1st
            self.gen_first_graph()

            self.gen_od_graph_sate_select()

        else:
            # self.calc_cus_belong_sate()
            self.gen_second_graph_no_depot_selection()
            # 1st
            self.gen_first_graph()

            self.gen_od_graph_no_select()

            # 添加初始的 alns_dict
            for sate in self.sate_list:
                self.ins.alns_dict[sate] = self.sate_serv_cus[sate]

        # od
        # self.gen_od_graph()

        if self.ins.is_select is True:
            self.gen_pdp_graph_sate_select()

        else:
            self.gen_pdp_graph()

        self.arc_dict = {**self.first_echelon_graph.arc_dict, **self.second_echelon_graph.arc_dict,
                         **self.od_graph.arc_dict}

    def add_vertex(self, vertex):
        """
        add a single vertex into the graph
        :param vertex:
        :return:
        """
        self.vertex_dict[vertex.id_] = vertex

    def calc_echelons_list(self):

        self.first_echelon_list = self.depot_list + self.sate_list
        self.second_echelon_list = self.sate_list + self.customer_list + self.sate_depot_list

    def calc_cus_belong_sate(self):
        """
        如果 is_select = True， 也需要计算归属，方便计算 od 的 取货地点

        :return:
        """
        for cus_id in self.customer_list:

            cus_to_sate_dis = float('inf')
            belong_sate = None

            for sate_id in self.sate_list:

                cur_dis = calc_travel_time(x_1=self.vertex_dict[cus_id].x_coord,
                                           y_1=self.vertex_dict[cus_id].y_coord,
                                           x_2=self.vertex_dict[sate_id].x_coord,
                                           y_2=self.vertex_dict[sate_id].y_coord, )

                if cur_dis < cus_to_sate_dis:
                    belong_sate = sate_id
                    cus_to_sate_dis = cur_dis

            self.cus_belong_sate[cus_id] = belong_sate
            self.sate_serv_cus[belong_sate].append(cus_id)
            self.vertex_dict[belong_sate].demand += self.vertex_dict[cus_id].demand

    def gen_first_graph(self):

        self.first_echelon_graph = Subgraph(
            ins=self.ins,
            level=1,
            vertex_id_list=self.first_echelon_list
        )

        for head_vertex_id in self.first_echelon_list:
            for tail_vertex_id in self.first_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if tail_vertex_id == 0 or head_vertex_id == self.depot_list[1]:
                        # del 从虚拟depot出发 和 向 depot 0 行驶的弧
                        cur_adj = 0

                    if head_vertex_id == 0 and tail_vertex_id == self.depot_list[1]:
                        # depot to depot
                        cur_adj = 0

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + self.ins.model_para.t_unload - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    # if (head_vertex_id == 1 and tail_vertex_id == 40) or (head_vertex_id == 2 and tail_vertex_id == 40):
                    #     print()
                    self.first_echelon_graph.add_arc(arc=new_arc)

        self.first_echelon_graph.preprocess(subgraph=self.first_echelon_graph)

    def gen_second_graph_sate_select(self):
        """ 2nd-echelon , sate 可以每个 符合约束的客户服务"""
        self.second_echelon_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list
        )

        for head_vertex_id in self.second_echelon_list:
            for tail_vertex_id in self.second_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    service_time = self.ins.model_para.service_time if head_vertex_id in self.customer_list else 0

                    # if head_vertex_id == 1 and tail_vertex_id == 25:
                    #     print()

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # 从 return 的 depot 出发
                    if head_vertex_id in self.sate_depot_list:
                        cur_adj = 0

                    # 驶向 sate
                    if tail_vertex_id in self.sate_list:
                        cur_adj = 0

                    # sate to sate_depot
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list):
                        cur_adj = 0

                    # sate to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.second_echelon_graph.add_arc(arc=new_arc)

        self.second_echelon_graph.preprocess(subgraph=self.second_echelon_graph)

    def gen_second_graph_no_depot_selection(self):
        """ 在 2nd-echelon 的arc中 customer 只存在与 对应的sate 链接的弧度 """
        self.second_echelon_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list
        )

        for head_vertex_id in self.second_echelon_list:
            for tail_vertex_id in self.second_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # 从 return 的 depot 出发
                    if head_vertex_id in self.sate_depot_list:
                        cur_adj = 0

                    # 驶向 sate
                    if tail_vertex_id in self.sate_list:
                        cur_adj = 0

                    # sate to sate_depot
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list):
                        cur_adj = 0

                    # sate to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_list):
                        cur_adj = 0

                    # sate to customer, bus customer do not belong to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.customer_list) and (
                            tail_vertex_id not in self.sate_serv_cus[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_depot_list) and (
                            tail_vertex_id != self.sate_to_depot[self.cus_belong_sate[head_vertex_id]]):
                        cur_adj = 0

                    # customer 不属于同一个 sate
                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.customer_list) and (
                            self.cus_belong_sate[head_vertex_id] != self.cus_belong_sate[tail_vertex_id]):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.second_echelon_graph.add_arc(arc=new_arc)

        self.second_echelon_graph.preprocess(subgraph=self.second_echelon_graph)

    def gen_od_graph_sate_select(self):
        """ Hungarian Algorithm """
        od_list = self.sate_list + self.customer_list + self.od_o_list + self.od_d_list

        self.od_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list + self.od_o_list + self.od_d_list
        )

        for head_vertex_id in od_list:
            for tail_vertex_id in od_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list) and \
                            (tail_vertex_id != self.sate_to_depot[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_o_list):
                        # sate to sate_depot
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_list) and (
                            head_vertex_id in self.sate_serv_cus[tail_vertex_id]):
                        # customer to sate (do not match)
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        # sate t
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.od_graph.add_arc(arc=new_arc)
                    # self.od_graph.arc_dict[new_arc.head_vertex, new_arc.tail_vertex] = new_arc

        self.od_graph.preprocess(subgraph=self.od_graph)

    def gen_od_graph_no_select(self):

        """  """
        od_list = self.sate_list + self.customer_list + self.od_o_list + self.od_d_list

        self.od_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list + self.od_o_list + self.od_d_list
        )

        for head_vertex_id in od_list:
            for tail_vertex_id in od_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # if (head_vertex_id in self.sate_depot_list) or (tail_vertex_id in self.sate_list):
                    #     # 从虚拟depot出发， 向 satellite 行驶
                    #     cur_adj = 0
                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list) and \
                            (tail_vertex_id != self.sate_to_depot[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_d_list) and (
                            tail_vertex_id != self.o_to_d[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_list) and (
                            head_vertex_id in self.sate_serv_cus[tail_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.od_graph.add_arc(arc=new_arc)
                    # self.od_graph.arc_dict[new_arc.head_vertex, new_arc.tail_vertex] = new_arc

        self.od_graph.preprocess(subgraph=self.od_graph)

    def gen_pdp_graph(self):
        """ PDP graph 是为 gurobi model 准备的 """
        self.pickup_id_list = [len(self.vertex_dict) + i for i in range(len(self.customer_list))]
        self.pd_list = [(self.pickup_id_list[i], self.customer_list[i]) for i in range(self.ins.customer_num)]
        self.pdp_dict = bidict(self.pd_list)
        self.pdp_dict_corr = self.pdp_dict

        for cus_index in range(len(self.customer_list)):
            customer = self.customer_list[cus_index]
            sate = self.cus_belong_sate[customer]

            pickup_vertex = deepcopy(self.vertex_dict[sate])
            pickup_vertex.id_ = self.pickup_id_list[cus_index]
            pickup_vertex.demand = self.vertex_dict[customer].demand

            self.pick_dict[self.pickup_id_list[cus_index]] = pickup_vertex
            self.vertex_dict[pickup_vertex.id_] = pickup_vertex

        self.pdp_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.pickup_id_list + self.od_o_list + self.od_d_list + self.customer_list
        )

        pdp_list = self.pickup_id_list + self.customer_list + self.od_o_list + self.od_d_list

        for head_vertex_id in pdp_list:
            for tail_vertex_id in pdp_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if (head_vertex_id in self.od_d_list) or (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    # delivery to pick up
                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.pickup_id_list) and (
                            head_vertex_id == self.pdp_dict[tail_vertex_id]):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.pdp_graph.add_arc(arc=new_arc)

        self.pdp_graph.preprocess(subgraph=self.pdp_graph)

    def print_customer_info(self):
        for cus in self.customer_list:
            print(
                f'cus.{cus},coord=[{self.vertex_dict[cus].x_coord}, {self.vertex_dict[cus].y_coord}],'
                f' time window=[{self.vertex_dict[cus].ready_time, self.vertex_dict[cus].due_time}]')

    def print_od_info(self):
        for o in self.od_o_list:
            d = self.o_to_d[o]

            print(
                f'OD: NO.{o}(coord=[{self.vertex_dict[o].x_coord}, {self.vertex_dict[o].y_coord}],'
                f'time window=[{self.vertex_dict[o].ready_time, self.vertex_dict[o].due_time}])'
                f'NO.{d}(coord=[{self.vertex_dict[d].x_coord}, {self.vertex_dict[d].y_coord}],'
                f'time window=[{self.vertex_dict[d].ready_time, self.vertex_dict[d].due_time}])'
            )

    def gen_pdp_graph_sate_select(self):
        """ PDP graph 是为 gurobi model 准备的 """
        # 每个 customer 对应的 pickup sate 没有确定， 所以对应的 pickup 地点是所有的 sate
        self.pickup_id_list = [len(self.vertex_dict) + i for i in range(len(self.customer_list) * self.ins.sate_num)]

        self.pd_list = [
            (
                tuple(self.pickup_id_list[i] + self.customer_num * j for j in range(self.ins.sate_num)),
                self.customer_list[i]
            ) for i in range(self.ins.customer_num)
        ]  # (  [sate0, sate1,...], customer  )
        self.pdp_dict = bidict(self.pd_list)

        for c in self.customer_list:
            sate = self.cus_belong_sate[c]
            sate_index = self.sate_list.index(sate)
            self.pd_list_corr.append((self.pdp_dict.inverse[c][sate_index], c))

        self.pdp_dict_corr = bidict(self.pd_list_corr)

        for cus_index in range(len(self.customer_list)):
            customer = self.customer_list[cus_index]

            for sate in range(len(self.sate_list)):
                pickup_vertex = deepcopy(self.vertex_dict[self.sate_list[sate]])
                pickup_vertex.id_ = self.pdp_dict.inverse[customer][sate]
                pickup_vertex.demand = self.vertex_dict[customer].demand

                self.pick_dict[self.pickup_id_list[cus_index]] = pickup_vertex
                self.vertex_dict[pickup_vertex.id_] = pickup_vertex

        self.pdp_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.pickup_id_list + self.od_o_list + self.od_d_list + self.customer_list
        )

        pdp_list = self.pickup_id_list + self.customer_list + self.od_o_list + self.od_d_list

        for head_vertex_id in pdp_list:
            for tail_vertex_id in pdp_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = calc_travel_time(
                        x_1=self.vertex_dict[head_vertex_id].x_coord,
                        x_2=self.vertex_dict[tail_vertex_id].x_coord,
                        y_1=self.vertex_dict[head_vertex_id].y_coord,
                        y_2=self.vertex_dict[tail_vertex_id].y_coord
                    )
                    cur_adj = 1

                    if (head_vertex_id in self.od_d_list) or (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    # delivery to pick up
                    if (head_vertex_id in self.customer_list) and (
                            tail_vertex_id in self.pdp_dict.inverse[head_vertex_id]):
                        cur_adj = 0

                    # 同一个 customer 的 pickup 的 sate 不能相连
                    if head_vertex_id in self.pickup_id_list and tail_vertex_id in self.pickup_id_list:
                        result = [pair for pair in self.pdp_dict.keys() if head_vertex_id in pair]
                        key_ = result[0]
                        if tail_vertex_id in key_:
                            cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.pdp_graph.add_arc(arc=new_arc)

        self.pdp_graph.preprocess(subgraph=self.pdp_graph)

    def gen_first_graph_real_case(self):

        self.first_echelon_graph = Subgraph(
            ins=self.ins,
            level=1,
            vertex_id_list=self.first_echelon_list
        )

        for head_vertex_id in self.first_echelon_list:
            for tail_vertex_id in self.first_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if tail_vertex_id == 0 or head_vertex_id == self.depot_list[1]:
                        # del 从虚拟depot出发 和 向 depot 0 行驶的弧
                        cur_adj = 0

                    if head_vertex_id == 0 and tail_vertex_id == self.depot_list[1]:
                        # depot to depot
                        cur_adj = 0

                    if self.vertex_dict[
                        head_vertex_id].ready_time + cur_distance + self.ins.model_para.t_unload - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.first_echelon_graph.add_arc(arc=new_arc)

        self.first_echelon_graph.preprocess(subgraph=self.first_echelon_graph)

    def gen_second_graph_sate_select_real_case(self):
        """ 2nd-echelon , sate 可以每个 符合约束的客户服务"""
        self.second_echelon_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list
        )

        for head_vertex_id in self.second_echelon_list:
            for tail_vertex_id in self.second_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    service_time = self.ins.model_para.service_time if head_vertex_id in self.customer_list else 0

                    # if head_vertex_id == 1 and tail_vertex_id == 25:
                    #     print()

                    if self.vertex_dict[head_vertex_id].ready_time + cur_distance + service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # 从 return 的 depot 出发
                    if head_vertex_id in self.sate_depot_list:
                        cur_adj = 0

                    # 驶向 sate
                    if tail_vertex_id in self.sate_list:
                        cur_adj = 0

                    # sate to sate_depot
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list):
                        cur_adj = 0

                    # sate to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.second_echelon_graph.add_arc(arc=new_arc)

        self.second_echelon_graph.preprocess(subgraph=self.second_echelon_graph)

    def gen_second_graph_no_depot_selection_real_case(self):
        """ 在 2nd-echelon 的arc中 customer 只存在与 对应的sate 链接的弧度 """
        self.second_echelon_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list
        )

        for head_vertex_id in self.second_echelon_list:
            for tail_vertex_id in self.second_echelon_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if self.vertex_dict[
                        head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # 从 return 的 depot 出发
                    if head_vertex_id in self.sate_depot_list:
                        cur_adj = 0

                    # 驶向 sate
                    if tail_vertex_id in self.sate_list:
                        cur_adj = 0

                    # sate to sate_depot
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list):
                        cur_adj = 0

                    # sate to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_list):
                        cur_adj = 0

                    # sate to customer, bus customer do not belong to sate
                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.customer_list) and (
                            tail_vertex_id not in self.sate_serv_cus[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_depot_list) and (
                            tail_vertex_id != self.sate_to_depot[self.cus_belong_sate[head_vertex_id]]):
                        cur_adj = 0

                    # customer 不属于同一个 sate
                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.customer_list) and (
                            self.cus_belong_sate[head_vertex_id] != self.cus_belong_sate[tail_vertex_id]):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.second_echelon_graph.add_arc(arc=new_arc)

        self.second_echelon_graph.preprocess(subgraph=self.second_echelon_graph)

    def gen_od_graph_sate_select_real_case(self):
        """ Hungarian Algorithm """
        od_list = self.sate_list + self.customer_list + self.od_o_list + self.od_d_list

        self.od_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list + self.od_o_list + self.od_d_list
        )

        for head_vertex_id in od_list:
            for tail_vertex_id in od_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if self.vertex_dict[
                        head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list) and \
                            (tail_vertex_id != self.sate_to_depot[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_o_list):
                        # sate to sate_depot
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_list) and (
                            head_vertex_id in self.sate_serv_cus[tail_vertex_id]):
                        # customer to sate (do not match)
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        # sate t
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.od_graph.add_arc(arc=new_arc)
                    # self.od_graph.arc_dict[new_arc.head_vertex, new_arc.tail_vertex] = new_arc

        self.od_graph.preprocess(subgraph=self.od_graph)

    def gen_od_graph_no_select_real_case(self):

        """  """
        od_list = self.sate_list + self.customer_list + self.od_o_list + self.od_d_list

        self.od_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.second_echelon_list + self.od_o_list + self.od_d_list
        )

        for head_vertex_id in od_list:
            for tail_vertex_id in od_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if self.vertex_dict[
                        head_vertex_id].ready_time + cur_distance + self.ins.model_para.service_time - \
                            self.vertex_dict[tail_vertex_id].due_time > 0:
                        # do not satisfy time window
                        cur_adj = 0

                    # if (head_vertex_id in self.sate_depot_list) or (tail_vertex_id in self.sate_list):
                    #     # 从虚拟depot出发， 向 satellite 行驶
                    #     cur_adj = 0
                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_depot_list) or (head_vertex_id in self.od_d_list):
                        # 从虚拟depot出发， 向 satellite 行驶
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.sate_depot_list) and \
                            (tail_vertex_id != self.sate_to_depot[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    if (head_vertex_id in self.od_o_list) and (tail_vertex_id in self.od_d_list) and (
                            tail_vertex_id != self.o_to_d[head_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.sate_list) and (
                            head_vertex_id in self.sate_serv_cus[tail_vertex_id]):
                        cur_adj = 0

                    if (head_vertex_id in self.sate_list) and (tail_vertex_id in self.od_d_list):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.od_graph.add_arc(arc=new_arc)
                    # self.od_graph.arc_dict[new_arc.head_vertex, new_arc.tail_vertex] = new_arc

        self.od_graph.preprocess(subgraph=self.od_graph)

    def gen_pdp_graph_real_case(self):
        """ PDP graph 是为 gurobi model 准备的 """
        self.pickup_id_list = [len(self.vertex_dict) + i for i in range(len(self.customer_list))]
        self.pd_list = [(self.pickup_id_list[i], self.customer_list[i]) for i in range(self.ins.customer_num)]
        self.pdp_dict = bidict(self.pd_list)
        self.pdp_dict_corr = self.pdp_dict

        for cus_index in range(len(self.customer_list)):
            customer = self.customer_list[cus_index]
            sate = self.cus_belong_sate[customer]

            pickup_vertex = deepcopy(self.vertex_dict[sate])
            pickup_vertex.id_ = self.pickup_id_list[cus_index]
            pickup_vertex.demand = self.vertex_dict[customer].demand

            self.pick_dict[self.pickup_id_list[cus_index]] = pickup_vertex
            self.vertex_dict[pickup_vertex.id_] = pickup_vertex

        self.pdp_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.pickup_id_list + self.od_o_list + self.od_d_list + self.customer_list
        )

        pdp_list = self.pickup_id_list + self.customer_list + self.od_o_list + self.od_d_list

        for head_vertex_id in pdp_list:
            for tail_vertex_id in pdp_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if (head_vertex_id in self.od_d_list) or (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    # delivery to pick up
                    if (head_vertex_id in self.customer_list) and (tail_vertex_id in self.pickup_id_list) and (
                            head_vertex_id == self.pdp_dict[tail_vertex_id]):
                        cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.pdp_graph.add_arc(arc=new_arc)

        self.pdp_graph.preprocess(subgraph=self.pdp_graph)

    def gen_pdp_graph_sate_select_real_case(self):
        """ PDP graph 是为 gurobi model 准备的 """
        # 每个 customer 对应的 pickup sate 没有确定， 所以对应的 pickup 地点是所有的 sate
        self.pickup_id_list = [len(self.vertex_dict) + i for i in range(len(self.customer_list) * self.ins.sate_num)]

        self.pd_list = [
            (
                tuple(self.pickup_id_list[i] + self.customer_num * j for j in range(self.ins.sate_num)),
                self.customer_list[i]
            ) for i in range(self.ins.customer_num)
        ]  # (  [sate0, sate1,...], customer  )
        self.pdp_dict = bidict(self.pd_list)

        for c in self.customer_list:
            sate = self.cus_belong_sate[c]
            sate_index = self.sate_list.index(sate)
            self.pd_list_corr.append((self.pdp_dict.inverse[c][sate_index], c))

        self.pdp_dict_corr = bidict(self.pd_list_corr)

        for cus_index in range(len(self.customer_list)):
            customer = self.customer_list[cus_index]

            for sate in range(len(self.sate_list)):
                pickup_vertex = deepcopy(self.vertex_dict[self.sate_list[sate]])
                pickup_vertex.id_ = self.pdp_dict.inverse[customer][sate]
                pickup_vertex.demand = self.vertex_dict[customer].demand

                self.pick_dict[self.pickup_id_list[cus_index]] = pickup_vertex
                self.vertex_dict[pickup_vertex.id_] = pickup_vertex

        self.pdp_graph = Subgraph(
            ins=self.ins,
            level=2,
            vertex_id_list=self.pickup_id_list + self.od_o_list + self.od_d_list + self.customer_list
        )

        pdp_list = self.pickup_id_list + self.customer_list + self.od_o_list + self.od_d_list

        for head_vertex_id in pdp_list:
            for tail_vertex_id in pdp_list:

                if head_vertex_id != tail_vertex_id:
                    cur_distance = geodesic((self.vertex_dict[head_vertex_id].x_coord,
                                             self.vertex_dict[head_vertex_id].y_coord),
                                            (self.vertex_dict[tail_vertex_id].x_coord,
                                             self.vertex_dict[tail_vertex_id].y_coord)).meters / self.vehicle_speed
                    cur_adj = 1

                    if (head_vertex_id in self.od_d_list) or (tail_vertex_id in self.od_o_list):
                        cur_adj = 0

                    # delivery to pick up
                    if (head_vertex_id in self.customer_list) and (
                            tail_vertex_id in self.pdp_dict.inverse[head_vertex_id]):
                        cur_adj = 0

                    # 同一个 customer 的 pickup 的 sate 不能相连
                    if head_vertex_id in self.pickup_id_list and tail_vertex_id in self.pickup_id_list:
                        result = [pair for pair in self.pdp_dict.keys() if head_vertex_id in pair]
                        key_ = result[0]
                        if tail_vertex_id in key_:
                            cur_adj = 0

                    new_arc = Arc(
                        head_vertex=head_vertex_id, tail_vertex=tail_vertex_id,
                        distance=cur_distance,
                        adj=cur_adj
                    )

                    self.pdp_graph.add_arc(arc=new_arc)

        self.pdp_graph.preprocess(subgraph=self.pdp_graph)

    def gen_sub_graphs_real_case(self):
        """ """
        # 2nd
        if self.ins.is_select is True:
            self.gen_second_graph_sate_select_real_case()
            # 1st
            self.gen_first_graph_real_case()

            self.gen_od_graph_sate_select_real_case()

        else:
            # self.calc_cus_belong_sate()
            self.gen_second_graph_no_depot_selection_real_case()
            # 1st
            self.gen_first_graph_real_case()

            self.gen_od_graph_no_select_real_case()

            # 添加初始的 alns_dict
            for sate in self.sate_list:
                self.ins.alns_dict[sate] = self.sate_serv_cus[sate]

        # od
        # self.gen_od_graph()

        if self.ins.is_select is True:
            self.gen_pdp_graph_sate_select_real_case()

        else:
            self.gen_pdp_graph_real_case()

        self.arc_dict = {**self.first_echelon_graph.arc_dict, **self.second_echelon_graph.arc_dict,
                         **self.od_graph.arc_dict}
