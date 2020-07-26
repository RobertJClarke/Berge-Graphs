# Combinatorics and graph theory utility functions.

import networkx as nx

from itertools import combinations, permutations, chain

import uuid
import random

def empty(S):
    return len(S) == 0

def union(F):
    if empty(F):
        return set()

    return set.union(*F)

def intersection(F):
    if empty(F):
        return set()
    
    return set.intersection(*F)

def arbitrary_element(S):
    return next(iter(S))

def distinct(iterable):
    return len(iterable) == len(set(iterable))

def pairwise_disjoint(sets):
    U = union(sets)
    n = sum([len(u) for u in sets])
    return n == len(U)

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def subsets_upto(iterable, k):
    for x in powerset(iterable):
        if len(x) > k:
            return

        yield x

def edge_exists(graph : nx.Graph, v1, v2):
    return graph.has_edge(v1, v2)

def edges_between(graph : nx.Graph, us, vs):
    edges = set()

    for u in us:
        for v in vs:
            if graph.has_edge(u, v):
                edges |= {(u, v)}

    return edges

def adj_any(graph : nx.Graph, u, vs):
    return any([graph.has_edge(u, v) for v in vs])

def vertex_set(graph : nx.Graph):
    return set(graph.nodes)

def edge_set(graph : nx.Graph):
    return set(graph.edges)

def neighbourhood(graph : nx.Graph, vs):
    if graph.has_node(vs):
        return set(graph.neighbors(vs))

    return union([set(graph.neighbors(v)) for v in vs] + [set()])

def unique_vertex():
    return str(uuid.uuid4())

def vertex_combinations(graph : nx.Graph, n):
    for combo in combinations(graph.nodes, n):
        yield combo

def shortest_path(graph : nx.Graph, u, v):
    try:
        return nx.shortest_path(graph, u, v)
    except nx.NetworkXNoPath:
        return None

def shortest_path_sets(graph : nx.Graph, A : set, B : set):
    # Find a shortest path between two connected sets of verts

    for a in A:
        for b in B:
            if graph.has_edge(a, b):
                return [a, b]

    F = nx.Graph(graph.subgraph(vertex_set(graph) - (A | B)))

    F.add_nodes_from(("a", "b"))

    for (u, v) in edge_set(graph):
        if u in A:
            F.add_edge("a", v)
        elif v in A:
            F.add_edge(u, "a")

        if u in B:
            F.add_edge("b", v)
        elif v in B:
            F.add_edge(u, "b")

    P = shortest_path(F, "a", "b")

    if P is None:
        return None

    new_a = (A & neighbourhood(graph, P[ 1])).pop()
    new_b = (B & neighbourhood(graph, P[-2])).pop()

    return [new_a] + P[1:-1] + [new_b]


def all_shortest_paths(graph : nx.Graph, u, v):
    if nx.has_path(graph, u, v):
        return nx.all_shortest_paths(graph, u, v)
    else:
        return []

def shortest_path_without_interior_vertices(graph : nx.Graph, v1, v2, forbidden_verts):
    for path in all_shortest_paths(graph, v1, v2):
        interior = set(path[1:-1])

        if interior.isdisjoint(forbidden_verts):
            return path

    return None

def shortest_path_without_interior_neighbours(graph : nx.Graph, v1, v2, forbidden_neighbours):
    for path in all_shortest_paths(graph, v1, v2):
        interior = path[1:-1]

        N = neighbourhood(graph, interior)

        if N.isdisjoint(forbidden_neighbours):
            return path

    return None

def is_connected(graph : nx.Graph):
    return nx.is_connected(graph)

def length_k_paths_step(graph : nx.Graph, k, v, prevs):

    if k == 0:
        yield []
        return

    if k == 1:
        yield [v]
        return

    for u in (neighbourhood(graph, v) - set(prevs)):
        for path in length_k_paths_step(graph, k-1, u, prevs + [v]):
            yield [v] + path

def length_k_paths(graph : nx.Graph, k):
    for v in vertex_set(graph):
        for path in length_k_paths_step(graph, k, v, []):
            yield path

def complete_verts(graph : nx.Graph, X):
    # Returns all the X-complete vertices in the graph.
    return intersection([neighbourhood(graph, x) for x in X])

# def to_label(v):
#     if isinstance(v, igraph.Vertex):
#         v = v.index

#     return str(v)

# def to_labels(vs):
#     return [to_label(v) for v in vs]

# def from_label(label):
#     return int(label)

# def from_labels(labels):
#     return [from_label(label) for label in labels]

# def original_index(graph : igraph.Graph, v, param="name"):
#     return from_label(graph.vs[v][param])

# def original_indices(graph : igraph.Graph, vs, param="name"):
#     return [original_index(graph, v, param) for v in vs]

# def new_index(graph : igraph.Graph, v, param="name"):
#     for u in graph.vs:
#         if u[param] == to_label(v):
#             return u.index

# def new_indices(graph : igraph.Graph, vs, param="name"):
#     return [new_index(graph, v, param) for v in vs]

# def label(graph : igraph.Graph, param="name"):
#     # Name all the vertices of the graph with their current index.
#     # Now if we take a subgraph, we can still refer to each vertex
#     # by its original index

#     for v in graph.vs:
#         v[param] = to_label(v)

# def clear_labels(graph : igraph.Graph, param="name"):
#     for v in graph.vs:
#         v[param] = None

def components(graph : nx.Graph, S : set):
    return (set(comp) for comp in nx.connected_components(graph.subgraph(S)))

def anticomponents(graph : nx.Graph, S : set):
    return components(nx.complement(graph), S)


def path_through(graph : nx.Graph, S, u, v):
    # Returns a path from u to v in G with all its interior vertices in S if 
    # one exists.

    S = set(S) | {u, v}

    return shortest_path(graph.subgraph(S), u, v)

def is_k_regular(graph : nx.Graph, k):
    for v in graph.nodes:
        if graph.degree(v) != k:
            return False

    return True

def is_cycle(graph : nx.Graph):
    return (nx.is_connected(graph) and is_k_regular(graph, 2))


def random_bipartite(n1, n2, p):
    return nx.algorithms.bipartite.generators.random_graph(n1, n2, p)

def random_chordal(n, p):
    graph = nx.Graph()

    for v in range(n):
        graph.add_node(v)

        for u in range(v+1, n+1):
            if random.random() < p * (n-v)/n:
                graph.add_edge(v, u)

        neighbours = [u for u in neighbourhood(graph, v) if u > v]

        for e in combinations(neighbours, 2):
            graph.add_edge(*e)

    return graph
