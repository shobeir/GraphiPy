import pandas as pd


class Graph:
    def __init__(self, nodes_dict={},  edges_dict={}):
        self.nodes = nodes_dict
        self.edges = edges_dict

    def create_node(self, node):
        self.nodes[node.get_id()] = node

    def create_edge(self, edge):
        self.edges[edge.get_id()] = edge

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_dataFrame(self, dataFrame_type="pandas"):
        if dataFrame_type is "pandas":
            node_list = []
            edge_list = []
            for id in self.nodes:
                attributes = vars(self.nodes[id])
                node_list.append(attributes)
            for id in self.edges:
                attributes = vars(self.edges[id])
                edge_list.append(attributes)

            node_df = pd.DataFrame(node_list)
            edge_df = pd.DataFrame(edge_list)
            return {
                "node": node_df,
                "edge": edge_df
            }

    def __add__(self, another_graph):
        nodes_copy = self.nodes.copy()
        edges_copy = self.edges.copy()
        nodes_copy.update(another_graph.get_nodes())
        edges_copy.update(another_graph.get_edges())
        return Graph(nodes_copy, edges_copy)


class Node:
    def __init__(self, _id, _label):
        self.Id = _id
        self.Label = _label

    def get_id(self):
        return self.Id


class Edge:
    def __init__(self, _source, _target):
        self.Source = _source
        self.Target = _target

    def get_id(self):
        return self.Source + self.Target
