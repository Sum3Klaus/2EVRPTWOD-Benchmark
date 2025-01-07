# -*- coding: utf-8 -*-
# @Time     : 2024-08-11-21:49
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import time
import random
from copy import deepcopy
from math import *
import DualCalculatorNoSelect
import DualCalculator
import ModelBuilderNoSelect
import PricingModelBuilder
from AlnsPara import AlnsParameters
# from GreatDelugeAlgorithm import GreatDelugeAlgorithm
from GreatDelugeAlgorithmTolerance import *
from Common import *
from Route import *
from Solution import Sol
from RandomDestroy import RandomDestroy
from ShawDestroy import ShawDestroy
from WorseDestroy import WorseDestroy
from GreedyRepair import GreedyRepair
from RandomRepair import RandomRepair
from RegretRepair import RegretRepair
from WaitingDestroy import WaitingDestroy
from HistroyBasdDestroy import HistoryBasedDestroy
from ConflictDestroy import ConflictDestroy
from HistoricalArriveDestroy import HistoricalArriveDestroy
from DistanceRepair import DistanceRepair
from DualDestroy import DualDestroy
from DualRepair import DualRepair
from SlackTimeRepair import SlackTimeRepair
from TabuList import TabuList
import itertools


class GbaTsAlns(object):
    destroyList = [RandomDestroy, ShawDestroy, WorseDestroy, WaitingDestroy, HistoryBasedDestroy,
                   ConflictDestroy, HistoricalArriveDestroy, DualDestroy]
    repairList = [GreedyRepair, RandomRepair, RegretRepair, DistanceRepair, DualRepair, SlackTimeRepair]

    next_iter_time = itertools.count(start=0)

    def __init__(self,
                 ins,
                 is_tabu,
                 is_dual,
                 is_gda,
                 depots_dict,
                 level,
                 params: AlnsParameters,
                 ini_sol,
                 target=None):
        """  """
        # self.iter_time = self.next_iter_time
        self.iter_time = 0

        self.ins = ins
        self.params = params
        self.depots_dict = depots_dict
        self.is_dual = is_dual
        self.is_tabu = is_tabu
        self.is_gda = is_gda
        self.level = level
        self.target = target

        self.best_sol = ini_sol
        self.best_sol.calc_carbon_cost()

        self.history_best_obj = []

        if is_dual:
            self.destroyList = [RandomDestroy, ShawDestroy, WorseDestroy, WaitingDestroy, HistoryBasedDestroy,
                                ConflictDestroy, HistoricalArriveDestroy, DualDestroy]
            # self.repairList = [GreedyRepair, RandomRepair, RegretRepair, DistanceRepair, DualRepair, SlackTimeRepair]
            self.repairList = [GreedyRepair, RandomRepair, RegretRepair, DistanceRepair, SlackTimeRepair, DualRepair]
        else:
            self.destroyList = [RandomDestroy, ShawDestroy, WorseDestroy]
            self.repairList = [GreedyRepair, RandomRepair, RegretRepair]
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
        self.gda = GreatDelugeAlgorithm(alns=self,
                                        alpha=self.params.gda_alpha,
                                        rain_speed=self.params.gba_rain_speed)

        # Dual value
        self.model_builder = PricingModelBuilder.ModelBuilder(alns=self)
        self.cg = DualCalculator.DualCalculator(alns=self)

        self.Duals = None  # {i: 0 for i in self.ins.alns_dict[target]} # vehicle constraints dual

        # routes record
        self.route_records = set()
        self.route_list_records = set()
        self.add_ini_routes()

        self.best_iterTimes = 0  # 最优解出现时的迭代次数
        self.best_runTime = 0  # 最优解出现时的计算时间
        self.total_runtime = 0
        self.total_iterTimes = self.params.pu * self.params.epochs

        # Tabu Search
        self.TabuListD = []  # 存放 removal tabu
        self.TabuListR = []  # 存放 insert tabu

        # Carbon cost and Vehicle cost and Travel cost
        self.cost_travel = 0
        self.cost_carbon = 0
        self.cost_vehicle = 0

    def calc_costs(self):
        self.cost_vehicle = self.ins.model_para.vehicle_2_cost * len(self.best_sol.routes)
        self.cost_travel = self.best_sol.totalCost - self.cost_vehicle

        self.cost_carbon = self.ins.model_para.c_p * (
                (self.cost_travel * self.ins.model_para.rho_2 * self.ins.model_para.c_r) * self.ins.model_para.phi
                - self.ins.model_para.Q_q_2
        )

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

    def depot_start_select(self,
                           route):
        best_depot_start = None
        best_distance = float('inf')

        for depot_start, depot_end in self.depots_dict.items():

            cur_distance = self.ins.graph.arc_dict[depot_start, route.route_list[0]].distance + self.ins.graph.arc_dict[
                route.route_list[-1], depot_end].distance

            if cur_distance < best_distance:
                best_depot_start = depot_start
                best_distance = cur_distance

        return best_depot_start

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

    def calc_latest_time_table(self,
                               route):
        """ 计算最晚开始时间表，然后计算 slack time """
        latest_time_table = deepcopy(route.timeTable)

        cur_id = len(route.route) - 1
        latest_time_table[cur_id] = route.route[-1].due_time
        pre_id = cur_id - 1

        while pre_id != 0:
            cur_distance = self.ins.graph.arc_dict[(route.route[pre_id].id_, route.route[cur_id].id_)].distance

            start_time_pre = min(latest_time_table[cur_id] - cur_distance - self.ins.model_para.service_time,
                                 route.route[pre_id].due_time)

            if start_time_pre < route.route[pre_id].ready_time:
                start_time_pre = route.route[pre_id].ready_time

            latest_time_table[pre_id] = start_time_pre

            cur_id -= 1
            pre_id = cur_id - 1

        return latest_time_table

    @staticmethod
    def print_result(sol,
                     epoch,
                     iteration):

        # now_time = time.time()
        print('********** epoch: No.%5s - %5s iteration time **********' % (epoch, iteration))
        print(f'Total Cost = {sol.totalCost} \n routes: {sol.routes}')
        # print("ALNS_time:", now_time - start_time)

    def get_remove_num(self,
                       op_id):
        """
        0: RandomDestroy,
        1: ShawDestroy,
        2: WorseDestroy,
        3: WaitingDestroy,
        4: DistanceDestroy,
        5: ConflictDestroy,
        6: HistoricalArriveDestroy,
        7: DualDestroy
        """
        if op_id == 1:
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

        max_remove_num = min(self.ins.graph.customer_num, 25)

        return destroy_num

    def split_route(self,
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
                best_sate = self.depot_start_select(route=new_route)
                best_sate_return = self.ins.graph.sate_to_depot[best_sate]
                # 更新路径信息
                new_route.input_start_and_return(ins=self.ins,
                                                 vertex_start=self.ins.graph.vertex_dict[best_sate],
                                                 vertex_return=self.ins.graph.vertex_dict[best_sate_return]
                                                 )
                new_route.cost += self.fixed_cost
                # add route into sol
                sol.add_route_into_sol(new_route)

                # 生成新路径
                new_route = self.gen_new_route_depot_select(vertex=cur_vertex)
                ver_assigned.append(cur_vertex)
                ver_index += 1

            if len(ver_assigned) == len(vertex_sequence):
                # 选择 最近的 sate
                best_sate = self.depot_start_select(route=new_route)
                best_sate_return = self.ins.graph.sate_to_depot[best_sate]
                # 更新路径信息
                new_route.input_start_and_return(ins=self.ins,
                                                 vertex_start=self.ins.graph.vertex_dict[best_sate],
                                                 vertex_return=self.ins.graph.vertex_dict[best_sate_return]
                                                 )
                new_route.cost += self.fixed_cost
                # add route into sol
                sol.add_route_into_sol(new_route)

                sol.calc_carbon_cost()
                return sol

        sol.calc_carbon_cost()
        return sol

    def operator_is_allowed(self,
                            vertex_id_sequence,
                            remove_num,
                            op_id,
                            destroy_or_repair):
        """ """
        # 不执行tabu过程
        if self.is_tabu is False:
            return True

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

        # self.params.random_destroy_min = self.params.random_destroy_min * update_rate
        # self.params.random_destroy_max = self.params.random_destroy_max * update_rate

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

    def run(self):
        """
        需要设置可接受的范围，GBA
        pu 也需要变化，因为到求解的后期，可能会长时间遇到不更新解的情况，在这个情况下可能会出现算子得分不好的情况，导致算子的选择
        在 sol_no_change_times 超过一定次数后，可以尝试强制执行一个 dual 破坏
        """
        self.next_iter_time = itertools.count(start=0)

        print('*' * 100)
        sol = self.best_sol

        self.iter_time = 0
        no_improvement_count = 0
        # algorithm_time = 0

        # while (self.iter_time < (self.params.epochs * self.params.pu)) and (
        #         self.total_runtime < self.params.max_compute_time) and (
        #         no_improvement_count < self.params.max_no_improve_iter):
        for epoch in range(self.params.epochs):

            self.reset_score()  # reset

            for iter_time in range(self.params.pu):

                if (self.iter_time < (self.params.epochs * self.params.pu)) and (
                        self.total_runtime < self.params.max_compute_time) and (
                        no_improvement_count < self.params.max_no_improve_iter):

                    # self.iter_time = next(self.next_iter_time)
                    self.iter_time += 1
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

                    # create new repair tabu
                    new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                                               op_id=repair_id,
                                               remove_num=remove_num,
                                               destroy_or_repair='R')
                    self.TabuListR.append(new_repair_tabu)

                    repair_op = self.repairList[repair_id]

                    # Do repair
                    new_vertex_sequence = repair_op.do_repair(unassigned_list=remove_list,
                                                              assigned_list=destroy_vertex_sequence,
                                                              alns_model=self)

                    self.destroy_select[destroy_id] += 1
                    self.repair_select[repair_id] += 1

                    new_sol = self.split_route(vertex_sequence=new_vertex_sequence)
                    end_time = time.time()

                    # for route in new_sol.routes:
                    #     self.route_records.add(route)
                    #     self.route_list_records.add(tuple(route.route_list))

                    if new_sol.totalCost + new_sol.carbon_cost < sol.totalCost + sol.carbon_cost:
                        # 优于当前解
                        sol = new_sol
                        no_improvement_count = 0

                        for route in new_sol.routes:
                            self.route_records.add(route)
                            self.route_list_records.add(tuple(route.route_list))

                        # # create new repair tabu
                        # new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                        #                            op_id=repair_id,
                        #                            remove_num=remove_num,
                        #                            destroy_or_repair='R')
                        # self.TabuListR.append(new_repair_tabu)

                        if new_sol.totalCost + new_sol.carbon_cost < self.best_sol.totalCost + self.best_sol.carbon_cost:
                            # 优于历史最优
                            self.best_sol = new_sol
                            self.best_cus_arrive_time = new_sol.cus_arriveTime
                            self.destroy_score[destroy_id] += self.params.rank_1
                            self.repair_score[repair_id] += self.params.rank_1

                            self.best_runTime = self.total_runtime + (end_time - start_time)
                            self.best_iterTimes = int(self.iter_time)

                            self.gda.adjust_rain_speed(situation=2)

                        else:
                            # 优于当前，差于最优
                            self.destroy_score[destroy_id] += self.params.rank_2
                            self.repair_score[repair_id] += self.params.rank_2

                    elif self.is_gda is True:
                        if self.gda.if_accept(sol=sol):
                            # 小于水位，接受当前解
                            sol = new_sol
                            self.destroy_score[destroy_id] += self.params.rank_3
                            self.repair_score[repair_id] += self.params.rank_3

                            no_improvement_count += 1
                        else:
                            no_improvement_count += 1
                            pass

                    else:
                        no_improvement_count += 1
                        self.destroy_score[destroy_id] += self.params.rank_4
                        self.repair_score[repair_id] += self.params.rank_4

                    self.gda.iter_update_params()
                    self.print_result(epoch=epoch,
                                      iteration=iter_time,
                                      sol=sol)
                    # algorithm_time += (end_time - start_time)
                    self.total_runtime += (end_time - start_time)
                    print(f'time using: {self.total_runtime}s')

                    self.history_best_obj.append(self.best_sol.totalCost)

                    # 更新 tabu 的解禁忌次数
                    self.tabu_iteration_update()

                    """
                    判断解没有更新的次数,
                    强制执行 dual destroy 次数 应该与 instance 的个数 和 难度相关
                    和 迭代的次数也相关
                    epoch 来控制
                    """
                    if self.is_dual:
                        if no_improvement_count > round(9 * log(epoch + 2)):
                            self.reset_operator_rate()
                            # self.gda.adjust_water_level()

                            # 减缓水位下降的速度
                            self.gda.adjust_rain_speed(situation=0)

                            # start_time = time.time()
                            # no_improvement_count = 0
                            #
                            # destroy_id = 6
                            # remove_num = self.get_remove_num(op_id=destroy_id)
                            # remove_num = remove_num if remove_num >= 2 else 2
                            #
                            # # create new removal tabu
                            # # new_removal_tabu = TabuList(vertex_id_sequence=sol.vertex_id_sequence,
                            # #                             op_id=destroy_id,
                            # #                             remove_num=remove_num,
                            # #                             destroy_or_repair='D')
                            # # self.TabuListD.append(new_removal_tabu)
                            #
                            # # Do destroy
                            # dual_destroy_op = DualDestroy
                            # (remove_list, remove_id_list,
                            #  destroy_vertex_sequence) = dual_destroy_op.gen_destroy(sol=sol,
                            #                                                         remove_num=remove_num,
                            #                                                         alns_model=self)
                            #
                            # repair_id = 4
                            # dual_repair_op = DualRepair
                            #
                            # # create new repair tabu
                            # # new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                            # #                            op_id=repair_id,
                            # #                            remove_num=remove_num,
                            # #                            destroy_or_repair='R')
                            # # self.TabuListR.append(new_repair_tabu)
                            #
                            # # Do repair
                            # new_vertex_sequence = dual_repair_op.do_repair(unassigned_list=remove_list,
                            #                                                assigned_list=destroy_vertex_sequence,
                            #                                                alns_model=self)
                            #
                            # # self.destroy_select[destroy_id] += 1
                            # # self.repair_select[repair_id] += 1
                            #
                            # new_sol = self.split_route(vertex_sequence=new_vertex_sequence)
                            # end_time = time.time()
                            #
                            # if new_sol.totalCost < sol.totalCost:
                            #     # 优于当前解
                            #     sol = new_sol
                            #     no_improvement_count = 0
                            #
                            #     for route in new_sol.routes:
                            #         self.route_records.add(route)
                            #         self.route_list_records.add(tuple(route.route_list))
                            #
                            #     # # create new repair tabu
                            #     # new_repair_tabu = TabuList(vertex_id_sequence=destroy_vertex_id_sequence,
                            #     #                            op_id=repair_id,
                            #     #                            remove_num=remove_num,
                            #     #                            destroy_or_repair='R')
                            #     # self.TabuListR.append(new_repair_tabu)
                            #
                            #     if new_sol.totalCost < self.best_sol.totalCost:
                            #         # 优于历史最优
                            #         self.best_sol = new_sol
                            #         self.best_cus_arrive_time = new_sol.cus_arriveTime
                            #         self.destroy_score[destroy_id] += self.params.rank_1
                            #         self.repair_score[repair_id] += self.params.rank_1
                            #
                            #         self.best_runTime = self.total_runtime + (end_time - start_time)
                            #         self.best_iterTimes = self.iter_time
                            #
                            #     else:
                            #         # 优于当前，差于最优
                            #         self.destroy_score[destroy_id] += self.params.rank_2
                            #         self.repair_score[repair_id] += self.params.rank_2
                            #
                            # elif self.is_gda is True:
                            #     if self.gda.if_accept(sol=sol):
                            #         # 小于水位，接受当前解
                            #         sol = new_sol
                            #         self.destroy_score[destroy_id] += self.params.rank_3
                            #         self.repair_score[repair_id] += self.params.rank_3
                            #
                            # else:
                            #     self.destroy_score[destroy_id] += self.params.rank_4
                            #     self.repair_score[repair_id] += self.params.rank_4
                            #
                            # self.print_result(epoch=epoch,
                            #                   iteration=iter_time,
                            #                   sol=sol)
                            # # algorithm_time += (end_time - start_time)
                            # self.total_runtime += (end_time - start_time)
                            # print(f'time using: {self.total_runtime}s')

                        else:

                            # 加速水位下降
                            self.gda.adjust_rain_speed(situation=1)

            print(f'destroy score: {self.destroy_score} | repair score: {self.repair_score}')
            self.update_weight()
            self.update_operator_rate()

        print('*' * 50, 'final solution', '*' * 50)
        print(f'Total Cost = {self.best_sol.totalCost} \n routes: {self.best_sol.routes}')

        print(self.history_best_obj)
        self.calc_costs()
