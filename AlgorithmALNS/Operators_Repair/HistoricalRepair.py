# -*- coding: utf-8 -*-
# @Time     : 2024-07-19-14:05
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class HistoricalRepair(object):
    """ """

    def __init__(self):
        self.no = 5

    @staticmethod
    def do_repair(unassigned_list,
                  assigned_list,
                  alns_model):
        """  """

        def insert_values_at_indices(lst,
                                     indices_and_values):

            # Sort indices_and_values by the index to handle insertion in correct order
            indices_and_values.sort(key=lambda x: x[0])

            # Insert each value at the specified index
            for index, value in indices_and_values:
                # Adjust the index considering the current length of the list
                lst.insert(index, value)

            return lst