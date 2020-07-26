# Implementations of extra routines mentioned in the paper which are not needed for the final algorithm.

import networkx as nx

from util import *

from multiprocessing import Pool
from functools import partial
import itertools as it

def check_odd_hole(vs, graph : nx.Graph):
    # Algorithm 4.2

    u, v, w = vs

    uv_path = shortest_path(graph, u, v)

    if (not uv_path):
        return None

    vw_path = shortest_path(graph, v, w)

    if (not vw_path):
        return None

    wu_path = shortest_path(graph, w, u)

    if (not wu_path):
        return None

    if not pairwise_disjoint([set(uv_path), set(vw_path[1:-1]), set(wu_path[:-1])]):
        return None

    cycle = uv_path + vw_path[1:-1] + wu_path[:-1]

    if len(cycle) < 4 or len(cycle) % 2 == 0:
        return None

    for (a, b) in combinations(cycle, 2):
        # Check for chords

        cycle_dist = abs(cycle.index(a) - cycle.index(b))

        if cycle_dist == 1 or cycle_dist == len(cycle)-1:
            # Vertices adjacent in cycle
            continue

        if edge_exists(graph, a, b):
            # Found a chord
            return None

    return cycle

def find_odd_hole(graph : nx.Graph, pool : Pool):
    # NOTE: Our graph is required to be jewel and pyramid free
    # If we return None, the graph is guaranteed to contain
    # no clean shortest odd hole.

    check = partial(check_odd_hole, graph=graph)

    for hole in pool.imap_unordered(check, vertex_combinations(graph, 3), chunksize=512):
        if hole:
            return hole

    return None

def is_near_cleaner_wasteful(X, graph : nx.Graph, pool : Pool):
    for Y in subsets_upto(vertex_set(graph), 3):
        hole = find_odd_hole(graph.subgraph(vertex_set(graph) - (set(X) - set(Y))), pool)
        if hole:
            return True

    return False

def is_berge_naive(graph : nx.Graph, pool : Pool):
    subsets = it.chain.from_iterable(
        ( it.combinations(graph.nodes, k) 
        for k in range(5, len(graph.nodes), 2) )
    )

    graphs = it.chain.from_iterable(
        ( (graph.subgraph(S), nx.complement(graph.subgraph(S))) 
          for S in subsets )
    )

    for hole_found in pool.imap_unordered(is_cycle, graphs, chunksize=4096):
        if hole_found:
            return False

    return True

