import pytumblr
import pandas as pd


def create_blog_node(blog):
    blog_node = {
        #"id": blog['id'],  # ???
        "name": blog['name'],
        "title": blog['title'],
        #"posts": blog['posts'],  # Number num_posts
        "updated": blog['updated'], # Number The time of the most recent post, in seconds since the epoch
        "description": blog['description'],
        # "ask": blog.ask, # Boolean Indicates whether the blog allows questions
        # "ask_anon": blog.ask_anon,  # Boolean Indicates whether the blog allows anonymous questions
        # "likes": blog['likes'],  # Number Number of likes for this use
        # "is_blocked_from_primary": blog.is_blocked_from_primary
        # Boolean Indicates whether this blog has been blocked by the calling user's primary blog
    }
    return blog_node


def create_post_node(post):
    post_node = {
        "id": post['id'],  # ???
        "blog_name": post['blog_name'],
        "post_url": post['post_url'],
        "type": post['type'],
        "timestamp": post['timestamp'],  # Number The time of the post, in seconds since the epoch
        "date": post['date'],  # The GMT date and time of the post, as a string
        "format": post['format'],  # String The post format: html or markdown
        # "reblog_key": post.reblog_key,  # String The key used to reblog this post
        "tags": post['tags'],  # Array(string) Tags applied to the post
        # "bookmarklet": post.bookmarklet,  # Boolean Indicates whether the post was created via the Tumblr bookmarklet
        # "mobile": post.mobile,  # Boolean Indicates whether the post was created via mobile / email publishing
        # "source_url": post['source_url'],  # String The URL for the source of the content ( for quotes, reblogs, etc.)
        # "source_title": post['source_title'],
        # "liked": post.liked,
        "state": post['state'],
        # "total_posts": post['total_posts']
    }
    return post_node


# Typed post nodes are coming...

def create_edge(source, target):
    edge = {
        "Source": source,
        "Target": target,
        "Type": "undirected"
    }
    return edge


class Tumblr:
    def __init__(self, api):
        self.tumblr = pytumblr.TumblrRestClient(
            consumer_key=api["consumer_key"],
            consumer_secret=api["consumer_secret"],
            oauth_token=api["oauth_token"],
            oauth_secret=api["oauth_secret"]
        )

    def exportCSV(self, dataframes, prefix):

        for key in dataframes.keys():
            dataframes[key].to_csv(
                prefix + "_" + key + ".csv", encoding="utf-8", index=False)

    def fetch_tumblr_blog(
            self,
            blog_name
    ):
        dataframes_info = self.fetch_tumblr_blog_info(blog_name)
        self.exportCSV(dataframes_info, "tumblr")
        dataframes_followed_bogs = self.fetch_tumblr_followed_blogs(blog_name)
        self.exportCSV(dataframes_followed_bogs, "tumblr")
        dataframes_published_posts = self.fetch_tumblr_published_posts(blog_name)
        self.exportCSV(dataframes_published_posts, "tumblr")
        dataframes_liked_posts = self.fetch_tumblr_liked_posts(blog_name)
        self.exportCSV(dataframes_liked_posts, "tumblr")
        return

    def fetch_tumblr_blog_info(
        self,
        blog_name
    ):
        blogs_list = []
        blogs_list.append(create_blog_node(self.tumblr.blog_info(blog_name)['blog']))
        dataframes = {
            "blogs": pd.DataFrame(blogs_list)
        }
        return dataframes

    def fetch_tumblr_followed_blogs(
        self,
        blog_name,
        limit=20,
        offset=0
    ):
        blog_node_self = create_blog_node(self.tumblr.blog_info(blog_name)['blog'])
        blogs_following = self.tumblr.blog_following(blog_name)['blogs']

        blogs_list = []
        follow_blog_edges = []

        blogs_list.append(blog_node_self)

        for blog in blogs_following:
            blog_node = create_blog_node(blog)
            blogs_list.append(blog_node)
            follow_blog_edges.append(create_edge(blog_node_self['name'], blog_node['name']))

        dataframes = {
            "blogs": pd.DataFrame(blogs_list),
            "follow_blog_edges": pd.DataFrame(follow_blog_edges)
        }
        return dataframes

    # the api function call "blog_followers" doesn't seem to work
    """def fetch_tumblr_blog_followers(
        self,
        blog_name,
        limit=20,
        offset=0
    ):
        blogs = self.tumblr.blog_followers(blog_name)['blogs']
        
        blogs_list = []

        for blog in blogs:
            blogs.append(create_blog_node(blog))

        dataframes = {
            "blogs": pd.DataFrame(blogs_list)
        }
        return dataframes"""

    def fetch_tumblr_published_posts(
        self,
        blog_name,  # blog name
        type="text",
        tag="",
        limit=20,
        offset=0,
        before=0
    ):
        posts = self.tumblr.posts(blog_name)['posts']

        posts_list = []
        publish_post_edges = []

        for post in posts:
            post_node = create_post_node(post)
            posts_list.append(post_node)
            publish_post_edges.append(create_edge(blog_name, post_node['id']))

        dataframes = {
            "posts": pd.DataFrame(posts_list),
            "publish_post_edges": pd.DataFrame(publish_post_edges)
        }
        return dataframes

    def fetch_tumblr_liked_posts(
        self,
        blog_name,
        limit=20,
        offset=0,
        before=0,
        after=0
    ):
        posts = self.tumblr.blog_likes(blog_name)['liked_posts']

        posts_list = []
        like_post_edges = []

        for post in posts:
            post_node = create_post_node(post)
            posts_list.append(post_node)
            like_post_edges.append(create_edge(blog_name, post_node['id']))

        dataframes = {
            "posts": pd.DataFrame(posts_list),
            "like_post_edges": pd.DataFrame(like_post_edges)
        }
        return dataframes

    def fetch_tumblr_posts_tagged(
        self,
        tag,
        blog_name="",
        limit=20,
        before=0,
        filter=""
    ):
        posts = self.tumblr.tagged(tag)

        posts_list = []

        for post in posts:
            posts_list.append(create_post_node(post))

        dataframes = {
            "posts": pd.DataFrame(posts_list)
        }
        return dataframes
