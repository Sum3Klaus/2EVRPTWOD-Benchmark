# -*- coding: utf-8 -*-
# @Time     : 2024-07-09-14:41
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random
from copy import deepcopy


class ConflictDestroy(object):
    """
    Span time window_{cur} = (TimeWindow_cur ∩ TimeWindow_next)
    The rationale of this operator is that these jobs can be scheduled in other time windows easily.
    效果有待评价
    """

    def __init__(self):
        self.no = 5

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        根据访问的距离
        :param sol:
        :param remove_num:
        :param alns_model:
        :return:
        """

        def interval_intersection(interval1, interval2):
            """
            计算两个区间的交叉范围。

            参数:
            interval1: 第一个区间 (start1, end1)
            interval2: 第二个区间 (start2, end2)

            返回:
            交叉范围的区间 (start, end)，如果没有交叉则返回 None。
            """
            start1, end1 = interval1
            start2, end2 = interval2

            # 计算交叉的起始和结束点
            start = max(start1, start2)
            end = min(end1, end2)

            # 如果交叉区间有效，则返回交叉区间
            if start <= end:
                return start, end
            else:
                return 0, 0

        def calc_conflict(sol_):
            span_time_dict_ = dict()

            for vertex1 in sol_.vertex_sequence:
                span_time = 0
                for vertex2 in sol_.vertex_sequence:
                    if vertex1.id_ != vertex2.id_:
                        span_time_cur = interval_intersection(interval1=(vertex1.ready_time,
                                                                         vertex1.due_time),
                                                              interval2=(vertex2.ready_time,
                                                                         vertex2.due_time))
                        span_time += span_time_cur[1] - span_time_cur[0]
                span_time_dict_[vertex1] = (span_time / (
                        vertex1.due_time + alns_model.ins.model_para.service_time - vertex1.ready_time))

            span_time_dict_sort_ = sorted(span_time_dict_.items(), key=lambda x: x[1], reverse=True)

            return span_time_dict_, span_time_dict_sort_

        def if_calc(sol_,
                    sate):

            if len(sol_.ins.span_time_dict_sate[sate]) == 0:
                return True
            else:
                return False

        check_vertex = random.choice(sol.vertex_sequence)
        belong_to_sate = sol.ins.graph.cus_belong_sate[check_vertex.id_]
        if if_calc(sol_=sol,
                   sate=belong_to_sate):
            alns_model.ins.span_time_dict_sate[belong_to_sate], alns_model.ins.span_time_dict_sate_sort[
                belong_to_sate] = calc_conflict(sol)
        else:
            pass

        remove_list = []
        remove_id_list = []
        destroy_list = []
        destroy_num = remove_num

        sol_cp = deepcopy(sol)
        destroy_vertex_sequence = sol_cp.vertex_sequence

        for i in range(destroy_num):
            # destroy_list.append(sol_cp.ins.span_time_dict_sate_sort[belong_to_sate][i][0])
            cur_vertex_id = sol.ins.span_time_dict_sate_sort[belong_to_sate][i][0].id_
            for index, vertex in enumerate(destroy_vertex_sequence):
                if vertex.id_ == cur_vertex_id:
                    destroy_list.append(destroy_vertex_sequence[index])

        # print(f'destroy_list = {destroy_list}')
        for vertex_ in destroy_list:
            # print(f'vertex = {vertex_}')
            remove_list.append(vertex_)
            destroy_vertex_sequence.remove(vertex_)
            remove_id_list.append(vertex_.id_)
            # print('finished')

        return remove_list, remove_id_list, destroy_vertex_sequence
