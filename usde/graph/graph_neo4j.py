from py2neo import Graph

from usde.graph.graph_base import BaseGraph


class NeoGraph(BaseGraph):
    def __init__(self, credentials):
        BaseGraph.__init__(self)
        self.graph = Graph(credentials)

    def export_all_CSV(self, prefix):
        query = "MATCH (n) RETURN n"
        table = self.graph.run(query).to_table()
        csv_file = open(prefix + ".csv", "w")
        table.write_csv(file=csv_file)
        csv_file.close()

    def export_CSV(self, prefix, node_option=set()):
        for key in node_option:
            query = "MATCH (n:" + key + ") RETURN n"
            csv_file = open(prefix + "_" + key + ".csv", "w")
            self.graph.run(query).to_table().write_csv(file=csv_file)

    def export_CSV_attr(self, prefix, node_option={}):
        for key in node_option:
            query = ["MATCH (n:", key, ") RETURN "]
            csv_file = open(prefix + "_" + key + "_node.csv", "w")
            if not node_option[key]:
                query.append("n")
                query = ''.join(query)
                self.graph.run(query).to_table().write_csv(file=csv_file)
            else:
                for attribute in node_option[key]:
                    query.append("n.")
                    query.append(attribute)
                    query.append(",")
                query.pop()
                query = ''.join(query)
                self.graph.run(query).to_table().write_csv(file=csv_file)
            csv_file.close()

    def export_CSV_query(self, prefix, query, params):
        table = self.graph.run(query, params=params).to_table()
        csv_file = open(prefix + ".csv", "w")
        table.write_csv(file=csv_file)

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
        return self.graph.run("MATCH (n) RETURN n").to_table()

    def get_edges(self):
        pass

    def execute(self, query, param={}):
        self.graph.run(query, parameters=param)
