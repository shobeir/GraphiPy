import pandas as pd


class Graph:
    def __init__(self, option="pandas"):
        self.option = option
        self.node_count = 0
        self.edge_count = 0
        if option == "neo4j":
            pass
        elif option == "pandas":
            self.nodes = {}
            self.edges = {}
            self.nodes_df = {}
            self.edges_df = {}
        else:
            self.nodes = nodes_dict
            self.edges = edges_dict

    def export_all_CSV(self, prefix):
        if self.option == "pandas":
            nodes = self.get_nodes()
            for key in nodes.keys():
                nodes[key].to_csv(prefix + "_" + key +
                                  "_node.csv", encoding="utf-8", index=False)
            edges = self.get_edges()
            for key in edges.keys():
                edges[key].to_csv(prefix + "_" + key +
                                  "_edge.csv", encoding="utf-8", index=False)

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        if self.option == "pandas":
            if len(node_option) > 0:
                nodes = self.get_nodes()
                for key in nodes.keys():
                    if key in node_option:
                        nodes[key].to_csv(
                            prefix + "_" + key + "_node.csv", encoding="utf-8", index=False)
            if len(edge_option) > 0:
                edges = self.get_edges()
                for key in edges.keys():
                    if key in edge_option:
                        edges[key].to_csv(prefix + "_" + key +
                                          "edge.csv", encoding="utf-8", index=False)

    def create_node(self, node):
        label = node.get_label_attribute()
        _id = node.get_id()
        if self.option == "neo4j":
            pass
        else:
            if label not in self.nodes:
                self.nodes[label] = {}
                if self.option == "pandas":
                    self.nodes_df[label] = pd.DataFrame(
                        columns=vars(node).keys())
            self.nodes[label][_id] = node

        self.node_count += 1
        if (self.node_count == 1000):
            self.generate_df("node")

    def generate_df(self, option):
        if option == "node":
            for key in self.nodes_df:
                nodes_list = []
                for _id in self.nodes[key]:
                    nodes_list.append(vars(self.nodes[key][_id]))
                df = pd.DataFrame(nodes_list)
                self.nodes_df[key] = self.nodes_df[key].append(
                    df, sort=False, ignore_index=True)
                self.nodes[key] = {}
            self.node_count = 0

        else:
            for key in self.edges_df:
                edges_list = []
                for _id in self.edges[key]:
                    edges_list.append(vars(self.edges[key][_id]))
                df = pd.DataFrame(edges_list)
                self.edges_df[key] = self.edges_df[key].append(
                    df, sort=False, ignore_index=True)
                self.edges[key] = {}
            self.edge_count = 0

    def create_edge(self, edge):
        label = edge.get_label_attribute()
        _id = edge.get_id()
        if self.option == "neo4j":
            pass
        else:
            if label not in self.edges:
                self.edges[label] = {}
                if self.option == "pandas":
                    self.edges_df[label] = pd.DataFrame(
                        columns=vars(edge).keys())
            self.edges[label][_id] = edge

        self.edge_count += 1
        if (self.edge_count == 2000):
            self.generate_df("edge")

    def get_nodes(self):
        if self.option == "pandas":
            return self.nodes_df
        return self.nodes

    def get_edges(self):
        if self.option == "pandas":
            return self.edges_df
        return self.edges

    def get_dataFrame(self, dataFrame_type="pandas"):
        if dataFrame_type is "pandas":
            node_list = []
            edge_list = []
            for _id in self.nodes:
                attributes = vars(self.nodes[_id])
                node_list.append(attributes)
            for _id in self.edges:
                attributes = vars(self.edges[_id])
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
    def __init__(self, _id, label, label_attribute):
        self._id = _id
        self.label = label
        self.label_attribute = label_attribute

    def get_id(self):
        return self._id

    def get_label_attribute(self):
        return self.label_attribute


class Edge:
    def __init__(self, source, target, label):
        self.Source = source
        self.Target = target
        self.label = label
        self.label_attribute = label

    def get_id(self):
        return self.Source + self.Target

    def get_label_attribute(self):
        return self.label_attribute
