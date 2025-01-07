# -*- coding: utf-8 -*-
# @Time     : 2024-11-21-17:18
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# # Step 1: Define the data
# objectives = ['Tra 2nd', 'Veh 2nd', 'Carbon 2nd', 'Tra 1st', 'Veh 1st', 'Carbon 1st']
# n_objectives = len(objectives)
#
# # Initial solution (baseline, outer boundary)
# baseline = [673.77, 2200, 2069.773063, 83.83111111, 1555.555556, 3100.139202]
#
# # Algorithm solutions as ratios to the baseline (normalized)
# alns1 = [417.0777778, 1013.333333, 1262.184037, 79.52444444, 1000, 471.6572939]
# alns2 = [407.5657778, 1004.444444, 1232.257977, 79.52444444, 1000, 471.6572939]
# alns3 = [394.6764444, 1000, 1191.706362, 79.52444444, 1000, 471.6572939]
#
# # Step 2: Set up the radar chart
# angles = np.linspace(0, 2 * np.pi, n_objectives, endpoint=False).tolist()
# angles += angles[:1]  # Close the circle
#
#
# # Function to plot each algorithm's data
# def plot_radar(ax, data, label, color):
#     data += data[:1]  # Close the polygon
#     ax.plot(angles, data, label=label, color=color, linewidth=2)
#     ax.fill(angles, data, color=color, alpha=0.25)
#
#
# # Initialize radar chart
# fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
#
# # Add baseline
# baseline += baseline[:1]
# ax.plot(angles, baseline, label='Baseline', color='black', linestyle='--', linewidth=1.5)
# ax.fill(angles, baseline, color='gray', alpha=0.1)
#
# # Plot each ALNS algorithm
# plot_radar(ax, alns1, 'ALNS', 'blue')
# plot_radar(ax, alns2, 'GDALNS/T', 'green')
# plot_radar(ax, alns3, 'GDALNS/TD', 'red')
#
# # Step 3: Customize the chart
# ax.set_theta_offset(np.pi / 2)  # Rotate to start at the top
# ax.set_theta_direction(-1)  # Reverse direction to go clockwise
#
# # Add labels for each objective
# ax.set_xticks(angles[:-1])
# ax.set_xticklabels(objectives)
#
# # Set the radial scale
# ax.set_rscale('linear')
# ax.set_ylim(0, 1.1)  # Adjust based on data
#
# # Add a legend and title
# ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
# ax.set_title("Comparison of ALNS Algorithms by Objectives", va='bottom')
#
# # Show the plot
# plt.tight_layout()
# plt.show()

# =========================================================================

# # Step 1: Define the data
# objectives = ['Tra 2nd', 'Veh 2nd', 'Carbon 2nd', 'Tra 1st', 'Veh 1st', 'Carbon 1st']
# n_objectives = len(objectives)
#
# # Initial solution (baseline, outer boundary)
# baseline = np.array([673.77, 2200, 2069.773063, 83.83111111, 1555.555556, 3100.139202])
#
# # Algorithm solutions
# alns1 = np.array([417.0777778, 1013.333333, 1262.184037, 79.52444444, 1000, 471.6572939])
# alns2 = np.array([407.5657778, 1004.444444, 1232.257977, 79.52444444, 1000, 471.6572939])
# alns3 = np.array([394.6764444, 1000, 1191.706362, 79.52444444, 1000, 471.6572939])
#
# # Step 2: Normalize the data relative to the baseline
# alns1_normalized = alns1 / baseline
# alns2_normalized = alns2 / baseline
# alns3_normalized = alns3 / baseline
# baseline_normalized = np.ones_like(baseline)  # Baseline normalized to 1
#
# # Step 3: Set up the radar chart
# angles = np.linspace(0, 2 * np.pi, n_objectives, endpoint=False).tolist()
# angles += angles[:1]  # Close the circle
#
#
# # Function to plot each algorithm's data
# def plot_radar(ax, data, label, color):
#     data = np.append(data, data[0])  # Close the polygon
#     ax.plot(angles, data, label=label, color=color, linewidth=2)
#     ax.fill(angles, data, color=color, alpha=0.25)
#
#
# # Initialize radar chart
# fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
#
# # Add baseline
# plot_radar(ax, baseline_normalized, 'Baseline', 'black')
#
# # Plot each ALNS algorithm
# plot_radar(ax, alns1_normalized, 'ALNS', 'blue')
# plot_radar(ax, alns2_normalized, 'GDALNS/T', 'green')
# plot_radar(ax, alns3_normalized, 'GDALNS/TD', 'red')
#
# # Step 4: Customize the chart
# ax.set_theta_offset(np.pi / 2)  # Rotate to start at the top
# ax.set_theta_direction(-1)  # Reverse direction to go clockwise
#
# # Add labels for each objective
# ax.set_xticks(angles[:-1])
# ax.set_xticklabels(objectives)
#
# # Set the radial scale
# ax.set_ylim(0, 1.1)  # Adjust based on data
#
# # Add a legend and title
# ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
# ax.set_title("Comparison of ALNS Algorithms by Objectives", va='bottom')
#
# # Display the plot
# plt.show()

# =========================================================================
# 数据
objectives = ['Tra 2nd', 'Carbon 2nd', 'Tra 1st', 'Carbon 1st', 'Veh']
baseline = np.array([673.77, 2069.773063, 83.83111111, 1555.555556, 5300.139202])
alns1 = np.array([417.0777778, 1262.184037, 79.52444444, 1000, 1484.990627])
alns2 = np.array([407.5657778, 1232.257977, 79.52444444, 1000, 1476.101738])
alns3 = np.array([394.6764444, 1191.706362, 79.52444444, 1000, 1471.657294])

# 归一化处理
data = np.vstack([baseline, alns1, alns2, alns3])
normalized_data = data / data.max(axis=0)  # 每列归一化

# 配色
colors = ['gray', 'blue', 'green', 'red']
labels = ['Baseline', 'ALNS', 'GDALNS/T', 'GDALNS/TD']

# 绘图
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

# 角度划分
angles = np.linspace(0, 2 * np.pi, len(objectives), endpoint=False).tolist()
angles += angles[:1]  # 闭合圆

# 绘制每个算法的环形
for idx, (algo_data, color, label) in enumerate(zip(normalized_data, colors, labels)):
    algo_data = np.append(algo_data, algo_data[0])  # 闭合数据
    ax.fill(angles, algo_data, color=color, alpha=0.3, label=label)
    ax.plot(angles, algo_data, color=color, linewidth=2)

# 设置标题和标签
ax.set_xticks(angles[:-1])
ax.set_xticklabels(objectives, fontsize=12)
ax.set_ylim(0, 1)  # 归一化范围为 0-1
ax.set_title("Algorithm Performance Comparison", fontsize=16, va='bottom')

# 图例
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.show()