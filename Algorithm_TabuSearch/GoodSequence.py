# -*- coding: utf-8 -*-
# @Time     : 2024-07-16-13:49
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class GoodSequence(object):

    def __init__(self,
                 ins,
                 sequence):
        """ """
        self.ins = ins
        self.sequence = sequence
        self.sequence_list = [i.id_ for i in self.sequence]
        self.distance = self.calc_distance()

    def __repr__(self):
        return f'Sequence: {self.sequence_list}, | Distance = {self.distance}'

    def calc_distance(self):
        distance = 0

        for index_ in range(len(self.sequence) - 1):

            distance += self.ins.graph.arc_dict[self.sequence[index_].id_, self.sequence[index_ + 1].id_].distance

        return distance
