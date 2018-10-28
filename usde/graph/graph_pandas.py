import pandas as pd
from usde.graph.graph_base import BaseGraph


# Graph object implemented by pandas
class PandasGraph(BaseGraph):
    def __init__(self):
        BaseGraph.__init__(self)
        # a dict of node data frames and edge data frames
        # key=label, value=dataframe
        self.nodes_df = {}
        self.edges_df = {}

    def export_all_CSV(self, prefix):
        # get node data frames
        n_df = self.get_nodes()
        for key in n_df.keys():
            # convert data frame to csv
            n_df[key].to_csv(prefix + "_" + key + "_node.csv",
                             encoding="utf-8", index=False)
        # get edge data frames
        e_df = self.get_edges()
        for key in e_df.keys():
            # convert data frame to csv
            e_df[key].to_csv(prefix + "_" + key + "_edge.csv",
                             encoding="utf-8", index=False)

    # export data frame to csv specified by node label and edge label
    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        if len(node_option) > 0:
            # get node data frames
            n_df = self.get_nodes()
            for key in n_df.keys():
                # if matches node label that user wants
                if key in node_option:
                    n_df[key].to_csv(prefix + "_" + key +
                                     "_node.csv", encoding="utf-8", index=False)
        if len(edge_option) > 0:
            # get edge data frames
            e_df = self.get_edges()
            for key in e_df.keys():
                 # if matches edge label that user wants
                if key in edge_option:
                    e_df[key].to_csv(prefix + "_" + key +
                                     "_edge.csv", encoding="utf-8", index=False)

    def create_node(self, node):
        node_label = node.get_label_attribute()
        # if there is no data frame for this label
        if node_label not in self.nodes_df:
            # create a data frame and add to dict with label as the key
            self.nodes_df[node_label] = pd.DataFrame.from_dict([vars(node)])
        # if there is data frame for this label
        else:
            # create a new data frame and append it to original data frame in dict
            self.nodes_df[node_label] = self.nodes_df[node_label].append(
                pd.DataFrame.from_dict([vars(node)]))

    def create_edge(self, edge):
        edge_label = edge.get_label_attribute()
        # if there is no data frame for this label
        if edge_label not in self.edges_df:
            # create a data frame and add to dict with label as the key
            self.edges_df[edge_label] = pd.DataFrame.from_dict([vars(edge)])
        # if there is data frame for this label
        else:
            # create a new data frame and append it to original data frame in dict
            self.edges_df[edge_label] = self.edges_df[edge_label].append(
                pd.DataFrame.from_dict([vars(edge)]))

    def get_nodes(self):
        """ returns all node dataframes """
        return self.nodes_df

    def get_edges(self):
        """ returns all edge dataframes """
        return self.edges_df

    def get_df(self, node_df, edge_df):
        """ returns specified dataframes """
        dataframes = {
            "node": {},
            "edge": {}
        }
        for node in node_df:
            if node in self.nodes_df:
                dataframes["node"][node] = self.nodes_df[node]
        for edge in edge_df:
            if edge in self.edges_df:
                dataframes["edge"][edge] = self.edges_df[edge]
        return dataframes

    def get_df_single(self, name, _type="node"):
        """ returns a single specified dataframe """
        if _type == "node":
            if name in self.nodes_df:
                return self.nodes_df[name]
        else:
            if name in self.edges_df:
                return self.edges_df[name]
