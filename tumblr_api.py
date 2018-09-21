import pytumblr


class Tumblr:
    def __init__(self, api):
        self.tumblr = pytumblr.TumblrRestClient(
            consumer_key=api["consumer_key"],
            consumer_secret=api["consumer_secret"],
            oauth_token=api["oauth_token"],
            oauth_secret=api["oauth_secret"]
        )

    def fetch_tumblr_blog_info(
        self,
        blog_hostname
    ):
        self.tumblr.blog_info(blog_hostname) # TODO: put data into a Blog node object

    def fetch_tumblr_blog_following(
        self,
        blog_hostname,
        limit=20,
        offset=0
    ):
        self.tumblr.blog_following(blog_hostname) # TODO: put data in Blog node objects and Follow_blog edge objects

    def fetch_tumblr_blog_followers(
        self,
        blog_hostname,
        limit=20,
        offset=0
    ):
        self.tumblr.followers(blog_hostname)  # TODO: put data in Blog node objects and Follow_blog edge objects

    def fetch_tumblr_posts_published(
        self,
        blog_hostname,
        type="text",
        tag="",
        limit=20,
        offset=0,
        before=0
    ):
        self.tumblr.client.posts(blog_hostname, **params)  # TODO: put data in a Blog node object and Post node objects

    def fetch_tumblr_posts_liked(
        self,
        blog_hostname,
        limit=20,
        offset=0,
        before=0,
        after=0
    ):
        self.tumblr.client.blog_likes(blog_hostname)
        # TODO: put data in a Blog node object, Post node objects and Like_post edge objects

    def fetch_tumblr_posts_tagged(
        self,
        blog_hostname,
        tag="",
        limit=20,
        before=0,
        filter=""
    ):
        self.tumblr.client.tagged(tag, **params)  # TODO: put data in Post node objects