from graphipy.api.reddit_api import Reddit
from graphipy.api.pinterest_api import Pinterest
from graphipy.api.youtube_api import Youtube
from graphipy.api.facebook_api import Facebook
from graphipy.api.tumblr_api import Tumblr
from graphipy.api.twitter_api import Twitter
from graphipy.api.linkedin_api import Linkedin

from graphipy.graph.graph_pandas import PandasGraph
from graphipy.graph.graph_dict import DictGraph
from graphipy.graph.graph_neo4j import NeoGraph

from matplotlib import colors as c
import matplotlib.pyplot as plt
import networkx as nx
import random
import os
import csv


class GraphiPy:
    def __init__(self, option="pandas"):
        self.option = option

    """creates an api instance"""

    def get_reddit(self, api):
        return Reddit(api)

    def get_pinterest(self, api):
        return Pinterest(api)

    def get_facebook(self, api):
        return Facebook(api)

    def get_youtube(self, api):
        return Youtube(api)

    def get_tumblr(self, api):
        return Tumblr(api)

    def get_twitter(self, api):
        return Twitter(api)

    def get_linkedin(self, api):
        return Linkedin(api)

    def create_graph(self, option="", credentials=None):
        """creates a graph based on option"""

        if option == "":
            option = self.option

        if option == "dictionary":
            return DictGraph()

        elif option == "neo4j":
            if credentials is None:
                return None
            return NeoGraph(credentials)

        return PandasGraph()

    def nx_create_from_pd(self, nodes_df, edges_df, nx_graph=None, directional=False):
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
                _id = row["_id"]
                node = nx_graph.node[_id]

                for attr in row.keys():
                    node[attr] = row[attr]

        return nx_graph

    def nx_create_from_dict(self, nodes_dict, edges_dict, nx_graph=None, directional=False):
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
                    "_id": edge._id
                }
                nx_graph.add_edge(source, target, **attr)

        # Add node attributes
        for key in nodes_dict:
            nodes = nodes_dict[key]

            for key in nodes.keys():
                node = vars(nodes[key])
                nx_node = nx_graph.node[key]

                for attr in node.keys():
                    nx_node[attr] = node[attr]

        return nx_graph

    def nx_create_from_csv(self, edges_path, nodes_path, nx_graph=None, directional=False):

        if nx_graph is None:
            if directional:
                nx_graph = nx.DiGraph()
            else:
                nx_graph = nx.Graph()

        for filename in os.listdir(edges_path):
            reader = csv.DictReader(
                open(edges_path + filename, encoding="utf-8"))
            for edge in reader:
                source = edge["Source"]
                target = edge["Target"]
                attr = {
                    "Label": edge["Label"],
                    "label_attribute": edge["label_attribute"],
                    "_id": edge["_id"]
                }
                nx_graph.add_edge(source, target, **attr)

        for filename in os.listdir(nodes_path):
            reader = csv.DictReader(
                open(nodes_path + filename, encoding="utf-8"))
            for node in reader:
                node_id = node["_id"]
                nx_node = nx_graph.node[node_id]
                for attr in node.keys():
                    nx_node[attr] = node[attr]

        return nx_graph

    def nx_create_from_neo4j(self, nodes, edges, nx_graph=None, directional=False):

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
                "_id": edge["_id"]
            }
            nx_graph.add_edge(source, target, **attr)

        for node in nodes:
            node = node["n"]
            node_id = node["_id"]
            nx_node = nx_graph.node[node_id]
            for attr in node.keys():
                nx_node[attr] = node[attr]

        return nx_graph

    def nx_draw_random(self, nx_graph=None, pos=None, options=None, legend=False, axis=False):

        if pos is None:
            pos = nx.spring_layout(nx_graph)

        if not axis:
            plt.axis('off')

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
                node_categories[key].append(node["_id"])
            else:
                node_categories[key] = [node["_id"]]

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
        if color_set:
            colors = color_set.copy()
        else:
            colors = set(c.CSS4_COLORS)
            self.remove_light_colors(colors)
        chosen = set()
        draw_nodes = []
        for key in node_categories:
            color = random.choice(tuple(colors))
            draw_nodes.append(nx.draw_networkx_nodes(
                node_categories[key], pos, node_color=color, node_size=200, label=key))
            colors.remove(color)

        # Draw edges
        draw_edges = []
        if colorful_edges:
            if color_set:
                colors = color_set.copy()
            else:
                colors = set(c.CSS4_COLORS)
                self.remove_light_colors(colors)
            for key in edge_categories:
                color = random.choice(tuple(colors))
                draw_edges.append(nx.draw_networkx_edges(
                    nx_graph, edgelist=edge_categories[key], pos=pos, edge_color=color, label=key, width=2))
                colors.remove(color)
        else:
            draw_edges.append(nx.draw_networkx_edges(
                nx_graph, edgelist=nx_graph.edges(), pos=pos, edge_color="b", width=2))

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
            return plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=ncol)

    def remove_light_colors(self, colors):
        colors.remove("white")
        pass
