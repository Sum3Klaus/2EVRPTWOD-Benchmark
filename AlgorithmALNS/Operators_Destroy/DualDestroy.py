# -*- coding: utf-8 -*-
# @Time     : 2024-07-18-16:15
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class DualDestroy(object):
    """
    建立覆盖集模型，
    求解得到对偶值进行排序
    """

    def __init__(self):
        self.no = 6

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        :param sol:
        :param remove_num:
        :param alns_model:
        :return:
        """
        remove_list = []
        remove_id_list = []
        destroy_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)
        destroy_vertex_sequence = sol_cp.vertex_sequence

        if alns_model.model_builder.RMP is None:
            alns_model.model_builder.build_rmp_and_sp()
            alns_model.cg.set_model(model_builder=alns_model.model_builder)

        for route in alns_model.route_records:
            if route.route_list not in alns_model.model_builder.column_pool.values():
                alns_model.cg.route_index = next(alns_model.cg.next_iter_time)
                cur_column = alns_model.cg.get_column(route_list=route.route_list)
                alns_model.cg.add_column_into_rmp(route=route,
                                                  new_column=cur_column,
                                                  iter_times=alns_model.cg.route_index)

        alns_model.cg.solve_rmp_and_get_duals()

        dual_sort = sorted(alns_model.cg.RMP_duals.items(), key=lambda x: x[1], reverse=True)

        for i in range(destroy_num):
            cur_vertex_id = int(dual_sort[i][0])
            cur_vertex_route_index = sol_cp.vertex_id_sequence.index(cur_vertex_id)
            destroy_list.append(destroy_vertex_sequence[cur_vertex_route_index])

        for vertex_ in destroy_list:
            remove_list.append(vertex_)
            destroy_vertex_sequence.remove(vertex_)
            remove_id_list.append(vertex_.id_)

        return remove_list, remove_id_list, destroy_vertex_sequence
