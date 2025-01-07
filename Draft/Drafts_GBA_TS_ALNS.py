# -*- coding: utf-8 -*-
# @Time     : 2024-08-06-10:58
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import time
import random
from math import *
import DualCalculatorNoSelect
import DualCalculator
import ModelBuilderNoSelect
import PricingModelBuilder
from AlnsPara import AlnsParameters
from GreatDelugeAlgorithm import GreatDelugeAlgorithm
from Common import *
from Solution import Sol
from RandomDestroy import RandomDestroy
from ShawDestroy import ShawDestroy
from WorseDestroy import WorseDestroy
from GreedyRepair import GreedyRepair
from RandomRepair import RandomRepair
from RegretRepair import RegretRepair
from WaitingDestroy import WaitingDestroy
from DistanceDestroy import DistanceDestroy
from ConflictDestroy import ConflictDestroy
from HistoricalArriveDestroy import HistoricalArriveDestroy
from DistanceRepair import DistanceRepair
from DualDestroy import DualDestroy
from DualRepair import DualRepair
from SlackTimeRepair import SlackTimeRepair
from TabuList import TabuList
import itertools


class GbaTsAlns(object):
    destroyList = [RandomDestroy, ShawDestroy, WorseDestroy, WaitingDestroy, DistanceDestroy,
                   ConflictDestroy, HistoricalArriveDestroy, DualDestroy]
    repairList = [GreedyRepair, RandomRepair, RegretRepair, DistanceRepair, DualRepair, SlackTimeRepair]

    next_iter_time = itertools.count(start=0)

    def __init__(self,
                 ins,
                 is_select,
                 depots_dict,
                 level,
                 params: AlnsParameters,
                 ini_sol):
        """  """
        self.iter_time = 0

        self.ins = ins
        self.params = params
        self.depots_dict = depots_dict
        self.is_select = is_select
        self.level = level

        self.best_sol = ini_sol
        self.history_best_obj = []

        self.destroyList = [RandomDestroy, ShawDestroy, WorseDestroy, WaitingDestroy, DistanceDestroy,
                            ConflictDestroy, HistoricalArriveDestroy, DualDestroy]
        self.repairList = [GreedyRepair, RandomRepair, RegretRepair, DistanceRepair, DualRepair, SlackTimeRepair]
        self.des_num = len(self.destroyList)
        self.rep_num = len(self.repairList)

        # destroy operators rank
        self.destroy_weight = np.ones(self.des_num) * 10  # ## d_weight
        self.destroy_select = np.zeros(self.des_num)  # ## d_select    choose times
        self.destroy_score = np.zeros(self.des_num)  # ## d_score

        self.destroy_history_select = np.zeros(self.des_num)  # ## d_history_select
        self.destroy_history_score = np.zeros(self.des_num)  # ## d_history_score

        # repair operators rank
        self.repair_weight = np.ones(self.rep_num) * 10  # ## r_weight
        self.repair_select = np.zeros(self.rep_num)  # ## r_select
        self.repair_score = np.zeros(self.rep_num)  # ## r_score
        self.repair_history_select = np.zeros(self.rep_num)  # ## r_history_select
        self.repair_history_score = np.zeros(self.rep_num)  # ## r_history_score

        self.fixed_cost = self.ins.model_para.vehicle_2_cost if level == 2 else self.ins.model_para.vehicle_1_cost
        self.graph = self.ins.graph.second_echelon_graph if level == 2 else self.ins.graph.first_echelon_graph

        self.best_cus_arrive_time = self.best_sol.cus_arriveTime

        # The great deluge algorithm
        self.gda = GreatDelugeAlgorithm.GreatDelugeAlgorithm(alns_model=self)

        # Dual value
        if is_select is True:
            self.model_builder = PricingModelBuilder.ModelBuilder(alns=self)
            self.cg = DualCalculator.DualCalculator(alns=self)
        else:
            self.model_builder = ModelBuilderNoSelect.ModelBuilder(alns=self)
            self.cg = DualCalculatorNoSelect.DualCalculator(alns=self)
        self.Duals = None  # {i: 0 for i in self.ins.alns_dict[target]} # vehicle constraints dual

        # routes record
        self.route_records = set()
        self.route_list_records = set()
        self.add_ini_routes()

        # Tabu Search
        self.TabuListD = []  # 存放 removal tabu
        self.TabuListR = []  # 存放 insert tabu

    def add_ini_routes(self):
        for route in self.best_sol.routes:
            self.route_records.add(route)
            self.route_list_records.add(tuple(route.route_list))

    def gen_new_route_depot_select(self,
                                   vertex):
        new_route = Route()
        new_route.insert_vertex(0, vertex=vertex)

        new_route.arriveTime[0] = new_route.timeTable[0] = vertex.ready_time
        new_route.cost += self.fixed_cost

        return new_route

    def gen_new_route_no_select(self,
                                depot_start):
        new_route = Route()
        new_route.set_sate_route(sate=depot_start)

        new_route.arriveTime[0] = new_route.timeTable[0] = self.ins.graph.vertex_dict[depot_start].ready_time
        new_route.cost += self.fixed_cost

        return new_route

    def sate_select(self,
                    route):
        best_sate = None
        best_distance = float('inf')

        for sate_id in self.ins.graph.sate_list:
            sate_depot = self.ins.graph.sate_to_depot[sate_id]

            cur_distance = self.ins.graph.arc_dict[sate_id, route.route_list[0]].distance + self.ins.graph.arc_dict[
                route.route_list[0], sate_depot].distance

            if cur_distance < best_distance:
                best_sate = sate_id
                best_distance = cur_distance

        return best_sate

    def select_destroy(self):
        """ """
        destroy_weight = self.destroy_weight
        destroy_cumsumprob = (destroy_weight / sum(destroy_weight)).cumsum()  # return axis sum
        destroy_cumsumprob -= np.random.rand()

        destroy_id = list(destroy_cumsumprob > 0).index(True)

        return destroy_id

    def select_repair(self):
        """ """
        repair_weight = self.repair_weight
        repair_cumsumprob = (repair_weight / sum(repair_weight)).cumsum()
        repair_cumsumprob -= np.random.rand()
        repair_id = list(repair_cumsumprob > 0).index(True)

        return repair_id

    def reset_score(self):
        self.destroy_select = np.zeros(self.des_num)
        self.destroy_score = np.zeros(self.des_num)

        self.repair_select = np.zeros(self.rep_num)
        self.repair_score = np.zeros(self.rep_num)

    def update_weight(self):
        # destroy
        for index in range(self.destroy_weight.shape[0]):
            if self.destroy_select[index] > 0:
                self.destroy_weight[index] = self.destroy_weight[index] * (1 - self.params.rho) + \
                                             self.params.rho * self.destroy_score[index] / self.destroy_select[index]
            else:
                # 未被选中降低
                self.destroy_weight[index] = self.destroy_weight[index] * (1 - self.params.rho)
        # repair
        for index in range(self.repair_weight.shape[0]):
            if self.repair_select[index] > 0:
                self.repair_weight[index] = self.repair_weight[index] * (1 - self.params.rho) + \
                                            self.params.rho * self.repair_score[index] / self.repair_select[index]
            else:
                self.repair_weight[index] = self.repair_weight[index] * (1 - self.params.rho)

        self.destroy_history_select = self.destroy_history_select + self.destroy_select
        self.destroy_history_score = self.destroy_history_score + self.destroy_score

        self.repair_history_select = self.repair_history_select + self.repair_select
        self.repair_history_score = self.repair_history_score + self.repair_score

    def print_result(self,
                     epoch,
                     iteration):

        # now_time = time.time()
        print('********** epoch: No.%5s - %5s iteration time **********' % (epoch, iteration))
        print(f'Total Cost = {self.best_sol.totalCost} \n routes: {self.best_sol.routes}')
        # print("ALNS_time:", now_time - start_time)

    def get_remove_num(self,
                       op_id):
        """ """
        if op_id == 0:
            destroy_rate = random.uniform(self.params.random_destroy_min, self.params.random_destroy_max)

        elif op_id == 1:
            destroy_rate = random.uniform(self.params.worst_destroy_min, self.params.worst_destroy_max)

        elif op_id == 2:
            destroy_rate = random.uniform(self.params.worst_destroy_min, self.params.worst_destroy_max)

        elif op_id == 6:
            destroy_rate = random.uniform(self.params.dual_destroy_min, self.params.dual_destroy_max)

        else:
            destroy_rate = random.uniform(self.params.common_destroy_min, self.params.common_destroy_max)

        destroy_num = math.floor(destroy_rate * len(self.best_sol.vertex_sequence))
        destroy_num = destroy_num if destroy_num >= 1 else 1

        if destroy_num == len(self.best_sol.vertex_sequence):
            destroy_num -= 2

        return destroy_num

    def split_route_depot_select(self,
                                 vertex_sequence):

        ver_index = 0
        sol = Sol(ins=self.ins)
        ver_assigned = []

        cur_vertex = vertex_sequence[ver_index]
        new_route = self.gen_new_route_depot_select(vertex=cur_vertex)
        ver_assigned.append(cur_vertex)
        ver_index += 1

        while len(ver_assigned) != len(vertex_sequence):
            cur_vertex = vertex_sequence[ver_index]

            # 检查 时间窗 和 容量 约束
            # 满足则 add vertex into route
            if check_time_and_capacity(route=new_route,
                                       vertex=cur_vertex,
                                       ins=self.ins,
                                       level=self.level):
                new_route.add_vertex_into_route(vertex=cur_vertex,
                                                distance=self.graph.arc_dict[
                                                    (new_route.route[-1].id_, cur_vertex.id_)].distance,
                                                service_time=self.ins.model_para.service_time)
                ver_assigned.append(cur_vertex)
                ver_index += 1

            # 不满足 则选择 sate 并且更新 route info， 然后添加进入 sol
            else:
                # 选择 最近的 sate
                best_sate = self.sate_select(route=new_route)
                best_sate_return = self.ins.graph.sate_to_depot[best_sate]
                # 更新路径信息
                new_route.input_start_and_return(ins=self.ins,
                                                 vertex_start=self.ins.graph.vertex_dict[best_sate],
                                                 vertex_return=self.ins.graph.vertex_dict[best_sate_return]
                                                 )
                # add route into sol
                sol.add_route_into_sol(new_route)

                # 生成新路径
                new_route = self.gen_new_route_depot_select(vertex=cur_vertex)
                ver_assigned.append(cur_vertex)
                ver_index += 1

            if len(ver_assigned) == len(vertex_sequence):
                # 选择 最近的 sate
                best_sate = self.sate_select(route=new_route)
                best_sate_return = self.ins.graph.sate_to_depot[best_sate]
                # 更新路径信息
                new_route.input_start_and_return(ins=self.ins,
                                                 vertex_start=self.ins.graph.vertex_dict[best_sate],
                                                 vertex_return=self.ins.graph.vertex_dict[best_sate_return]
                                                 )
                # add route into sol
                sol.add_route_into_sol(new_route)

                return sol

        return sol

    def split_route_no_select(self,
                              depot_start,
                              depot_return,
                              vertex_sequence):

        ver_index = 0
        sol = Sol(ins=self.ins)
        ver_assigned = []

        new_route = self.gen_new_route_no_select(depot_start=depot_start)

        while len(ver_assigned) != len(vertex_sequence):
            cur_vertex = vertex_sequence[ver_index]

            if check_time_and_capacity(route=new_route,
                                       vertex=cur_vertex,
                                       ins=self.ins,
                                       level=self.level) and cur_vertex.id_ != depot_return:
                new_route.add_vertex_into_route(vertex=cur_vertex,
                                                distance=self.graph.arc_dict[
                                                    (new_route.route[-1].id_, cur_vertex.id_)].distance,
                                                service_time=self.ins.model_para.service_time)
                ver_assigned.append(cur_vertex)
                ver_index += 1

            else:
                new_route.add_vertex_into_route(vertex=self.ins.graph.vertex_dict[depot_return],
                                                distance=self.graph.arc_dict[
                                                    (new_route.route[-1].id_, depot_return)].distance,
                                                service_time=self.ins.model_para.service_time)

                sol.add_route_into_sol(new_route)

                new_route = self.gen_new_route_no_select(depot_start=depot_start)

            if len(ver_assigned) == len(vertex_sequence):
                new_route.add_vertex_into_route(vertex=cur_vertex,
                                                distance=self.graph.arc_dict[
                                                    (new_route.route[-1].id_, cur_vertex.id_)].distance,
                                                service_time=self.ins.model_para.service_time)

                sol.add_route_into_sol(new_route)

                return sol

        return sol

    def operator_is_allowed(self,
                            vertex_id_sequence,
                            remove_num,
                            op_id,
                            destroy_or_repair):
        """ """
        if len(self.TabuListD) < 1:
            # 没有 removal tabu
            return True

        if destroy_or_repair == 'D':
            # return not, 因为在禁忌表中存在，就不允许执行，所以需要加上 not
            return not self.tabu_contains(tabu_list=self.TabuListD,
                                          flitter=lambda x: x.check_is_in_tabu(vertex_id_sequence,
                                                                               op_id,
                                                                               remove_num))
        elif destroy_or_repair == 'R':

            return not self.tabu_contains(tabu_list=self.TabuListR,
                                          flitter=lambda x: x.check_is_in_tabu(vertex_id_sequence,
                                                                               op_id,
                                                                               remove_num))

    def tabu_iteration_update(self):

        for tabu_d in self.TabuListD:
            if tabu_d.check_tabu_iteration() < 0:

                self.TabuListD.remove(tabu_d)

        for tabu_r in self.TabuListR:
            if tabu_r.check_tabu_iteration() < 0:
                self.TabuListR.remove(tabu_r)

    def reset_operator_rate(self):
        """
        在迭代后期，可以适当增加破坏操作的程度，例如每次破坏更多的客户节点。这有助于探索更大的解空间，
        从而增加找到更优解的可能性。
        :return:
        """
        self.params.random_destroy_max = 0.5

        self.params.worst_destroy_max = 0.4

        self.params.shaw_destroy_max = 0.4

        self.params.common_destroy_max = 0.45

        self.params.dual_destroy_max = 0.4

        self.params.regret_n = round(len(self.best_sol.vertex_sequence) / 20) + 2

    def update_operator_rate(self):
        """
        在迭代过程中更新算子的概率
        iteration_sum = self.params.pu * self.params.epochs
        当前的次数： self.iter_time
        :return:
        """
        update_rate = 1 - (len(self.best_sol.vertex_sequence) / 10) / (self.params.pu * self.params.epochs)

        self.params.random_destroy_min = self.params.random_destroy_min * update_rate
        self.params.random_destroy_max = self.params.random_destroy_max * update_rate

        self.params.worst_destroy_min = self.params.worst_destroy_min * update_rate
        self.params.worst_destroy_max = self.params.worst_destroy_max * update_rate

        self.params.shaw_destroy_min = self.params.shaw_destroy_min * update_rate
        self.params.shaw_destroy_max = self.params.shaw_destroy_max * update_rate

        self.params.common_destroy_min = self.params.common_destroy_min * update_rate
        self.params.common_destroy_max = self.params.common_destroy_max * update_rate

        self.params.dual_destroy_min = self.params.dual_destroy_min * update_rate
        self.params.dual_destroy_max = self.params.dual_destroy_max * update_rate

        self.params.regret_n = self.params.regret_n * update_rate

        self.params.rank_3 = round(self.params.rank_3 * update_rate)

    @staticmethod
    def tabu_contains(tabu_list,
                      flitter):
        """

        :param tabu_list:
        :param flitter: a function, 过滤方法
        :return:
        """
        for tabu in tabu_list:
            if flitter(tabu):
                return True

        return False

    def run_depot_select(self):
        """
        需要设置可接受的范围，GBA
        pu 也需要变化，因为到求解的后期，可能会长时间遇到不更新解的情况，在这个情况下可能会出现算子得分不好的情况，导致算子的选择
        在 sol_no_change_times 超过一定次数后，可以尝试强制执行一个 dual 破坏
        """
        print('*' * 100)
        sol = self.best_sol

        sol_no_change_times = 0
        algorithm_time = 0
        for epoch in range(self.params.epochs):

            self.reset_score()  # reset

            for iter_time in range(self.params.pu):

                self.iter_time = next(self.next_iter_time)
                start_time = time.time()

                # destroy_id, repair_id = self.select_destroy_repair()
                destroy_id = self.select_destroy()
                remove_num = self.get_remove_num(op_id=destroy_id)
                remove_num = remove_num if remove_num >= 2 else 2

                # 判断是否接受算子
                if self.operator_is_allowed(vertex_id_sequence=sol.vertex_id_sequence,
                                            remove_num=remove_num,
                                            op_id=destroy_id,
                                            destroy_or_repair='D'):
                    # create new removal tabu
                    new_removal_tabu = TabuList(vertex_id_sequence=sol.vertex_id_sequence,
                                                op_id=destroy_id,
                                                remove_num=remove_num,
                                                destroy_or_repair='D')
                    self.TabuListD.append(new_removal_tabu)
                else:
                    while self.operator_is_allowed(vertex_id_sequence=sol.vertex_id_sequence,
                                                   remove_num=remove_num,
                                                   op_id=destroy_id,
                                                   destroy_or_repair='D'):
                        destroy_id = self.select_destroy()
                        remove_num = self.get_remove_num(op_id=destroy_id)

                    # create new removal tabu
                    new_removal_tabu = TabuList(vertex_id_sequence=sol.vertex_id_sequence,
                                                op_id=destroy_id,
                                                remove_num=remove_num,
                                                destroy_or_repair='D')
                    self.TabuListD.append(new_removal_tabu)

                destroy_op = self.destroyList[destroy_id]
                # Do destroy
                remove_list, remove_id_list, destroy_vertex_sequence = destroy_op.gen_destroy(sol=sol,
                                                                                              remove_num=remove_num,
                                                                                              alns_model=self)
                destroy_vertex_id_sequence = [i.id_ for i in destroy_vertex_sequence]
                repair_id = self.select_repair()
                # 判断是否接受算子
                if self.operator_is_allowed(vertex_id_sequence=destroy_vertex_id_sequence,
                                            remove_num=remove_num,
                                            op_id=repair_id,
                                            destroy_or_repair='R'):
                    pass
                else:

                    while self.operator_is_allowed(vertex_id_sequence=destroy_vertex_id_sequence,
                                                   remove_num=remove_num,
                                                   op_id=repair_id,
                                                   destroy_or_repair='R'):
                        repair_id = self.select_repair()

                repair_op = self.repairList[repair_id]

                # Do repair
                new_vertex_sequence = repair_op.do_repair(unassigned_list=remove_list,
                                                          assigned_list=destroy_vertex_sequence,
                                                          alns_model=self)

                self.destroy_select[destroy_id] += 1
                self.repair_select[repair_id] += 1

                new_sol = self.split_route_depot_select(vertex_sequence=new_vertex_sequence)
                end_time = time.time()

                # 将新的路径添加的记录中
                for route in new_sol.routes:
                    self.route_records.add(route)
                    self.route_list_records.add(route.route_list)

                # 判断解的质量
                if new_sol.totalCost < sol.totalCost:
                    # 优于当前解
                    sol = new_sol
                    sol_no_change_times = 0

                    # create new removal tabu
                    new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                                               op_id=repair_id,
                                               remove_num=remove_num,
                                               destroy_or_repair='R')
                    self.TabuListR.append(new_repair_tabu)

                    if new_sol.totalCost < self.best_sol.totalCost:
                        # 优于历史最优
                        self.best_sol = new_sol
                        self.best_cus_arrive_time = new_sol.cus_arriveTime
                        self.destroy_score[destroy_id] += self.params.rank_1
                        self.repair_score[repair_id] += self.params.rank_1

                    else:
                        # 优于当前，差于最优
                        self.destroy_score[destroy_id] += self.params.rank_2
                        self.repair_score[repair_id] += self.params.rank_2

                elif sol.totalCost < new_sol.totalCost <= self.gda.water_level:
                    # 小于水位，接受当前解
                    sol = new_sol
                    self.destroy_score[destroy_id] += self.params.rank_3
                    self.repair_score[repair_id] += self.params.rank_3

                else:
                    sol_no_change_times += 1

                self.gda.iter_update_params(sol=sol)
                self.print_result(epoch=epoch,
                                  iteration=iter_time)
                algorithm_time += (end_time - start_time)
                print(f'time using: {algorithm_time}s')

                self.history_best_obj.append(self.best_sol.totalCost)

                # 更新 tabu 的解禁忌次数
                self.tabu_iteration_update()

                # 更新 GBA 的参数，水位等
                self.gda.iter_update_params(sol=sol)
                self.print_result(epoch=epoch,
                                  iteration=iter_time)
                algorithm_time += (end_time - start_time)
                print(f'time using: {algorithm_time}s')

                self.history_best_obj.append(self.best_sol.totalCost)

                """
                判断解没有更新的次数,
                强制执行 dual destroy 次数 应该与 instance 的个数 和 难度相关
                和 迭代的次数也相关
                epoch 来控制
                """
                if sol_no_change_times > round(9 * log(epoch + 2)):
                    self.reset_operator_rate()

                    start_time = time.time()
                    sol_no_change_times = 0

                    destroy_id = 6
                    remove_num = self.get_remove_num(op_id=destroy_id)
                    remove_num = remove_num if remove_num >= 2 else 2

                    # create new removal tabu
                    new_removal_tabu = TabuList(vertex_id_sequence=sol.vertex_id_sequence,
                                                op_id=destroy_id,
                                                remove_num=remove_num,
                                                destroy_or_repair='D')
                    self.TabuListD.append(new_removal_tabu)

                    # Do destroy
                    remove_list, remove_id_list, destroy_vertex_sequence = destroy_op.gen_destroy(sol=sol,
                                                                                                  remove_num=remove_num,
                                                                                                  alns_model=self)

                    repair_id = 4
                    repair_op = self.repairList[repair_id]

                    # Do repair
                    new_vertex_sequence = repair_op.do_repair(unassigned_list=remove_list,
                                                              assigned_list=destroy_vertex_sequence,
                                                              alns_model=self)

                    self.destroy_select[destroy_id] += 1
                    self.repair_select[repair_id] += 1

                    new_sol = self.split_route_depot_select(vertex_sequence=new_vertex_sequence)
                    end_time = time.time()

                    if new_sol.totalCost < sol.totalCost:
                        # 优于当前解
                        sol = new_sol
                        sol_no_change_times = 0

                        for route in new_sol.routes:
                            self.route_records.add(route)
                            self.route_list_records.add(route.route_list)

                        # create new removal tabu
                        new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                                                   op_id=repair_id,
                                                   remove_num=remove_num,
                                                   destroy_or_repair='R')
                        self.TabuListR.append(new_repair_tabu)

                        if new_sol.totalCost < self.best_sol.totalCost:
                            # 优于历史最优
                            self.best_sol = new_sol
                            self.best_cus_arrive_time = new_sol.cus_arriveTime
                            self.destroy_score[destroy_id] += self.params.rank_1
                            self.repair_score[repair_id] += self.params.rank_1

                        else:
                            # 优于当前，差于最优
                            self.destroy_score[destroy_id] += self.params.rank_2
                            self.repair_score[repair_id] += self.params.rank_2

                    elif new_sol.totalCost <= self.gda.water_level:
                        # 小于水位，接受当前解
                        sol = new_sol
                        self.destroy_score[destroy_id] += self.params.rank_3
                        self.repair_score[repair_id] += self.params.rank_3

                    else:
                        sol_no_change_times += 1

                    self.print_result(epoch=epoch,
                                      iteration=iter_time)
                    algorithm_time += (end_time - start_time)
                    print(f'time using: {algorithm_time}s')

            print(f'destroy score: {self.destroy_score} | repair score: {self.repair_score}')
            self.update_weight()
            self.update_operator_rate()

        print('*' * 50, 'final solution', '*' * 50)
        print(f'Total Cost = {self.best_sol.totalCost} \n routes: {self.best_sol.routes}')

    def split_route(self,
                    vertex_sequence):
        if self.is_select is True:
            self.split_route_depot_select(vertex_sequence=vertex_sequence)

