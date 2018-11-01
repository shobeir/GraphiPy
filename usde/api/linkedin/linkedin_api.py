import httplib2
from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge, BaseGraph as Graph

class UserNode(Node):
    def __init__(self, user):
        Node.__init__(self,user["id"], user["firstName"] + " " + user["lastName"], "user")
        self.headline = user["headline"]

class Linkedin:
    def __init__(self,api, options="pandas"):
        pass

    def get_self_info(self):
        url = "https://api.linkedin.com/v1/people/~?format=json"
        http = httplib2.Http()
        response = http.request(url, method="GET")


