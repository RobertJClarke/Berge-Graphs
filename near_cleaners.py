import networkx as nx

from util import *

def is_near_cleaner(X, graph : nx.Graph):
    # Algorithm 5.1

    # Takes a pyramid and jewel free graph, and a subset of its vertices X,
    # and returns True iff there is a shortest odd hole C s.t. X is a
    # near cleaner for C, false otherwise

    X = set(X)

    inf = float("inf")

    R = dict()
    r = dict()

    for x in vertex_set(graph):
        for y in vertex_set(graph):
            R[(x, y)] = shortest_path_without_interior_vertices(graph, x, y, X)

            if R[(x, y)]:
                r[(x, y)] = len(R[(x, y)])
            else:
                r[(x, y)] = inf

    for y1 in vertex_set(graph) - X:
        for x1, x3, x2 in length_k_paths(graph, 3):
            
            if y1 in (x1, x3, x2):
                continue

            if edge_exists(graph, x1, x2):
                continue
            
            if r[(x1, y1)] == inf:
                continue

            if r[(x2, y1)] == inf:
                continue
            
            y2 = R[(x2, y1)][-2]
            n = r[(x1, y2)]

            if r[(x2, y1)] == r[(x1, y1)]+1 == n:
                if r[(x3, y1)] >= n:
                    if r[(x3, y2)] >= n:
                        return True

    return False
