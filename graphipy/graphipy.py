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

from graphipy.graph.graph_base import BaseNode, BaseEdge

from graphipy.exportnx import ExportNX


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

    def get_nx_exporter(self):
        return ExportNX()

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

    def convert_graph(self, old_graph, _type, credentials=None):
        old_type = old_graph.graph_type()
        if old_type == _type:
            return old_graph

        if _type == "dictionary":
            new_graph = DictGraph()
        elif _type == "pandas":
            new_graph = PandasGraph()
        elif _type == "neo4j":
            if credentials is None:
                return old_graph
            new_graph = NeoGraph(credentials)
        else:
            return None

        old_nodes = old_graph.get_nodes()
        old_edges = old_graph.get_edges()

        if old_type == "dictionary":
            for key in old_nodes:
                for node in old_nodes[key].values():
                    new_graph.create_node(node)
            for key in old_edges:
                for edge in old_edges[key].values():
                    new_graph.create_edge(edge)

        elif old_type == "pandas":
            for df in old_nodes.values():
                header = list(df.columns)
                for node in df.iterrows():
                    data = node[1]
                    node = BaseNode(
                        data["Id"], data["Label"], data["label_attribute"])
                    for attr in header:
                        setattr(node, attr, data[attr])
                    new_graph.create_node(node)

            for df in old_edges.values():
                header = list(df.columns)
                for edge in df.iterrows():
                    data = edge[1]
                    edge = BaseEdge(
                        data["Source"], data["Target"], data["Label"])
                    for attr in header:
                        setattr(edge, attr, data[attr])
                    new_graph.create_edge(edge)

        elif old_type == "neo4j":
            for node in old_nodes:
                data = node["n"]
                node = BaseNode(data["Id"], data["Label"],
                                data["label_attribute"])
                for attr in data.keys():
                    setattr(node, attr, data[attr])
                new_graph.create_node(node)
            for edge in old_edges:
                data = edge["r"]
                edge = BaseEdge(
                    data["Source"], data["Target"], data["label_attribute"])
                for attr in data.keys():
                    setattr(edge, attr, data[attr])
                new_graph.create_edge(edge)
        else:
            return None

        return new_graph
