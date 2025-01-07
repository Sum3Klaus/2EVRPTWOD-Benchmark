# -*- coding: utf-8 -*-
# @Time     : 2024-08-19-14:11
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from AlgorithmFramework import *
import pandas as pd
import numpy as np
import datetime


def main():
    file_solomon = r"C:\Users\SumTEO\PycharmProjects\2E-VRPOD\BranchAndPrice\Solomn_VRP_benchmark\solomon-100\In\c101.txt"
    file_bp = r"C:\Users\SumTEO\Desktop\WestChina\算例\2evrp_instances(BandP)\Set2a_E-n22-k4-s6-17.dat"
    file_kc = r"C:\Users\SumTEO\Desktop\WestChina\算例\2E_VRP-kancharla\dataset\Set2\E-n22-k4-s08-14.dat"
    f = r"C:\Users\SumTEO\Desktop\2-E_CVRPTW_WITH_OD\Solomn_VRP_benchmark\homberger_400_customer_instances\C1_4_1.TXT"

    model_info = {"files": {0: f, 1: file_bp, 2: file_kc},
                  'benchmark_id': 0,
                  "file_name": f,
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

    # is: 0-False, 1-True
    algorithm_results = {
        'Instance': [],
        'Customer Num': [],
        'Satellite Num': [],
        'OD Num': [],
        'Random Seed': [],
        'Is Select': [],
        'Is OD': [],
        'Algorithm': [],
        'Ini Algorithm': [],
        'Ini Obj': [],
        'Is Dual': [],
        'Is Tabu': [],
        'Is GDA': [],
        'Time': [],  # model.Runtime
        'Total Obj': [],  # model.ObjVal
        '1st travel cost': [],
        '1st vehicle cost': [],
        '1st carbon cost': [],
        '1st routes': [],
        '2nd travel cost': [],
        '2nd vehicle cost': [],
        '2nd carbon cost': [],
        '2nd routes': [],
        'OD travel cost': [],  # ins.od_travel_compensation
        'OD Compensation': [],  # len(ins.customer_list_od) * ins.model_para.compensation
        'OD match': [],  # alg.iter_hungarian.od_ser_cus    //// grb_model.od_info
        'customer extend time': [],
        'od extend time': [],
    }

    # Iterative Hungarian Numeric Designation
    iter_hungarian = {
        'Instance': f.split('\\')[-1],
        'Customer Num': [10, 15, 20, 25],  # [10, 15, 20]
        'Satellite Num': 2,
        'OD Num': [2, 3],
        'Random Seed': [42, 3407, 114514, 20231031, 203853699],  # [42, 3407, 114514, 20231031, 203853699]
        'Is Select': False,
        'Is OD': True,
        'Algorithm': [],
        'Ini Algorithm': '/',
        'Ini Obj': '/',
        'Is Dual': '/',
        'Is Tabu': '/',
        'Is GDA': '/',
        'Time': [],
        'Total Obj': [],
        '1st travel cost': [],
        '1st vehicle cost': [],
        '1st carbon cost': [],
        '1st routes': [],
        '2nd travel cost': [],
        '2nd vehicle cost': [],
        '2nd carbon cost': [],
        '2nd routes': [],
        'OD travel cost': [],
        'OD Compensation': [],
        'OD routes': [],
        'customer_extend_time': [100, 150],
        'od_extend_time': [50, 100],
    }

    # 写入数据
    for random_seed in iter_hungarian['Random Seed']:
        for cus in iter_hungarian['Customer Num']:
            for od in iter_hungarian['OD Num']:
                for i in range(len(iter_hungarian['od_extend_time'])):
                    # random seed
                    np.random.seed(random_seed)

                    alg = AlgorithmFramework(model_info=model_info)
                    alg.build_instance()

                    """求解 Gurobi Model"""
                    alg.solve_gurobi_model()

                    algorithm_results['Instance'].append(iter_hungarian['Instance'])
                    algorithm_results['Customer Num'].append(cus)
                    algorithm_results['Satellite Num'].append(2)
                    algorithm_results['OD Num'].append(od)
                    algorithm_results['Random Seed'].append(random_seed)
                    algorithm_results['Is Select'].append(iter_hungarian['Is Select'])
                    algorithm_results['Is OD'].append(iter_hungarian['Is OD'])
                    algorithm_results['Algorithm'].append('Gurobi')
                    algorithm_results['Ini Algorithm'].append(iter_hungarian['Ini Algorithm'])
                    algorithm_results['Ini Obj'].append(iter_hungarian['Ini Obj'])
                    algorithm_results['Is Dual'].append(iter_hungarian['Is Dual'])
                    algorithm_results['Is Tabu'].append(iter_hungarian['Is Tabu'])
                    algorithm_results['Is GDA'].append(iter_hungarian['Is GDA'])
                    algorithm_results['Time'].append(alg.grb_model.model.Runtime)
                    algorithm_results['Total Obj'].append(alg.grb_model.model.ObjVal)
                    algorithm_results['1st travel cost'].append(alg.grb_model.objs['1st travel cost'].getValue())
                    algorithm_results['1st carbon cost'].append(alg.grb_model.objs['1st carbon cost'].getValue())
                    algorithm_results['1st vehicle cost'].append(alg.grb_model.objs['1st vehicle cost'].getValue())
                    algorithm_results['1st routes'].append(alg.grb_model_routes_1st)
                    algorithm_results['2nd travel cost'].append(alg.grb_model.objs['2nd travel cost'].getValue())
                    algorithm_results['2nd carbon cost'].append(alg.grb_model.objs['2nd carbon cost'].getValue())
                    algorithm_results['2nd vehicle cost'].append(alg.grb_model.objs['2nd vehicle cost'].getValue())
                    algorithm_results['2nd routes'].append(alg.grb_model_routes_2nd)
                    algorithm_results['OD travel cost'].append(alg.grb_model.objs['od travel cost'].getValue())
                    algorithm_results['OD Compensation'].append(alg.grb_model.objs['od compensation cost'].getValue())
                    algorithm_results['OD match'].append(alg.grb_model.od_info)
                    algorithm_results['customer extend time'].append(iter_hungarian['customer_extend_time'][i])
                    algorithm_results['od extend time'].append(iter_hungarian['od_extend_time'][i])

                    """求解 Iterative Hungarian"""
                    alg.run_iter_hungarian()

                    algorithm_results['Instance'].append(iter_hungarian['Instance'])
                    algorithm_results['Customer Num'].append(cus)
                    algorithm_results['Satellite Num'].append(2)
                    algorithm_results['OD Num'].append(od)
                    algorithm_results['Random Seed'].append(random_seed)
                    algorithm_results['Is Select'].append(iter_hungarian['Is Select'])
                    algorithm_results['Is OD'].append(iter_hungarian['Is OD'])
                    algorithm_results['Algorithm'].append('IH')
                    algorithm_results['Ini Algorithm'].append(iter_hungarian['Ini Algorithm'])
                    algorithm_results['Ini Obj'].append(iter_hungarian['Ini Obj'])
                    algorithm_results['Is Dual'].append(iter_hungarian['Is Dual'])
                    algorithm_results['Is Tabu'].append(iter_hungarian['Is Tabu'])
                    algorithm_results['Is GDA'].append(iter_hungarian['Is GDA'])
                    algorithm_results['Time'].append(alg.ih_runtime)
                    algorithm_results['Total Obj'].append('/')
                    algorithm_results['1st travel cost'].append('/')
                    algorithm_results['1st carbon cost'].append('/')
                    algorithm_results['1st vehicle cost'].append('/')
                    algorithm_results['1st routes'].append('/')
                    algorithm_results['2nd travel cost'].append('/')
                    algorithm_results['2nd carbon cost'].append('/')
                    algorithm_results['2nd vehicle cost'].append('/')
                    algorithm_results['2nd routes'].append('/')
                    algorithm_results['OD travel cost'].append(alg.ins.od_travel_compensation)
                    algorithm_results['OD Compensation'].append(
                        len(alg.ins.customer_list_od) * alg.ins.model_para.compensation)
                    algorithm_results['OD match'].append(alg.iter_hungarian.od_ser_cus)
                    algorithm_results['customer extend time'].append(iter_hungarian['customer_extend_time'][i])
                    algorithm_results['od extend time'].append(iter_hungarian['od_extend_time'][i])

                    """求解 Gurobi without OD"""
                    alg.solve_gurobi_model_without_od(cus_served_by_od_list=alg.ins.customer_list_od)

                    algorithm_results['Instance'].append(iter_hungarian['Instance'])
                    algorithm_results['Customer Num'].append(cus)
                    algorithm_results['Satellite Num'].append(2)
                    algorithm_results['OD Num'].append(od)
                    algorithm_results['Random Seed'].append(random_seed)
                    algorithm_results['Is Select'].append(iter_hungarian['Is Select'])
                    algorithm_results['Is OD'].append(iter_hungarian['Is OD'])
                    algorithm_results['Algorithm'].append('Gurobi without OD')
                    algorithm_results['Ini Algorithm'].append(iter_hungarian['Ini Algorithm'])
                    algorithm_results['Ini Obj'].append(iter_hungarian['Ini Obj'])
                    algorithm_results['Is Dual'].append(iter_hungarian['Is Dual'])
                    algorithm_results['Is Tabu'].append(iter_hungarian['Is Tabu'])
                    algorithm_results['Is GDA'].append(iter_hungarian['Is GDA'])
                    algorithm_results['Time'].append(alg.grb_model_without_od.model.Runtime)
                    algorithm_results['Total Obj'].append(alg.grb_model_without_od.model.ObjVal)
                    algorithm_results['1st travel cost'].append(
                        alg.grb_model_without_od.objs['1st travel cost'].getValue())
                    algorithm_results['1st carbon cost'].append(
                        alg.grb_model_without_od.objs['1st carbon cost'].getValue())
                    algorithm_results['1st vehicle cost'].append(
                        alg.grb_model_without_od.objs['1st vehicle cost'].getValue())
                    algorithm_results['1st routes'].append(alg.grb_model_without_od_routes_1st)
                    algorithm_results['2nd travel cost'].append(
                        alg.grb_model_without_od.objs['2nd travel cost'].getValue())
                    algorithm_results['2nd carbon cost'].append(
                        alg.grb_model_without_od.objs['2nd carbon cost'].getValue())
                    algorithm_results['2nd vehicle cost'].append(
                        alg.grb_model_without_od.objs['2nd vehicle cost'].getValue())
                    algorithm_results['2nd routes'].append(alg.grb_model_without_od_routes_2nd)
                    algorithm_results['OD travel cost'].append('/')
                    algorithm_results['OD Compensation'].append('/')
                    algorithm_results['OD match'].append('/')
                    algorithm_results['customer extend time'].append(iter_hungarian['customer_extend_time'][i])
                    algorithm_results['od extend time'].append(iter_hungarian['od_extend_time'][i])

    file_name = f'{datetime.date.today().strftime("%Y-%m-%d")}.xlsx'
    algorithm_results_df = pd.DataFrame(algorithm_results)
    algorithm_results_df.to_excel(file_name, index=False)


if __name__ == '__main__':
    main()