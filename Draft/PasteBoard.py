# -*- coding: utf-8 -*-
# @Time     : 2024-10-10-14:47
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
"""

# capacity
for i in self.ins.graph.first_echelon_list:
    for j in self.ins.graph.first_echelon_list:
        if judge_arc(arc_id=(i, j),
                     graph=self.ins.graph.first_echelon_graph):

            for k in range(self.ins.vehicle_num_1st):
                con_name_capacity = '1st-3-con_capacity-' + f'{i}' + '_' + f'{j}' + '_' + f'{k}'

                self.cons[con_name_capacity] = self.model.addConstr(
                    self.w_s[i, k] - self.w_s[j, k] + (
                            self.ins.graph.vertex_dict[j].demand + self.ins.model_para.vehicle_1_capacity) *
                    self.x[i, j, k] <= self.ins.model_para.vehicle_1_capacity,
                    name=con_name_capacity
                )

for i in self.ins.graph.sate_list:
    sate_service_lq = LinExpr()
    sate_service_coe = []
    sate_service_var = []

    con_name_capacity = '1st-3-con_capacity_sate-' + f'{i}'
    for k in range(self.ins.vehicle_num_1st):
        sate_service_coe.append(1)
        sate_service_var.append(self.w_s[i, k])

    sate_service_lq.addTerms(sate_service_coe, sate_service_var)
    self.cons[con_name_capacity] = self.model.addConstr(
        sate_service_lq == self.ins.graph.vertex_dict[i].demand,
        name=con_name_capacity
    )

for k in range(self.ins.vehicle_num_1st):
    vehicle_service_lq = LinExpr()
    vehicle_service_coe = []
    vehicle_service_var = []

    con_name_capacity = '1st-3-con_capacity_vehicle-' + f'{k}'

    for i in self.ins.graph.sate_list:
        vehicle_service_coe.append(1)
        vehicle_service_var.append(self.w_s[i, k])
    vehicle_service_lq.addTerms(vehicle_service_coe, vehicle_service_var)

    self.cons[con_name_capacity] = self.model.addConstr(
        vehicle_service_lq <= self.para.vehicle_1_capacity,
        name=con_name_capacity
    )


"""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# 创建一个图
G = nx.Graph()
edges = [(1, 2), (2, 3), (3, 1), (2, 4), (4, 3)]
G.add_edges_from(edges)

# 检查图是否有欧拉回路
if nx.is_eulerian(G):
    euler_circuit = list(nx.eulerian_circuit(G))
else:
    euler_circuit = None

# 绘制原图
pos = nx.spring_layout(G)  # 使用弹簧布局
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=700, font_size=16, font_color='black')

# 绘制欧拉回路（如果存在）
if euler_circuit:
    euler_edges = [(u, v) for u, v in euler_circuit]
    euler_pos = {}

    # 为欧拉回路的边计算圆弧位置
    for (u, v) in euler_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        # 计算中点和偏移
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        offset = 0.1  # 偏移量
        if x1 == x2:  # 垂直线
            arc_x = mid_x + offset
            arc_y = mid_y
        else:
            arc_x = mid_x
            arc_y = mid_y + offset

        euler_pos[(u, v)] = (arc_x, arc_y)
        euler_pos[(v, u)] = (arc_x, arc_y)

    # 绘制欧拉回路的圆弧
    for (u, v) in euler_edges:
        arc = np.linspace(0, np.pi, 100)
        x_arc = np.linspace(pos[u][0], pos[v][0], 100) + (arc - np.pi / 2) * (0.1 if pos[u][0] < pos[v][0] else -0.1)
        y_arc = np.linspace(pos[u][1], pos[v][1], 100) + (arc - np.pi / 2) * (0.1 if pos[u][1] < pos[v][1] else -0.1)
        plt.plot(x_arc, y_arc, color='orange', lw=2)

# 显示图形
plt.title("Euler Circuit in Graph")
plt.axis('equal')
plt.show()
