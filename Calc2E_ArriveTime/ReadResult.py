# -*- coding: utf-8 -*-
# @Time     : 2024-09-20-14:53
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import os
from AlgorithmFramework import *
from IterGreedyHungarian import *


def read_routes(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # 初始化变量
    sate_info = {}
    # layer1_info = []
    # layer2_routes = []
    in_layer1 = False
    in_layer2 = False
    sate_ser_weight = 0
    sate_routes = []
    routes = []

    # 解析文件内容
    for line in lines:
        line = line.strip()

        # 识别 Layer 1 的开始和结束
        if "Layer1" in line:
            in_layer1 = True
            in_layer2 = False
            continue
        elif "Layer2" in line:
            in_layer1 = False
            in_layer2 = True
            continue

        # 提取 Layer 1 的信息
        if in_layer1 and "Weight" in line:
            parts = line.split('Weight(')[1].split(')')
            weight = float(parts[0])

            # 判断是否有空置的sate
            cur_str = line.split('Cust(1) ')

            if len(cur_str) == 1:
                start_node = 9999
            else:
                start_node = int(line.split('Cust(1) ')[1])
            # layer1_info.append((weight, start_node))
            sate_info[start_node] = (weight, [])

        # 提取 Layer 2 的路径信息
        if in_layer2 and 'Vehicles' in line:
            sate_ser_weight = 0
            sate_routes.append([])
        if in_layer2 and "Cust" in line:

            parts = line.split('Weight(')[1].split(')')
            weight = float(parts[0])
            sate_ser_weight += weight
            customers = list(map(int, line.split('Cust(')[1].split(')')[1].strip().split()))
            # layer2_routes.append((weight, customers))
            sate_routes[-1].append((weight, customers))

    # 将 Layer 1 的载重信息和 Layer 2 的路径进行匹配，生成完整的路径
    full_routes = []

    # 判断 layer2 的路径的起始点
    for sate_route in sate_routes:
        cur_weight = 0
        cur_sate = None

        for route_info in sate_route:
            cur_weight += route_info[0]

        for key, value in sate_info.items():
            if cur_weight == value[0]:
                cur_sate = key

        for route_info in sate_route:
            sate_info[cur_sate][1].append(route_info[1])
            full_routes.append([cur_sate] + route_info[1] + [cur_sate])

    return sate_info, full_routes


def turn_instance(sate_num,
                  routes):
    for route in routes:
        for id_ in range(1, len(route) - 1):
            route[id_] += sate_num


# 使用示例
result_path = "../Benchmarks/2E_VRP-kancharla/result/set2/02-Jan-2016_1_300_E-n22-k4-s08-14.dat"
cur_sate_info, cur_routes = read_routes(result_path)

# 输出完整路径
# print(cur_routes)
# turn_instance(sate_num=len(list(cur_sate_info.keys())),
#               routes=cur_routes)
#
# print(cur_routes)
file_solomon = "../Benchmarks/Solomn_VRP_benchmark/homberger_400_customer_instances/C1_4_1.TXT"

file_bp = "../Benchmarks/2evrp_instances(BandP)/Set2a_E-n22-k4-s6-17.dat"
file_kc = "../Benchmarks/2E_VRP-kancharla/dataset/Set2/E-n22-k4-s08-14.dat"


model_info = {"files": {0: file_solomon, 1: file_bp, 2: file_kc},
              'benchmark_id': 2,
              "file_name": file_solomon,
              "random_seed": 3407,
              'satellite_num': 2,
              'customer_num': 60,
              'od_num': 2,
              'is_select': True,
              'customer_extend_time': 15,
              'od_extend_time': 15,
              'is_calc_od': True,
              'ini_sol_algorithm': 0,  # 0: greedy, 1: saving algorithm
              'is_tabu': True,
              'is_dual': True,
              'is_gda': False,
              'vehicle_num_1st': 3,
              'vehicle_num_2nd': 5}

np.random.seed(42)
alg = AlgorithmFramework(model_info=model_info)
alg.build_instance()

for cus in alg.ins.graph.customer_list:
    print(alg.ins.graph.vertex_dict[cus].ready_time, alg.ins.graph.vertex_dict[cus].due_time)

arrive_time_dict = alg.ins.get_benchmark_result(result_path=result_path)

alg.ins.set_time_window(arrive_time_dict=arrive_time_dict)
for cus in alg.ins.graph.customer_list:
    print(alg.ins.graph.vertex_dict[cus].ready_time, alg.ins.graph.vertex_dict[cus].due_time)

print()