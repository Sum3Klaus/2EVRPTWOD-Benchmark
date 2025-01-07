# -*- coding: utf-8 -*-
# @Time     : 2024-08-30-15:28
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from gurobipy import *


def add_valid_inequalities(self):
    """ 添加有效不等式 """
    def judge_arc(arc_id, graph):
        return True

    # 1
    # The Two-Echelon Capacitated Vehicle Routing  Problem: Models and Math-Based Heuristics
    # 对应 eq 27
    visit_list1 = self.graph.customer_list + self.graph.sate_list  # i \in v1
    visit_list2 = self.graph.customer_list + self.graph.sate_depot_list  # l \in v2
    for s in self.graph.sate_list:
        visit_list1 = self.graph.customer_list + [s]  # i \in v1
        visit_list2 = self.graph.customer_list + [self.graph.sate_to_depot[s]]  # l \in v2
        for j in self.graph.customer_list:
            for k in range(self.ins.vehicle_num_2nd):
                lq_1 = LinExpr()
                lq_1_coe = []
                lq_1_var = []
                for c in self.graph.customer_list:
                    lq_1_coe.append(1)
                    lq_1_var.append(self.var_y[s, c, k])
                lq_1.addTerms(lq_1_coe, lq_1_var)

                lq_2 = QuadExpr()
                lq_2_coe = []
                lq_2_var1 = []
                lq_2_var2 = []
                for i in visit_list1:
                    if judge_arc(arc_id=(i, j),
                                 graph=self.graph.second_echelon_graph):
                        # lq_2.addTerm(1, self.var_y[i, j, k], self.w_c_k2[j, k])
                        lq_2_coe.append(1)
                        lq_2_var1.append(self.var_y[i, j, k])
                        lq_2_var2.append(self.w_c_k2[j, k])
                lq_2.addTerms(lq_2_coe, lq_2_var1, lq_2_var2)
                self.valid_vars_1_1[s, j, k, 1] = self.model.addVar(name='valid_1_1+' + str((j, k)))
                self.model.addConstr(
                    self.valid_vars_1_1[s, j, k, 1] == lq_2
                )

                lq_3 = QuadExpr()
                lq_3_coe = []
                lq_3_var1 = []
                lq_3_var2 = []
                for l in visit_list2:
                    if judge_arc(arc_id=(j, l),
                                 graph=self.graph.second_echelon_graph):
                        # lq_3.addTerm(1, self.var_y[j, l, k], self.w_c_k2[l, k])
                        # lq_3 += self.var_y[j, l, k] * self.w_c_k2[l, k]
                        lq_3_coe.append(1)
                        lq_3_var1.append(self.var_y[j, l, k])
                        lq_3_var2.append(self.w_c_k2[l, k])
                lq_3.addTerms(lq_3_coe, lq_3_var1, lq_3_var2)
                self.valid_vars_1_2[s, j, k, 2] = self.model.addVar(name='valid_1_2+' + str((j, k)))
                self.model.addConstr(
                    self.valid_vars_1_2[s, j, k, 2] == lq_3
                )

                # expr = lq_2.getLinExpr() + lq_3.getLinExpr()
                # expr = lq_2 + lq_3

                self.valid_inequalities[s, j, k] = self.model.addQConstr(
                    lq_1 * (self.valid_vars_1_1[s, j, k, 1] + self.valid_vars_1_2[s, j, k, 2]) <=
                    self.graph.vertex_dict[j].demand * self.zeta_c_s[j, s],
                    name='valid-1_' + str(s) + '_' + str(j) + '_' + str(k)
                )
    self.model.update()