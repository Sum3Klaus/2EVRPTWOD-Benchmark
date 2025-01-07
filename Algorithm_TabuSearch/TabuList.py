# -*- coding: utf-8 -*-
# @Time     : 2024-07-22-21:08
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class TabuList(object):

    def __init__(self,
                 vertex_id_sequence,
                 op_id,
                 remove_num: int,
                 destroy_or_repair
                 ):
        """

        :param vertex_id_sequence
        :param op_id: 破坏算子的id
        :param remove_num: (破坏前解的 index, 修复后解的 index)
        :param destroy_or_repair
        :param : 检查迭代次数 theta
        """
        self.vertex_id_sequence = vertex_id_sequence
        self.op_id = op_id
        self.remove_num = remove_num
        self.destroy_or_repair = destroy_or_repair
        self.valid_for = 20  # valid_for

    def __repr__(self):
        return (f'{self.vertex_id_sequence} | {self.destroy_or_repair}-NO.{self.op_id} | Num = {self.remove_num} '
                f'| remain iteration = {self.valid_for}')

    def check_tabu_iteration(self):
        # 检查是否可以去禁
        if self.valid_for > 0:
            self.valid_for -= 1
            return self.valid_for

        else:
            return -1

    def check_is_in_tabu(self,
                         vertex_id_sequence,
                         op_id,
                         remove_num):
        if (self.op_id == op_id) and (self.vertex_id_sequence == vertex_id_sequence) and (
                self.remove_num == remove_num) and (self.valid_for > 0):
            print("found tabu match op : {0} {1} operator (remove num {2}) : {3}".format(self.destroy_or_repair,
                                                                                         self.op_id, self.remove_num,
                                                                                         self.vertex_id_sequence))
            return True
        return False
