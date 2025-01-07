# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-13:53
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class Vertex(object):

    def __init__(self,
                 id_,
                 x_coord, y_coord,
                 ready_time, due_time,
                 demand=0,
                 ):
        """
        customer and od origin and terminate
        """
        self.id_ = id_
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.ready_time = ready_time
        self.due_time = due_time
        self.demand = demand
        self.service_time = 0

        self.predecessors_1st = []  # 当前节点的前序节点List 如果是2级点，1级则是所属的sate
        self.successors_1st = []  # 当前节点的后续节点List

        self.predecessors_2nd = []  # 当前节点的前序节点List
        self.successors_2nd = []  # 当前节点的后续节点List

        self.waiting_time = 0

    def __repr__(self):
        return f'NO.{self.id_}'

    def print_vertex(self):
        print(f'NO.{self.id_}, ({self.x_coord}, {self.y_coord}, [{self.ready_time}, {self.due_time}])')