import praw
import pandas as pd
import pprint
from graph import Graph, Node, Edge

class Reddit:
    def __init__(self, api):
        self.reddit = praw.Reddit(
            client_id=api["client_id"],
            client_secret=api["client_secret"],
            user_agent=api["user_agent"]
        )

    def test(self):
        # node = Subreddit('100', 'subreddit', 'pics')
        # self.graph.create_node(node)

        return 0

    def fetch_subreddits_by_name(
        self,
        keyword,
        limit=20,
        nsfw=True,
        exact=False
    ):
        subreddits = self.reddit.subreddits.search_by_name(
            "t", include_nsfw=nsfw, exact=exact)

        graph = Graph()
        for subreddit in subreddits:
            graph.create_node(Subreddit(subreddit))
        return graph.get_dataFrame()

       
    def fetch_subreddits_by_topic(
        self,
        keyword,
        limit=20
    ):
        subreddits = self.reddit.subreddits.search(
            keyword, limit=limit)

        graph = Graph()
        for subreddit in subreddits:
            graph.create_node(Subreddit(subreddit))
        return graph.get_dataFrame()


    def fetch_subreddit_submissions(
        self,
        keyword="",
        subreddit_name="all",
        limit=20,
        sort="top",
        time_filter="month"
    ):
        if keyword == "":
            submissions = self.reddit.subreddit(subreddit_name)

            if sort == "hot":
                submissions = submissions.hot(
                    limit=limit, time_filter=time_filter)
            elif sort == "new":
                submissions = submissions.new(
                    limit=limit, time_filter=time_filter)
            elif sort == "controversial":
                submissions = submissions.controversial(
                    limit=limit, time_filter=time_filter)
            elif sort == "rising":
                submissions = submissions.rising(
                    limit=limit, time_filter=time_filter)
            else:
                submissions = submissions.top(
                    limit=limit, time_filter=time_filter)
        else:
            submissions = self.reddit.subreddit(subreddit_name).search(
                keyword, sort=sort, time_filter=time_filter, limit=limit)

        graph = Graph()
        for submission in submissions:
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id))
            graph.create_edge(
                Edge(submission.id, submission.subreddit.id))
        return graph.get_dataFrame()

       
    def fetch_submission_comments(
        self,
        submission_id,
        limit=20,
        sort="top",
        time_filter="month",
        top_level=False
    ):

        submission = self.reddit.submission(id=submission_id)

        submission.comment_sort = sort

        if limit is None or limit > 32:
            submission.comments.replace_more(limit=None)
        else:
            submission.comments.replace_more(limit=limit)

        i = 0
        if top_level is True:
            comments = submission.comments
        else:
            comments = submission.comments.list()

        graph = Graph()
        for comment in comments:
            if comment.author is None:
                continue
            # Redditor Node
            graph.create_node(Redditor(comment.author))

            # Comment Node Edge
            graph.create_node(Comment(comment))
            graph.create_edge(
                Edge(comment.author.fullname[3:], comment.id))
            graph.create_edge(Edge(comment.id, comment.parent_id[3:]))
            i += 1
            if i == limit:
                break

        # Submission Node Edge
        graph.create_node(Submission(submission))
        graph.create_edge(
            Edge(submission.author.fullname[3:], submission.id))
        graph.create_edge(Edge(submission.id, submission.subreddit.id))

        # Subreddit Node
        graph.create_node(Subreddit(submission.subreddit))

        return graph.get_dataFrame()

        
    def fetch_redditor_comments(
        self,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):
        redditor = self.reddit.redditor(username)

        if sort == "top":
            comments = redditor.comments.top(
                limit=limit, time_filter=time_filter)
        elif sort == "hot":
            comments = redditor.comments.hot(
                limit=limit, time_filter=time_filter)
        elif sort == "controversial":
            comments = redditor.comments.controversial(
                limit=limit, time_filter=time_filter)
        else:
            comments = redditor.comments.new(
                limit=limit, time_filter=time_filter)

        graph = Graph()
        i = 0
        for comment in comments:
            if comment.author is None:
                continue

            # Redditor Node
            graph.create_node(Redditor(comment.author))

            # Submission Node Edge
            submission = self.reddit.submission(id=comment.link_id[3:])
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id))
            graph.create_edge(Edge(submission.id, submission.subreddit.id))

            # Subreddit Node
            graph.create_node(Subreddit(submission.subreddit))

            # Comment Node Edge
            graph.create_node(Comment(comment))
            graph.create_edge(
                Edge(comment.author.fullname[3:], comment.id))
            graph.create_edge(Edge(comment.id, comment.parent_id[3:]))

            i += 1
            if i == limit:
                break

        graph.create_node(Redditor(redditor))

        return graph.get_dataFrame()

        
    def fetch_redditor_submissions(
        self,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):

        redditor = self.reddit.redditor(username)

        if sort == "top":
            submissions = redditor.submissions.top(
                limit=limit, time_filter=time_filter)
        elif sort == "hot":
            submissions = redditor.submissions.hot(
                limit=limit, time_filter=time_filter)
        elif sort == "controversial":
            submissions = redditor.submissions.controversial(
                limit=limit, time_filter=time_filter)
        else:
            submissions = redditor.submissions.new(
                limit=limit, time_filter=time_filter)

        graph = Graph()
        for submission in submissions:

            # Subreddit Node
            graph.create_node(Subreddit(submission.subreddit))

            # Submission Node Edge
            graph.create_node(Submission(submission))
            graph.create_edge(
                Edge(submission.author.fullname[3:], submission.id))
            graph.create_edge(
                Edge(submission.id, submission.subreddit.id))

        # Redditor Node
        graph.create_node(Redditor(redditor))

        return graph.get_dataFrame()


class Redditor (Node):
    def __init__(
        self,
        redditor
    ):
        Node.__init__(self, redditor.fullname[3:], "u/" + redditor.name)
        self.label_attribute = "redditor"
        self.username = redditor.name
        self.created = redditor.created
        self.link_karma = redditor.link_karma
        self.comment_karma = redditor.comment_karma
        self.upvotes = redditor.link_karma + redditor.comment_karma


class Submission (Node):
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

        Node.__init__(self, submission.id, "submission_" + submission.id)
        self.author_id = submission.author_fullname[3:]
        self.subreddit_id = submission.subreddit_id[3:]
        self.label_attribute = "submission"
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


class Subreddit (Node):
    def __init__(
        self,
        subreddit
    ):
        Node.__init__(self, subreddit.id, subreddit.display_name_prefixed)
        self.label_attribute = "subreddit"
        self.display_name = subreddit.display_name
        self.created = subreddit.created
        self.description = subreddit.description
        self.header_title = subreddit.header_title
        self.subreddit_type = subreddit.subreddit_type
        self.over18 = subreddit.over18
        self.subscribers = subreddit.subscribers
        self.title = subreddit.title
        self.url = "https://reddit.com"+subreddit.url

    def to_dict(self):
        return {
            'id': self._id,
            'label': self.label,
            'label_attribute': self.label_attribute
        }


class Comment (Node):
    def __init__(
        self,
        comment
    ):
        Node.__init__(self, comment.id, "comment_" + comment.id)
        self.label_attribute = "comment"
        self.parent_id = comment.parent_id[3:]
        self.author_id = comment.author_fullname[3:]
        self.submisison_id = comment.link_id[3:]
        self.subreddit_id = comment.subreddit_id[3:]
        self.text = comment.body
        self.permalink = "https://reddit.com" + comment.permalink
        self.upvotes = comment.score
