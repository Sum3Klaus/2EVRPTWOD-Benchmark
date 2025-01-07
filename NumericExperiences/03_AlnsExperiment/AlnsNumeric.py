# -*- coding: utf-8 -*-
# @Time     : 2024-08-21-14:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import math

from AlgorithmFramework import *
from NumericInfo_Alns_IniInfo import *
import pandas as pd
import numpy as np
import datetime
import itertools
import os


def main():
    f = '../../Benchmarks/Solomn_VRP_benchmark/homberger_400_customer_instances/C1_4_1.TXT'
    f_bp = "../../Benchmarks/2evrp_instances(BandP)/Set2a_E-n22-k4-s6-17.dat"
    f_kc = "../../Benchmarks/2E_VRP-kancharla/dataset/Set2/E-n22-k4-s08-14.dat"

    # folder_path = '../../Benchmarks/2evrp_instances(BandP)'  # '../../Benchmarks/2E_VRP-kancharla/dataset/Set2'
    #  = '../../Benchmarks/2E_VRP-kancharla/dataset/Set2'
    """
    customer 21
    "../../Benchmarks/2E_VRP-kancharla/dataset/Set2"
    '../../Benchmarks/2E_VRP-kancharla/result/Set2/02-Jan-2016_1_300_'
    
    customer 50
    "../../Benchmarks/2E_VRP-kancharla/dataset/Set4"
    '../../Benchmarks/2E_VRP-kancharla/result/Set4/04-Jan-2016_1_50_1000'
    
    
    Gonzale Perboli Tadei Vigo
    "../../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Benchmark/set2b"
    "../../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Result/2b"
    """
    folder_path = "../../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Benchmark/set3"
    result_path_pre_str = "../../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Result/3/"
    # set4  04-Jan-2016_1_50_1000
    # set3 02-Jan-2016_1_300_
    # 初始化已读取的文件计数器
    files_read = 0
    numeric_info = None
    file_path = None

    for filename in os.listdir(folder_path):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        print(file_path)

        filename_str = filename.split('.')
        # if files_read < 6:
        #     tail_str = '.pif'
        # else:
        #     tail_str = '.psf'

        result_path = result_path_pre_str + filename + '.psf'
        cur_alg = None

        if files_read < 100:
            # 确保是文件而不是文件夹

            model_info = {"files": {0: f, 1: file_path, 2: file_path, 3: file_path},
                          'benchmark_id': 3,
                          "file_name": file_path,
                          "random_seed": 3407,
                          'satellite_num': 2,
                          'customer_num': 10,
                          'od_num': 2,
                          'is_select': True,
                          'customer_extend_time': 0,
                          'od_extend_time': 0,
                          'is_calc_od': True,
                          'ini_sol_algorithm': 0,  # 0: greedy, 1: saving algorithm
                          'is_tabu': True,
                          'is_dual': True,
                          'is_gda': True,
                          'vehicle_num_1st': 3,
                          'vehicle_num_2nd': 5}

            if os.path.isfile(file_path):

                files_read += 1

                numeric_info = NumericInfo(f=file_path)

                # model_info['od_num'] = math.ceil(
                #         math.log(model_info['customer_num']) * 2 + ((model_info['customer_num'] - 20) / 5)
                # )

                # combinations = []

                combinations = [
                    [True, True, True], [False, True, True], [False, False, False]
                ]

                for combination in combinations:
                    for times in range(10):
                        # random_seed = combination[0]
                        is_dual = combination[0]
                        is_gda = combination[1]
                        is_tabu = combination[2]
                        # customer_extend_time = combination[4]
                        # od_extend_time = combination[5]
                        # ini_algorithm = combination[3]

                        numeric_info.update_model_algorithm_setting(model_info=model_info,
                                                                    is_select=True, ini_algorithm=0,
                                                                    is_tabu=is_tabu, is_dual=is_dual, is_gda=is_gda)
                        model_info['customer_extend_time'] = 0
                        model_info['od_extend_time'] = 0
                        random_seed = 42

                        np.random.seed(model_info['random_seed'])

                        alg = AlgorithmFramework(model_info=model_info)
                        # alg.build_instance()
                        alg.build_instance(is_input_result=True,
                                           result_selection=1,
                                           result_path=result_path,
                                           random_seed=model_info['random_seed'])
                        cur_alg = alg

                        # alg.ins.gen_od_task.get_customer_square()
                        # od_s = []
                        # for i in range(10):
                        #     origin_coord, destination_coord = alg.ins.gen_od_task.gen_od_origin_and_destination()
                        #     od_s.append([origin_coord, destination_coord])

                        # 加入时间窗
                        # arrive_time_dict = alg.ins.get_benchmark_result(result_path=result_path)
                        # alg.ins.set_time_window(arrive_time_dict=arrive_time_dict,
                        #                         random_seed=random_seed)
                        # """
                        alg.run()

                        # calc ini sol info
                        # 1st
                        ini_veh_1st = len(alg.ini_sol_1st.routes) * alg.ins.model_para.vehicle_1_cost
                        ini_tra_1st = alg.ini_sol_1st.totalCost - ini_veh_1st
                        ini_carbon_cost_1st = alg.ini_sol_1st.carbon_cost
                        # 2nd
                        ini_veh_2nd = len(alg.ini_sol.routes) * alg.ins.model_para.vehicle_2_cost
                        ini_tra_2nd = alg.ini_sol.totalCost - ini_veh_2nd
                        ini_carbon_cost_2nd = alg.ini_sol.carbon_cost

                        # 1st
                        if alg.grb_1st.model.status == GRB.OPTIMAL:
                            grb_1st_obj = alg.grb_1st.model.ObjVal
                            tra_cost_1st = alg.grb_1st.objs['1st travel cost'].getValue()
                            carbon_cost_1st = alg.grb_1st.objs['1st carbon cost'].getValue()
                            vehicle_cost_1st = alg.grb_1st.objs['1st vehicle cost'].getValue()
                        else:
                            grb_1st_obj = 0
                            tra_cost_1st = 0
                            carbon_cost_1st = 0
                            vehicle_cost_1st = 0

                        total_obj = (grb_1st_obj + alg.alns.cost_travel + alg.alns.cost_carbon + alg.alns.cost_vehicle +
                                     alg.ins.od_travel_compensation + len(
                                    alg.ins.customer_list_od) * alg.ins.model_para.compensation)
                        numeric_info.append_numeric_result(instance=file_path.split('\\')[-1],
                                                           cus_num=alg.ins.customer_num,
                                                           sate_num=alg.ins.sate_num,
                                                           od_num=model_info['od_num'],
                                                           random_seed=model_info['random_seed'],
                                                           is_select=True, is_od=True, algorithm=combination,
                                                           ini_algorithm=0,

                                                           ini_tra_1st=ini_tra_1st,
                                                           ini_veh_1st=ini_veh_1st,
                                                           ini_carbon_cost_1st=ini_carbon_cost_1st,
                                                           ini_tra_2nd=ini_tra_2nd,
                                                           ini_veh_2nd=ini_veh_2nd,
                                                           ini_carbon_cost_2nd=ini_carbon_cost_2nd,

                                                           is_dual=is_dual,
                                                           is_tabu=is_tabu,
                                                           is_gda=is_gda,
                                                           customer_extend_time=model_info['customer_extend_time'],
                                                           od_extend_time=model_info['od_extend_time'],
                                                           runtime=alg.alns.total_runtime,
                                                           total_obj=total_obj,
                                                           ub=total_obj, lb=total_obj,
                                                           tra_cost_1st=tra_cost_1st,
                                                           carbon_cost_1st=carbon_cost_1st,
                                                           vehicle_cost_1st=vehicle_cost_1st,
                                                           routes_1st=alg.best_sol_1st.routes,
                                                           tra_cost_2nd=alg.alns.cost_travel,
                                                           carbon_cost_2nd=alg.alns.cost_carbon,
                                                           vehicle_cost_2nd=alg.alns.cost_vehicle,
                                                           routes_2nd=alg.alns.best_sol.routes,
                                                           tra_cost_od=alg.ins.od_travel_compensation,
                                                           compensation_od=len(alg.ins.customer_list_od) *
                                                                           alg.ins.model_para.compensation,
                                                           od_match=alg.iter_hungarian.od_ser_cus,
                                                           best_iter_times=alg.alns.best_iterTimes,
                                                           total_runtime=alg.alns.total_runtime,
                                                           best_runtime=alg.alns.best_runTime,
                                                           total_iter_times=alg.alns.total_iterTimes)
                        # """

                    # 添加空行，方便计算实验
                    numeric_info.append_numeric_result(instance=None, cus_num=None, sate_num=None, od_num=None,
                                                       random_seed=None, is_select=None, is_od=None, algorithm=None,
                                                       ini_algorithm=None, ini_tra_1st=None,
                                                       ini_veh_1st=None,
                                                       ini_carbon_cost_1st=None,
                                                       ini_tra_2nd=None,
                                                       ini_veh_2nd=None,
                                                       ini_carbon_cost_2nd=None,
                                                       is_dual=None, is_tabu=None,
                                                       is_gda=None, customer_extend_time=None, od_extend_time=None,
                                                       runtime=None, total_obj=None, ub=None, lb=None,
                                                       tra_cost_1st=None,
                                                       carbon_cost_1st=None, vehicle_cost_1st=None, routes_1st=None,
                                                       tra_cost_2nd=None, carbon_cost_2nd=None, vehicle_cost_2nd=None,
                                                       routes_2nd=None, tra_cost_od=None, compensation_od=None,
                                                       od_match=None, best_iter_times=None, total_runtime=None,
                                                       best_runtime=None, total_iter_times=None)

            # '''
            """ 先输出 alns 结果 """
            """ Gurobi """
            file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}' + file_path.split('\\')[
                -1] + f'1500iter(30x50)_GPTV_ALNS_3407' + '.xlsx'
            algorithm_results_df = pd.DataFrame(numeric_info.algorithm_results)
            algorithm_results_df.to_excel(file_name, index=False)

            # 如果已经读取了15个文件，就中断循环
            # if files_read >= 3:
            #     break
            
            """求解 Gurobi Model"""
            model_info['customer_extend_time'] = 0
            model_info['od_extend_time'] = 0
            random_seed = model_info['random_seed']

            np.random.seed(random_seed)

            alg = AlgorithmFramework(model_info=model_info)
            # alg.build_instance()
            alg.build_instance(is_input_result=True,
                               result_selection=1,
                               result_path=result_path,
                               random_seed=model_info['random_seed'])
            alg.solve_gurobi_model()
            if alg.grb_model.model.status == GRB.OPTIMAL:
                numeric_info.append_numeric_result(instance=file_path.split('\\')[-1], cus_num=alg.ins.customer_num,
                                                   # sate_num=model_info['satellite_num'],
                                                   sate_num=alg.ins.sate_num,
                                                   od_num=model_info['od_num'], random_seed=random_seed,
                                                   is_select=True, is_od=True, algorithm='Gurobi',
                                                   ini_algorithm='/',
                                                   ini_tra_1st='/',
                                                   ini_veh_1st='/',
                                                   ini_carbon_cost_1st='/',
                                                   ini_tra_2nd='/',
                                                   ini_veh_2nd='/',
                                                   ini_carbon_cost_2nd='/',
                                                   is_dual='/', is_tabu='/', is_gda='/',
                                                   customer_extend_time=model_info['customer_extend_time'],
                                                   od_extend_time=model_info['od_extend_time'],
                                                   runtime=alg.grb_model.model.Runtime,
                                                   total_obj=alg.grb_model.model.ObjVal,
                                                   ub=alg.grb_model.model.ObjVal,
                                                   lb=alg.grb_model.model.objBound,
                                                   tra_cost_1st=alg.grb_model.objs['1st travel cost'].getValue(),
                                                   carbon_cost_1st=alg.grb_model.objs['1st carbon cost'].getValue(),
                                                   vehicle_cost_1st=alg.grb_model.objs[
                                                       '1st vehicle cost'].getValue(),
                                                   routes_1st=alg.grb_model_routes_1st,
                                                   tra_cost_2nd=alg.grb_model.objs['2nd travel cost'].getValue(),
                                                   carbon_cost_2nd=alg.grb_model.objs['2nd carbon cost'].getValue(),
                                                   vehicle_cost_2nd=alg.grb_model.objs[
                                                       '2nd vehicle cost'].getValue(),
                                                   routes_2nd=alg.grb_model_routes_2nd,
                                                   tra_cost_od=alg.grb_model.objs['od travel cost'].getValue(),
                                                   compensation_od=alg.grb_model.objs[
                                                       'od compensation cost'].getValue(),
                                                   od_match=alg.grb_model.od_info, best_iter_times=None,
                                                   total_runtime=None,
                                                   best_runtime=None, total_iter_times=None)

            elif alg.grb_model.model.status == GRB.TIME_LIMIT:
                if alg.grb_model.model.SolCount > 0:
                    numeric_info.append_numeric_result(instance=file_path.split('\\')[-1], cus_num=alg.ins.customer_num,
                                                       # sate_num=model_info['satellite_num'],
                                                       sate_num=alg.ins.sate_num,
                                                       od_num=model_info['od_num'], random_seed=random_seed,
                                                       is_select=True, is_od=True, algorithm='Gurobi',
                                                       ini_algorithm='/',
                                                       ini_tra_1st='/',
                                                       ini_veh_1st='/',
                                                       ini_carbon_cost_1st='/',
                                                       ini_tra_2nd='/',
                                                       ini_veh_2nd='/',
                                                       ini_carbon_cost_2nd='/',
                                                       is_dual='/', is_tabu='/', is_gda='/',
                                                       customer_extend_time=model_info['customer_extend_time'],
                                                       od_extend_time=model_info['od_extend_time'],
                                                       runtime=alg.grb_model.model.Runtime,
                                                       total_obj=alg.grb_model.model.ObjVal,
                                                       ub=alg.grb_model.model.ObjVal,
                                                       lb=alg.grb_model.model.objBound,
                                                       tra_cost_1st=alg.grb_model.objs['1st travel cost'].getValue(),
                                                       carbon_cost_1st=alg.grb_model.objs['1st carbon cost'].getValue(),
                                                       vehicle_cost_1st=alg.grb_model.objs[
                                                           '1st vehicle cost'].getValue(),
                                                       routes_1st=alg.grb_model_routes_1st,
                                                       tra_cost_2nd=alg.grb_model.objs['2nd travel cost'].getValue(),
                                                       carbon_cost_2nd=alg.grb_model.objs['2nd carbon cost'].getValue(),
                                                       vehicle_cost_2nd=alg.grb_model.objs[
                                                           '2nd vehicle cost'].getValue(),
                                                       routes_2nd=alg.grb_model_routes_2nd,
                                                       tra_cost_od=alg.grb_model.objs['od travel cost'].getValue(),
                                                       compensation_od=alg.grb_model.objs[
                                                           'od compensation cost'].getValue(),
                                                       od_match=alg.grb_model.od_info, best_iter_times=None,
                                                       total_runtime=None,
                                                       best_runtime=None, total_iter_times=None)

                else:
                    numeric_info.append_numeric_result(instance='/', cus_num='/', sate_num='/', od_num='/',
                                                       random_seed='/', is_select='/', is_od='/', algorithm='/',
                                                       ini_algorithm='/',
                                                       ini_tra_1st='/',
                                                       ini_veh_1st='/',
                                                       ini_carbon_cost_1st='/',
                                                       ini_tra_2nd='/',
                                                       ini_veh_2nd='/',
                                                       ini_carbon_cost_2nd='/',
                                                       is_dual='/', is_tabu='/',
                                                       is_gda='/', customer_extend_time='/', od_extend_time='/',
                                                       runtime='/', total_obj='/', ub='/', lb='/',
                                                       tra_cost_1st='/',
                                                       carbon_cost_1st='/', vehicle_cost_1st='/', routes_1st='/',
                                                       tra_cost_2nd='/', carbon_cost_2nd='/', vehicle_cost_2nd='/',
                                                       routes_2nd='/', tra_cost_od='/', compensation_od='/',
                                                       od_match='/', best_iter_times='/', total_runtime='/',
                                                       best_runtime='/', total_iter_times='/')
            else:
                numeric_info.append_numeric_result(instance='/', cus_num='/', sate_num='/', od_num='/',
                                                   random_seed='/', is_select='/', is_od='/', algorithm='/',
                                                   ini_algorithm='/', ini_tra_1st='/',
                                                   ini_veh_1st='/',
                                                   ini_carbon_cost_1st='/',
                                                   ini_tra_2nd='/',
                                                   ini_veh_2nd='/',
                                                   ini_carbon_cost_2nd='/',
                                                   is_dual='/', is_tabu='/',
                                                   is_gda='/', customer_extend_time='/', od_extend_time='/',
                                                   runtime='/', total_obj='/', ub='/', lb='/',
                                                   tra_cost_1st='/',
                                                   carbon_cost_1st='/', vehicle_cost_1st='/', routes_1st='/',
                                                   tra_cost_2nd='/', carbon_cost_2nd='/', vehicle_cost_2nd='/',
                                                   routes_2nd='/', tra_cost_od='/', compensation_od='/',
                                                   od_match='/', best_iter_times='/', total_runtime='/',
                                                   best_runtime='/', total_iter_times='/')
            # '''

        """ 输出benchmark """
        # 'OD task id, capacity, origin id, x_coord,
        # y_coord, ready time, due time, destination id, x_coord, y_coord, ready time, due time'
        source_file = file_path  # 目标文件名
        new_benchmark_file = filename_str[0] + '_od_tw.txt'
        # 读取源文 件内容
        with open(source_file, 'r', encoding='utf-8') as src:
            content = src.read()
        # 将内容写入目标文件，并在后面追加新内容
        with open(new_benchmark_file, 'a', encoding='utf-8') as dest:
            dest.write(content)  # 写入源文件的内容
            dest.write('!----------------------------------------------------------------\n')
            dest.write('!Customer id, ready time, due time\n')
            for i in cur_alg.ins.graph.customer_list:
                cus_id = i
                cus_ready_time = cur_alg.ins.graph.vertex_dict[i].ready_time
                cus_due_time = cur_alg.ins.graph.vertex_dict[i].due_time
                dest.write(f'({cus_id},{cus_ready_time},{cus_due_time}), ')
            dest.write('\n!----------------------------------------------------------------\n')

            dest.write(f'!OD capacity: {cur_alg.ins.model_para.vehicle_od_capacity}\n')
            dest.write('!----------------------------------------------------------------\n')

            dest.write(
                '!Task id, origin id, x_coord, y_coord, ready time, due time, terminate id, x_coord, y_coord, ready time, due time\n')
            for task in cur_alg.ins.graph.od_task_dict:
                task_id = task
                # origin = alg.ins.graph.od_task_dict[task_id].origin_node
                # terminate = alg.ins.graph.od_task_dict[task_id].terminate_node
                o_id = cur_alg.ins.graph.od_task_dict[task_id].origin_node.id_
                o_x = cur_alg.ins.graph.od_task_dict[task_id].origin_node.x_coord
                o_y = cur_alg.ins.graph.od_task_dict[task_id].origin_node.y_coord
                o_ready_time = cur_alg.ins.graph.od_task_dict[task_id].origin_node.ready_time
                o_due_time = cur_alg.ins.graph.od_task_dict[task_id].origin_node.due_time

                d_id = cur_alg.ins.graph.od_task_dict[task_id].terminate_node.id_
                d_x = cur_alg.ins.graph.od_task_dict[task_id].terminate_node.x_coord
                d_y = cur_alg.ins.graph.od_task_dict[task_id].terminate_node.y_coord
                d_ready_time = cur_alg.ins.graph.od_task_dict[task_id].terminate_node.ready_time
                d_due_time = cur_alg.ins.graph.od_task_dict[task_id].terminate_node.due_time

                dest.write(
                    f'({task_id},{o_id},{o_x},{o_y},{o_ready_time},{o_due_time},{d_id},{d_x},{d_y},{d_ready_time},{d_due_time}), ')

        # _accept_insert
        """ ALNS """
        # file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}' + file_path.split('\\')[
        #     -1] + '24x25_Tabu_gda_operator_1000iter_kc_set2' + '.xlsx'
        """ Gurobi """
        file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}' + file_path.split('\\')[
            -1] + f'1500iter(30x50)_GPTV_ALNS_3407' + '.xlsx'
        algorithm_results_df = pd.DataFrame(numeric_info.algorithm_results)
        algorithm_results_df.to_excel(file_name, index=False)


if __name__ == '__main__':
    main()
