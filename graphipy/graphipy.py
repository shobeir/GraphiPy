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
