# -*- coding: utf-8 -*-
# @Time     : 2024-07-31-14:05
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
from GRB import *
from Instance import *
from ModelPara import *

# "C:\Users\SumTEO\Desktop\2-E_CVRPTW_WITH_OD\Solomn_VRP_benchmark\homberger_400_customer_instances\C1_4_1.TXT"
# r"C:\Users\SumTEO\PycharmProjects\2E-VRPOD\BranchAndPrice\Solomn_VRP_benchmark\solomon-100\In\rc101.txt"
file_solomon = r"C:\Users\SumTEO\PycharmProjects\2E-VRPOD\BranchAndPrice\Solomn_VRP_benchmark\solomon-100\In\c101.txt"

file_bp = r"C:\Users\SumTEO\Desktop\WestChina\算例\2evrp_instances(BandP)\Set2a_E-n22-k4-s6-17.dat"
file_kc = r"C:\Users\SumTEO\Desktop\WestChina\算例\2E_VRP-kancharla\dataset\Set2\E-n22-k4-s08-14.dat"

params = ModelParameters()

model_info = {"params": params,
              "file_name": file_solomon,
              "random_seed": 3407,
              'satellite_num': 2,
              'customer_num': 100,
              'od_num': 2,
              'is_select': True,
              'customer_extend_time': 100,
              'od_extend_time': 35,
              'instance_select': 2,
              'is_calc_od': True,
              'is_tabu': False}
np.random.seed(model_info["random_seed"])
ins = Instance(params=params,
               od_num=0,
               is_select=model_info['is_select'],
               benchmark_id=0)
ins.read_data(file_solomon,
              sate_num=2,
              cus_num=15,
              customer_extend_time=150
              )
# ins.read_data(file_bp)
# ins.read_data(file_kc)

ins.gen_od(od_extend_time=model_info['od_extend_time'])
# ins.input_info()
ins.gen_graph()
# ins.model_para.vehicle_1_capacity = 50000
grb = GurobiModelBuilder(ins=ins)

""" No sate selection """
# grb.add_first_variables()
# grb.add_second_variables_no_select()
# grb.add_od_variables_pdp()
""" Sate selection """
# grb.add_second_variables_sate_select()
# grb.add_variables()
#
# grb.set_objs()
# grb.add_binding_cons()
#
# grb.add_cons()
grb.build_model()

grb.model.optimize()
# grb.model.write('model.lp')
# grb.model.computeIIS()
# grb.model.write("compute_test.ilp")
print('=' * 50)
for var in grb.model.getVars():
    if var.x >= 0.5:
        if var.varName.startswith('x') or var.varName.startswith('y') or var.varName.startswith(
                'r') or var.varName.startswith('z'):
            print(var)

print()
