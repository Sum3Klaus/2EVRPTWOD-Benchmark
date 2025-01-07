# -*- coding: utf-8 -*-
# @Time     : 2024-08-21-10:28
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163


class NumericInfo(object):

    def __init__(self,
                 f):
        self.instance = f.split('\\')[-1]
        self.cus_num = [10, 15]  # [10, 15, 20, 25]
        self.sate_num = 2
        self.od_num = [2, 3]  # [2, 3]
        self.random_seed = [42, 3407]  # [42, 3407, 114514, 20231031, 203853699]
        self.is_select = True  # [True, False]
        self.is_od = True
        self.algorithm = ['GdaTabuAlns', 'TabuAlns', 'GbaAlns', 'Alns']
        self.ini_algorithm = [0, 1]
        self.ini_obj = '/'
        self.is_tabu = [True, False]
        self.is_dual = [True, False]
        self.is_gda = [True, False]
        self.customer_extend_time = [0, 100]  # [0, 100]
        self.od_extend_time = [50, 100]  # [50, 100]

        # is: 0-False, 1-True
        self.algorithm_results = {
            'Instance': [],
            'Customer Num': [],
            'Satellite Num': [],
            'OD Num': [],
            'Random Seed': [],
            'Is Select': [],
            'Is OD': [],
            'Algorithm': [],
            'Ini Algorithm': [],
            'Ini 1st travel cost': [],
            'Ini 1st vehicle cost': [],
            'Ini 1st Carbon cost': [],
            'Ini 2nd travel cost': [],
            'Ini 2nd vehicle cost': [],
            'Ini 2nd Carbon cost': [],
            'Is Dual': [],
            'Is Tabu': [],
            'Is GDA': [],
            'Time': [],  # model.Runtime
            'Total Obj': [],  # alg.grb_1st.model.ObjVal + alg.alns.cost_travel + alg.alns.cost_carbon +
            # alg.alns.cost_vehicle +
            # ins.od_travel_compensation + len(ins.customer_list_od) * ins.model_para.compensation
            'UB': [],
            "LB": [],
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
            'best sol iter time': [],   # alg.alns.best_iterTimes
            'Total iter times': [],  # # alg.alns.params.pu * alg.alns.params.epoch
            'best sol runtime': [],  # alg.alns.best_runtime
            'Total Runtime': [],   # alg.alns.total_runtime
        }

    def append_numeric_result(self,
                              instance, cus_num, sate_num, od_num, random_seed, is_select, is_od, algorithm,
                              ini_algorithm,
                              ini_tra_1st, ini_veh_1st, ini_carbon_cost_1st,
                              ini_tra_2nd, ini_veh_2nd, ini_carbon_cost_2nd,
                              is_dual, is_tabu, is_gda, customer_extend_time, od_extend_time,
                              runtime, total_obj, ub, lb,
                              tra_cost_1st, carbon_cost_1st, vehicle_cost_1st, routes_1st,
                              tra_cost_2nd, carbon_cost_2nd, vehicle_cost_2nd, routes_2nd,
                              tra_cost_od, compensation_od, od_match,
                              best_iter_times, total_runtime, best_runtime, total_iter_times):
        self.algorithm_results['Instance'].append(instance)
        self.algorithm_results['Customer Num'].append(cus_num)
        self.algorithm_results['Satellite Num'].append(sate_num)
        self.algorithm_results['OD Num'].append(od_num)
        self.algorithm_results['Random Seed'].append(random_seed)
        self.algorithm_results['Is Select'].append(is_select)
        self.algorithm_results['Is OD'].append(is_od)
        self.algorithm_results['Algorithm'].append(algorithm)
        self.algorithm_results['Ini Algorithm'].append(ini_algorithm)

        self.algorithm_results['Ini 1st travel cost'].append(ini_tra_1st)
        self.algorithm_results['Ini 1st vehicle cost'].append(ini_veh_1st)
        self.algorithm_results['Ini 1st Carbon cost'].append(ini_carbon_cost_1st)
        self.algorithm_results['Ini 2nd travel cost'].append(ini_tra_2nd)
        self.algorithm_results['Ini 2nd vehicle cost'].append(ini_veh_2nd)
        self.algorithm_results['Ini 2nd Carbon cost'].append(ini_carbon_cost_2nd)

        self.algorithm_results['Is Dual'].append(is_dual)
        self.algorithm_results['Is Tabu'].append(is_tabu)
        self.algorithm_results['Is GDA'].append(is_gda)
        self.algorithm_results['customer extend time'].append(customer_extend_time)
        self.algorithm_results['od extend time'].append(od_extend_time)

        self.algorithm_results['Time'].append(runtime)
        self.algorithm_results['Total Obj'].append(total_obj)
        self.algorithm_results['UB'].append(ub)
        self.algorithm_results['LB'].append(lb)
        self.algorithm_results['1st travel cost'].append(tra_cost_1st)
        self.algorithm_results['1st carbon cost'].append(carbon_cost_1st)
        self.algorithm_results['1st vehicle cost'].append(vehicle_cost_1st)
        self.algorithm_results['1st routes'].append(routes_1st)
        self.algorithm_results['2nd travel cost'].append(tra_cost_2nd)
        self.algorithm_results['2nd carbon cost'].append(carbon_cost_2nd)
        self.algorithm_results['2nd vehicle cost'].append(vehicle_cost_2nd)
        self.algorithm_results['2nd routes'].append(routes_2nd)
        self.algorithm_results['OD travel cost'].append(tra_cost_od)
        self.algorithm_results['OD Compensation'].append(compensation_od)
        self.algorithm_results['OD match'].append(od_match)

        self.algorithm_results['best sol iter time'].append(best_iter_times)
        self.algorithm_results['Total Runtime'].append(total_runtime)
        self.algorithm_results['best sol runtime'].append(best_runtime)
        self.algorithm_results['Total iter times'].append(total_iter_times)

    @staticmethod
    def update_model_info(model_info,
                          f, benchmark_id, random_seed, sate_num, cus_num, od_num,
                          customer_extend_time, od_extend_time,
                          ):
        model_info['file_name'] = f
        model_info['benchmark_id'] = benchmark_id
        model_info['random_seed'] = random_seed
        model_info['satellite_num'] = sate_num
        model_info['customer_num'] = cus_num
        model_info['od_num'] = od_num

        model_info['customer_extend_time'] = customer_extend_time
        model_info['od_extend_time'] = od_extend_time

    @staticmethod
    def update_model_algorithm_setting(model_info,
                                       is_select, ini_algorithm, is_dual, is_tabu, is_gda):
        model_info['is_select'] = is_select
        model_info['ini_sol_algorithm'] = ini_algorithm
        model_info['is_tabu'] = is_tabu
        model_info['is_dual'] = is_dual
        model_info['is_gda'] = is_gda

    @staticmethod
    def update_mathematical_setting(model_info,
                                    is_select,
                                    is_od):
        model_info['is_select'] = is_select
        model_info['is_calc_od'] = is_od
