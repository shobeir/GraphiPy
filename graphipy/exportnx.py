import networkx as nx
import random
import os
import csv


class ExportNX:
    def __init__(self):
        pass

    def create_from_pd(self, pd_graph, nx_graph=None, directional=False):

        nodes_df = pd_graph.get_nodes()
        edges_df = pd_graph.get_edges()

        # Create graph from edgelist dataframes
        if nx_graph is None:
            if directional:
                nx_graph = nx.DiGraph()
            else:
                nx_graph = nx.Graph()

        for key in edges_df:
            new_graph = nx.from_pandas_edgelist(
                edges_df[key], source="Source", target="Target", edge_attr=True)

            nx_graph = nx.compose(nx_graph, new_graph)

        # Add node attributes
        for key in nodes_df:
            df = nodes_df[key]

            for index, row in df.iterrows():
                _id = row["Id"]
                node = nx_graph.nodes[_id]

                for attr in row.keys():
                    node[attr] = row[attr]

        return nx_graph

    def create_from_dict(self, dict_graph, nx_graph=None, directional=False):
        nodes_dict = dict_graph.get_nodes()
        edges_dict = dict_graph.get_edges()

        # Create graph from edge dictionaries
        if nx_graph is None:
            if directional:
                nx_graph = nx.DiGraph()
            else:
                nx_graph = nx.Graph()

        for key in edges_dict:
            edges = edges_dict[key]

            for edge in edges.values():
                source = edge.Source
                target = edge.Target
                attr = {
                    "Label": edge.Label,
                    "label_attribute": edge.label_attribute,
                    "Id": edge.Id
                }
                nx_graph.add_edge(source, target, **attr)

        # Add node attributes
        for key in nodes_dict:
            nodes = nodes_dict[key]

            for key in nodes.keys():
                node = vars(nodes[key])
                nx_node = nx_graph.nodes[key]

                for attr in node.keys():
                    nx_node[attr] = node[attr]

        return nx_graph

    def create_from_csv(self, filepath, nx_graph=None, directional=False):

        if nx_graph is None:
            if directional:
                nx_graph = nx.DiGraph()
            else:
                nx_graph = nx.Graph()

        nodes_path = filepath + "nodes\\"
        edges_path = filepath + "edges\\"

        for filename in os.listdir(edges_path):
            reader = csv.DictReader(
                open(edges_path + filename, encoding="utf-8"))
            for edge in reader:
                source = edge["Source"]
                target = edge["Target"]
                attr = {
                    "Label": edge["Label"],
                    "label_attribute": edge["label_attribute"],
                    "Id": edge["Id"]
                }
                nx_graph.add_edge(source, target, **attr)

        for filename in os.listdir(nodes_path):
            reader = csv.DictReader(
                open(nodes_path + filename, encoding="utf-8"))
            for node in reader:
                node_id = node["Id"]
                nx_node = nx_graph.nodes[node_id]
                for attr in node.keys():
                    nx_node[attr] = node[attr]

        return nx_graph

    def create_from_neo4j(self, neo_graph, nx_graph=None, directional=False):
        nodes = neo_graph.get_nodes()
        edges = neo_graph.get_edges()

        if nx_graph is None:
            if directional:
                nx_graph = nx.DiGraph()
            else:
                nx_graph = nx.Graph()

        for edge in edges:
            edge = edge["r"]
            source = edge["Source"]
            target = edge["Target"]
            attr = {
                "Label": edge["Label"],
                "label_attribute": edge["label_attribute"],
                "Id": edge["Id"]
            }
            nx_graph.add_edge(source, target, **attr)

        for node in nodes:
            node = node["n"]
            node_id = node["Id"]
            nx_node = nx_graph.nodes[node_id]
            for attr in node.keys():
                nx_node[attr] = node[attr]

        return nx_graph

    def draw_random(self, nx_graph, pos=None, options=None, legend=None):

        if pos is None:
            pos = nx.spring_layout(nx_graph)

        node_label = None
        edge_label = None
        colorful_edges = False
        color_set = None
        if options:
            if "node_label" in options:
                node_label = options["node_label"]
            if "edge_label" in options:
                edge_label = options["edge_label"]
            if "colorful_edges" in options:
                colorful_edges = options["colorful_edges"]
            if "color_set" in options:
                color_set = options["color_set"]

        # Separate nodes by category
        node_categories = {"_other": []}
        for node in nx_graph.nodes(data=True):
            if "label_attribute" not in node[1]:
                node_categories["_other"].append(node[0])
                continue
            node = node[1]
            key = node["label_attribute"]
            if key in node_categories:
                node_categories[key].append(node["Id"])
            else:
                node_categories[key] = [node["Id"]]

        # Separate edges by category
        edge_categories = {"_other": []}
        for edge in nx_graph.edges(data=True):
            if "label_attribute" not in edge[2]:
                edge_categories["_other"].append((edge[0], edge[1]))
                continue
            key = edge[2]["label_attribute"]
            if key in edge_categories:
                edge_categories[key].append((edge[0], edge[1]))
            else:
                edge_categories[key] = [(edge[0], edge[1])]

        # Draw nodes
        draw_nodes = []
        if color_set:
            colors = color_set.copy()
        for key in node_categories:
            if color_set:
                color = random.choice(tuple(colors))
                colors.remove(color)
            else:
                color = "r"
            draw_nodes.append(nx.draw_networkx_nodes(
                node_categories[key], pos, node_color=color, node_size=200, label=key))

        # Draw edges
        draw_edges = []
        if colorful_edges and color_set:
            colors = color_set.copy()
        for key in edge_categories:
            if colorful_edges and color_set:
                color = random.choice(tuple(colors))
                colors.remove(color)
                label = key
            else:
                color = "b"
                label = None
            draw_edges.append(nx.draw_networkx_edges(
                nx_graph, edgelist=edge_categories[key], pos=pos, edge_color=color, label=label, width=2))

        # Draw labels
        if node_label is not None:
            node_labels = nx.get_node_attributes(nx_graph, node_label)
            nx.draw_networkx_labels(nx_graph, pos, node_labels)

        if edge_label is not None:
            edge_labels = nx.get_edge_attributes(nx_graph, edge_label)
            nx.draw_networkx_edge_labels(
                nx_graph, pos, edge_labels)

        if legend:
            ncol = len(node_categories) if len(node_categories) > len(
                edge_categories) else len(edge_categories)
            if ncol > 4:
                ncol = 4
            return legend.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=ncol)

    def remove_light_colors(self, colors):
        # White nodes would not be seen in a white background
        # Remove more colors as necessary
        colors.remove("white")
