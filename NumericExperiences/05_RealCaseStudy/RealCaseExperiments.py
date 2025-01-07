# -*- coding: utf-8 -*-
# @Time     : 2024-12-09-16:35
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
    file_path = 'real_case_wuhou_52_4_18.txt'
    numeric_info = NumericInfo(f=file_path)

    model_info = {"files": {0: file_path, 1: file_path, 2: file_path, 3: file_path,
                            4: file_path, 5: file_path},
                  'benchmark_id': 5,
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

    combinations = [
        [True, True], [False, False]
    ]
    # combinations = [
    #     [True, True]
    # ]

    for combination in combinations:
        is_select = combination[0]
        is_od = combination[1]

        numeric_info.update_mathematical_setting(model_info=model_info,
                                                 is_select=is_select,
                                                 is_od=is_od)

        alg = AlgorithmFramework(model_info=model_info)
        alg.build_real_case_ins()
        model_info['od_num'] = alg.ins.od_num
        model_info['customer_num'] = alg.ins.customer_num
        model_info['satellite_num'] = alg.ins.sate_num
        # """
        alg.run()
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

        # calc ini sol info
        # 1st
        ini_veh_1st = len(alg.ini_sol_1st.routes) * alg.ins.model_para.vehicle_1_cost
        ini_tra_1st = alg.ini_sol_1st.totalCost - ini_veh_1st
        ini_carbon_cost_1st = alg.ini_sol_1st.carbon_cost
        # 2nd
        ini_veh_2nd = len(alg.ini_sol.routes) * alg.ins.model_para.vehicle_2_cost
        ini_tra_2nd = alg.ini_sol.totalCost - ini_veh_2nd
        ini_carbon_cost_2nd = alg.ini_sol.carbon_cost

        if model_info['is_select'] and model_info['is_calc_od']:

            total_obj = (grb_1st_obj + alg.alns.cost_travel + alg.alns.cost_carbon + alg.alns.cost_vehicle +
                         alg.ins.od_travel_compensation + len(
                        alg.ins.customer_list_od) * alg.ins.model_para.compensation)

            numeric_info.append_numeric_result(instance=file_path.split('\\')[-1],
                                               cus_num=alg.ins.customer_num,
                                               sate_num=alg.ins.sate_num,
                                               od_num=model_info['od_num'],
                                               random_seed=model_info['random_seed'],
                                               is_select=True, is_od=True, algorithm='GDALNS/TD',
                                               ini_algorithm=0,

                                               ini_tra_1st=ini_tra_1st,
                                               ini_veh_1st=ini_veh_1st,
                                               ini_carbon_cost_1st=ini_carbon_cost_1st,
                                               ini_tra_2nd=ini_tra_2nd,
                                               ini_veh_2nd=ini_veh_2nd,
                                               ini_carbon_cost_2nd=ini_carbon_cost_2nd,

                                               is_dual=True,
                                               is_tabu=True,
                                               is_gda=True,
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
            # 添加空行，方便计算实验
            numeric_info.append_numeric_result(instance=None, cus_num=None, sate_num=None, od_num=None,
                                               random_seed=None, is_select=None, is_od=None, algorithm=None,
                                               ini_algorithm=None,
                                               ini_tra_1st=None,
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

        else:

            veh_2nd = 0
            tra_2nd = 0
            carbon_cost_2nd = 0
            best_iter = 0
            total_iter = 0
            best_run_time = 0
            total_run_time = 0

            # calc solution
            for sate in alg.ins.graph.sate_list:
                cur_alns = alg.alns_sol_dict[sate]

                best_iter += cur_alns.best_iterTimes
                total_iter += cur_alns.total_iterTimes
                best_run_time += cur_alns.best_runTime
                total_run_time += cur_alns.total_runtime

            alns_veh = len(alg.best_sol_2nd.routes) * alg.ins.model_para.vehicle_2_cost
            alns_tra = alg.best_sol_2nd.totalCost - alns_veh
            alns_carbon = alg.best_sol_2nd.carbon_cost

            # total_obj = (grb_1st_obj + alns_tra + alns_veh + alns_carbon + alg.ins.od_travel_compensation + len(
            #     alg.ins.customer_list_od) * alg.ins.model_para.compensation)

            total_obj = (ini_veh_1st + ini_tra_1st + ini_carbon_cost_1st) + alns_veh + alns_tra + alns_carbon

            numeric_info.append_numeric_result(instance=file_path.split('\\')[-1],
                                               cus_num=alg.ins.customer_num,
                                               sate_num=alg.ins.sate_num,
                                               od_num=model_info['od_num'],
                                               random_seed=model_info['random_seed'],
                                               is_select=False, is_od=False, algorithm='GDALNS/TD',
                                               ini_algorithm=0,

                                               ini_tra_1st=ini_tra_1st,
                                               ini_veh_1st=ini_veh_1st,
                                               ini_carbon_cost_1st=ini_carbon_cost_1st,
                                               ini_tra_2nd=ini_tra_2nd,
                                               ini_veh_2nd=ini_veh_2nd,
                                               ini_carbon_cost_2nd=ini_carbon_cost_2nd,

                                               is_dual=True,
                                               is_tabu=True,
                                               is_gda=True,
                                               customer_extend_time=model_info['customer_extend_time'],
                                               od_extend_time=model_info['od_extend_time'],
                                               runtime=total_run_time,
                                               total_obj=total_obj,
                                               ub=total_obj, lb=total_obj,
                                               # tra_cost_1st=tra_cost_1st,
                                               # carbon_cost_1st=carbon_cost_1st,
                                               # vehicle_cost_1st=vehicle_cost_1st,
                                               # routes_1st=alg.best_sol_1st.routes,
                                               tra_cost_1st=ini_tra_1st,
                                               carbon_cost_1st=ini_carbon_cost_1st,
                                               vehicle_cost_1st=ini_veh_1st,
                                               routes_1st=alg.ini_sol_1st.routes,

                                               tra_cost_2nd=alns_tra,
                                               carbon_cost_2nd=alns_carbon,
                                               vehicle_cost_2nd=alns_veh,
                                               routes_2nd=alg.best_sol_2nd.routes,
                                               tra_cost_od='/',
                                               compensation_od='/',
                                               od_match='/',
                                               best_iter_times=best_iter,
                                               total_runtime=total_run_time,
                                               best_runtime=best_run_time,
                                               total_iter_times=total_iter)
        # """

        """ Gurobi """
        """
        alg.solve_gurobi_model()

        if alg.grb_model.model.status == GRB.OPTIMAL:
            numeric_info.append_numeric_result(instance=file_path.split('\\')[-1], cus_num=alg.ins.customer_num,
                                               # sate_num=model_info['satellite_num'],
                                               sate_num=alg.ins.sate_num,
                                               od_num=model_info['od_num'], random_seed=model_info['random_seed'],
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
            """

    file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}' + file_path.split('\\')[
        -1] + f'real_case_study_wuhou_52_4_18' + '.xlsx'
    algorithm_results_df = pd.DataFrame(numeric_info.algorithm_results)
    algorithm_results_df.to_excel(file_name, index=False)


if __name__ == '__main__':
    main()
