import praw

from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge


class Reddit:
    """the Reddit object that is powered by PRAW"""

    def __init__(self, api):
        self.reddit = praw.Reddit(
            client_id=api["client_id"],
            client_secret=api["client_secret"],
            user_agent=api["user_agent"]
        )

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
        subreddits = self.reddit.subreddits.search_by_name(
            keyword, include_nsfw=nsfw, exact=exact)

        # create new node for every subreddit found
        i = 0
        for subreddit in subreddits:
            if i == limit:
                break
            i += 1
            graph.create_node(Subreddit(subreddit))

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
        subreddits = self.reddit.subreddits.search(
            keyword, limit=limit)

        # create new node for every subreddit found
        for subreddit in subreddits:
            graph.create_node(Subreddit(subreddit))

    def fetch_subreddit_submissions(
        self,
        graph,
        keyword="",
        subreddit_name="all",
        limit=20,
        sort="top",
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

        # get subreddit object
        subreddit = self.reddit.subreddit(subreddit_name)

        # gets submissions on a subreddit sorted by parameter
        if keyword == "":
            if sort == "hot":
                submissions = subreddit.hot(
                    limit=limit, time_filter=time_filter)
            elif sort == "new":
                submissions = subreddit.new(
                    limit=limit, time_filter=time_filter)
            elif sort == "controversial":
                submissions = subreddit.controversial(
                    limit=limit, time_filter=time_filter)
            elif sort == "rising":
                submissions = subreddit.rising(
                    limit=limit, time_filter=time_filter)
            else:
                submissions = subreddit.top(
                    limit=limit, time_filter=time_filter)

        # gets submissions on a subreddit by keyword
        else:
            submissions = subreddit.search(
                keyword, sort=sort, time_filter=time_filter, limit=limit)

        # Subreddit Node
        graph.create_node(Subreddit(subreddit))

        for submission in submissions:
            # Redditor Node
            graph.create_node(Redditor(submission.author))

            # Submission Node
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id, "POSTED"))
            graph.create_edge(
                Edge(submission.id, submission.subreddit.id, "ON"))

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

        submission = self.reddit.submission(id=submission_id)

        submission.comment_sort = sort

        # maximum replacement is 32 (limitation of API)
        if limit is None or limit > 32:
            submission.comments.replace_more(limit=None)
        else:
            submission.comments.replace_more(limit=limit//10)

        # gets top level comment or not based on parameter
        if top_level is True:
            comments = submission.comments
        else:
            comments = submission.comments.list()

        # Redditor Node (Author)
        graph.create_node(Redditor(submission.author))

        # Subreddit Node
        graph.create_node(Subreddit(submission.subreddit))

        # Submission Node Edge
        graph.create_node(Submission(submission))
        graph.create_edge(
            Edge(submission.author.fullname[3:], submission.id, "POSTED"))
        graph.create_edge(
            Edge(submission.id, submission.subreddit.id, "ON"))

        i = 0
        for comment in comments:

            # if reached number of comments desired
            if i == limit:
                break
            i += 1

            # skips deleted comment
            if comment.author is None:
                continue
            # Redditor Node
            graph.create_node(Redditor(comment.author))

            # Comment Node Edge
            graph.create_node(Comment(comment))
            graph.create_edge(
                Edge(comment.author.fullname[3:], comment.id, "COMMENTED"))
            graph.create_edge(
                Edge(comment.id, comment.parent_id[3:], "ON"))

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
            - subreddit
            - submission
            - redditor
            - comment
        edges:
            - submission
            - comment
        """
        redditor = self.reddit.redditor(username)

        # set sort parameter
        if sort == "top":
            comments = redditor.comments.top(
                limit=limit, time_filter=time_filter)
        elif sort == "hot":
            comments = redditor.comments.hot(
                limit=limit)
        elif sort == "controversial":
            comments = redditor.comments.controversial(
                limit=limit, time_filter=time_filter)
        else:
            comments = redditor.comments.new(
                limit=limit)

        # Redditor Node
        graph.create_node(Redditor(redditor))

        i = 0
        for comment in comments:

            # if reached number of comments desired
            if i == limit:
                break
            i += 1

            # skips deleted comment
            if comment.author is None:
                continue

            submission = self.reddit.submission(id=comment.link_id[3:])

            # Subreddit Node
            graph.create_node(Subreddit(submission.subreddit))

            # Submission Node Edge
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id, "POSTED"))
            graph.create_edge(
                Edge(submission.id, submission.subreddit.id, "ON"))

            # Comment Node Edge
            graph.create_node(Comment(comment))
            graph.create_edge(
                Edge(comment.author.fullname[3:], comment.id,
                     "COMMENTED"))

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

        redditor = self.reddit.redditor(username)

        # set sort parameter
        if sort == "top":
            submissions = redditor.submissions.top(
                limit=limit, time_filter=time_filter)
        elif sort == "hot":
            submissions = redditor.submissions.hot(
                limit=limit)
        elif sort == "controversial":
            submissions = redditor.submissions.controversial(
                limit=limit, time_filter=time_filter)
        else:
            submissions = redditor.submissions.new(
                limit=limit)

        # Redditor Node
        graph.create_node(Redditor(redditor))

        for submission in submissions:

            # Subreddit Node
            graph.create_node(Subreddit(submission.subreddit))

            # Submission Node Edge
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id, "POSTED"))
            graph.create_edge(
                Edge(submission.id, submission.subreddit.id, "ON"))


class Redditor(Node):
    """Reddit's users are called Redditors"""

    def __init__(
        self,
        redditor
    ):
        Node.__init__(
            self, redditor.fullname[3:], "u/" + redditor.name, "redditor")
        self.username = redditor.name
        self.created = redditor.created
        self.link_karma = redditor.link_karma
        self.comment_karma = redditor.comment_karma
        self.upvotes = redditor.link_karma + redditor.comment_karma


class Submission(Node):
    """Reddit's posts are called Submissions"""

    def __init__(
        self,
        submission
    ):
        media_url = None
        if submission.media:
            if "reddit_video" in submission.media:
                media_url = submission.media["reddit_video"]["dash_url"]
            elif "oembed" in submission.media:
                html = submission.media["oembed"]["html"]
                start = html.find("src=\"")
                end = html.find("\"", start + 5)
                media_url = html[start+5:end]

        image_url = None
        try:
            if submission.preview:
                if "images" in submission.preview:
                    if "source" in submission.preview["images"]:
                        image_url = submission.preview["images"]["source"]["url"]
        except AttributeError:
            pass

        Node.__init__(self, submission.id, "submission_" +
                      submission.id, "submission")
        self.author_id = submission.author_fullname[3:]
        self.subreddit_id = submission.subreddit_id[3:]
        self.created = submission.created
        self.title = submission.title
        self.url = submission.url
        self.permalink = "https://reddit.com" + submission.permalink
        self.upvote_ratio = submission.upvote_ratio
        self.upvotes = submission.score
        self.selftext = submission.selftext
        self.over_18 = submission.over_18
        self.media_url = media_url
        self.image_url = image_url
        self.author_name = submission.author.name
        self.subreddit_name = submission.subreddit.display_name


class Subreddit(Node):
    """Reddit's communities are called Subreddits"""

    def __init__(
        self,
        subreddit
    ):
        Node.__init__(self, subreddit.id,
                      "subreddit", "subreddit")
        self.display_name = subreddit.display_name
        self.created = subreddit.created
        self.description = subreddit.description
        self.header_title = subreddit.header_title
        self.subreddit_type = subreddit.subreddit_type
        self.over18 = subreddit.over18
        self.subscribers = subreddit.subscribers
        self.title = subreddit.title
        self.url = "https://reddit.com"+subreddit.url


class Comment(Node):
    """Comments of a post"""

    def __init__(
        self,
        comment
    ):
        Node.__init__(self, comment.id, "comment_" + comment.id, "comment")
        self.parent_id = comment.parent_id[3:]
        self.author_id = comment.author_fullname[3:]
        self.submisison_id = comment.link_id[3:]
        self.subreddit_id = comment.subreddit_id[3:]
        self.text = comment.body
        self.permalink = "https://reddit.com" + comment.permalink
        self.upvotes = comment.score
