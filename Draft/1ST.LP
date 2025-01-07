\ Model First Echelon Model
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  864.7953361249999 x_0_1_0 + 864.7953361249999 x_0_1_1
   + 864.7953361249999 x_0_1_2 + 864.7953361249999 x_0_1_3
   + 864.7953361249999 x_0_1_4 + 864.7953361249999 x_0_1_5
   + 1025.6983295 x_0_2_0 + 1025.6983295 x_0_2_1 + 1025.6983295 x_0_2_2
   + 1025.6983295 x_0_2_3 + 1025.6983295 x_0_2_4 + 1025.6983295 x_0_2_5
   + 364.7953361249999 x_1_71_0 + 364.7953361249999 x_1_71_1
   + 364.7953361249999 x_1_71_2 + 364.7953361249999 x_1_71_3
   + 364.7953361249999 x_1_71_4 + 364.7953361249999 x_1_71_5
   + 337.609690425 x_1_2_0 + 337.609690425 x_1_2_1 + 337.609690425 x_1_2_2
   + 337.609690425 x_1_2_3 + 337.609690425 x_1_2_4 + 337.609690425 x_1_2_5
   + 525.6983295000001 x_2_71_0 + 525.6983295000001 x_2_71_1
   + 525.6983295000001 x_2_71_2 + 525.6983295000001 x_2_71_3
   + 525.6983295000001 x_2_71_4 + 525.6983295000001 x_2_71_5
   + 337.609690425 x_2_1_0 + 337.609690425 x_2_1_1 + 337.609690425 x_2_1_2
   + 337.609690425 x_2_1_3 + 337.609690425 x_2_1_4 + 337.609690425 x_2_1_5
   + 0 w_0_0 + 0 w_0_1 + 0 w_0_2 + 0 w_0_3 + 0 w_0_4 + 0 w_0_5 + 0 w_71_0
   + 0 w_71_1 + 0 w_71_2 + 0 w_71_3 + 0 w_71_4 + 0 w_71_5 - 100 Constant
