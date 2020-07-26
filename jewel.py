import networkx as nx

from util import *

from multiprocessing import Pool
from functools import partial

def check_jewel(vs, graph: nx.Graph):
    # Algorithm 3.1

    v2, v3, v5 = vs

    N_v2 = neighbourhood(graph, v2)

    if v3 not in N_v2:
        return None
    
    N_v3 = neighbourhood(graph, v3)
    N_v5 = neighbourhood(graph, v5)

    F = vertex_set(graph) - (N_v2 | N_v3 | N_v5)
    comps = components(graph, F)

    X1 = N_v2 & N_v5 - N_v3
    X2 = N_v3 & N_v5 - N_v2

    for v1 in X1:
        for v4 in X2:
            if v1 in graph.neighbors(v4):
                continue

            N_v1 = neighbourhood(graph, v1)
            N_v4 = neighbourhood(graph, v4)
            
            for comp in comps:
                if not (N_v1.isdisjoint(comp) or N_v4.isdisjoint(comp)):

                    P = path_through(graph, F, v1, v4)

                    return (v1, v2, v3, v4, v5)

    return None

def find_jewel(graph: nx.Graph, pool : Pool):
    check = partial(check_jewel, graph=graph)

    for jewel in pool.imap_unordered(check, vertex_combinations(graph, 3), chunksize=4096):
        if jewel:
            return jewel

    return None