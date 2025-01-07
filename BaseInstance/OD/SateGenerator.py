# -*- coding: utf-8 -*-
# @Time     : 2024-04-13-15:35
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from Vertex import Vertex
from Graph import Graph
import pandas as pd
from sklearn.cluster import KMeans
from copy import deepcopy
import warnings
warnings.filterwarnings('ignore')


class GenSate(object):

    def __init__(self,
                 graph: Graph):
        self.graph_ = graph

        # Feature
        self.train_df = None
        self.customer_x = []
        self.customer_y = []
        self.time_tables = []

        # result of generational satellites
        self.labels = None
        self.centroids = None

    def get_features(self):
        for i in self.graph_.customer_list:
            self.customer_x.append(self.graph_.vertex_dict[i].x_coord)
            self.customer_y.append(self.graph_.vertex_dict[i].y_coord)

            self.time_tables.append([self.graph_.vertex_dict[i].ready_time,
                                     self.graph_.vertex_dict[i].due_time])

        train_data = {
            'timestamp': self.time_tables,
            'x_coord': self.customer_x,
            'y_coord': self.customer_y,
        }

        self.train_df = pd.DataFrame(train_data)

    def start_cluster(self):

        kmeans = KMeans(
            n_clusters=self.graph_.ins.sate_num, random_state=0).fit(self.train_df[['x_coord', 'y_coord']]
                                                                 )

        # 获取每个点的簇标签
        self.labels = kmeans.labels_

        # 获取簇中心
        self.centroids = kmeans.cluster_centers_

        for i in range(self.graph_.ins.sate_num):
            sate_id = self.graph_.sate_list[i]

            new_vertex = Vertex(id_=sate_id,
                                ready_time=0,
                                due_time=1440,
                                x_coord=int(self.centroids[i, 0]),
                                y_coord=int(self.centroids[i, 1]))

            self.graph_.add_vertex(vertex=new_vertex)

            # add satellite as depot
            new_vertex_depot = deepcopy(new_vertex)

            # 更新 id 和 时间窗
            new_vertex_depot.id_ = self.graph_.sate_list[i] + self.graph_.ins.sate_num + self.graph_.customer_num
            new_vertex_depot.ready_time = self.graph_.vertex_dict[self.graph_.sate_list[i]].ready_time
            # new_vertex_depot.due_time = 1440

            self.graph_.add_vertex(vertex=new_vertex_depot)

            # if self.graph_.ins.is_select is True:
            #     for j in range(len(self.labels)):
            #         cus_id = self.graph_.ins.sate_num + 1 + j
            #
            #         self.graph_.cus_belong_sate[cus_id] = self.graph_.sate_list[self.labels[j]]
            #
            #         self.graph_.sate_serv_cus[self.graph_.sate_list[self.labels[j]]].append(cus_id)
            #
            #         # self.graph_.vertex_dict[self.graph_.sate_list[self.labels[j]]].demand +=
            #         self.graph_.vertex_dict[cus_id].demand
            #         self.graph_.vertex_dict[self.graph_.sate_list[self.labels[j]]].demand =
            #         self.graph_.ins.model_para.m_s

        for j in range(len(self.labels)):
            cus_id = self.graph_.ins.sate_num + 1 + j

            self.graph_.cus_belong_sate[cus_id] = self.graph_.sate_list[self.labels[j]]

            self.graph_.sate_serv_cus[self.graph_.sate_list[self.labels[j]]].append(cus_id)
            # self.graph_.vertex_dict[self.graph_.sate_list[self.labels[j]]].demand = self.graph_.ins.model_para.m_s

            self.graph_.vertex_dict[self.graph_.sate_list[self.labels[j]]].demand += self.graph_.vertex_dict[
                cus_id].demand

    def plot_map(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Arrow
        from matplotlib.patches import FancyArrowPatch

        od_o_x = []
        od_o_y = []

        od_d_x = []
        od_d_y = []

        for i in self.graph_.od_o_list:
            od_o_x.append(self.graph_.vertex_dict[i].x_coord)
            od_o_y.append(self.graph_.vertex_dict[i].y_coord)

            od_d_x.append(self.graph_.vertex_dict[self.graph_.o_to_d[i]].x_coord)
            od_d_y.append(self.graph_.vertex_dict[self.graph_.o_to_d[i]].y_coord)

        plt.scatter(od_o_x, od_o_y, cmap='viridis', c='yellow')
        plt.scatter(od_d_x, od_d_y, cmap='viridis', c='yellow')

        for task in range(self.graph_.ins.od_num):
            arrow_ = FancyArrowPatch((od_o_x[task], od_o_y[task]),
                                     (od_d_x[task], od_d_y[task]),
                                     arrowstyle='->', mutation_scale=10, color='y')

            # 将箭头添加到图形中
            plt.gca().add_patch(arrow_)

        # 可视化结果
        plt.scatter(self.train_df['x_coord'], self.train_df['y_coord'], c=self.labels, cmap='viridis')
        plt.scatter(self.centroids[:, 0], self.centroids[:, 1], s=300, c='red', marker='x')
        plt.title('K-Means Clustering with Time Window')
        plt.xlabel('x_coord')
        plt.ylabel('y_coord ')
        plt.show()