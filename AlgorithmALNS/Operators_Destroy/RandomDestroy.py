# -*- coding: utf-8 -*-
# @Time     : 2024-04-15-16:42
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
import math
from copy import deepcopy


class RandomDestroy(object):

    def __init__(self):
        self.no = 0

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """

        :param sol:
        :param remove_num
        :param alns_model:
        :return:
        """
        destroy_vertex_sequence = deepcopy(sol.vertex_sequence)
        destroy_num = remove_num

        # destroy_rate = random.uniform(alns_model.params.random_destroy_min, alns_model.params.random_destroy_max)
        # destroy_num = math.floor(destroy_rate * len(sol.vertex_sequence))

        if destroy_num == len(sol.vertex_sequence):
            destroy_num -= 2

        remove_list = random.sample(destroy_vertex_sequence, destroy_num)
        remove_id_list = []

        for vertex in remove_list:
            destroy_vertex_sequence.remove(vertex)
            remove_id_list.append(vertex.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence
