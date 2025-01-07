# -*- coding: utf-8 -*-
# @Time     : 2024-10-23-18:04
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import ast
import re

data_path = "../Benchmarks/2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/Benchmark/set2a/Set2a_E-n22-k4-s6-17.dat"


def read_benchmark_in_result_files(d):
    depot_dict = dict()
    sate_dict = dict()
    customer_dict = dict()

    with open(d, 'r') as file:
        lines = file.readlines()
        cnt = 0

        for line in lines:
            cnt += 1
            line = line.strip()

            if cnt >= 4:
                print(line)

                str_info = line.split(';')

                if str_info[-1] == 'depot':
                    depot_dict[0] = [[str_info[1], str_info[2]], str_info[3]]

                elif str_info[-1] == 'satellite':
                    sate_dict[cnt - 4] = [[str_info[1], str_info[2]], str_info[3]]

                elif str_info[-1] == 'customer':
                    customer_dict[cnt - 4] = [[str_info[1], str_info[2]], str_info[3]]


result_path = r"C:\Users\SumTEO\Desktop\2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo\Result\2\Set2a_E-n22-k4-s6-17.dat_417.psf"


def read_result(r):
    routes_1st = dict()
    routes_2nd = dict()

    with open(r, 'r') as file:
        lines = file.readlines()
        cnt = 0
        vehicle_1st = 0
        vehicle_2nd = 0

        for line in lines:
            cnt += 1

            if cnt >= 7:
                line = line.strip()

                str_info = line.split(';')

                if str_info[-1] == 'Truck':
                    routes_1st[vehicle_1st] = ast.literal_eval(str_info[1])
                    vehicle_1st += 1

                elif str_info[-1] == 'CityFreighter':
                    routes_2nd[vehicle_2nd] = ast.literal_eval(str_info[1])
                    vehicle_2nd += 1

    print()


def read_1(d):
    data = {
        'trucks': {},
        'city_freighters': {},
        'stores': dict(),
        'customers': dict()
    }

    with open(d, 'r') as file:
        lines = file.readlines()
        cnt = 0

        current_section = None

        for line in lines:
            line = line.strip()
            # 判断信息类型
            if line.startswith('!'):
                if 'Trucks' in line:
                    current_section = 'trucks'
                elif 'CityFreighters' in line:
                    current_section = 'city_freighters'
                elif 'Stores' in line:
                    current_section = 'stores'
                elif 'Customers' in line:
                    current_section = 'customers'

            # 记录数据
            else:
                if current_section == 'trucks':
                    parts = line.split(',')
                    data['trucks'] = {
                        'total': int(parts[0]),
                        'capacity': int(parts[1]),
                        'cost_per_distance': int(parts[2]),
                        'fixcost': int(parts[3])
                    }

                elif current_section == 'city_freighters':
                    parts = line.split(',')
                    data['city_freighters'] = {
                        'max_cf_per_sat': int(parts[0]),
                        'total': int(parts[1]),
                        'capacity': int(parts[2]),
                        'cost_per_distance': int(parts[3]),
                        'fixcost': int(parts[4])
                    }

                elif current_section == 'stores':
                    data['stores'] = [
                        tuple(map(int, store.split(',')))
                        for store in line.split()
                    ]
                elif current_section == 'customers':
                    if line == '':
                        pass
                    else:
                        data['customers'] = [
                            list(map(int, customer.split(',')))
                            for customer in line.split()
                        ]
                    print()

    print()


set4_result_path = r"C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\Benchmarks\2E_VRP-kancharla\result\set4\04-Jan-2016_1_50_1000Instance50-s2-04.dat"
#
# with open(set4_result_path, 'r') as file:
#     lines = file.readlines()
#     cnt = 0
#     # 分割为行
#
#     # 变量存储提取的数据
#     layer1_data = []
#     layer2_data = []
#
#     # 读取 Layer1 数据
#     layer1_section = False
#     layer2_section = False
#
#     for line in lines:
#         # 检测段落
#         if "Layer1" in line:
#             layer1_section = True
#             continue
#         elif "Layer2" in line:
#             layer1_section = False
#             layer2_section = True
#             continue
#
#         if layer1_section and line.strip():
#             # 提取 Layer1 的信息
#             match = re.search(r'Cost\(([\d.]+)\),Weight\(([\d.]+)\),Cust\((\d+)\)', line)
#             if match:
#                 cost = float(match.group(1))
#                 weight = float(match.group(2))
#                 cust_count = int(match.group(3))
#                 # 提取路径
#                 path_data = line.split('Cust(')[-1].split(')')[-1].strip().split()
#                 # 检查路径长度是否与客户数量一致
#                 if len(path_data) == cust_count:
#                     layer1_data.append({
#                         'cost': cost,
#                         'weight': weight,
#                         'cust_count': cust_count,
#                         'path': path_data
#                     })
#
#         elif layer2_section and line.strip():
#             # 提取 Layer2 的信息
#             match = re.search(r'Cost\(([\d.]+)\),Weight\(([\d.]+)\),Cust\((\d+)\)', line)
#             if match:
#                 cust_count = int(match.group(3))
#                 path_data = line.split('Cust(')[-1].split(')')[1].strip().split()
#                 layer2_data.append({
#                     'cost': float(match.group(1)),
#                     'weight': float(match.group(2)),
#                     'cust_count': cust_count,
#                     'path': path_data
#                 })
#
#     print()


filepath = '../NumericExperiences/03_AlnsExperiment/Operators/Experiment-2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo/set 3/Set3_E-n51-k5-s12-18_od_tw.txt'