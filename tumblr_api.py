import pytumblr
import pandas as pd
import pprint
from graph import Graph, Node, Edge


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

    def fetch_followed_blogs_by_blog_name(
            self,
            blog_name,
            limit=20,
            offset=0
    ):
        followed_blogs = self.tumblr.blog_following(blog_name)['blogs']
        blog = self.tumblr.blog_info(blog_name)['blog']
        graph = Graph()
        for followed_blog in followed_blogs:
            graph.create_node(Blog(followed_blog))
            graph.create_edge(Edge(blog['name'], followed_blog['name']))
        return graph.get_dataFrame()

    # the api function call "blog_followers" doesn't seem to work

    def fetch_published_posts_by_blog_name(
        self,
        blog_name,  # blog name
        type="text",
        tag="",
        limit=20,
        offset=0,
        before=0
    ):
        published_posts = self.tumblr.posts(blog_name)['posts']
        blog = self.tumblr.blog_info(blog_name)['blog']
        graph = Graph()
        for published_post in published_posts:
            graph.create_node(Post(published_post))
            graph.create_edge(Edge(blog['name'], str(published_post['id'])))
        return graph.get_dataFrame()

    def fetch_liked_posts_by_blog_name(
        self,
        blog_name,
        limit=20,
        offset=0,
        before=0,
        after=0
    ):
        liked_posts = self.tumblr.blog_likes(blog_name)['liked_posts']
        blog = self.tumblr.blog_info(blog_name)['blog']
        graph = Graph()
        for liked_post in liked_posts:
            graph.create_node(Post(liked_post))
            graph.create_edge(Edge(blog['name'], str(liked_post['id'])))
        return graph.get_dataFrame()

    def fetch_posts_tagged_by_tag(
        self,
        tag,
        blog_name="",
        limit=20,
        before=0,
        filter=""
    ):
        posts_tagged = self.tumblr.tagged(tag)

        graph = Graph()
        for post_tagged in posts_tagged:
            graph.create_node(Post(post_tagged))
        return graph.get_dataFrame()


class Blog (Node):
    def __init__(
        self,
        blog
    ):
        Node.__init__(self, blog['name'], blog['title'])
        self.label_attribute = "blog",
        self.name = blog['name'],
        self.title = blog['title'],
        self.updated = blog['updated'],
        self.description = blog['description']


class Post (Node):
    def __init__(
        self,
        post
    ):
        Node.__init__(self, post['id'], post['id'])
        self.blog_name = post['blog_name'],
        self.post_url = post['post_url'],
        self.type = post['type'],
        self.timestamp = post['timestamp'],  # The time of the post, in seconds since the epoch
        self.date = post['date'],  # The GMT date and time of the post, as a string
        self.format = post['format'],  # String The post format: html or markdown
        self.tags = post['tags'],  # Array(string) Tags applied to the post
        self.state = post['state']

# Typed post nodes are coming...

