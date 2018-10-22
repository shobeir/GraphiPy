from graph import Graph, Node, Edge
import csv

class Graph_Dict(Graph):
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def export_all_CSV(self, prefix):
        nodes = self.get_nodes()
        edges = self.get_edges()

        for key in nodes:
            with open(prefix + "_" + key + "_node_by_dict.csv", 'w') as f:
                w = csv.writer(f)
                has_first_row = False;
                for id in nodes[key]:
                    if has_first_row == False:
                        key_row = vars(nodes[key][id]).keys()
                        w.writerow([unicode(s).encode("utf-8") for s in key_row])
                        has_first_row = True
                    value_row = vars(nodes[key][id]).values()
                    w.writerow([unicode(s).encode("utf-8") for s in value_row])

        for key in edges:
            with open(prefix + "_" + key + "_edge_by_dict.csv", 'w') as f:
                w = csv.writer(f)
                has_first_row = False;
                for id in edges[key]:
                    if has_first_row == False:
                        key_row = vars(edges[key][id]).keys()
                        w.writerow([unicode(s).encode("utf-8") for s in key_row])
                        has_first_row = True
                    value_row = vars(edges[key][id]).values()
                    w.writerow([unicode(s).encode("utf-8") for s in value_row])

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        if len(node_option) > 0:
            nodes = self.get_nodes()
            for key in nodes.keys():
                if key in node_option:
                    with open(prefix + "_" + key + "_node_by_dict.csv", 'w') as f:
                        w = csv.writer(f)
                        has_first_row = False;
                        for id in nodes[key]:
                            if has_first_row == False:
                                key_row = vars(nodes[key][id]).keys()
                                w.writerow([unicode(s).encode("utf-8") for s in key_row])
                                has_first_row = True
                            value_row = vars(nodes[key][id]).values()
                            w.writerow([unicode(s).encode("utf-8") for s in value_row])
        if len(edge_option) > 0:
            edges = self.get_edges()
            for key in edges.keys():
                if key in edge_option:
                    with open(prefix + "_" + key + "_edge_by_dict.csv", 'w') as f:
                        w = csv.writer(f)
                        has_first_row = False;
                        for id in edges[key]:
                            if has_first_row == False:
                                key_row = vars(edges[key][id]).keys()
                                w.writerow([unicode(s).encode("utf-8") for s in key_row])
                                has_first_row = True
                            value_row = vars(edges[key][id]).values()
                            w.writerow([unicode(s).encode("utf-8") for s in value_row])

    def create_node(self, node):
        node_label = node.get_label_attribute()
        node_id = node.get_id()
        if node_label not in self.nodes:
            self.nodes[node_label] = {}
        self.nodes[node_label][node_id] = node

    def create_edge(self, edge):
        edge_label = edge.get_label_attribute()
        edge_id = edge.get_id()
        if edge_label not in self.edges:
            self.edges[edge_label] = {}
        self.edges[edge_label][edge_id] = edge

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges
