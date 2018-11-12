import json
import httplib2

from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge


class Pinterest:
    def __init__(self, api):
        self.access_token = api["access_token"]

    # get a single user info in JSON format by username
    def get_single_user(self, username):
        url = "https://api.pinterest.com/v1/users/" + username + "/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cimage%2Caccount_type%2Cbio%2Ccounts%2Ccreated_at"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        return result

    # get a single board info in JSON format by board_url
    def get_single_board(self, board_url):
        url = "https://api.pinterest.com/v1/boards/" + board_url + "/?access_token=" + self.access_token + \
            "&fields=id%2Cname%2Curl%2Ccounts%2Ccreated_at%2Ccreator%2Cdescription%2Cimage%2Cprivacy"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        return result

    # get a single pin info in JSON format by pin_id
    def get_single_pin(self, pin_id):
        url = "https://api.pinterest.com/v1/pins/" + pin_id + "/?access_token=" + self.access_token + \
            "&fields=note%2Curl%2Cboard%2Ccolor%2Ccounts%2Ccreated_at%2Ccreator%2Cimage%2Cid"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        return result

    # get all pins on one board in JSON format by board_url
    def get_pins_from_board(self, board_url):
        url = "https://api.pinterest.com/v1/boards/" + board_url + \
            "/pins/?access_token=" + self.access_token + "&fields=id"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        return result

    # get the graph for a single user by username
    def fetch_pinterest_user_by_username(self, graph, username):
        result = self.get_single_user(username)
        user = PinterestUser(result["data"])
        graph.create_node(user)
        return graph
 
    # get the graph for a single board by board_url
    def fetch_pinterest_board_by_url(self, graph, board_url):
        board_result = self.get_single_board(board_url)
        print(board_result)
        board = PinterestBoard(board_result["data"])
        graph.create_node(board)

        creator_username = board_result["data"]["creator"]["url"].split('/')[3]
        user_result = self.get_single_user(creator_username)
        user = PinterestUser(user_result["data"])
        graph.create_node(user)

        graph.create_edge(Edge(board.get_id(), user.get_id(), "CREATED_BY"))
        graph.create_edge(Edge(user.get_id(), board.get_id(), "CREATED"))

        pin_result = self.get_pins_from_board(board_url)
        for pin in pin_result["data"]:
            single_pin_result = self.get_single_pin(pin["id"])
            single_pin = PinterestPin(single_pin_result["data"])
            graph.create_node(single_pin)
            graph.create_edge(Edge(board.get_id(), single_pin.get_id(), "HAS"))
            graph.create_edge(Edge(single_pin.get_id(), board.get_id(), "ON"))
    
        return graph

    # get the graph for a single pin by pin_id
    def fetch_pinterest_pin_by_id(self, graph, pin_id):

        pin_result = self.get_single_pin(pin_id)
        pin = PinterestPin(pin_result["data"])
        graph.create_node(pin)

        creator_username = pin_result["data"]["creator"]["url"].split('/')[3]
        user_result = self.get_single_user(creator_username)
        user = PinterestUser(user_result["data"])
        graph.create_node(user)

        graph.create_edge(Edge(pin.get_id(), user.get_id(), "CREATED_BY"))
        graph.create_edge(Edge(user.get_id(), pin.get_id(), "CREATED"))

        board_url = pin_result["data"]["board"]["url"].split(
            '/')[3] + "/" + pin_result["data"]["board"]["url"].split('/')[4]
        board_result = self.get_single_board(board_url)
        board = PinterestBoard(board_result["data"])
        graph.create_node(board)

        graph.create_edge(Edge(pin.get_id(), board.get_id(), "ON"))
        graph.create_edge(Edge(board.get_id(), pin.get_id(), "HAS"))

        return graph

    # get the graph for mine as user node
    def fetch_pinterest_my_usernode(self, graph):
        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        user = PinterestUser(result["data"])
        graph.create_node(user)

        return graph

    # get the graph of my boards 
    def fetch_pinterest_my_boards(self, graph):

        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        user = PinterestUser(result["data"])
        graph.create_node(user)

        url = "https://api.pinterest.com/v1/me/boards/?access_token=" + self.access_token + \
            "&fields=id%2Cname%2Curl%2Ccounts%2Ccreated_at%2Ccreator%2Cdescription%2Cimage%2Cprivacy"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        for myboard in result["data"]:
            board = PinterestBoard(myboard)
            graph.create_node(board)
            graph.create_edge(Edge(board.get_id(), user.get_id(), "CREATED_BY"))
            graph.create_edge(Edge(user.get_id(), board.get_id(), "CREATED"))

        return graph

    # get the graph of my pins
    def fetch_pinterest_my_pins(self, graph):

        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        user = PinterestUser(result["data"])
        graph.create_node(user)

        url = "https://api.pinterest.com/v1/me/pins/?access_token=" + self.access_token + \
            "&fields=note%2Curl%2Cboard%2Ccolor%2Ccounts%2Ccreated_at%2Ccreator%2Cimage%2Cid"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        for mypin in result["data"]:
            pin = PinterestPin(mypin)
            graph.create_node(pin)
            graph.create_edge(Edge(pin.get_id(), user.get_id(), "CREATED_BY"))
            graph.create_edge(Edge(user.get_id(), pin.get_id(), "CREATED"))

        return graph

    # get the graph of my followers
    def fetch_pinterest_my_followers(self, graph):

        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        user = PinterestUser(result["data"])
        graph.create_node(user)

        url = "https://api.pinterest.com/v1/me/followers/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        for myfollower in result["data"]:
            follower = PinterestUser(myfollower)
            graph.create_node(follower)
            graph.create_edge(Edge(user.get_id(), follower.get_id(), "FOLLOWED_BY"))

        return graph

    # get the graph of my following users
    def fetch_pinterest_my_following_users(self, graph):

        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        user = PinterestUser(result["data"])
        graph.create_node(user)

        url = "https://api.pinterest.com/v1/me/following/users/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        for myfollowing in result["data"]:
            following = PinterestUser(myfollowing)
            graph.create_node(following)
            graph.create_edge(Edge(user.get_id(), following.get_id(), "FOLLOWING"))

        return graph

    # get the graph of my following boards
    def fetch_pinterest_my_following_boards(self, graph):

        url = "https://api.pinterest.com/v1/me/?access_token=" + self.access_token + \
            "&fields=first_name%2Cid%2Clast_name%2Curl%2Cbio%2Caccount_type%2Ccounts%2Ccreated_at%2Cimage%2Cusername"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())
        user = PinterestUser(result["data"])
        graph.create_node(user)

        url = "https://api.pinterest.com/v1/me/following/boards/?access_token=" + self.access_token + \
            "&fields=id%2Cname%2Curl%2Ccounts%2Ccreated_at%2Ccreator%2Cdescription%2Cimage%2Cprivacy"
        http = httplib2.Http()
        response, content = http.request(url, method="GET")
        result = json.loads(content.decode())

        for myfollowingboard in result["data"]:
            followingboard = PinterestBoard(myfollowingboard)
            graph.create_node(followingboard)
            graph.create_edge(Edge(user.get_id(), followingboard.get_id(), "FOLLOWING"))

            creator_username = myfollowingboard["creator"]["url"].split('/')[3]
            creator_result = self.get_single_user(creator_username)
            creator = PinterestUser(creator_result["data"])
            graph.create_node(creator)

            graph.create_edge(Edge(followingboard.get_id(), creator.get_id(), "CREATED_BY"))
            graph.create_edge(Edge(creator.get_id(), followingboard.get_id(), "CREATED"))

            board_url = myfollowingboard["url"].split(
                '/')[3] + "/" + myfollowingboard["url"].split('/')[4]
            pin_result = self.get_pins_from_board(board_url)
            for pin in pin_result["data"]:
                single_pin_result = self.get_single_pin(pin["id"])
                single_pin = PinterestPin(single_pin_result["data"])
                graph.create_node(single_pin)
                graph.create_edge(Edge(followingboard.get_id(), single_pin.get_id(), "HAS"))
                graph.create_edge(Edge(single_pin.get_id(), followingboard.get_id(), "ON"))

        return graph


