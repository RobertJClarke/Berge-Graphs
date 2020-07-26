import networkx as nx

from util import *

from multiprocessing import Pool
from functools import partial
from itertools import combinations
import enum

def check_5_hole(vs, graph : nx.Graph):
    hole = graph.subgraph(vs)

    if is_cycle(hole):
        return vs

def find_5_hole(graph : nx.Graph, pool : Pool):
    check = partial(check_5_hole, graph=graph)


    if pool is not None:
        for hole in pool.imap_unordered(check, vertex_combinations(graph, 5), chunksize=4096):
            if hole:
                return hole

    else:
        for vs in vertex_combinations(graph, 5):
            hole = check(vs)

            if hole:
                return hole

    return None

def check_7_hole(vs, graph : nx.Graph):

    hole = graph.subgraph(vs)

    if is_cycle(hole):
        return vs

def find_7_hole(graph : nx.Graph, pool : Pool):
    check = partial(check_7_hole, graph=graph)

    if pool is not None:
        for hole in pool.imap_unordered(check, vertex_combinations(graph, 7), chunksize=4096):
            if hole:
                return hole

    else:
        for vs in vertex_combinations(graph, 7):
            hole = check(vs)

            if hole:
                return hole

    return None

class TwoJoin():
    def __init__(self):
        self.V1 = set()
        self.V2 = set()
        self.A1 = set()
        self.A2 = set()
        self.B1 = set()
        self.B2 = set()

    def __str__(self):
        return str((self.V1, self.V2, self.A1, self.A2, self.B1, self.B2))

class ValidationResult(enum.Enum):
    NO_2_JOIN    = enum.auto()
    VALID_2_JOIN = enum.auto()
    RETRY        = enum.auto()


def validate_2_join(graph : nx.Graph, join : TwoJoin):
    if (len(join.V2) == 2 or 
       (len(join.A2) == len(join.B2) == 1 and 
        nx.is_simple_path(graph, join.V2))):
            
            return ValidationResult.NO_2_JOIN

    elif (len(join.A1) >= 2 or 
          len(join.B1) >= 2 or 
          not nx.is_simple_path(graph, join.V1)):

            return ValidationResult.VALID_2_JOIN

    else:
        return ValidationResult.RETRY

def apply_movement_rules(graph : nx.Graph, V1, V2, a1, a2, b1, b2):

    to_move = V1

    res = TwoJoin()

    res.V2 = V1 | V2
    res.V1 = set()

    forbidden = complete_verts(graph, {a2, b2})

    N_a2 = neighbourhood(graph, a2)
    N_b2 = neighbourhood(graph, b2)

    while not empty(to_move):
        if not to_move.isdisjoint(forbidden):
            return None

        res.V1.update(to_move)
        res.V2 -= to_move
        to_move.clear()

        res.A1 = res.V1 & N_a2
        res.B1 = res.V1 & N_b2
        AB = (res.A1 | res.B1)
        S = res.V1 - AB

        to_move.update(res.V2 & neighbourhood(graph, S))

        for v in (res.V2 & neighbourhood(graph, AB)):
            if not (neighbourhood(graph, v) & AB) in (res.A1, res.B1):
                to_move.add(v)

    res.A2 = res.V2 & neighbourhood(graph, res.A1)
    res.B2 = res.V2 & neighbourhood(graph, res.B1)

    return res

def two_join_combinations(graph : nx.Graph):

    for (a1, a2), (b1, b2) in combinations(graph.edges, 2):
        
        if graph.has_edge(a1, b2) or graph.has_edge(a2, b1):
            continue

        for u in vertex_set(graph) - (complete_verts(graph, {a2, b2}) ):
            
            if distinct((a1, a2, b1, b2, u)):
                yield (a1, a2, b1, b2, u)

def check_2_join(vs, graph : nx.Graph):
    a1, a2, b1, b2, u = vs

    V1 = {a1, b1, u}
    V2 = vertex_set(graph) - V1

    join = apply_movement_rules(graph, V1, V2, a1, a2, b1, b2)

    if join is None:
        return None

    res = validate_2_join(graph, join)

    if res == ValidationResult.NO_2_JOIN:
        return None

    elif res == ValidationResult.VALID_2_JOIN:
        return join

    elif res == ValidationResult.RETRY:
        for h in join.V2 - {a2, b2}:
            new_V1 = {a1, b1, u, h}
            new_V2 = vertex_set(graph) - new_V1

            join = apply_movement_rules(graph, new_V1, new_V2, a1, a2, b1, b2)

            if join is None:
                continue

            if validate_2_join(graph, join) == ValidationResult.VALID_2_JOIN:
                return join

    return None

def find_2_join(graph : nx.Graph, pool : Pool):
    check = partial(check_2_join, graph=graph)

    if pool is not None:
        for join in pool.imap_unordered(check, two_join_combinations(graph), chunksize=4096):
            if join:
                return join

    else:
        for vs in two_join_combinations(graph):
            join = check(vs)
            if join:
                return join

    return None

def block(graph : nx.Graph, V1, V2, A2, B2):
    
    Q = None

    for comp in components(graph, V2):
        A = A2 & comp
        B = B2 & comp

        if not empty(A) and not empty(B):
            new = shortest_path_sets(graph.subgraph(comp), A, B)

            if Q is None or len(new) < len(Q):
                Q = new
    
    if Q is None:
        a = arbitrary_element(A2)
        b = arbitrary_element(B2)

        return graph.subgraph(V1 | {a, b})

    a = Q[ 0]
    b = Q[-1]

    F = nx.Graph(graph.subgraph(V1 | {a, b}))

    v1 = unique_vertex()
    v2 = unique_vertex()
    v3 = unique_vertex()

    if len(Q) % 2 == 0:
        F.add_edges_from(( 
            (a, v1),
            (v1, v2),
            (v2, b)
        ))

    else:
        F.add_edges_from(( 
            (a, v1),
            (v1, v2),
            (v2, v3),
            (v3, b)
        ))

    return F

def blocks(graph : nx.Graph, join : TwoJoin):
    return (
        block(graph, join.V1, join.V2, join.A2, join.B2),
        block(graph, join.V2, join.V1, join.A1, join.B1)
    )

ODD_HOLE_FOUND = object()

def two_join_decomposition(graph : nx.Graph, pool : Pool):

    next_ = {graph}

    while not empty(next_):
        F = next_.pop()

        join = find_2_join(F, pool)

        if join is None:
            yield F
            continue

        if empty(join.V1 - (join.A1 | join.B1)) and empty(join.V2 - (join.A2 | join.B2)):
            continue

        for block, V in zip(blocks(graph, join), (join.V1, join.V2)):
            if len(V) <= 7:
                if find_5_hole(block, pool) or find_7_hole(block, pool):
                    yield ODD_HOLE_FOUND
                    return

            else:
                next_.add(block)