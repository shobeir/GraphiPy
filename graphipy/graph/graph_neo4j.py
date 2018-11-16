from py2neo import Graph
import os
import csv
import pprint

from graphipy.graph.graph_base import BaseGraph


class NeoGraph(BaseGraph):
    def __init__(self, credentials):
        BaseGraph.__init__(self)
        self._type = "neo4j"
        self.graph = Graph(credentials)
        self.path = os.getcwd() + "\\csv"
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def graph_type(self):
        return self._type

    def get_labels(self, cursor, _type):
        labels = []
        if _type == "node":
            for record in cursor:
                for l in record:
                    labels.append(l)
        else:
            for record in cursor:
                labels.append(record["type(n)"])
        return labels

    def export_helper(self, labels, _type, prefix):
        """ helper function for export """

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

        for label in labels:

            if _type == "node":
                query = "MATCH (n) WHERE n.label_attribute = '" + \
                    label + "' RETURN n"
            else:
                query = "MATCH (m)-[n:`" + label + "`]->(o) RETURN n"

            data = self.graph.run(query).data()
            if not data:
                return

            if _type == "node":
                path = export_path_node
            else:
                path = export_path_edge

            if not os.path.exists(export_path):
                os.mkdir(export_path)

            with open(
                    path + label + ".csv",
                    "w", newline="", encoding="utf-8") as outfile:
                w = csv.DictWriter(
                    outfile, data[0]["n"].keys(), extrasaction="ignore")
                w.writeheader()
                for record in data:
                    w.writerow(record["n"])

        return export_path

    def export_all_csv(self, prefix):
        """ exports the whole graph as CSV file and returns path to file """

        query = "MATCH (n) WHERE EXISTS (n.label_attribute) RETURN DISTINCT n.label_attribute"
        cursor = self.graph.run(query)
        labels = self.get_labels(cursor, "node")
        self.export_helper(labels, "node", prefix)

        query = "MATCH (m)-[n]->(o) RETURN distinct type(n)"
        cursor = self.graph.run(query).data()
        labels = self.get_labels(cursor, "edge")
        return self.export_helper(labels, "edge", prefix)

    def export_csv(self, prefix, node_option=set(), edge_option=set()):
        """ exports selected nodes as separate CSV files and returns path to file """

        self.export_helper(node_option, "node", prefix)
        return self.export_helper(edge_option, "edge", prefix)

    def export_csv_attr(self, prefix, node_option={}, edge_option=set()):
        """
        allows user to select specific attributes for each node 
        node_option = {
            "node_label": [attribute1, attribute2, attribute3, ...]
        }

        if no attribute is specified, returns all the attributes

        function returns path to file exported
        """

        # Create folders to export to
        export_path = self.path + "\\" + prefix + "\\"
        export_path_node = export_path + "nodes\\"

        if not os.path.exists(export_path):
            os.mkdir(export_path)

        if not os.path.exists(export_path_node):
            os.mkdir(export_path_node)

        for key in node_option:
            query = ["MATCH (n:`", key.lower(), "`) RETURN "]
            csv_file = open(export_path_node + key + ".csv", "w")
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

        return self.export_helper(edge_option, "edge", prefix)

    def create_node(self, node):
        """ Inserts a node into the graph """
        parameter_dict = {'params': vars(node)}
        query_list = [
            "MERGE (node: `",
            node.Label,
            "` {_id: '",
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
            "'}) MERGE(source)-[r:`",
            edge.Label,
            "`]->(target) SET r = {params}"
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
        return self.graph.run(query, parameters=param)

    def delete_graph(self):
        """ Deletes all nodes and relationships in the graph """
        self.graph.run("MATCH (n) DETACH DELETE n")
