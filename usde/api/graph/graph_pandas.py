from api.graph.graph import BaseGraph
import pandas as pd


class PandasGraph(BaseGraph):
    def __init__(self):
        BaseGraph.__init__(self)
        self.nodes_df = {}
        self.edges_df = {}

    def export_all_CSV(self, prefix):
        n_df = self.get_nodes()
        for key in n_df.keys():
            n_df[key].to_csv(prefix + "_" + key + "_node.csv",
                             encoding="utf-8", index=False)
        e_df = self.get_edges()
        for key in e_df.keys():
            e_df[key].to_csv(prefix + "_" + key + "_edge.csv",
                             encoding="utf-8", index=False)

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        if len(node_option) > 0:
            n_df = self.get_nodes()
            for key in n_df.keys():
                if key in node_option:
                    n_df[key].to_csv(prefix + "_" + key +
                                     "_node.csv", encoding="utf-8", index=False)
        if len(edge_option) > 0:
            e_df = self.get_edges()
            for key in e_df.keys():
                if key in edge_option:
                    e_df[key].to_csv(prefix + "_" + key +
                                     "_edge.csv", encoding="utf-8", index=False)

    def create_node(self, node):
        node_label = node.get_label_attribute()
        if node_label not in self.nodes_df:
            self.nodes_df[node_label] = pd.DataFrame.from_dict([vars(node)])
        else:
            self.nodes_df[node_label] = self.nodes_df[node_label].append(
                pd.DataFrame.from_dict([vars(node)]))

    def create_edge(self, edge):
        edge_label = edge.get_label_attribute()
        if edge_label not in self.edges_df:
            self.edges_df[edge_label] = pd.DataFrame.from_dict([vars(edge)])
        else:
            self.edges_df[edge_label] = self.edges_df[edge_label].append(
                pd.DataFrame.from_dict([vars(edge)]))

    def get_nodes(self):
        return self.nodes_df

    def get_edges(self):
        return self.edges_df
