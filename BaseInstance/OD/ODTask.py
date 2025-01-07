# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-14:57
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Vertex import Vertex


class ODTask(object):

    def __init__(self,
                 _id,
                 origin_node: Vertex,
                 terminate_node: Vertex,
                 arc,
                 dis):
        self.id = _id
        self.origin_node = origin_node
        self.terminate_node = terminate_node
        self.task_dis = dis

        self.od_arc = arc

    def __repr__(self):
        return f'NO.{self.id}, ({self.origin_node.x_coord}, {self.origin_node.y_coord})' \
               f'-[{self.origin_node.ready_time}, {self.origin_node.due_time}]' \
               f'——({self.terminate_node.x_coord}, {self.terminate_node.y_coord})' \
               f'-[{self.terminate_node.ready_time}, {self.terminate_node.due_time}] | {self.task_dis})'