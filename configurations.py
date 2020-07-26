# Algorithms to detect the three "configurations" from section 6 of the paper.

import networkx as nx

from util import *

from multiprocessing import Pool
from functools import partial

def check_config_T2(vs, graph : nx.Graph):
    # Algorithm 6.1

    v1, v2, v3, v4 = vs

    if any({   
            edge_exists(graph, *e)
            for e in {(v1, v3), (v1, v4), (v2, v4)}
        }):
        return None

    Y = complete_verts(graph, {v1, v2, v4})

    for X in anticomponents(graph, Y):

        U = (vertex_set(graph) - 
        ({v2, v3} | neighbourhood(graph, v2) | neighbourhood(graph, v3)
        | set(X) | complete_verts(graph, X)))

        P = path_through(graph, U, v1, v4)

        if P:
            return (v1, v2, v3, v4, X, P)

    return None

def find_config_T2(graph : nx.Graph, pool : Pool):

    check = partial(check_config_T2, graph=graph)

    for config in pool.imap_unordered(check, length_k_paths(graph, 4), chunksize=4096):
        if config is not None:
            return config

    return None

def check_config_T3(vs, graph : nx.Graph, return_config=True):
    #Algorithm 6.4

    v1, v2, v5 = vs

    if (not edge_exists(graph, v1, v2) 
        or edge_exists(graph, v1, v5) 
        or edge_exists(graph, v2, v5)):
        return None

    Gc = nx.complement(graph)

    Y = complete_verts(graph, {v1, v2, v5})

    for X in anticomponents(graph, Y):
        X_complete_verts = complete_verts(graph, X)

        F_prime = {v5}
        next_ = neighbourhood(graph, v5)
        seen = set()

        while len(next_) != 0:
            u = next_.pop()
            seen.add(u)

            if not (u in X_complete_verts 
                or edge_exists(graph, u, v1) 
                or edge_exists(graph, u, v2)):

                F_prime.add(u)
                next_.update(neighbourhood(graph, u) - seen)

        F = F_prime | (X_complete_verts & neighbourhood(graph, F_prime) - neighbourhood(graph, {v1, v2, v5}))

        U = ( (neighbourhood(graph, v1) - neighbourhood(graph, {v2, v5})) 
            & neighbourhood(graph, F) & neighbourhood(Gc, X) )

        for v4 in U:
            W = (complete_verts(graph, {v2, v4, v5}) & neighbourhood(Gc, X)) - neighbourhood(graph, v1)

            if len(W) != 0:
                # We know there is a congifuration of type T3 in the graph. We 
                # now just complete it and return it.

                v3 = W.pop()
                v6 = (neighbourhood(graph, v4) & F).pop()

                P = path_through(graph, F_prime, v5, v6)

                return (v1, v2, v3, v4, v5, v6, X, P)


def find_config_T3(graph : nx.Graph, pool : Pool):
    check = partial(check_config_T3, graph=graph)

    for config in pool.imap_unordered(check, vertex_combinations(graph, 3), chunksize=4096):
        if config is not None:
            return config

    return None
