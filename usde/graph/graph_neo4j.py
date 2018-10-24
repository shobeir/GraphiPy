from py2neo import Graph

from usde.graph.graph_base import BaseGraph


class NeoGraph(BaseGraph):
    def __init__(self, credentials):
        BaseGraph.__init__(self)
        self.graph = Graph(credentials)

    def export_all_CSV(self, prefix):
        pass

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        pass

    def create_node(self, node):
        parameter_dict = {'params': vars(node)}
        query_list = [
            "MERGE (node: ",
            node.Label,
            " {_id: '",
            node.get_id(),
            "'}) SET node = {params}"
        ]
        query = ''.join(query_list)
        self.graph.run(query, parameters=parameter_dict)

    def create_edge(self, edge):
        source = edge.Source
        target = edge.Target
        parameter_dict = {'params': vars(edge)}
        query_list = [
            "MATCH (source {_id: '",
            source,
            "'}) MATCH(target {_id: '",
            target,
            "'}) MERGE(source)-[r:",
            edge.Label,
            "]->(target) SET r = {params}"
        ]
        query = ''.join(query_list)
        self.graph.run(query, parameters=parameter_dict)

    def get_nodes(self):
        pass

    def get_edges(self):
        pass

    def execute(self, query, param={}):
        self.graph.run(query, parameters=param)
