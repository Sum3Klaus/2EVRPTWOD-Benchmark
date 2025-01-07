# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-14:09
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class Arc(object):

    def __init__(self,
                 head_vertex, tail_vertex,
                 distance,
                 adj=1
                 ):
        self.head_vertex = head_vertex
        self.tail_vertex = tail_vertex
        self.arc = (self.head_vertex, self.tail_vertex)
        self.distance = distance
        self.adj = adj  # whether the arc is feasible

    def __repr__(self):
        return f'arc-{self.arc}={self.distance}|adj={self.adj}'