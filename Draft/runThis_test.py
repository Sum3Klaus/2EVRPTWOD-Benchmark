# -*- coding: utf-8 -*-
# @Time     : 2024-08-14-16:16
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from AlgorithmFramework import *
import numpy as np
import matplotlib.pyplot as plt

file_solomon = r"C:\Users\SumTEO\PycharmProjects\2E-VRPOD\BranchAndPrice\Solomn_VRP_benchmark\solomon-100\In\r101.txt"
file_bp = r"C:\Users\SumTEO\Desktop\WestChina\算例\2evrp_instances(BandP)\Set2a_E-n22-k4-s6-17.dat"
file_kc = r"C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\dataset\Set4\Instance50-s2-01.dat"
# C:\Users\SumTEO\Desktop\WestChina\算例\2E_VRP-kancharla\dataset\Set2\E-n22-k4-s08-14.dat
# C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\dataset\Set3\E-n51-k5-s12-43.dat
# C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\dataset\Set5\2eVRP_100-5-1
# C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\dataset\Set4\Instance50-s2-01.dat
file_gptv = "../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Benchmark/set2a/Set2a_E-n22-k4-s6-17.dat"


model_info = {"files": {0: file_solomon, 1: file_bp, 2: file_kc, 3: file_gptv},
              'benchmark_id': 3,
              "file_name": file_solomon,
              "random_seed": 3407,
              'satellite_num': 2,
              'customer_num': 15,
              'od_num': 13,
              'is_select': True,
              'customer_extend_time': 180,
              'od_extend_time': 30,
              'is_calc_od': True,
              'ini_sol_algorithm': 0,  # 0: greedy, 1: saving algorithm
              'is_tabu': True,
              'is_dual': True,
              'is_gda': True,
              'vehicle_num_1st': 3,
              'vehicle_num_2nd': 5}

# 读取最佳路径，添加对应的时间窗
# 02-Jan-2016_1_300_E-n51-k5-s12-43
# C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\result\set4\04-Jan-2016_1_50_1000Instance50-s2-01.dat
# result_path = "../Benchmarks/2E_VRP-kancharla/result/set4/04-Jan-2016_1_50_1000Instance50-s2-01.dat"
result_path = r"C:\Users\SumTEO\Desktop\2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo\Result\2\Set2a_E-n22-k4-s6-17.dat_417.psf"

np.random.seed(model_info['random_seed'])

alg = AlgorithmFramework(model_info=model_info)
alg.build_instance(is_input_result=True,
                   result_selection=1,
                   result_path=result_path,
                   random_seed=model_info['random_seed'])
# alg.ins.plot_vertices()

# for cus in alg.ins.graph.customer_list:
#     print(alg.ins.graph.vertex_dict[cus].ready_time, alg.ins.graph.vertex_dict[cus].due_time)

# alg.ins.gen_od_task.get_customer_square()
# od_s = []
# for i in range(10):
#
#     origin_coord, destination_coord = alg.ins.gen_od_task.gen_od_origin_and_destination()
#     od_s.append([origin_coord, destination_coord])
# alg.ins.gen_od_task.gen_od_task(od_extend_time=0)

# arrive_time_dict = alg.ins.get_benchmark_result(result_path=result_path)
# alg.ins.set_time_window(arrive_time_dict=arrive_time_dict,
#                         random_seed=3407)
# alg.ins.gen_od_task.get_customer_square()
# alg.ins.gen_od_task.gen_od_task(od_extend_time=0)
# alg.input_result_info(result_path=result_path,
#                       random_seed=3407,
#                       od_extend_time=0)

# for cus in alg.ins.graph.customer_list:
#     print(alg.ins.graph.vertex_dict[cus].ready_time, alg.ins.graph.vertex_dict[cus].due_time)
alg.get_1st_ini_solution()
alg.run()
# alg.grb_1st.model.write('1ST.LP')
print(alg.sate_last_arrive_time, alg.ins.graph.arc_dict[1, 2].distance)

alg.solve_gurobi_model()

# print(alg.alns.gda.history)

# alg.solve_gurobi_model()
# print(f'gurobi solving time: {alg.grb_model.model.runTime}')

# alg.solve_gurobi_model_without_od(cus_served_by_od_list=[15])

""" 绘制 alns 解的图 """
# r1 = []
# for r in alg.best_sol_1st.routes:
#     r1.append(r.route_list)
# r2 = []
# for r in alg.best_sol_2nd.routes:
#     r2.append(r.route_list)
# r_od = list(alg.iter_hungarian.od_routes.values())
#
# alg.ins.plot_routes(routes_1st=r1,
#                     routes_2nd=r2,
#                     routes_od=r_od)


print()

"""
for i in range(len(alg.best_sol_2nd.routes[0].route) - 1):
    print(f'{alg.best_sol_2nd.routes[0].route[i]} to {alg.best_sol_2nd.routes[0].route[i+1]} = {alg.ins.graph.arc_dict[alg.best_sol_2nd.routes[0].route[i].id_, alg.best_sol_2nd.routes[0].route[i + 1].id_].distance}')
    
new_time_table = alg.calc_last_time_table(route=alg.best_sol_2nd.routes[0])

"""


def plot_obj(y):
    plt.figure(figsize=(10, 8))
    x = list(range(len(y)))
    plt.plot(x, y, color='cyan', linewidth=2)
    # 防止重复标签
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Depot, Satellites, Customers, and Routes')
    plt.grid(True)
    plt.show()