Subject To
 1st_con_start_0: x_0_1_0 + x_0_2_0 <= 1
 1st_con_return_0: x_1_71_0 + x_2_71_0 <= 1
 1st_con_start_equ_return-0: x_0_1_0 + x_0_2_0 - x_1_71_0 - x_2_71_0 = 0
 1st_con_start_1: x_0_1_1 + x_0_2_1 <= 1
 1st_con_return_1: x_1_71_1 + x_2_71_1 <= 1
 1st_con_start_equ_return-1: x_0_1_1 + x_0_2_1 - x_1_71_1 - x_2_71_1 = 0
 1st_con_start_2: x_0_1_2 + x_0_2_2 <= 1
 1st_con_return_2: x_1_71_2 + x_2_71_2 <= 1
 1st_con_start_equ_return-2: x_0_1_2 + x_0_2_2 - x_1_71_2 - x_2_71_2 = 0
 1st_con_start_3: x_0_1_3 + x_0_2_3 <= 1
 1st_con_return_3: x_1_71_3 + x_2_71_3 <= 1
 1st_con_start_equ_return-3: x_0_1_3 + x_0_2_3 - x_1_71_3 - x_2_71_3 = 0
 1st_con_start_4: x_0_1_4 + x_0_2_4 <= 1
 1st_con_return_4: x_1_71_4 + x_2_71_4 <= 1
 1st_con_start_equ_return-4: x_0_1_4 + x_0_2_4 - x_1_71_4 - x_2_71_4 = 0
 1st_con_start_5: x_0_1_5 + x_0_2_5 <= 1
 1st_con_return_5: x_1_71_5 + x_2_71_5 <= 1
 1st_con_start_equ_return-5: x_0_1_5 + x_0_2_5 - x_1_71_5 - x_2_71_5 = 0
 1st_con_flow_balance-1_0: x_0_1_0 - x_1_71_0 - x_1_2_0 + x_2_1_0 <= 0
 1st_con_flow_balance-1_1: x_0_1_1 - x_1_71_1 - x_1_2_1 + x_2_1_1 <= 0
 1st_con_flow_balance-1_2: x_0_1_2 - x_1_71_2 - x_1_2_2 + x_2_1_2 <= 0
 1st_con_flow_balance-1_3: x_0_1_3 - x_1_71_3 - x_1_2_3 + x_2_1_3 <= 0
 1st_con_flow_balance-1_4: x_0_1_4 - x_1_71_4 - x_1_2_4 + x_2_1_4 <= 0
 1st_con_flow_balance-1_5: x_0_1_5 - x_1_71_5 - x_1_2_5 + x_2_1_5 <= 0
 1st_con_flow_balance-2_0: x_0_2_0 + x_1_2_0 - x_2_71_0 - x_2_1_0 <= 0
 1st_con_flow_balance-2_1: x_0_2_1 + x_1_2_1 - x_2_71_1 - x_2_1_1 <= 0
 1st_con_flow_balance-2_2: x_0_2_2 + x_1_2_2 - x_2_71_2 - x_2_1_2 <= 0
 1st_con_flow_balance-2_3: x_0_2_3 + x_1_2_3 - x_2_71_3 - x_2_1_3 <= 0
 1st_con_flow_balance-2_4: x_0_2_4 + x_1_2_4 - x_2_71_4 - x_2_1_4 <= 0
 1st_con_flow_balance-2_5: x_0_2_5 + x_1_2_5 - x_2_71_5 - x_2_1_5 <= 0
 1st-con_sate_visit_1: x_1_71_0 + x_1_71_1 + x_1_71_2 + x_1_71_3 + x_1_71_4
   + x_1_71_5 + x_1_2_0 + x_1_2_1 + x_1_2_2 + x_1_2_3 + x_1_2_4 + x_1_2_5
   >= 1
 1st-con_sate_visit_2: x_2_71_0 + x_2_71_1 + x_2_71_2 + x_2_71_3 + x_2_71_4
   + x_2_71_5 + x_2_1_0 + x_2_1_1 + x_2_1_2 + x_2_1_3 + x_2_1_4 + x_2_1_5
   >= 1
 1st-3-con_capacity_sate-1: w_1_0 + w_1_1 + w_1_2 + w_1_3 + w_1_4 + w_1_5
   = 663
 1st-3-con_capacity_sate-2: w_2_0 + w_2_1 + w_2_2 + w_2_3 + w_2_4 + w_2_5
   = 114
 1st-3-con_capacity_vehicle-0: w_1_0 + w_2_0 <= 400
 1st-3-con_capacity_vehicle-1: w_1_1 + w_2_1 <= 400
 1st-3-con_capacity_vehicle-2: w_1_2 + w_2_2 <= 400
 1st-3-con_capacity_vehicle-3: w_1_3 + w_2_3 <= 400
 1st-3-con_capacity_vehicle-4: w_1_4 + w_2_4 <= 400
 1st-3-con_capacity_vehicle-5: w_1_5 + w_2_5 <= 400
 1st-4-con_time_window_0-0_0: var_zeta_0_0 - tau_0_0 <= 0
 1st-4-con_time_window_1-0_0: tau_0_0 >= 0
 1st-4-con_time_window_2-0_0: tau_0_0 <= 1440
 1st-4-con_time_window_3-0_1_0: 2000 x_0_1_0 + tau_0_0 - var_zeta_1_0
   <= 1865.45
 1st-4-con_time_window_3-0_2_0: 2000 x_0_2_0 + tau_0_0 - var_zeta_2_0
   <= 1845.8
 1st-4-con_time_window_0-71_0: var_zeta_71_0 - tau_71_0 <= 0
 1st-4-con_time_window_1-71_0: tau_71_0 >= 0
 1st-4-con_time_window_2-71_0: tau_71_0 <= 1440
 1st-4-con_time_window_0-1_0: var_zeta_1_0 - tau_1_0 <= 0
 1st-4-con_time_window_1-1_0: tau_1_0 >= 44.55
 1st-4-con_time_window_2-1_0: tau_1_0 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_0: 2000 x_1_71_0 - var_zeta_71_0 + tau_1_0
   <= 1865.45
 1st-4-con_time_window_3-1_2_0: 2000 x_1_2_0 + tau_1_0 - var_zeta_2_0
   <= 1868.77
 1st-4-con_time_window_0-2_0: var_zeta_2_0 - tau_2_0 <= 0
 1st-4-con_time_window_1-2_0: tau_2_0 >= 64.2
 1st-4-con_time_window_2-2_0: tau_2_0 <= 1440
 1st-4-con_time_window_3-2_71_0: 2000 x_2_71_0 - var_zeta_71_0 + tau_2_0
   <= 1845.8
 1st-4-con_time_window_3-2_1_0: 2000 x_2_1_0 - var_zeta_1_0 + tau_2_0
   <= 1868.77
 1st-4-con_time_window_0-0_1: var_zeta_0_1 - tau_0_1 <= 0
 1st-4-con_time_window_1-0_1: tau_0_1 >= 0
 1st-4-con_time_window_2-0_1: tau_0_1 <= 1440
 1st-4-con_time_window_3-0_1_1: 2000 x_0_1_1 + tau_0_1 - var_zeta_1_1
   <= 1865.45
 1st-4-con_time_window_3-0_2_1: 2000 x_0_2_1 + tau_0_1 - var_zeta_2_1
   <= 1845.8
 1st-4-con_time_window_0-71_1: var_zeta_71_1 - tau_71_1 <= 0
 1st-4-con_time_window_1-71_1: tau_71_1 >= 0
 1st-4-con_time_window_2-71_1: tau_71_1 <= 1440
 1st-4-con_time_window_0-1_1: var_zeta_1_1 - tau_1_1 <= 0
 1st-4-con_time_window_1-1_1: tau_1_1 >= 44.55
 1st-4-con_time_window_2-1_1: tau_1_1 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_1: 2000 x_1_71_1 - var_zeta_71_1 + tau_1_1
   <= 1865.45
 1st-4-con_time_window_3-1_2_1: 2000 x_1_2_1 + tau_1_1 - var_zeta_2_1
   <= 1868.77
 1st-4-con_time_window_0-2_1: var_zeta_2_1 - tau_2_1 <= 0
 1st-4-con_time_window_1-2_1: tau_2_1 >= 64.2
 1st-4-con_time_window_2-2_1: tau_2_1 <= 1440
 1st-4-con_time_window_3-2_71_1: 2000 x_2_71_1 - var_zeta_71_1 + tau_2_1
   <= 1845.8
 1st-4-con_time_window_3-2_1_1: 2000 x_2_1_1 - var_zeta_1_1 + tau_2_1
   <= 1868.77
 1st-4-con_time_window_0-0_2: var_zeta_0_2 - tau_0_2 <= 0
 1st-4-con_time_window_1-0_2: tau_0_2 >= 0
 1st-4-con_time_window_2-0_2: tau_0_2 <= 1440
 1st-4-con_time_window_3-0_1_2: 2000 x_0_1_2 + tau_0_2 - var_zeta_1_2
   <= 1865.45
 1st-4-con_time_window_3-0_2_2: 2000 x_0_2_2 + tau_0_2 - var_zeta_2_2
   <= 1845.8
 1st-4-con_time_window_0-71_2: var_zeta_71_2 - tau_71_2 <= 0
 1st-4-con_time_window_1-71_2: tau_71_2 >= 0
 1st-4-con_time_window_2-71_2: tau_71_2 <= 1440
 1st-4-con_time_window_0-1_2: var_zeta_1_2 - tau_1_2 <= 0
 1st-4-con_time_window_1-1_2: tau_1_2 >= 44.55
 1st-4-con_time_window_2-1_2: tau_1_2 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_2: 2000 x_1_71_2 - var_zeta_71_2 + tau_1_2
   <= 1865.45
 1st-4-con_time_window_3-1_2_2: 2000 x_1_2_2 + tau_1_2 - var_zeta_2_2
   <= 1868.77
 1st-4-con_time_window_0-2_2: var_zeta_2_2 - tau_2_2 <= 0
 1st-4-con_time_window_1-2_2: tau_2_2 >= 64.2
 1st-4-con_time_window_2-2_2: tau_2_2 <= 1440
 1st-4-con_time_window_3-2_71_2: 2000 x_2_71_2 - var_zeta_71_2 + tau_2_2
   <= 1845.8
 1st-4-con_time_window_3-2_1_2: 2000 x_2_1_2 - var_zeta_1_2 + tau_2_2
   <= 1868.77
 1st-4-con_time_window_0-0_3: var_zeta_0_3 - tau_0_3 <= 0
 1st-4-con_time_window_1-0_3: tau_0_3 >= 0
 1st-4-con_time_window_2-0_3: tau_0_3 <= 1440
 1st-4-con_time_window_3-0_1_3: 2000 x_0_1_3 + tau_0_3 - var_zeta_1_3
   <= 1865.45
 1st-4-con_time_window_3-0_2_3: 2000 x_0_2_3 + tau_0_3 - var_zeta_2_3
   <= 1845.8
 1st-4-con_time_window_0-71_3: var_zeta_71_3 - tau_71_3 <= 0
 1st-4-con_time_window_1-71_3: tau_71_3 >= 0
 1st-4-con_time_window_2-71_3: tau_71_3 <= 1440
 1st-4-con_time_window_0-1_3: var_zeta_1_3 - tau_1_3 <= 0
 1st-4-con_time_window_1-1_3: tau_1_3 >= 44.55
 1st-4-con_time_window_2-1_3: tau_1_3 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_3: 2000 x_1_71_3 - var_zeta_71_3 + tau_1_3
   <= 1865.45
 1st-4-con_time_window_3-1_2_3: 2000 x_1_2_3 + tau_1_3 - var_zeta_2_3
   <= 1868.77
 1st-4-con_time_window_0-2_3: var_zeta_2_3 - tau_2_3 <= 0
 1st-4-con_time_window_1-2_3: tau_2_3 >= 64.2
 1st-4-con_time_window_2-2_3: tau_2_3 <= 1440
 1st-4-con_time_window_3-2_71_3: 2000 x_2_71_3 - var_zeta_71_3 + tau_2_3
   <= 1845.8
 1st-4-con_time_window_3-2_1_3: 2000 x_2_1_3 - var_zeta_1_3 + tau_2_3
   <= 1868.77
 1st-4-con_time_window_0-0_4: var_zeta_0_4 - tau_0_4 <= 0
 1st-4-con_time_window_1-0_4: tau_0_4 >= 0
 1st-4-con_time_window_2-0_4: tau_0_4 <= 1440
 1st-4-con_time_window_3-0_1_4: 2000 x_0_1_4 + tau_0_4 - var_zeta_1_4
   <= 1865.45
 1st-4-con_time_window_3-0_2_4: 2000 x_0_2_4 + tau_0_4 - var_zeta_2_4
   <= 1845.8
 1st-4-con_time_window_0-71_4: var_zeta_71_4 - tau_71_4 <= 0
 1st-4-con_time_window_1-71_4: tau_71_4 >= 0
 1st-4-con_time_window_2-71_4: tau_71_4 <= 1440
 1st-4-con_time_window_0-1_4: var_zeta_1_4 - tau_1_4 <= 0
 1st-4-con_time_window_1-1_4: tau_1_4 >= 44.55
 1st-4-con_time_window_2-1_4: tau_1_4 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_4: 2000 x_1_71_4 - var_zeta_71_4 + tau_1_4
   <= 1865.45
 1st-4-con_time_window_3-1_2_4: 2000 x_1_2_4 + tau_1_4 - var_zeta_2_4
   <= 1868.77
 1st-4-con_time_window_0-2_4: var_zeta_2_4 - tau_2_4 <= 0
 1st-4-con_time_window_1-2_4: tau_2_4 >= 64.2
 1st-4-con_time_window_2-2_4: tau_2_4 <= 1440
 1st-4-con_time_window_3-2_71_4: 2000 x_2_71_4 - var_zeta_71_4 + tau_2_4
   <= 1845.8
 1st-4-con_time_window_3-2_1_4: 2000 x_2_1_4 - var_zeta_1_4 + tau_2_4
   <= 1868.77
 1st-4-con_time_window_0-0_5: var_zeta_0_5 - tau_0_5 <= 0
 1st-4-con_time_window_1-0_5: tau_0_5 >= 0
 1st-4-con_time_window_2-0_5: tau_0_5 <= 1440
 1st-4-con_time_window_3-0_1_5: 2000 x_0_1_5 + tau_0_5 - var_zeta_1_5
   <= 1865.45
 1st-4-con_time_window_3-0_2_5: 2000 x_0_2_5 + tau_0_5 - var_zeta_2_5
   <= 1845.8
 1st-4-con_time_window_0-71_5: var_zeta_71_5 - tau_71_5 <= 0
 1st-4-con_time_window_1-71_5: tau_71_5 >= 0
 1st-4-con_time_window_2-71_5: tau_71_5 <= 1440
 1st-4-con_time_window_0-1_5: var_zeta_1_5 - tau_1_5 <= 0
 1st-4-con_time_window_1-1_5: tau_1_5 >= 44.55
 1st-4-con_time_window_2-1_5: tau_1_5 <= 344.9630793903856
 1st-4-con_time_window_3-1_71_5: 2000 x_1_71_5 - var_zeta_71_5 + tau_1_5
   <= 1865.45
 1st-4-con_time_window_3-1_2_5: 2000 x_1_2_5 + tau_1_5 - var_zeta_2_5
   <= 1868.77
 1st-4-con_time_window_0-2_5: var_zeta_2_5 - tau_2_5 <= 0
 1st-4-con_time_window_1-2_5: tau_2_5 >= 64.2
 1st-4-con_time_window_2-2_5: tau_2_5 <= 1440
 1st-4-con_time_window_3-2_71_5: 2000 x_2_71_5 - var_zeta_71_5 + tau_2_5
   <= 1845.8
 1st-4-con_time_window_3-2_1_5: 2000 x_2_1_5 - var_zeta_1_5 + tau_2_5
   <= 1868.77