# User node of Pinterest
class PinterestUser(Node):
    def __init__(self, result):
        label = result["first_name"] + " " + result["last_name"]
        Node.__init__(self, result["id"], label, "user")
        self.bio = result["bio"]
        self.first_name = result["first_name"]
        self.last_name = result["last_name"]
        self.account_type = result["account_type"]
        self.url = result["url"]
        self.image_url = result["image"]["60x60"]["url"]
        self.created_at = result["created_at"]
        self.pins_count = result["counts"]["pins"]
        self.following_count = result["counts"]["following"]
        self.followers_count = result["counts"]["followers"]
        self.boards_count = result["counts"]["boards"]


# Board node of Pinterest
class PinterestBoard(Node):
    def __init__(self, result):
        Node.__init__(self, result["id"], result["name"], "board")
        self.url = result["url"]
        self.image_url = result["image"]["60x60"]["url"]
        self.created_at = result["created_at"]
        self.privacy = result["privacy"]
        self.pins_count = result["counts"]["pins"]
        self.collaborators_count = result["counts"]["collaborators"]
        self.followers_count = result["counts"]["followers"]
        self.description = result["description"]


# Pin node of Pinterest
class PinterestPin(Node):
    def __init__(self, result):
        Node.__init__(self, result["id"], "pin_" + result["id"], "pin")
        self.url = result["url"]
        self.image_url = result["image"]["original"]["url"]
        self.created_at = result["created_at"]
        self.note = result["note"]
        self.color = result["color"]
        self.saves = result["counts"]["saves"]
        self.comments = result["counts"]["comments"]
