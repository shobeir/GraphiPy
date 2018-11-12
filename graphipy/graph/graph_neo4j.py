from py2neo import Graph
import csv
import pprint

from graphipy.graph.graph_base import BaseGraph


class NeoGraph(BaseGraph):
    def __init__(self, credentials):
        BaseGraph.__init__(self)
        self.graph = Graph(credentials)

    def get_labels(self, cursor, _type):
        labels = []
        if _type == "node":
            for record in cursor:
                for l in record["labels(n)"]:
                    labels.append(l)
        else:
            for record in cursor:
                labels.append(record["type(n)"])
        return labels

    def export_helper(self, labels, _type, prefix):

        for label in labels:

            if _type == "node":
                query = "MATCH (n:" + label + ") RETURN n"
            else:
                query = "MATCH (m)-[n:" + label + "]->(o) RETURN n"

            data = self.graph.run(query).data()
            if not data:
                return

            with open(
                    prefix + "_" + label + "_" + _type + ".csv",
                    "w", newline="", encoding="utf-8") as outfile:
                w = csv.DictWriter(
                    outfile, data[0]["n"].keys(), extrasaction="ignore")
                w.writeheader()
                for record in data:
                    w.writerow(record["n"])

    def export_all_CSV(self, prefix):
        """ exports the whole graph as CSV file """
        query = "MATCH (n) RETURN distinct labels(n)"
        cursor = self.graph.run(query).data()
        labels = self.get_labels(cursor, "node")
        self.export_helper(labels, "node", prefix)

        query = "MATCH (m)-[n]->(o) RETURN distinct type(n)"
        cursor = self.graph.run(query).data()
        labels = self.get_labels(cursor, "edge")
        self.export_helper(labels, "edge", prefix)

    def export_CSV(self, prefix, node_option=set(), edge_option=set()):
        """ exports selected nodes as separate CSV files """

        self.export_helper(node_option, "node", prefix)
        self.export_helper(edge_option, "node", prefix)

    def export_CSV_attr(self, prefix, node_option={}, edge_option=set()):
        """
        allows user to select specific attributes for each node 
        node_option = {
            "node_label": [attribute1, attribute2, attribute3, ...]
        }

        if no attribute is specified, returns all the attributes
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

        self.export_helper(edge_option, "edge", prefix)

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
        """ returns a neo4j cursor of all the nodes """
        return self.graph.run("MATCH (n) RETURN n").data()

    def get_edges(self):
        """ returns a neo4j cursor of all the edges """
        return self.graph.run("MATCH (n)-[r]->(m) RETURN r").data()

    def execute(self, query, param={}):
        """ Allows users to execute their own query """
        self.graph.run(query, parameters=param)

    def delete_graph(self):
        self.graph.run("MATCH (n) DETACH DELETE n")
