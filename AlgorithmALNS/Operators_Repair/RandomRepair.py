# -*- coding: utf-8 -*-
# @Time     : 2024-04-15-22:09
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
from copy import deepcopy


class RandomRepair(object):

    def __init__(self):
        self.no = 0

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """
        repair_vertex_sequence = deepcopy(assigned_list)

        for vertex in unassigned_list:

            insert_index = random.randint(0, len(repair_vertex_sequence))
            repair_vertex_sequence.insert(insert_index, vertex)

        return repair_vertex_sequence