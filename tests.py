# /usr/bin python3

import networkx as nx
import numpy as np

from util import *
from multiprocessing import Pool
import random
import sys

def test_random_chordal():
    for i in range(1, 100):
        assert(nx.is_chordal(random_chordal(i, p=random.random())))

def test_find_jewel(pool : Pool):

    from jewel import find_jewel

    for i in range(10):
        # Bipartite graphs and their complements never have jewels
        graph = random_bipartite(n1=20, n2=20, p=.5)
        assert(find_jewel(graph, pool) is None)
        assert(find_jewel(nx.complement(graph), pool) is None)

    assert(find_jewel(nx.cycle_graph(4), pool) is None)
    assert(find_jewel(nx.cycle_graph(5), pool) is not None)
    assert(find_jewel(nx.cycle_graph(6), pool) is None)

    assert(find_jewel(nx.petersen_graph(), pool) is not None)

    assert(find_jewel(nx.house_graph(), pool) is None)

def test_find_pyramid(pool : Pool):

    from pyramid import find_pyramid

    # Assuming the frame of the pyramid is returned in the order
    # (a, b0, b1, b2, s0, s1, s2, m0, m1, m2)

    for i in range(10):
        # Bipartite graphs and their complements never have pyramids
        graph = random_bipartite(n1=7, n2=7, p=.5)
        assert(find_pyramid(graph, pool) is None)
        assert(find_pyramid(nx.complement(graph), pool) is None)

    # Pyramid on 6 vertices
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 5), (4, 5)])

    assert(find_pyramid(graph, pool) == (5, 2, 0, 1, 2, 3, 4, 2, 0, 1))

    # Pyramid on 7 vertices
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 6), (4, 6), (5, 6)])
    assert(find_pyramid(graph, pool) == (6, 0, 1, 2, 3, 4, 5, 0, 1, 2))

    # Pyramid on 10 vertices
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 8), (0, 9), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6), (5, 7), (6, 8), (7, 9), (8, 9)])
    assert(find_pyramid(graph, pool) == (3, 0, 8, 9, 2, 4, 5, 1, 6, 7))

    graph = nx.frucht_graph()
    assert(find_pyramid(graph, pool) is not None)
    # Not sure we have correct output for the Frucht graph

    A = np.array([
        [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0], 
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0], 
        [1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0], 
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], 
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0], 
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1], 
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0], 
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]]
    )

    graph = nx.from_numpy_array(A)

    assert(find_pyramid(graph, pool)[:7] == (0, 4, 3, 6, 4, 1, 5))

def test_near_cleaners(pool : Pool):

    from near_cleaners import is_near_cleaner
    from extras import is_near_cleaner_wasteful

    for i in range(5):
        graph = nx.fast_gnp_random_graph(11, .25)

        for X in subsets_upto(vertex_set(graph), 2):
            a = is_near_cleaner_wasteful(X, graph, pool)
            b = is_near_cleaner(X, graph)

            # The outputs are not always equal but b -> a
            if (b):
                assert(a)

def test_config_T2(pool : Pool):

    from configurations import find_config_T2

    graph = nx.cycle_graph(7)

    graph.add_node(7)
    graph.add_edge(7, 0)
    graph.add_edge(7, 1)
    graph.add_edge(7, 3)

    x = find_config_T2(graph, pool)

    assert(x is not None)
    assert(x[:4] == (0, 1, 2, 3))
    assert(set(x[4]) == {7})
    assert(set(x[5]) == {0, 3, 4, 5, 6})

    for i in range(10):
        graph = random_bipartite(n1=12, n2=12, p=.5)
        assert(find_config_T2(graph, pool) is None)
        assert(find_config_T2(nx.complement(graph), pool) is None)

def test_config_T3(pool : Pool):

    from configurations import find_config_T3

    graph = nx.Graph()

    graph.add_edges_from((
        (0, 1), (2, 3), (0, 3), (1, 2), (2, 4), (3, 5) 
    ))

    graph.add_edges_from((
        (6, 0), (6, 1), (6, 4),
        (7, 0), (7, 1), (7, 4),
    ))

    graph.add_edges_from((
        (4, 8), (8, 9), (9, 5),
    ))

    x = find_config_T3(graph, pool)

    assert(x is not None)
    assert(x[:6] == (0, 1, 2, 3, 4, 5))
    assert(set(x[6]) == {6, 7})
    assert(set(x[7]) == {4, 8, 9, 5})

    for i in range(10):
        graph = random_bipartite(n1=12, n2=12, p=.5)
        assert(find_config_T3(graph, pool) is None)
        assert(find_config_T3(nx.complement(graph), pool) is None)

def test_is_berge(pool : Pool, alt=False):
    
    if alt:
        from alternate import is_berge_alt as is_berge
    else:
        from berge import is_berge

    # Note that graphs are perfect iff they are Berge

    for i in range(5):
        # Bipartite graphs are always Berge

        n1, n2 = random.randint(1, 12), random.randint(1, 12)
        
        graph = random_bipartite(n1=n1, n2=n2, p=.4)

        assert(is_berge(graph, pool=pool))

    for i in range(5):
        graph = nx.line_graph(random_bipartite(n1=10, n2=10, p=.15))

        # Line graphs of bipartite graphs are perfect by Konig's theorem

        assert(is_berge(graph, pool=pool))

    for i in range(10, 15):
        assert(is_berge(nx.complete_graph(i),  pool=pool))

    for i in range(5):

        # Make sure we work properly on disconnected graphs

        graph = nx.disjoint_union_all([
            random_bipartite(
                random.randint(1, 6), 
                random.randint(1, 6), .2) 
            for i in range(3)])

        assert(is_berge(graph,  pool=pool))

    for i in range(5):
        m = random.randint(2, 12)

        graph = nx.triangular_lattice_graph(m, 2)

        assert(is_berge(graph, pool=pool))

    for i in range(5):
        n = random.randint(4, 20)

        graph = random_chordal(n, .2)

        assert(is_berge(graph, pool=pool))

    for i in range(10):
        n = random.randint(4, 20)

        graph = nx.cycle_graph(n)

        assert(is_berge(graph, pool=pool) == (n % 2 == 0))


def main():

    if len(sys.argv) > 1:
        n_cores = int(sys.argv[1])
    else:
        n_cores = None

    with Pool(n_cores) as pool:

        test_random_chordal()

        #test_find_jewel(pool)

        #test_find_pyramid(pool)

        #test_near_cleaners(pool)

        #test_config_T2(pool)

        #test_config_T3(pool)

        test_is_berge(pool)

        print("All tests passed.")

if __name__ == "__main__":
    main()