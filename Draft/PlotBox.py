# -*- coding: utf-8 -*-
# @Time     : 2024-09-29-9:57
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163

import matplotlib.pyplot as plt
import numpy as np








# 示例数据
data = [[4161.041066,
         4161.041066,
         4161.041066,
         4173.147788,
         4173.147788,
         ],
        [4333.925327,
         4323.69404,
         4289.61279,
         4372.401483,
         4245.788117,
         ]
        ]

# 创建箱线图
plt.boxplot(data, patch_artist=True)

# 设置y轴的取值范围
plt.ylim(3000, 4500)

# 设置x轴的命名
plt.xticks([1, 2], ['MyAlns', 'Alns'])

# 设置标题和轴标签
plt.title('Boxplot Example')
plt.xlabel('Groups')
plt.ylabel('Values')

# 显示图形
plt.show()
