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

    def fetch_followed_blogs(
            self,
            blog_name,
            limit=20,
            offset=0
    ):
        followed_blogs = self.tumblr.blog_following(blog_name, limit=limit, offset=offset)['blogs']
        blog = self.tumblr.blog_info(blog_name)['blog']

        graph = Graph()
        graph.create_node(Blog(blog))
        for followed_blog in followed_blogs:
            graph.create_node(Blog(followed_blog))
            graph.create_edge(Edge(blog['name'], followed_blog['name'], "followed_blog"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    # the api function call "blog_followers" doesn't seem to work

    def fetch_published_posts(
        self,
        blog_name,  # blog name
        type="text",
        tag="",
        limit=20,
        offset=0
    ):
        published_posts = self.tumblr.posts(blog_name, type=type, tag=tag, limit=limit, offset=offset)['posts']
        blog = self.tumblr.blog_info(blog_name)['blog']
        graph = Graph()
        graph.create_node(Blog(blog))
        for published_post in published_posts:
            graph.create_node(Post(published_post))
            graph.create_edge(Edge(blog['name'], str(published_post['id']), "published_post"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_liked_posts(
        self,
        blog_name,
        limit=20,
        offset=0,
        before=0,
        after=0
    ):
        liked_posts = self.tumblr.blog_likes(blog_name, limit=limit, offset=offset, before=before, after=after)['liked_posts']
        blog = self.tumblr.blog_info(blog_name)['blog']

        graph = Graph()
        graph.create_node(Blog(blog))
        for liked_post in liked_posts:
            graph.create_node(Post(liked_post))
            graph.create_edge(Edge(blog['name'], str(liked_post['id']), "liked_post"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_posts_tagged(
        self,
        tag,
        limit=20,
        before=0,
        filter=""
    ):
        posts_tagged = self.tumblr.tagged(tag=tag, limit=limit, before=before, filter=filter)

        graph = Graph()
        for post_tagged in posts_tagged:
            graph.create_node(Post(post_tagged))
            blog = self.tumblr.blog_info(post_tagged['blog_name'])['blog']
            graph.create_node(Blog(blog))
            graph.create_edge(Edge(blog['name'], str(post_tagged['id']), "published_post"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph


class Blog (Node):
    def __init__(
        self,
        blog
    ):
        Node.__init__(self, blog['name'], blog['title'], "blog")
        self.name = blog['name'],
        self.title = blog['title'],
        self.updated = blog['updated'],
        self.description = blog['description']


class Post (Node):
    def __init__(
        self,
        post
    ):
        Node.__init__(self, post['id'], post['id'], "post")
        self.blog_name = post['blog_name'],
        self.post_url = post['post_url'],
        self.type = post['type'],
        self.timestamp = post['timestamp'],  # The time of the post, in seconds since the epoch
        self.date = post['date'],  # The GMT date and time of the post, as a string
        self.format = post['format'],  # String The post format: html or markdown
        self.tags = post['tags'],  # Array(string) Tags applied to the post
        self.state = post['state']


