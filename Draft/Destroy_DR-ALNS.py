# -*- coding: utf-8 -*-
# @Time     : 2024-08-09-15:37
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import copy
from numpy import random
import numpy as np


class NeighborGraph:
    def __init__(self, num_nodes):
        self.graph = np.full((num_nodes + 1, num_nodes + 1), np.inf, dtype=np.float64)

    def update_edge(self, node_a, node_b, cost):
        # graph is kept single directional
        self.graph[node_a][node_b] = cost

    def get_edge_weight(self, node_a, node_b):
        return self.graph[node_a][node_b]


def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def determine_nr_nodes_to_remove(nb_customers, omega_bar_minus=5, omega_minus=0.1, omega_bar_plus=50, omega_plus=0.4):
    n_plus = min(omega_bar_plus, omega_plus * nb_customers)
    n_minus = min(n_plus, max(omega_bar_minus, omega_minus * nb_customers))
    r = random.randint(round(n_minus), round(n_plus))
    return r


def relatedness_removal(current, random_state, nr_nodes_to_remove=None, prob=5):
    destroyed_solution = copy.deepcopy(current)
    visited_customers = [customer for route in destroyed_solution.routes for customer in route]

    if nr_nodes_to_remove is None:
        nr_nodes_to_remove = determine_nr_nodes_to_remove(destroyed_solution.nb_customers)

    node_to_remove = random_state.choice(visited_customers)
    for route in destroyed_solution.routes:
        while node_to_remove in route:
            route.remove(node_to_remove)
            visited_customers.remove(node_to_remove)

    for i in range(nr_nodes_to_remove - 1):
        related_nodes = []
        normalized_distances = NormalizeData(destroyed_solution.dist_matrix_data[node_to_remove - 1])
        route_node_to_remove = [route for route in current.routes if node_to_remove in route][0]
        for route in destroyed_solution.routes:
            for node in route:
                if node in route_node_to_remove:
                    related_nodes.append((node, normalized_distances[node - 1]))
                else:
                    related_nodes.append((node, normalized_distances[node - 1] + 1))

        if random_state.random() < 1 / prob:
            node_to_remove = random_state.choice(visited_customers)
        else:
            node_to_remove = min(related_nodes, key=lambda x: x[1])[0]
        for route in destroyed_solution.routes:
            while node_to_remove in route:
                route.remove(node_to_remove)
                visited_customers.remove(node_to_remove)
    destroyed_solution.routes = [route for route in destroyed_solution.routes if route != []]

    return destroyed_solution


# --- neighbor/history graph removal
# see: A unified heuristic for a large class of Vehicle Routing Problems with Backhauls
def neighbor_graph_removal(current, random_state, nr_nodes_to_remove=None, prob=5):
    destroyed_solution = copy.deepcopy(current)

    if nr_nodes_to_remove is None:
        nr_nodes_to_remove = determine_nr_nodes_to_remove(destroyed_solution.nb_customers)

    values = {}
    for route in destroyed_solution.routes:
        if len(route) == 1:
            values[route[0]] = current.graph.get_edge_weight(0, route[0]) + current.graph.get_edge_weight(route[0], 0)
        else:
            for i in range(len(route)):
                if i == 0:
                    values[route[i]] = current.graph.get_edge_weight(0, route[i]) + current.graph.get_edge_weight(
                        route[i], route[1])
                elif i == len(route) - 1:
                    values[route[i]] = current.graph.get_edge_weight(route[i - 1],
                                                                     route[i]) + current.graph.get_edge_weight(
                        route[i], 0)
                else:
                    values[route[i]] = current.graph.get_edge_weight(route[i - 1],
                                                                     route[i]) + current.graph.get_edge_weight(
                        route[i], route[i + 1])

    removed_nodes = []
    while len(removed_nodes) < nr_nodes_to_remove:
        # sort the nodes based on their neighbor graph scores in descending order
        sorted_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)
        # select the node to remove
        removal_option = 0
        while random_state.random() < 1 / prob and removal_option < len(sorted_nodes) - 1:
            removal_option += 1
        node_to_remove, score = sorted_nodes[removal_option]

        # remove the node from its route
        for route in destroyed_solution.routes:
            if node_to_remove in route:
                route.remove(node_to_remove)
                removed_nodes.append(node_to_remove)

                values.pop(node_to_remove)
                if len(route) == 0:
                    destroyed_solution.routes.remove([])

                elif len(route) == 1:
                    values[route[0]] = current.graph.get_edge_weight(0, route[0]) + current.graph.get_edge_weight(
                        route[0], 0)
                else:
                    for i in range(len(route)):
                        if i == 0:
                            values[route[i]] = current.graph.get_edge_weight(0, route[
                                i]) + current.graph.get_edge_weight(route[i], route[1])
                        elif i == len(route) - 1:
                            values[route[i]] = current.graph.get_edge_weight(route[i - 1], route[
                                i]) + current.graph.get_edge_weight(route[i], 0)
                        else:
                            values[route[i]] = current.graph.get_edge_weight(route[i - 1], route[
                                i]) + current.graph.get_edge_weight(route[i], route[i + 1])

                break

    return destroyed_solution
