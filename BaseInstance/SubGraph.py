# -*- coding: utf-8 -*-
# @Time     : 2024-07-30-11:41
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class Subgraph(object):

    def __init__(self,
                 ins,
                 level,
                 vertex_id_list):

        self.ins = ins
        self.level = level
        self.vertex_id_list = vertex_id_list
        self.arc_dict = {}

    def add_arc(self,
                arc):
        """
        add a single edge into the graph
        :param arc
        :return:
        """
        self.arc_dict[arc.head_vertex, arc.tail_vertex] = arc

        if self.level == 1:
            # update the successors and predecessors accordingly
            if arc.tail_vertex not in self.ins.graph.vertex_dict[arc.head_vertex].successors_1st:
                self.ins.graph.vertex_dict[arc.head_vertex].successors_1st.append(arc.tail_vertex)

            if arc.head_vertex not in self.ins.graph.vertex_dict[arc.tail_vertex].predecessors_1st:
                self.ins.graph.vertex_dict[arc.tail_vertex].predecessors_1st.append(arc.head_vertex)

        elif self.level == 2:
            # update the successors and predecessors accordingly
            if arc.tail_vertex not in self.ins.graph.vertex_dict[arc.head_vertex].successors_2nd:
                self.ins.graph.vertex_dict[arc.head_vertex].successors_2nd.append(arc.tail_vertex)

            if arc.head_vertex not in self.ins.graph.vertex_dict[arc.tail_vertex].predecessors_2nd:
                self.ins.graph.vertex_dict[arc.tail_vertex].predecessors_2nd.append(arc.head_vertex)

    def del_vertex(self, removed_vertex_id):
        """
        remove a single vertex from the current graph
        in python dict delete element only through key:"del" "pop" "popitem" and "clear"
        :param removed_vertex_id:
        :return:
        """
        # remove the current node
        self.ins.vertex_dict.pop(removed_vertex_id)

        # remove all the edges that uses this vertex
        key_lst = list(self.arc_dict.keys())  # (from_vertex, to_vertex)
        for i in range(len(key_lst)):
            key = key_lst[i]
            if (key[0] == removed_vertex_id) or (key[1] == removed_vertex_id):
                self.arc_dict.pop(key)

        # revise successors and predecessors for each vertex
        for vertex_ID in self.ins.vertex_dict.keys():

            # predecessors
            if self.level == 1:
                if removed_vertex_id in self.ins.vertex_dict[vertex_ID].predecessors_1st:
                    self.ins.vertex_dict[vertex_ID].predecessors_1st.remove(removed_vertex_id)

                # successors
                if removed_vertex_id in self.ins.vertex_dict[vertex_ID].successors_1st:
                    self.ins.vertex_dict[vertex_ID].successors_1st.remove(removed_vertex_id)

            elif self.level == 2:
                if removed_vertex_id in self.ins.vertex_dict[vertex_ID].predecessors_2nd:
                    self.ins.vertex_dict[vertex_ID].predecessors_2nd.remove(removed_vertex_id)

                # successors
                if removed_vertex_id in self.ins.vertex_dict[vertex_ID].successors_2nd:
                    self.ins.vertex_dict[vertex_ID].successors_2nd.remove(removed_vertex_id)

        del_arc_list = []
        for key, value in self.arc_dict.items():
            if removed_vertex_id in key:
                del_arc_list.append(key)

        for del_arc in del_arc_list:
            del self.arc_dict[del_arc]

    def preprocess(self,
                   subgraph):

        for arc_id, arc in subgraph.arc_dict.items():

            head_vertex = arc_id[0]
            tail_vertex = arc_id[1]

            if arc.adj == 0:

                if subgraph.level == 1:

                    self.ins.graph.vertex_dict[head_vertex].successors_1st.remove(tail_vertex)
                    self.ins.graph.vertex_dict[tail_vertex].predecessors_1st.remove(head_vertex)

                elif subgraph.level == 2:

                    self.ins.graph.vertex_dict[head_vertex].successors_2nd.remove(tail_vertex)
                    self.ins.graph.vertex_dict[tail_vertex].predecessors_2nd.remove(head_vertex)