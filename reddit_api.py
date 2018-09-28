import praw
import pandas as pd
import pprint


def create_subreddit_node(subreddit):
    subreddit_node = {
        "id": subreddit.id,
        "label_attribute": "subreddit",
        "label": subreddit.display_name_prefixed,
        "display_name": subreddit.display_name,
        "created": subreddit.created,
        "description": subreddit.description,
        "header_title": subreddit.header_title,
        "subreddit_type": subreddit.subreddit_type,
        "over18": subreddit.over18,
        "subscribers": subreddit.subscribers,
        "title": subreddit.title,
        "url": "https://reddit.com" + subreddit.url,
        "subreddit_type": subreddit.subreddit_type
    }
    return subreddit_node


def create_submission_node(submission):
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

    submission_node = {
        "id": submission.id,
        # this is the author of the submission
        "author_id": submission.author_fullname[3:],
        # this is the subreddit the submission was posted to
        "subreddit_id": submission.subreddit_id[3:],
        "label_attribute": "submission",
        "label": "submission_" + submission.id,
        "created": submission.created,
        "title": submission.title,
        "url": submission.url,
        "permalink": "https://reddit.com" + submission.permalink,
        "upvote_ratio": submission.upvote_ratio,
        "upvotes": submission.score,
        "selftext": submission.selftext,
        "over_18": submission.over_18,
        "media_url": media_url,
        "image_url": image_url,
        "author_name": submission.author.name,
        "subreddit_name": submission.subreddit.display_name
    }

    return submission_node


def create_redditor_node(redditor):
    redditor_node = {
        "id": redditor.fullname[3:],
        "label_attribute": "redditor",
        "label": "u/" + redditor.name,
        "username": redditor.name,
        "created": redditor.created,
        "link_karma": redditor.link_karma,
        "comment_karma": redditor.comment_karma,
        "upvotes": redditor.link_karma + redditor.comment_karma
    }
    return redditor_node


def create_comment_node(comment):
    comment_node = {
        "id": comment.id,
        "label_attribute": "comment",
        "label": "comment_" + comment.id,
        "parent_id": comment.parent_id[3:],  # submission_id
        "author_id": comment.author_fullname[3:],  # author_id
        "submission_id": comment.link_id[3:],
        "subreddit_id": comment.subreddit_id[3:],
        "text": comment.body,
        "permalink": "https://reddit.com" + comment.permalink,
        "upvotes": comment.score
    }
    return comment_node


def create_edge(source, target):
    edge = {
        "Source": source,
        "Target": target,
        "Type": "undirected"
    }
    return edge


