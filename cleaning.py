# The cleaning algorithm, from section 9 of the paper

import networkx as nx

from util import *

from multiprocessing import Pool
from functools import partial

def cleaning(graph : nx.Graph):
    # Takes a graph G and outputs am iterator of subsets of V(G) 
    # s.t. if G has an amenable shortest odd hole C, one of them
    # is a near-cleaner for C.

    Gc = nx.complement(graph)

    relevant = (
        (a, b, c)
        for a in vertex_set(graph)
        for b in neighbourhood(Gc, a)
        for c in vertex_set(graph) - complete_verts(graph, {a, b})
    )

    def R(a, b, c):
        S = {
            tuple(X) 
            for X in anticomponents(graph, complete_verts(graph, (a, b))) if not set(X).isdisjoint( neighbourhood(Gc, c) ) 
        }

        if empty(S):
            return 0
        else:
            return max( {len(X) for X in S} )

    def Y(a, b, c):
        r = R(a, b, c)

        return union([
            set(X)
            for X in anticomponents(graph, complete_verts(graph, (a, b)))
            if len(X) > r
        ])

    def W(a, b, c):
        result = {c}
        next_ = neighbourhood(Gc, c)

        while not empty(next_):
            v = next_.pop()
            result.add(v)
            next_.update(neighbourhood(Gc, v) - result)

        return result

    cleaners = set()

    for (a, b, c) in relevant:

        y = Y(a, b, c)
        w = W(a, b, c)

        Z = complete_verts(graph, y | w)
        X = y | Z

        for (u, v) in edge_set(graph):
            cleaners.add( tuple(complete_verts(graph, (u, v)) | X) )

    return cleaners