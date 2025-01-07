# -*- coding: utf-8 -*-
# @Time     : 2024-08-21-14:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from AlgorithmFramework import *
from NumericInfo_Alns import *
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
    """
    folder_path = "../../Benchmarks/2E_VRP-kancharla/dataset/Set4"
    result_path_pre_str = '../../Benchmarks/2E_VRP-kancharla/result/Set4/04-Jan-2016_1_50_1000'
    # 初始化已读取的文件计数器
    files_read = 0

    for filename in os.listdir(folder_path):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        result_path = result_path_pre_str + filename

        numeric_info = NumericInfo(f=file_path)

        if files_read < 3:
            # 确保是文件而不是文件夹
            if os.path.isfile(file_path):

                files_read += 1

                model_info = {"files": {0: f, 1: file_path, 2: file_path},
                              'benchmark_id': 2,
                              "file_name": file_path,
                              "random_seed": 3407,
                              'satellite_num': 2,
                              'customer_num': 10,
                              'od_num': 2,
                              'is_select': True,
                              'customer_extend_time': 100,
                              'od_extend_time': 50,
                              'is_calc_od': True,
                              'ini_sol_algorithm': 0,  # 0: greedy, 1: saving algorithm
                              'is_tabu': True,
                              'is_dual': True,
                              'is_gda': True,
                              'vehicle_num_1st': 3,
                              'vehicle_num_2nd': 5}

                combinations = list(itertools.product(numeric_info.is_dual,
                                                      numeric_info.is_gda,
                                                      numeric_info.is_tabu))

                alns_combinations = [
                    [True, True, True],
                    [False, False, False]
                ]
                for combination in alns_combinations:
                    for times in range(5):
                        # random_seed = combination[0]
                        # is_dual = combination[0]
                        # is_gda = combination[1]
                        # is_tabu = combination[2]
                        # customer_extend_time = combination[4]
                        # od_extend_time = combination[5]
                        # ini_algorithm = combination[3]
                        is_dual = combination[0]
                        is_gda = combination[1]
                        is_tabu = combination[2]

                        numeric_info.update_model_algorithm_setting(model_info=model_info,
                                                                    is_select=True, ini_algorithm=0,
                                                                    is_tabu=is_tabu, is_dual=is_dual, is_gda=is_gda)
                        model_info['customer_extend_time'] = 0
                        model_info['od_extend_time'] = 15
                        random_seed = 3407

                        np.random.seed(random_seed)

                        alg = AlgorithmFramework(model_info=model_info)
                        alg.build_instance()

                        # 加入时间窗
                        arrive_time_dict = alg.ins.get_benchmark_result(result_path=result_path)
                        alg.ins.set_time_window(arrive_time_dict=arrive_time_dict,
                                                random_seed=random_seed)

                        alg.run()

                        # 1st
                        if alg.grb_1st.model.status == GRB.OPTIMAL:
                            grb_1st_obj = alg.grb_1st.model.ObjVal
                            tra_cost_1st = alg.grb_1st.objs['1st carbon cost'].getValue()
                            carbon_cost_1st = alg.grb_1st.objs['1st carbon cost'].getValue()
                            vehicle_cost_1st = alg.grb_1st.objs['1st vehicle cost'].getValue()
                        else:
                            grb_1st_obj = 0
                            tra_cost_1st = 0
                            carbon_cost_1st = 0
                            vehicle_cost_1st = 0

                        numeric_info.append_numeric_result(instance=file_path.split('\\')[-1],
                                                           cus_num=alg.ins.customer_num,
                                                           sate_num=alg.ins.sate_num,
                                                           od_num=model_info['od_num'], random_seed=3407,
                                                           is_select=True, is_od=True, algorithm=combination,
                                                           ini_algorithm=0,
                                                           ini_obj=alg.ini_sol.totalCost, is_dual=is_dual,
                                                           is_tabu=is_tabu,
                                                           is_gda=is_gda,
                                                           customer_extend_time=model_info['customer_extend_time'],
                                                           od_extend_time=model_info['od_extend_time'],
                                                           runtime=alg.alns.total_runtime,
                                                           total_obj=grb_1st_obj + alg.alns.cost_travel +
                                                                     alg.alns.cost_carbon + alg.alns.cost_vehicle +
                                                                     alg.ins.od_travel_compensation + len(
                                                               alg.ins.customer_list_od) * alg.ins.model_para.compensation,
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

                        """求解 Gurobi Model"""
                        # alg.solve_gurobi_model()
                        # # numeric_info.append_numeric_result(instance=f.split('\\')[-1],
                        #                                    cus_num=alg.ins.customer_num,
                        #                                    sate_num=alg.ins.sate_num,
                        #                                    od_num=model_info['od_num'], random_seed=random_seed,
                        #                                    is_select=True, is_od=True, algorithm='Gurobi',
                        #                                    ini_algorithm='/',
                        #                                    ini_obj='/', is_dual='/', is_tabu='/', is_gda='/',
                        #                                    customer_extend_time=model_info['customer_extend_time'],
                        #                                    od_extend_time=model_info['od_extend_time'],
                        #                                    runtime=alg.grb_model.model.Runtime,
                        #                                    total_obj=alg.grb_model.model.ObjVal,
                        #                                    tra_cost_1st=alg.grb_model.objs['1st travel cost'].getValue(),
                        #                                    carbon_cost_1st=alg.grb_model.objs['1st carbon cost'].getValue(),
                        #                                    vehicle_cost_1st=alg.grb_model.objs[
                        #                                        '1st vehicle cost'].getValue(),
                        #                                    routes_1st=alg.grb_model_routes_1st,
                        #                                    tra_cost_2nd=alg.grb_model.objs['2nd travel cost'].getValue(),
                        #                                    carbon_cost_2nd=alg.grb_model.objs['2nd carbon cost'].getValue(),
                        #                                    vehicle_cost_2nd=alg.grb_model.objs[
                        #                                        '2nd vehicle cost'].getValue(),
                        #                                    routes_2nd=alg.grb_model_routes_2nd,
                        #                                    tra_cost_od=alg.grb_model.objs['od travel cost'].getValue(),
                        #                                    compensation_od=alg.grb_model.objs[
                        #                                        'od compensation cost'].getValue(),
                        #                                    od_match=alg.grb_model.od_info,
                        #                                    best_iter_times='/',
                        #                                    total_runtime='/',
                        #                                    best_runtime='/',
                        #                                    total_iter_times='/'
                        #                                    )

                    # 添加空行，方便计算实验
                    numeric_info.append_numeric_result(instance=None, cus_num=None, sate_num=None, od_num=None,
                                                       random_seed=None, is_select=None, is_od=None, algorithm=None,
                                                       ini_algorithm=None, ini_obj=None, is_dual=None, is_tabu=None,
                                                       is_gda=None, customer_extend_time=None, od_extend_time=None,
                                                       runtime=None, total_obj=None, tra_cost_1st=None,
                                                       carbon_cost_1st=None, vehicle_cost_1st=None, routes_1st=None,
                                                       tra_cost_2nd=None, carbon_cost_2nd=None, vehicle_cost_2nd=None,
                                                       routes_2nd=None, tra_cost_od=None, compensation_od=None,
                                                       od_match=None, best_iter_times=None, total_runtime=None,
                                                       best_runtime=None, total_iter_times=None)

                # 如果已经读取了15个文件，就中断循环
                # if files_read >= 3:
                #     break

        # _accept_insert
        file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}' + file_path.split('\\')[
            -1] + '24x25_Tabu_gda_operator_1000iter_kc_set2' + '.xlsx'
        algorithm_results_df = pd.DataFrame(numeric_info.algorithm_results)
        algorithm_results_df.to_excel(file_name, index=False)


if __name__ == '__main__':
    main()
