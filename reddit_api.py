import praw


class Reddit:
    def __init__(self, api):
        self.reddit = praw.Reddit(
            client_id=api["client_id"],
            client_secret=api["client_secret"],
            user_agent=api["user_agent"]
        )

    def fetch_reddit_submissions(
        self,
        keyword="",
        subreddit_name="all",
        limit=20,
        sort="top",
        time_filter="month"
    ):

        if keyword == "":
            submissions = self.reddit.subreddit(subreddit_name)

            if sort == "top":
                submissions = submissions.top(
                    limit=limit, time_filter=time_filter)
            elif sort == "hot":
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
            submissions = self.reddit.subreddit(subreddit_name).search(
                keyword, sort=sort, time_filter=time_filter, limit=limit)

        for submission in submissions:
            print submission.id

    def fetch_subreddits_by_topic(
        self,
        keyword,
        limit=20
    ):
        subreddits = self.reddit.subreddits.search(
            keyword, limit=limit)
        for subreddit in subreddits:
            print(subreddit)

    def fetch_subreddits_by_name(
        self,
        keyword,
        limit=20,
        nsfw=True,
        exact=False
    ):
        subreddits = self.reddit.subreddits.search_by_name(
            "t", include_nsfw=nsfw, exact=exact)
        for subreddit in subreddits:
            print(subreddit)

    def fetch_submission_top_level_comments(
        self,
        submission_id,
        limit=20,
        sort="top",
        time_filter="month"
    ):

        submission = self.reddit.submission(id=submission_id, limit=limit)
        submission.comment_sort = sort
        if limit == None:
            comments = list(submission.comments.replace_more(limit=None))
        else:
            comments = list(submisison.comments.replace_more(limit=limit))
        for comment in comments:
            print(comment.id)

    def fetch_submission_comments(
        self,
        submission_id,
        limit=20,
        sort="top",
        time_filter="month"
    ):
        submission = self.reddit.submission(id=submission_id)
        submission.comment_sort = sort
        if limit == None:
            comments = submission.comments.replace_more(limit=None)
        else:
            comments = submission.comments.replace_more(limit=0)
        for comment in comments:
            print(comment.id)

    def fetch_redditor_comments(
        self,
        user_id,
        api_credential,
        limit=20,
        sort="top",
        time_filter="month"
    ):
        pass

    def fetch_redditor_submissions(
        self,
        user_id,
        api_credential,
        limit=20,
        sort="top",
        time_filter="month"
    ):
        pass
