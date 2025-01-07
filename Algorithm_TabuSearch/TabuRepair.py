# -*- coding: utf-8 -*-
# @Time     : 2024-07-08-15:16
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


# class TabuRepair(object):
#
#     def __init__(self,
#                  vertex_id_sequence,
#                  op_id,
#                  remove_num: int,
#                  ):
#         """
#
#         :param vertex_id_sequence: 破坏后的序列
#         :param op_id: 修复算子的id
#         :param: 检查迭代次数 theta
#         """
#         self.vertex_id_sequence = vertex_id_sequence
#         self.op_id = op_id
#         self.remove_num = remove_num
#         self.valid_for = 7  # valid_for
#
#     def check_tabu_iteration(self):
#         # 检查是否可以去禁
#         if self.valid_for > 0:
#             self.valid_for -= 1
#             return self.valid_for
#
#         else:
#             return -1
#
#     def check_is_in_tabu(self,
#                          vertex_id_sequence,
#                          op_id,
#                          remove_num):
#         if (self.op_id == op_id) and (self.vertex_id_sequence == vertex_id_sequence) and (
#                 self.remove_num == remove_num) and (self.valid_for > 0):
#             print("found tabu match op : {0} operator (remove num {1}) : {2}".format(self.op_id, self.remove_num,
#                                                                                      self.vertex_id_sequence))
#             return True
#         return False