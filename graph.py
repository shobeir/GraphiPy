class Graph:
    def export_all_CSV(self, prefix):
        pass

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        pass

    def create_node(self, node):
        pass

    def create_edge(self, edge):
        pass

    def get_nodes(self):
        pass

    def get_edges(self):
        pass


class Node:
    def __init__(self, _id, label, label_attribute):
        self.Id = _id
        self.Label = label
        self.label_attribute = label_attribute

    def get_id(self):
        return self.Id

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
