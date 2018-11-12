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

    def nx_create_from_pd(self, nx_graph, edges_df, nodes_df, options):
        # Create graph from edgelist dataframes
        for key in edges_df:

            new_graph = nx.from_pandas_edgelist(
                edges_df[key], source=options["Source"], target=options["Target"], edge_attr=True)

            nx_graph = nx.compose(nx_graph, new_graph)

        # Add node attributes
        for key in nodes_df:
            df = nodes_df[key]

            for index, row in df.iterrows():
                _id = row["_id"]
                node = nx_graph.node[_id]

                for attr in row.keys():
                    node[attr] = row[attr]

    def nx_create_from_dict(self, nx_graph, edges_dict, nodes_dict, options):

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
                nx_graph.add_edge(source, target, attr_dict=attr)

        for key in nodes_dict:
            nodes = nodes_dict[key]

            for key in nodes.keys():
                node = vars(nodes[key])
                nx_node = nx_graph.node[key]

                for attr in node.keys():
                    nx_node[attr] = node[attr]
