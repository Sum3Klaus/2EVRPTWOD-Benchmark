# -*- coding: utf-8 -*-
# @Time     : 2024-08-12-10:55
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from copy import deepcopy


class HistoryBasedDestroy(object):
    """
    This removal operator keeps track of the shortest setup time of each job.
    pd jobs with setup times that have larger distance to their best setup times are removed.
    """

    def __init__(self):
        self.no = 4

    @staticmethod
    def gen_destroy(sol,
                    remove_num,
                    alns_model):
        """
        根据论文 DR-ALNS
        """
        remove_list = []
        remove_id_list = []
        destroy_list = []
        destroy_num = remove_num
        distance_dict = dict()

        sol_cp = deepcopy(sol)

        destroy_vertex_sequence = sol_cp.vertex_sequence

        def calc_neighbor_graph(sol_pre):
            neighbor_graph = dict()

            for r in sol_pre.routes:

                for index_ in range(1, len(r.route) - 1):
                    pre_arc = (r.route[index_ - 1].id_, r.route[index_].id_)
                    next_arc = (r.route[index_].id_, r.route[index_ + 1].id_)

                    neighbor_graph[r.route[index_]] = sol_cp.ins.graph.arc_dict[pre_arc].distance + \
                                                      sol_cp.ins.graph.arc_dict[next_arc].distance

            return neighbor_graph

        # calc neighbor_graph
        n_g = calc_neighbor_graph(sol_pre=sol_cp)

        while len(remove_list) < destroy_num:

            # 排序
            neighbor_graph_sorted = sorted(n_g.items(), key=lambda x: x[1], reverse=True)

            cur_removal_vertex = neighbor_graph_sorted[0][0]

            remove_list.append(cur_removal_vertex)
            remove_id_list.append(cur_removal_vertex.id_)
            destroy_vertex_sequence.remove(cur_removal_vertex)

            n_g.pop(cur_removal_vertex)

            if len(remove_list) == remove_num:
                break

            # remove the node from its route
            for route in sol_cp.routes:

                if cur_removal_vertex.id_ in route.route_list:
                    cur_route = route.route
                    cur_route.remove(cur_removal_vertex)

                    if len(cur_route) == 2:
                        pass

                    else:

                        for i in range(1, len(cur_route) - 1):
                            pre_arc = (cur_route[i - 1].id_, cur_route[i].id_)
                            next_arc = (cur_route[i].id_, cur_route[i + 1].id_)

                            n_g[cur_route[i]] = sol_cp.ins.graph.arc_dict[pre_arc].distance + \
                                                sol_cp.ins.graph.arc_dict[next_arc].distance

                    break

        return remove_list, remove_id_list, destroy_vertex_sequence
