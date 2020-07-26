import networkx as nx
from util import *

from multiprocessing import Pool
from functools import partial

from cleaning import cleaning
from berge import check_subgraphs
from double_star import double_star_decomposition
from two_join import find_7_hole, two_join_decomposition, ODD_HOLE_FOUND

def is_basic(graph : nx.Graph):
    
    if nx.is_bipartite(graph):
        return True

    try:
        inv = nx.inverse_line_graph(graph)
    except nx.NetworkXError:
        return False

    if nx.is_bipartite(inv) or nx.is_bipartite(nx.complement(inv)):
        return True

    return False

def cleaning_alt(graph : nx.Graph):
    potential_cleaners = set()

    for X in cleaning(graph):
        for Y in subsets_upto(X, 3):
            potential_cleaners.add(Y)

    return potential_cleaners

def is_odd_hole_free(graph : nx.Graph, pool : Pool):

    L1 = double_star_decomposition(graph, pool)
    L2 = set()

    for H in L1:
        for new in two_join_decomposition(graph.subgraph(H), pool):
            if new == ODD_HOLE_FOUND:
                return False

            L2.add(new)

    for H in L2:
        if not is_basic(graph.subgraph(H)):
            return False

    return True

def odd_hole_check(Y, graph : nx.Graph):
    for comp in nx.connected_components(graph.subgraph(vertex_set(graph) - set(Y))):
        if not is_odd_hole_free(graph.subgraph(comp), None):
            return False

    return True

def is_berge_alt(graph : nx.Graph, pool : Pool):
    Gc = nx.complement(graph)

    if not check_subgraphs(graph, Gc, pool):
        return False

    if find_7_hole(graph, pool) or find_7_hole(Gc, pool):
        return False

    check = partial(odd_hole_check, graph=graph)
    
    for odd_hole_free in pool.imap_unordered(check, cleaning_alt(graph)):
        if not odd_hole_free:
            return False

    check = partial(odd_hole_check, graph=Gc)

    for odd_hole_free in pool.imap_unordered(check, cleaning_alt(Gc)):
        if not odd_hole_free:
            return False

    return True