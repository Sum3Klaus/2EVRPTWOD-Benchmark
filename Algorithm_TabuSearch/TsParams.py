# -*- coding: utf-8 -*-
# @Time     : 2024-07-08-11:22
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import random

import numpy as np


class TsParams(object):

    def __init__(self,
                 ins):

        # self.theta = random.randint(0, np.sqrt(ins.customer_num / 2))    # max forbidden iterations
        self.theta = 9