class Reddit:
    def __init__(self, api):
        self.reddit = praw.Reddit(
            client_id=api["client_id"],
            client_secret=api["client_secret"],
            user_agent=api["user_agent"]
        )

    def test(self):

        submission = self.reddit.submission(id="9jcfw2")
        print(submission.title)
        pprint.pprint(vars(submission))
        # redditor = self.reddit.redditor("spez")
        # comments = redditor.comments.top(limit=1)
        # for comment in comments:
        #     print(comment.body)
        #     pprint.pprint(vars(comment))

    def fetch_subreddits_by_name(
        self,
        keyword,
        limit=20,
        nsfw=True,
        exact=False
    ):
        subreddits = self.reddit.subreddits.search_by_name(
            "t", include_nsfw=nsfw, exact=exact)

        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

        for subreddit in subreddits:
            subreddits_list.append(create_subreddit_node(subreddit))

        dataframes = {
            "subreddits": pd.DataFrame(subreddits_list),
            "submissions": pd.DataFrame(submissions_list),
            "redditors": pd.DataFrame(redditors_list),
            "comments": pd.DataFrame(comments_list),
            "submission_edges": pd.DataFrame(submission_edges),
            "comment_edges": pd.DataFrame(comment_edges)
        }
        return dataframes

    def fetch_subreddits_by_topic(
        self,
        keyword,
        limit=20
    ):
        subreddits = self.reddit.subreddits.search(
            keyword, limit=limit)

        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

        for subreddit in subreddits:
            subreddits_list.append(create_subreddit_node(subreddit))

        dataframes = {
            "subreddits": pd.DataFrame(subreddits_list),
            "submissions": pd.DataFrame(submissions_list),
            "redditors": pd.DataFrame(redditors_list),
            "comments": pd.DataFrame(comments_list),
            "submission_edges": pd.DataFrame(submission_edges),
            "comment_edges": pd.DataFrame(comment_edges)
        }
        return dataframes

    def fetch_subreddit_submissions(
        self,
        keyword="",
        subreddit_name="all",
        limit=20,
        sort="top",
        time_filter="month"
    ):
        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

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

        for submission in submissions:
            redditors_list.append(create_redditor_node(submission.author))

            submissions_list.append(create_submission_node(submission))
            submission_edges.append(create_edge(
                submission.id, submission.subreddit.id))
            submission_edges.append(create_edge(
                submission.author.fullname[3:], submission.id))

        subreddits_list.append(create_subreddit_node(submission.subreddit))

        dataframes = {
            "subreddits": pd.DataFrame(subreddits_list),
            "submissions": pd.DataFrame(submissions_list),
            "redditors": pd.DataFrame(redditors_list),
            "comments": pd.DataFrame(comments_list),
            "submission_edges": pd.DataFrame(submission_edges),
            "comment_edges": pd.DataFrame(comment_edges)
        }
        return dataframes

    def fetch_submission_comments(
        self,
        submission_id,
        limit=20,
        sort="top",
        time_filter="month",
        top_level=False
    ):

        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

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

        for comment in comments:
            if comment.author is None:
                continue

            redditors_list.append(create_redditor_node(comment.author))

            comments_list.append(create_comment_node(comment))
            comment_edges.append(create_edge(
                comment.id, comment.parent_id[3:]))
            comment_edges.append(create_edge(
                comment.author.fullname[3:], comment.id))

            i += 1
            if i == limit:
                break

        # pprint.pprint(vars(submission))
        submissions_list.append(create_submission_node(submission))
        submission_edges.append(create_edge(
            submission.id, submission.subreddit.id))
        submission_edges.append(create_edge(
            submission.author.fullname[3:], submission.id))

        subreddits_list.append(create_subreddit_node(submission.subreddit))

        dataframes = {
            "subreddits": pd.DataFrame(subreddits_list),
            "submissions": pd.DataFrame(submissions_list),
            "redditors": pd.DataFrame(redditors_list),
            "comments": pd.DataFrame(comments_list),
            "submission_edges": pd.DataFrame(submission_edges),
            "comment_edges": pd.DataFrame(comment_edges)
        }
        return dataframes

    def fetch_redditor_comments(
        self,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):
        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

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

        for comment in comments:

            comments_list.append(create_comment_node(comment))
            comment_edges.append(create_edge(
                redditor.fullname[3:], comment.id))
            comment_edges.append(create_edge(
                comment.id, comment.parent_id[3:]))

            submission = self.reddit.submission(id=comment.link_id[3:])
            submissions_list.append(create_submission_node(submission))
            submission_edges.append(create_edge(
                submission.id, submission.subreddit.id))
            submission_edges.append(create_edge(
                submission.author.fullname[3:], submission.id))

            subreddits_list.append(create_subreddit_node(comment.subreddit))

        redditors_list.append(redditor)
        dataframes = {
            "subreddits": pd.DataFrame(subreddits_list),
            "submissions": pd.DataFrame(submissions_list),
            "redditors": pd.DataFrame(redditors_list),
            "comments": pd.DataFrame(comments_list),
            "submission_edges": pd.DataFrame(submission_edges),
            "comment_edges": pd.DataFrame(comment_edges)
            # "nodes": {
            #     "subreddits": pd.DataFrame(subreddits_list),
            #     "submissions": pd.DataFrame(submissions_list),
            #     "redditors": pd.DataFrame(redditors_list),
            #     "comments": pd.DataFrame(comments_list)
            # },
            # "edges": {
            #     "submission_edges": pd.DataFrame(submission_edges),
            #     "comment_edges": pd.DataFrame(comment_edges)
            # }
        }
        return dataframes

    def fetch_redditor_submissions(
        self,
        username,
        limit=20,
        sort="new",
        time_filter="month"
    ):

        subreddits_list = []
        submissions_list = []
        redditors_list = []
        comments_list = []
        submission_edges = []
        comment_edges = []

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

        for submission in submissions:
            subreddits_list.append(create_subreddit_node(submission.subreddit))
            redditors_list.append(create_redditor_node(submission.author))

            submissions_list.append(create_submission_node(submission))
            submission_edges.append(create_edge(
                submission.id, submission.subreddit.id))
            submission_edges.append(create_edge(
                submission.author.fullname[3:], submission.id))

        dataframes = {
            "nodes": {
                "subreddits": pd.DataFrame(subreddits_list),
                "submissions": pd.DataFrame(submissions_list),
                "redditors": pd.DataFrame(redditors_list),
                "comments": pd.DataFrame(comments_list)
            },
            "edges": {
                "submission_edges": pd.DataFrame(submission_edges),
                "comment_edges": pd.DataFrame(comment_edges)
            }
        }
        return dataframes

# class Redditor (BareboneNode):
#     def __init__(
#         self,
#         id,
#         name,
#         created,
#         link_karma,
#         comment_karma
#     ):
#         BareboneNode.__init__(self, id)
#         self.name = name
#         self.created = created
#         self.link_karma = link_karma
#         self.comment_karma = comment_karma


# class Submission (BareboneNode):
#     def __init__(
#         self,
#         id,
#         created,
#         title,
#         url,
#         upvote_ratio,
#         score,
#         selftext,
#         over_18,
#         preview,
#         media,
#         author_fullname,
#     ):
#         BareboneNode.__init__(self, id)
#         self.created = created
#         self.title = title
#         self.url = url
#         self.upvote_ratio = upvote_ratio
#         self.score = score
#         self.selftext = selftext
#         self.over_18 = over_18
#         self.preview = preview
#         self.media = media
#         self.author_fullname = author_fullname


# class Subreddit (BareboneNode):
#     def __init__(
#         self,
#         id,
#         display_name,
#         active_user_count,
#         created,
#         description,
#         header_title,
#         public_description,
#         subscribers,
#         title,
#         url,
#         subreddit_type
#     ):
#         BareboneNode.__init__(self, id)
#         self.display_name = display_name
#         self.active_user_count = active_user_count
#         self.created = created
#         self.description = description
#         self.header_title = header_title
#         self.public_description = public_description
#         self.subscribers = subscribers
#         self.title = title
#         self.url = url
#         self.subreddit_type = subreddit_type


# class Comment (BareboneEdge):
#     def __init__(
#         self,
#         id,
#         score,
#         body,
#         created,
#         parent_id,
#         author_fullname,
#         subreddit_id
#     ):
#         BareboneEdge.__init__(self, id, parent_id, author_fullname)
#         self.score = score
#         self.body = body
#         self.created = created
#         self.subreddit_id = subreddit_id
