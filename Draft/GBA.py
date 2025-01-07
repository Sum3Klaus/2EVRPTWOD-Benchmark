# -*- coding: utf-8 -*-
# @Time     : 2024-08-13-10:22
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
class GreatDelugeAcceptance:
    def __init__(self, initial_water_level, rain_speed, min_water_level):
        self.current_water_level = initial_water_level
        self.rain_speed = rain_speed
        self.min_water_level = min_water_level

    def accept(self, candidate_solution_cost, current_solution_cost):
        # 如果候选解的成本低于当前水位线，则接受解
        if candidate_solution_cost <= self.current_water_level:
            return True

        # 否则，拒绝解
        return False

    def adjust_rain_speed_and_parameters(self, iteration, no_improvement_count):
        # 动态调整水位线
        self.current_water_level -= self.rain_speed

        # 避免水位线低于最小值
        if self.current_water_level < self.min_water_level:
            self.current_water_level = self.min_water_level

        # 如果在多个迭代中没有改进，调整雨速
        if no_improvement_count > 100:
            self.rain_speed *= 0.9  # 减慢雨速
        else:
            self.rain_speed *= 1.1  # 加快雨速

    def reset_parameters(self, initial_water_level, rain_speed):
        self.current_water_level = initial_water_level
        self.rain_speed = rain_speed


# Example usage in ALNS
def alns_with_gda_acceptance():
    initial_solution = generate_initial_solution()
    current_solution = initial_solution
    best_solution = current_solution

    initial_water_level = calculate_initial_water_level(current_solution.cost)
    rain_speed = calculate_initial_rain_speed()
    min_water_level = calculate_min_water_level()

    gda = GreatDelugeAcceptance(initial_water_level, rain_speed, min_water_level)

    iteration = 0
    no_improvement_count = 0

    while not termination_condition():
        candidate_solution = destroy_and_repair(current_solution)
        candidate_solution_cost = candidate_solution.calculate_cost()

        if gda.accept(candidate_solution_cost, current_solution.cost):
            current_solution = candidate_solution
            no_improvement_count = 0
            if candidate_solution_cost < best_solution.cost:
                best_solution = candidate_solution
        else:
            no_improvement_count += 1

        gda.adjust_rain_speed_and_parameters(iteration, no_improvement_count)
        iteration += 1

    return best_solution
