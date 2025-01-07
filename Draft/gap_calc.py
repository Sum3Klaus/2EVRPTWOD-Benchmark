# -*- coding: utf-8 -*-
# @Time     : 2024-11-15-11:31
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import math


def calc(minuend,
         subtrahend,
         denominator):
    gap = minuend - subtrahend
    gap_rate = gap / denominator

    return gap, gap_rate


def denominator_5(num):

    return num / 5


def calc_rate(num_1,
              num_2):
    return num_1 / num_2

""" gap and gap rate """
a, b, c = 4339.333319, 9867.803467, 9867.803467
result_gap, result_rate = calc(minuend=a,
                               subtrahend=b,
                               denominator=c)
print(result_gap, result_rate)

""" -5 """
# d = 4010.48
# print(denominator_5(num=d))

""" rate """
# print(calc_rate(num_1=802.096,
#                 num_2=765.91))