Bounds
 w_0_0 <= 400
 var_zeta_0_0 <= 1236
 tau_0_0 <= 1236
 w_0_1 <= 400
 var_zeta_0_1 <= 1236
 tau_0_1 <= 1236
 w_0_2 <= 400
 var_zeta_0_2 <= 1236
 tau_0_2 <= 1236
 w_0_3 <= 400
 var_zeta_0_3 <= 1236
 tau_0_3 <= 1236
 w_0_4 <= 400
 var_zeta_0_4 <= 1236
 tau_0_4 <= 1236
 w_0_5 <= 400
 var_zeta_0_5 <= 1236
 tau_0_5 <= 1236
 w_71_0 <= 400
 var_zeta_71_0 <= 1236
 tau_71_0 <= 1236
 w_71_1 <= 400
 var_zeta_71_1 <= 1236
 tau_71_1 <= 1236
 w_71_2 <= 400
 var_zeta_71_2 <= 1236
 tau_71_2 <= 1236
 w_71_3 <= 400
 var_zeta_71_3 <= 1236
 tau_71_3 <= 1236
 w_71_4 <= 400
 var_zeta_71_4 <= 1236
 tau_71_4 <= 1236
 w_71_5 <= 400
 var_zeta_71_5 <= 1236
 tau_71_5 <= 1236
 w_1_0 <= 400
 var_zeta_1_0 <= 1236
 tau_1_0 <= 1236
 w_1_1 <= 400
 var_zeta_1_1 <= 1236
 tau_1_1 <= 1236
 w_1_2 <= 400
 var_zeta_1_2 <= 1236
 tau_1_2 <= 1236
 w_1_3 <= 400
 var_zeta_1_3 <= 1236
 tau_1_3 <= 1236
 w_1_4 <= 400
 var_zeta_1_4 <= 1236
 tau_1_4 <= 1236
 w_1_5 <= 400
 var_zeta_1_5 <= 1236
 tau_1_5 <= 1236
 w_2_0 <= 400
 var_zeta_2_0 <= 1236
 tau_2_0 <= 1236
 w_2_1 <= 400
 var_zeta_2_1 <= 1236
 tau_2_1 <= 1236
 w_2_2 <= 400
 var_zeta_2_2 <= 1236
 tau_2_2 <= 1236
 w_2_3 <= 400
 var_zeta_2_3 <= 1236
 tau_2_3 <= 1236
 w_2_4 <= 400
 var_zeta_2_4 <= 1236
 tau_2_4 <= 1236
 w_2_5 <= 400
 var_zeta_2_5 <= 1236
 tau_2_5 <= 1236
 Constant = 1
Binaries
 x_0_1_0 x_0_1_1 x_0_1_2 x_0_1_3 x_0_1_4 x_0_1_5 x_0_2_0 x_0_2_1 x_0_2_2
 x_0_2_3 x_0_2_4 x_0_2_5 x_1_71_0 x_1_71_1 x_1_71_2 x_1_71_3 x_1_71_4
 x_1_71_5 x_1_2_0 x_1_2_1 x_1_2_2 x_1_2_3 x_1_2_4 x_1_2_5 x_2_71_0 x_2_71_1
 x_2_71_2 x_2_71_3 x_2_71_4 x_2_71_5 x_2_1_0 x_2_1_1 x_2_1_2 x_2_1_3
 x_2_1_4 x_2_1_5
End
