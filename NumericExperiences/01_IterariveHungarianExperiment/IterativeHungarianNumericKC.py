# -*- coding: utf-8 -*-
# @Time     : 2024-08-21-14:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from AlgorithmFramework import *
from NumericInfo_IH import *
import pandas as pd
import numpy as np
import datetime
import itertools


def main():
    f = '../../Benchmarks/Solomn_VRP_benchmark/homberger_400_customer_instances/C1_4_1.TXT'
    f_bp = "../../Benchmarks/2evrp_instances(BandP)/Set2a_E-n22-k4-s6-17.dat"
    f_kc = "../../Benchmarks/2E_VRP-kancharla/dataset/Set2/E-n22-k4-s08-14.dat"

    folder_path = '../../Benchmarks/2evrp_instances(BandP)'  # '../../Benchmarks/2E_VRP-kancharla/dataset/Set2'
    # folder_path = "../../Benchmarks/2E_VRP-kancharla/dataset/Set2"
    # 初始化已读取的文件计数器
    files_read = 0

    for filename in os.listdir(folder_path):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)

        numeric_info = NumericInfo(f=file_path)

        # 确保是文件而不是文件夹
        if os.path.isfile(file_path):
            files_read += 1

            model_info = {"files": {0: f, 1: f_bp, 2: f_kc},
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

            combinations = list(itertools.product(numeric_info.random_seed,
                                                  numeric_info.od_num,
                                                  numeric_info.od_extend_time))

            for combination in combinations:
                random_seed = combination[0]
                od_num = combination[1]
                od_extend_time = combination[2]

                numeric_info.update_model_info(model_info=model_info, f=file_path, benchmark_id=2,
                                               random_seed=random_seed, sate_num=2, cus_num='/',
                                               od_num=od_num, customer_extend_time=0, od_extend_time=od_extend_time)

                np.random.seed(random_seed)
                alg = AlgorithmFramework(model_info=model_info)
                alg.build_instance()

                """求解 Gurobi Model"""
                alg.solve_gurobi_model()
                numeric_info.append_numeric_result(instance=f.split('\\')[-1], cus_num='/',
                                                   sate_num=model_info['satellite_num'],
                                                   od_num=od_num, random_seed=random_seed,
                                                   is_select=False, is_od=True, algorithm='Gurobi', ini_algorithm='/',
                                                   ini_obj='/', is_dual='/', is_tabu='/', is_gda='/',
                                                   customer_extend_time=0,
                                                   od_extend_time=od_extend_time,
                                                   runtime=alg.grb_model.model.Runtime,
                                                   total_obj=alg.grb_model.model.ObjVal,
                                                   tra_cost_1st=alg.grb_model.objs['1st travel cost'].getValue(),
                                                   carbon_cost_1st=alg.grb_model.objs['1st carbon cost'].getValue(),
                                                   vehicle_cost_1st=alg.grb_model.objs['1st vehicle cost'].getValue(),
                                                   routes_1st=alg.grb_model_routes_1st,
                                                   tra_cost_2nd=alg.grb_model.objs['2nd travel cost'].getValue(),
                                                   carbon_cost_2nd=alg.grb_model.objs['2nd carbon cost'].getValue(),
                                                   vehicle_cost_2nd=alg.grb_model.objs['2nd vehicle cost'].getValue(),
                                                   routes_2nd=alg.grb_model_routes_2nd,
                                                   tra_cost_od=alg.grb_model.objs['od travel cost'].getValue(),
                                                   compensation_od=alg.grb_model.objs[
                                                       'od compensation cost'].getValue(),
                                                   od_match=alg.grb_model.od_info)

                """求解 Iterative Hungarian"""
                alg.run_iter_hungarian()
                numeric_info.append_numeric_result(instance=f.split('\\')[-1], cus_num='/',
                                                   sate_num=model_info['satellite_num'],
                                                   od_num=od_num, random_seed=random_seed,
                                                   is_select=False, is_od=True, algorithm='IH', ini_algorithm='/',
                                                   ini_obj='/', is_dual='/', is_tabu='/', is_gda='/',
                                                   customer_extend_time=0,
                                                   od_extend_time=od_extend_time,
                                                   runtime=alg.ih_runtime,
                                                   total_obj='/', tra_cost_1st='/', carbon_cost_1st='/',
                                                   vehicle_cost_1st='/',
                                                   routes_1st='/', tra_cost_2nd='/', carbon_cost_2nd='/',
                                                   vehicle_cost_2nd='/',
                                                   routes_2nd='/',
                                                   tra_cost_od=alg.ins.od_travel_compensation,
                                                   compensation_od=len(
                                                       alg.ins.customer_list_od) * alg.ins.model_para.compensation,
                                                   od_match=alg.iter_hungarian.od_ser_cus)

                """求解 Gurobi without OD"""
                alg.solve_gurobi_model_without_od(cus_served_by_od_list=alg.ins.customer_list_od)
                numeric_info.append_numeric_result(instance=f.split('\\')[-1], cus_num='/',
                                                   sate_num=model_info['satellite_num'],
                                                   od_num=od_num, random_seed=random_seed,
                                                   is_select=False, is_od=True, algorithm='Gurobi without OD',
                                                   ini_algorithm='/',
                                                   ini_obj='/', is_dual='/', is_tabu='/', is_gda='/',
                                                   customer_extend_time=0,
                                                   od_extend_time=od_extend_time,
                                                   runtime=alg.grb_model_without_od.model.Runtime,
                                                   total_obj=alg.grb_model_without_od.model.ObjVal,
                                                   tra_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st travel cost'].getValue(),
                                                   carbon_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st carbon cost'].getValue(),
                                                   vehicle_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st vehicle cost'].getValue(),
                                                   routes_1st=alg.grb_model_without_od.grb_model_without_od_routes_1st,
                                                   tra_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd travel cost'].getValue(),
                                                   carbon_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd carbon cost'].getValue(),
                                                   vehicle_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd vehicle cost'].getValue(),
                                                   routes_2nd=alg.grb_model_without_od_routes_2nd.grb_model_without_od_routes_2nd,
                                                   tra_cost_od='/',
                                                   compensation_od='/',
                                                   od_match='/')

                """求解 Gurobi no OD"""
                alg.solve_gurobi_model_without_od(cus_served_by_od_list=[])
                numeric_info.append_numeric_result(instance=f.split('\\')[-1], cus_num='/',
                                                   sate_num=model_info['satellite_num'],
                                                   od_num=od_num, random_seed=random_seed,
                                                   is_select=False, is_od=True, algorithm='Gurobi No OD',
                                                   ini_algorithm='/',
                                                   ini_obj='/', is_dual='/', is_tabu='/', is_gda='/',
                                                   customer_extend_time=0,
                                                   od_extend_time=od_extend_time,
                                                   runtime=alg.grb_model_without_od.model.Runtime,
                                                   total_obj=alg.grb_model_without_od.model.ObjVal,
                                                   tra_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st travel cost'].getValue(),
                                                   carbon_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st carbon cost'].getValue(),
                                                   vehicle_cost_1st=alg.grb_model_without_od.objs[
                                                       '1st vehicle cost'].getValue(),
                                                   routes_1st=alg.grb_model_without_od.grb_model_without_od_routes_1st,
                                                   tra_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd travel cost'].getValue(),
                                                   carbon_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd carbon cost'].getValue(),
                                                   vehicle_cost_2nd=alg.grb_model_without_od.objs[
                                                       '2nd vehicle cost'].getValue(),
                                                   routes_2nd=alg.grb_model_without_od_routes_2nd.grb_model_without_od_routes_2nd,
                                                   tra_cost_od='/',
                                                   compensation_od='/',
                                                   od_match='/')

            # 如果已经读取了15个文件，就中断循环
            if files_read >= 5:
                break

        file_name = 'IH_' + f'{datetime.date.today().strftime("%Y-%m-%d")}.xlsx'
        algorithm_results_df = pd.DataFrame(numeric_info.algorithm_results)
        algorithm_results_df.to_excel(file_name, index=False)


if __name__ == '__main__':
    main()
