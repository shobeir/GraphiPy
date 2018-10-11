class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def create_node(self, node):
        self.nodes[node.get_id()] = node

    def create_edge(self, edge):
        self.edges[edge.get_id()] = edge

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges


class Node:
    def __init__(self, _id):
        self._id = _id

    def get_id(self):
        return self._id


class Edge:
    def __init__(self, _id, _source, _target):
        self._id = _id
        self.source = _source
        self.target = _target

    def get_id(self):
        return self._id
