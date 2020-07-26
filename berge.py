# This code is an implementation of the algorithms given in the paper
# "Recognising Berge Graphs" - Chudnovsky, Cornuéjols, Liu, Seymour and Vušcović 2003

import networkx as nx

from multiprocessing import Pool
from functools import partial

from jewel import find_jewel
from configurations import find_config_T2, find_config_T3
from pyramid import find_pyramid
from cleaning import cleaning
from near_cleaners import is_near_cleaner


def check_subgraphs(graph : nx.Graph, Gc : nx.Graph, pool : Pool):
    # First we check the graph and its compliment for some subgraphs
    # This is routine 2

    if find_jewel(graph, pool):
        return False

    if find_jewel(Gc, pool):
        return False

    if find_config_T2(graph, pool):
        return False

    if find_config_T2(Gc, pool):
        return False

    if find_config_T3(graph, pool):
        return False

    if find_config_T3(Gc, pool):
        return False

    if find_pyramid(graph, pool):
        return False

    if find_pyramid(Gc, pool):
        return False

    return True


def is_berge(graph : nx.Graph, n_cores=None, pool = None):

    if pool is None:
        pool = Pool(n_cores)

    Gc = nx.complement(graph)

    if not check_subgraphs(graph, Gc, pool):
        return False

    check = partial(is_near_cleaner, graph=graph)

    for near_cleaner_found in pool.imap_unordered(check, cleaning(graph)):
        if (near_cleaner_found):
            return False

    check = partial(is_near_cleaner, graph=Gc)

    for near_cleaner_found in pool.imap_unordered(check, cleaning(Gc)):
        if (near_cleaner_found):
            return False

    return True