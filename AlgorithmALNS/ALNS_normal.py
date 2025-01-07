# -*- coding: utf-8 -*-
# @Time     : 2024-09-12-22:20
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import time
import random
from copy import deepcopy
from math import *
import DualCalculatorNoSelect
import DualCalculator
import ModelBuilderNoSelect
import PricingModelBuilder
from AlnsPara import AlnsParameters
# from GreatDelugeAlgorithm import GreatDelugeAlgorithm
from GreatDelugeAlgorithmTolerance import *
from Common import *
from Route import *
from Solution import Sol
from RandomDestroy import RandomDestroy
from ShawDestroy import ShawDestroy
from WorseDestroy import WorseDestroy
from GreedyRepair import GreedyRepair
from RandomRepair import RandomRepair
from RegretRepair import RegretRepair
from WaitingDestroy import WaitingDestroy
from HistroyBasdDestroy import HistoryBasedDestroy
from ConflictDestroy import ConflictDestroy
from HistoricalArriveDestroy import HistoricalArriveDestroy
from DistanceRepair import DistanceRepair
from DualDestroy import DualDestroy
from DualRepair import DualRepair
from SlackTimeRepair import SlackTimeRepair
from TabuList import TabuList
import itertools


class GbaTsAlns(object):
    destroyList = [RandomDestroy, ShawDestroy, WorseDestroy]
    repairList = [GreedyRepair, RandomRepair, RegretRepair]

    next_iter_time = itertools.count(start=0)