from py2neo import Graph

from usde.graph.graph_base import BaseGraph


class NeoGraph(BaseGraph):
    def __init__(self, credentials):
        BaseGraph.__init__(self)
        self.graph = Graph(credentials)

    def export_all_CSV(self, prefix):
        """ exports the whole graph as CSV file """
        query = "MATCH (n) RETURN n"
        table = self.graph.run(query).to_table()
        csv_file = open(prefix + ".csv", "w")
        table.write_csv(file=csv_file)
        csv_file.close()

    def export_CSV(self, prefix, node_option=set()):
        """ exports selected nodes as separate CSV files """
        for key in node_option:
            query = "MATCH (n:" + key.lower() + ") RETURN n"
            csv_file = open(prefix + "_" + key + ".csv", "w")
            self.graph.run(query).to_table().write_csv(file=csv_file)

    def export_CSV_attr(self, prefix, node_option={}):
        """
        allows user to select specific attributes for each node 
        node_option = {
            "node_label": [attribute1, attribute2, attribute3, ...]
        }
        """

        for key in node_option:
            query = ["MATCH (n:", key.lower(), ") RETURN "]
            csv_file = open(prefix + "_" + key + "_node.csv", "w")
            if not node_option[key]:
                query.append("n")
                query = ''.join(query)
                self.graph.run(query).to_table().write_csv(file=csv_file)
            else:
                for attribute in node_option[key]:
                    query.append("n.")
                    query.append(attribute.lower())
                    query.append(",")
                query.pop()
                query = ''.join(query)
                self.graph.run(query).to_table().write_csv(file=csv_file)
            csv_file.close()

    def export_CSV_query(self, prefix, query, params):
        """
        Allows users to run their own query and exports
        to CSV if applicable
        """

        table = self.graph.run(query, parameters=params).to_table()
        csv_file = open(prefix + ".csv", "w")
        table.write_csv(file=csv_file)

    def create_node(self, node):
        """ Inserts a node into the graph """
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
        """ Creates a relationship between two nodes """
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
        """ returns a table of all the nodes """
        return self.graph.run("MATCH (n) RETURN n").to_table()

    def get_edges(self):
        """ usde's NeoGraphh does not support querying edge """
        pass

    def execute(self, query, param={}):
        """ Allows users to execute their own query """
        self.graph.run(query, parameters=param)
