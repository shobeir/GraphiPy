import csv
import os
from graphipy.graph.graph_base import BaseGraph


# Graph object implemented by dict
class DictGraph(BaseGraph):
    def __init__(self):
        BaseGraph.__init__(self)
        # a dict of nodes and edges, key=label, value={id, node}
        self.nodes = {}
        self.edges = {}

        self.path = os.getcwd() + "\\csv"
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def export_all_csv(self, prefix):
        """ Exports all dictionaries as CSV files and returns path to file """

        # Create folders to export to
        export_path = self.path + "\\" + prefix + "\\"
        export_path_node = export_path + "nodes\\"
        export_path_edge = export_path + "edges\\"

        if not os.path.exists(export_path):
            os.mkdir(export_path)

        if not os.path.exists(export_path_node):
            os.mkdir(export_path_node)

        if not os.path.exists(export_path_edge):
            os.mkdir(export_path_edge)

        nodes = self.get_nodes()
        edges = self.get_edges()

        for key in nodes:
            # create a csv file and write in data
            with open(export_path_node + key + ".csv", "w", newline='', encoding="utf-8") as f:
                w = csv.writer(f)
                has_first_row = False
                for node_key in nodes[key]:
                    # if title row has not been created
                    if has_first_row == False:
                        # create the title row
                        key_row = vars(nodes[key][node_key]).keys()
                        w.writerow([s for s in key_row])
                        has_first_row = True
                    # add value row to csv file
                    value_row = vars(nodes[key][node_key]).values()
                    w.writerow([s for s in value_row])

        for key in edges:
            # create a csv file and write in data
            with open(export_path_edge + key + ".csv", "w", newline='', encoding="utf-8") as f:
                w = csv.writer(f)
                has_first_row = False
                for edge_key in edges[key]:
                    # if title row has not been created
                    if has_first_row == False:
                        # create the title row
                        key_row = vars(edges[key][edge_key]).keys()
                        w.writerow([s for s in key_row])
                        has_first_row = True
                    # add value row to csv file
                    value_row = vars(edges[key][edge_key]).values()
                    w.writerow([s for s in value_row])

        return export_path

    # export data frame to csv specified by node label and edge label
    def export_csv(self, prefix, node_option=set(), edge_option=set()):
        """ Exports specific nodes and edges as CSV files and returns path to file """

        # Create folders to export to
        export_path = self.path + "\\" + prefix + "\\"
        export_path_node = export_path + "nodes\\"
        export_path_edge = export_path + "edges\\"

        if not os.path.exists(export_path):
            os.mkdir(export_path)

        if not os.path.exists(export_path_node):
            os.mkdir(export_path_node)

        if not os.path.exists(export_path_edge):
            os.mkdir(export_path_edge)

        if len(node_option) > 0:
            # get all nodes
            nodes = self.get_nodes()
            for key in nodes.keys():
                # if matches node label that user wants
                if key in node_option:
                    # create a csv file and write in data
                    with open(export_path_node + key + ".csv", "w", newline='', encoding="utf-8") as f:
                        w = csv.writer(f)
                        has_first_row = False
                        # iterate through {id, node}
                        for node_key in nodes[key]:
                            # if title row has not been created
                            if has_first_row == False:
                                # create the title row
                                key_row = vars(nodes[key][node_key]).keys()
                                w.writerow([s for s in key_row])
                                has_first_row = True
                            # add value row to csv file
                            value_row = vars(nodes[key][node_key]).values()
                            w.writerow([s for s in value_row])

        if len(edge_option) > 0:
            # get all edges
            edges = self.get_edges()
            for key in edges.keys():
                # if matches edge label that user wants
                if key in edge_option:
                    # create a csv file and write in data
                    with open(export_path_edge + key + ".csv", "w", newline='', encoding="utf-8") as f:
                        w = csv.writer(f)
                        has_first_row = False
                        # iterate through {id, node}
                        for edge_key in edges[key]:
                            # if title row has not been created
                            if has_first_row == False:
                                key_row = vars(edges[key][edge_key]).keys()
                                w.writerow([s for s in key_row])
                                has_first_row = True
                            # add value row to csv file
                            value_row = vars(edges[key][edge_key]).values()
                            w.writerow([s for s in value_row])

        return export_path

    def create_node(self, node):
        node_label = node.get_label_attribute()
        node_id = node.get_id()
        # if no dict for this label in nodes{}, create a new dict with key=label
        if node_label not in self.nodes:
            self.nodes[node_label] = {}
        # add node to {id, node} in {label, {id, node}}
        self.nodes[node_label][node_id] = node

    def create_edge(self, edge):
        edge_label = edge.get_label_attribute()
        edge_id = edge.get_id()
        # if no dict for this label in edges{}, create a new dict with key=label
        if edge_label not in self.edges:
            self.edges[edge_label] = {}
        # add edge to {id, edge} in {label, {id, edge}}
        self.edges[edge_label][edge_id] = edge

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges
