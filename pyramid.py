import networkx as nx

from multiprocessing import Pool
from functools import partial

from util import *

def pyramid_combinations(graph : nx.Graph):
    # TODO: This can be made better with some reasoning, want to allow
    # s_i = b_i but not s_i = b_j, s_i = s_j or b_i = b_j

    for vs_1 in vertex_combinations(graph, 3):
        for vs_2 in vertex_combinations(graph, 3):
            yield vs_1 + vs_2

def pyramid_find_paths(graph : nx.Graph, M, b, s, i):
    P = {m : None for m in M | {b[i]} }

    if s[i] == b[i]:
        P[b[i]] = [b[i]]
        return P

    if edge_exists(graph, s[i], b[i]):
        # This check is not in the paper

        P[b[i]] = [s[i], b[i]]
        return P

    excluded = b[:i] + b[(i+1):] + s[:i] + s[(i+1):]

    for m in M:

        if adj_any(graph, m, excluded):
            continue

        S = shortest_path_without_interior_neighbours(graph, s[i], m, excluded)

        if not S:
            continue

        T = shortest_path_without_interior_neighbours(graph, m, b[i], excluded)

        if not T:
            continue

        if not set(S) & set(T) == {m}:
            continue

        N = neighbourhood(graph, S[:-1])

        if not N.isdisjoint(T[1:]):
            continue

        P[m] = S + T[1:]

    return P

def pyramid_good_pairs(graph : nx.Graph, P, M, b, i, j):

    good = []

    for m_i in M | {b[i]}:
        if not(P[i][m_i]):
            continue

        excluded = M & (set(P[i][m_i]) | neighbourhood(graph, P[i][m_i]))

        for m_j in M | {b[j]}:
            if not(P[j][m_j]):
                continue

            if excluded.isdisjoint(P[j][m_j]):
                good.append((m_i, m_j))

    return good


def check_pyramid(vs, graph : nx.Graph):
    # Algorithm 2.2

    b = list(vs[:3])
    s = list(vs[3:])

    overlap = set(b) & set(s)

    if len(overlap) > 1:
        return None
    if len(overlap) == 1:
        # If we have exactly one b_i = s_i, put them first in each list

        overlap_v = overlap.pop()

        b.remove(overlap_v)
        s.remove(overlap_v)

        b = tuple([overlap_v] + b)
        s = tuple([overlap_v] + s)

    N_s = [neighbourhood(graph, s[i]) for i in range(3)]

    for j in range(0, 3):
        for i in range(0, j):

            if not(edge_exists(graph, b[i], b[j])):
                return None

            edges = edges_between(graph, [b[i], s[i]], [b[j], s[j]])

            if len(edges) > 1:
                return None

    apex = None

    for v in set.intersection(*N_s):
        if sum([edge_exists(graph, v, b[i]) for i in range(3)]) <= 1:
            apex = v

    if apex is None:
        return None

    M = vertex_set(graph) - set(b + s)

    P = [{}, {}, {}]

    P[0] = pyramid_find_paths(graph, M, b, s, 0)
    P[1] = pyramid_find_paths(graph, M, b, s, 1)
    P[2] = pyramid_find_paths(graph, M, b, s, 2)
        
    good_pairs = [[], [], []]

    good_pairs[0] = pyramid_good_pairs(graph, P, M, b, 0, 1)
    good_pairs[1] = pyramid_good_pairs(graph, P, M, b, 0, 2)
    good_pairs[2] = pyramid_good_pairs(graph, P, M, b, 1, 2)

    for m0 in M | {b[0]}:
        for m1 in M | {b[1]}:
            for m2 in M | {b[2]}:
                if ((m0, m1) in good_pairs[0] and
                    (m0, m2) in good_pairs[1] and
                    (m1, m2) in good_pairs[2]):
                    
                    # We just found an optimal pyramid, return its frame
                    return (apex, b[0], b[1], b[2], s[0], s[1], s[2], m0, m1, m2)

    return None

def find_pyramid(graph : nx.Graph, pool : Pool):
    check = partial(check_pyramid, graph=graph)

    for pyramid in pool.imap_unordered(check, pyramid_combinations(graph), chunksize=4096):
        if pyramid:
            return pyramid

    return None