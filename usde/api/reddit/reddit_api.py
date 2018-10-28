import requests
import requests.auth
import pprint
import json

from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge


USER_API_URL = "https://oauth.reddit.com/user/"
SUBREDDIT_API_URL = "https://oauth.reddit.com/r/"


class Reddit:
    """the Reddit object"""

    def __init__(self, api):
        self.client_id = api["client_id"]
        self.client_secret = api["client_secret"]
        self.user_agent = api["user_agent"]

        client_auth = requests.auth.HTTPBasicAuth(
            self.client_id, self.client_secret)
        post_data = {
            "grant_type": "password",
            "username": api["username"],
            "password": api["password"]
        }
        headers = {"User-Agent": self.user_agent}
        response = requests.post("https://www.reddit.com/api/v1/access_token",
                                 auth=client_auth, data=post_data, headers=headers)
        response = response.json()
        self.headers = {
            "Authorization": "bearer " + response["access_token"],
            "User-Agent": self.user_agent
        }

    def get_request(self, url, params):
        return requests.get(url, params=params, headers=self.headers)

    def request_info(self, url, name):
        url = url + name + "/about"
        params = {}
        response = self.get_request(url, params)
        return response.json()["data"]

    def fetch_subreddits_by_name(
        self,
        graph,
        keyword,
        limit=20,
        nsfw=True,
        exact=False
    ):
        """
        Fetches subreddits based on matching keyword

        nodes:
            - subreddit
        edges:
            -
        """

        # searches subreddit by keyword
        url = "https://oauth.reddit.com/api/search_reddit_names"
        params = {'query': keyword, 'exact': exact, 'include_over_18': nsfw}
        response = self.get_request(url, params)

        # create new node for every subreddit found
        names = response.json()["names"]
        for subreddit_name in names:
            subreddit = self.request_info(SUBREDDIT_API_URL, subreddit_name)
            graph.create_node(Subreddit(subreddit))

        return graph

    def fetch_subreddits_by_topic(
        self,
        graph,
        keyword,
        limit=20
    ):
        """
        Fetches subreddits based on matching topic

        nodes:
            - subreddit
        edges:
            -
        """

        # searches subreddit by related topic

        # create new node for every subreddit found

        pass

    def fetch_subreddit_submissions(
        self,
        graph,
        keyword="",
        subreddit_name="all",
        limit=20,
        sort="hot",
        time_filter="month"
    ):
        """
        Fetches subreddit's submissions based on parameters

        nodes:
            - subreddit
            - submission
            - redditor
        edges:
            - submission
        """

        # request data
        url = SUBREDDIT_API_URL + subreddit_name
        params = {"limit": limit}
        if sort != "hot":
            params["sort"] = sort
            params["t"] = time_filter
        response = self.get_request(url, params)

        data = response.json()["data"]
        after = data["after"]
        total = int(data["dist"])
        submissions = data["children"]  # append next request to this list

        # request more submissions if limit is not reached
        while total < limit:
            url = SUBREDDIT_API_URL + subreddit_name + "?after=" + after
            params = {"limit": limit}
            if sort != "hot":
                params["sort"] = sort
                params["t"] = time_filter
            response = self.get_request(url, params)

            data = response.json()["data"]
            after = data["after"]
            dist = int(data["dist"])
            if dist == 0:
                break
            total += dist
            submissions.append(data["children"])

        # Subreddit Node
        subreddit = self.request_info(SUBREDDIT_API_URL, subreddit_name)
        graph.create_node(Subreddit(subreddit))

        for submission in submissions:
            submission = submission["data"]

            # Redditor Node
            redditor = self.request_info(USER_API_URL, submission["author"])
            graph.create_node(Redditor(redditor))

            # Submission Node
            graph.create_node(Submission(submission))

            # Edges
            graph.create_edge(Edge(redditor["id"], submission["id"], "POSTED"))
            graph.create_edge(
                Edge(submission["id"], redditor["id"], "CREATED_BY"))
            graph.create_edge(Edge(submission["id"], subreddit["id"], "ON"))
            graph.create_edge(
                Edge(subreddit["id"], submission["id"], "HAS_POST"))

    def fetch_submission_comments(
        self,
        graph,
        submission_id,
        limit=20,
        sort="top",
        top_level=False
    ):
        """
        Fetches comments of a submission

        nodes:
            - subreddit
            - submission
            - redditor
            - comment
        edges:
            - submission
            - comment
        """
        url = "https://oauth.reddit.com/comments/" + submission_id + "/"
        params = {
            "sort": sort,
            "limit": limit
        }
        response = self.get_request(url, params)
        data = response.json()

        # Submission Node
        submission = data[0]["data"]["children"][0]["data"]
        graph.create_node(Submission(submission))

        # Subreddit Node
        subreddit = self.request_info(
            SUBREDDIT_API_URL, submission["subreddit"])
        graph.create_node(Subreddit(subreddit))

        # Redditor Node
        redditor = self.request_info(USER_API_URL, submission["author"])
        graph.create_node(Redditor(redditor))

        # Edges
        graph.create_edge(Edge(redditor["id"], submission["id"], "POSTED"))
        graph.create_edge(
            Edge(submission["id"], redditor["id"], "CREATED_BY"))
        graph.create_edge(Edge(submission["id"], subreddit["id"], "ON"))
        graph.create_edge(
            Edge(subreddit["id"], submission["id"], "HAS_POST"))

        # iterate through comments
        comments = data[1]["data"]["children"]
        for comment in comments:
            if comment["kind"] == "more":
                continue

            comment = comment["data"]

            # Redditor Node
            redditor = self.request_info(USER_API_URL, comment["author"])
            graph.create_node(Redditor(redditor))

            # Comment Node
            graph.create_node(Comment(comment))

            # Edges
            graph.create_edge(
                Edge(redditor["id"], comment["id"], "COMMENTED"))
            graph.create_edge(
                Edge(comment["id"], redditor["id"], "CREATED_BY"))
            graph.create_edge(
                Edge(comment["id"], comment["parent_id"][3:], "ON"))
            graph.create_edge(
                Edge(comment["parent_id"][3:], comment["id"], "HAS_COMMENT"))

    def fetch_redditor_comments(
        self,
        graph,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):
        """
        Fetches comments a redditor has posted

        nodes:
            - redditor
            - comment
        edges:
            - comment
        """

        url = "https://oauth.reddit.com/user/" + username + "/comments"
        params = {
            "sort": sort,
            "limit": limit,
            "t": time_filter
        }
        response = self.get_request(url, params)
        data = response.json()

        # Redditor Node
        redditor = self.request_info(USER_API_URL, username)
        graph.create_node(Redditor(redditor))

        comments = data["data"]["children"]
        for comment in comments:
            if comment["kind"] == "more":
                continue

            comment = comment["data"]

            # Comment Node
            graph.create_node(Comment(comment))

            # Edges
            graph.create_edge(
                Edge(redditor["id"], comment["id"], "COMMENTED"))
            graph.create_edge(
                Edge(comment["id"], redditor["id"], "CREATED_BY"))

    def fetch_redditor_submissions(
        self,
        graph,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):
        """
        Fetches submissions a redditor has posted

        nodes:
            - subreddit
            - submission
            - redditor
        edges:
            - submission
        """

        url = USER_API_URL + username + "/submitted"
        params = {
            "sort": sort,
            "limit": limit,
            "t": time_filter
        }
        response = self.get_request(url, params)
        data = response.json()["data"]
        after = data["after"]
        total = int(data["dist"])
        submissions = data["children"]  # append next request to this list

        # request more submissions if limit is not reached
        while total < limit:
            url = USER_API_URL + username + "?after=" + after
            params = {"limit": limit}
            if sort != "hot":
                params["sort"] = sort
                params["t"] = time_filter
            response = self.get_request(url, params)

            data = response.json()["data"]
            after = data["after"]
            dist = int(data["dist"])
            if dist == 0:
                break
            total += dist
            submissions.append(data["children"])

        # Redditor Node
        redditor = self.request_info(USER_API_URL, username)
        graph.create_node(Redditor(redditor))

        for submission in submissions:
            submission = submission["data"]

            # Subreddit Node
            subreddit = self.request_info(
                SUBREDDIT_API_URL, submission["subreddit"])
            graph.create_node(Subreddit(subreddit))

            # Redditor Node
            redditor = self.request_info(USER_API_URL, submission["author"])
            graph.create_node(Redditor(redditor))

            # Submission Node
            graph.create_node(Submission(submission))

            # Edges
            graph.create_edge(Edge(redditor["id"], submission["id"], "POSTED"))
            graph.create_edge(
                Edge(submission["id"], redditor["id"], "CREATED_BY"))
            graph.create_edge(Edge(submission["id"], subreddit["id"], "ON"))
            graph.create_edge(
                Edge(subreddit["id"], submission["id"], "HAS_POST"))


class Redditor(Node):
    """Reddit's users are called Redditors"""

    def __init__(
        self,
        redditor
    ):
        Node.__init__(self, redditor["id"], "redditor", "redditor")
        for key in redditor:
            if key == "id":
                continue
            setattr(self, key, str(redditor[key]))


class Submission(Node):
    """Reddit's posts are called Submissions"""

    def __init__(
        self,
        submission
    ):
        Node.__init__(self, submission["id"], "submission", "submission")
        for key in submission:
            if key == "id":
                continue
            setattr(self, key, str(submission[key]))


class Subreddit(Node):
    """Reddit's communities are called Subreddits"""

    def __init__(
        self,
        subreddit
    ):
        Node.__init__(self, subreddit["id"],
                      "subreddit", "subreddit")
        for key in subreddit:
            if key == "id":
                continue
            setattr(self, key, str(subreddit[key]))


class Comment(Node):
    """Comments of a post"""

    def __init__(
        self,
        comment
    ):
        Node.__init__(self, comment["id"], "comment", "comment")
        for key in comment:
            if key == "id" or key == "replies":
                continue
            setattr(self, key, str(comment[key]))
