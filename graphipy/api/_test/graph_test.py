from graphipy.graph.graph_base import BaseEdge, BaseNode
from graphipy.graph.graph_dict import DictGraph
from graphipy.graph.graph_neo4j import NeoGraph
from graphipy.graph.graph_pandas import PandasGraph

import time

PANDAS = False
DICT = False
NEO = False

# PANDAS = True
# DICT = True
# NEO = True


class Node(BaseNode):
    def __init__(self, info):
        BaseNode.__init__(self, info[0], info[1], info[1])
        self.name = info[2]
        self.age = info[3]
        self.gender = info[4]


class Edge(BaseEdge):
    def __init__(self, info):
        BaseEdge.__init__(self, info[0], info[1], info[2])


def main():

    if DICT:
        dict_graph = DictGraph()
    if NEO:
        neo_graph = NeoGraph(" ")
    if PANDAS:
        pd_graph = PandasGraph()

    f = open("sample_data.txt")

    start_time = time.time()
    nodes_count = int(f.readline())

    for i in range(nodes_count):
        line = f.readline().strip()
        line = line.split(",")
        if DICT:
            dict_graph.create_node(Node(line))
        if NEO:
            neo_graph.create_node(Node(line))
        if PANDAS:
            pd_graph.create_node(Node(line))

    edges_count = int(f.readline())
    for i in range(edges_count):
        line = f.readline().strip()
        line = line.split(",")
        if DICT:
            dict_graph.create_edge(Edge(line))
        if NEO:
            neo_graph.create_edge(Edge(line))
        if PANDAS:
            pd_graph.create_edge(Edge(line))

    print("runtime: " + str(time.time() - start_time))

    if DICT:
        dict_graph.export_all_CSV("dict")
    if NEO:
        pass
    if PANDAS:
        pd_graph.export_all_CSV("pandas")
    f.close()


if __name__ == '__main__':
    main()
