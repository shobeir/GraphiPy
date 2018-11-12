import json
import httplib2
from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge, BaseGraph as Graph
from usde.graph.graph_pandas import PandasGraph

class LinkedinPosition(Node):
    def __init__(self, position):
        Node.__init__(self, position["id"], position["title"], "Position")
        self.company = position["company"]
        self.company_id = position["company"]["id"]
        self.company_industry = position["company"]["industry"]
        self.company_name = position["company"]["name"]
        self.company_size = position["company"]["size"]
        self.company_type = position["company"]["type"]
        self.is_current = position["isCurrent"]
        self.location = position["location"]["name"]
        self.start_month = position["startDate"]["month"]
        self.start_year = position["startDate"]["year"]
        self.summary = position["summary"]

class LinkedinProfile(Node):
    def __init__(self, profile):
        Node.__init__(self, profile["id"], profile["formattedName"], "Profile")
        self.first_name = profile["firstName"]
        self.last_name = profile["lastName"]
        self.headline = profile["headline"]
        self.industry = profile["industry"]
        self.location = profile["location"]
        self.location_name = profile["location"]["name"]
        self.location_country = profile["location"]["country"]["code"]
        self.num_connections = profile["numConnections"]
        self.num_connections_capped = profile["numConnectionsCapped"]
        self.picture_url = profile["pictureUrl"]
        self.summary = profile["summary"]
        if "maidenName" in profile:
            self.maiden_name = profile["maidenName"]
        if "phonetic-first-name" in profile:
            self.phonetic_first_name = profile["phoneticFirstName"]
        if "phonetic-last-name" in profile:
            self.phonetic_last_name = profile["phoneticLastName"]
        if "formatted-phonetic-name" in profile:
            self.formatted_phonetic_name = profile["formattedPhoneticName"]
        if "specialities" in profile:
            self.specialties = profile["specialities"]


class Linkedin:
    def __init__(self,api, options="pandas"):
        self.access_token = api["access_token"]

    def get_self_info(self):
        url =  "https://api.linkedin.com/v1/people/~:(" \
               "id," \
               "first-name," \
               "last-name," \
               "maiden-name," \
               "formatted-name," \
               "phonetic-first-name," \
               "phonetic-last-name," \
               "formatted-phonetic-name," \
               "picture-url," \
               "headline," \
               "location," \
               "industry," \
               "num-connections," \
               "current-share," \
               "num-connections-capped," \
               "summary," \
               "specialties," \
               "positions" \
               ")?format=json"
        http = httplib2.Http()
        headers = {"Host": "api.linkedin.com",
                   "Connection": "Keep-Alive",
                   "Authorization": self.access_token}
        response, content = http.request(url, method="GET", headers=headers)
        result = json.loads(content.decode())
        return result

    def process_positions(self, graph, profile):
        positions = profile["positions"]
        num = positions["_total"]
        positions_array = positions["values"]
        for i in range(num):
            position = positions_array[i]
            position_node = LinkedinPosition(position)
            graph.create_node(position_node)
        return graph


    def fetch_self_node(self, graph):
        profile = self.get_self_info()

        profile_node = LinkedinProfile(profile)
        graph.create_node(profile_node)
        graph = self.process_positions(graph, profile)

        return graph
