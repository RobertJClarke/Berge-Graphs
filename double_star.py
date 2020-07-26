import networkx as nx
from util import *

from multiprocessing import Pool
from functools import partial

def double_star_cutset_combinations(graph : nx.Graph):
    Gc = nx.complement(graph)

    for u, v in graph.edges:
        for comp in nx.connected_components(graph):
            for x, y in Gc.subgraph(comp).edges():
                yield (u, v, x, y)

def check_double_star_cutset(vs, graph : nx.Graph):
    u, v, x, y = vs

    S = (neighbourhood(graph, {u, v}) | {u, v})

    if x in S or y in S:
        return None

    if not nx.has_path(graph.subgraph(vertex_set(graph) - S), x, y):
        return S

    return None

def find_double_star_cutset(graph : nx.Graph, pool : Pool):
    check = partial(check_double_star_cutset, graph=graph)

    
    if pool is not None:
        for cutset in pool.imap_unordered(check, double_star_cutset_combinations(graph), chunksize=4096):
            if cutset:
                return cutset

    else:
        for vs in double_star_cutset_combinations(graph):
            cutset = check(vs)

            if cutset:
                return cutset

    return None

def double_star_decomposition(graph : nx.Graph, pool : Pool):
    
    next_ = {graph}

    while not empty(next_):
        F = next_.pop()

        flag = False

        for u, v in vertex_combinations(F, 2):
            path = shortest_path(graph, u, v)

            if path and len(path) > 4:
                flag = True
                break

        if not flag:
            continue

        S = find_double_star_cutset(F, pool)

        if S is None:
            yield F
            continue

        for H in nx.connected_components(F.subgraph(vertex_set(F)-S)):
            next_.add(graph.subgraph(set(H | S)))