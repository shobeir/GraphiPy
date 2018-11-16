import pytumblr

from graphipy.graph.graph_base import BaseGraph as Graph, BaseNode as Node, BaseEdge as Edge


class Tumblr:
    """the Tumblr object that is powered by Pytumblr"""

    def __init__(self, api):
        self.tumblr = pytumblr.TumblrRestClient(
            consumer_key=api["consumer_key"],
            consumer_secret=api["consumer_secret"],
            oauth_token=api["oauth_token"],
            oauth_secret=api["oauth_secret"]
        )

    def fetch_blog(
        self,
        graph,
        blog_name
    ):
        """
        Fetches information of a blog with the identifier "blog_name"

        node:
            - blog
        """
        blog = self.tumblr.blog_info(blog_name)['blog']
        graph.create_node(Blog(blog))

        return graph

    def fetch_blogs_following(
            self,
            graph,
            blog_name,
            limit=20,
            offset=0  # From which blog the fetch starts
    ):
        """
        Fetches blogs followed by the blog with the identifier "blog_name"

        nodes:
            - blog
        edges:
            - FOLLOWING
        """

        blogs_following_raw = self.tumblr.blog_following(blog_name, limit=limit, offset=offset)

        try:
            blogs_following = blogs_following_raw['blogs']
            blog = self.tumblr.blog_info(blog_name)['blog']

            # Create a node for each blog
            graph.create_node(Blog(blog))
            for blog_following in blogs_following:
                graph.create_node(Blog(blog_following))
                graph.create_edge(Edge(blog['name'], blog_following['name'], "FOLLOWING"))
        except KeyError as error:
            print(error)
            print(blogs_following_raw)

        return graph

    def fetch_followers(
            self,
            graph,
            blog_name,
            limit=20,
            offset=0
    ):
        """
            Fetches blogs following the blog with the identifier "blog_name"

            nodes:
                - blog
            edges:
                - FOLLOWER
        """
        followers_raw = self.tumblr.followers(blog_name, limit=limit, offset=offset)

        try:
            followers = followers_raw ['users']
            blog = self.tumblr.blog_info(blog_name)['blog']

            # Create a graph for each node
            graph.create_node(Blog(blog))
            for follower in followers:
                graph.create_node(Blog(follower))
                graph.create_edge(Edge(blog['name'], follower['name'], "FOLLOWER"))
        except KeyError as error:
            print(error)
            print(followers_raw)

        return graph

    def fetch_published_posts(
        self,
        graph,
        blog_name,
        type=None,
        tag="",
        limit=20,
        offset=0
    ):
        """
            Fetches posts published by the blog with the identifier "blog_name"

            nodes:
                - blog
                - post
            edges:
                - PUBLISHED
        """
        published_posts_raw = self.tumblr.posts(blog_name, type=type, tag=tag, limit=limit, offset=offset)

        try:
            published_posts = published_posts_raw['posts']
            blog = self.tumblr.blog_info(blog_name)['blog']

            graph.create_node(Blog(blog))
            # Create a post node for each post
            for published_post in published_posts:
                graph.create_node(Post(published_post))
                graph.create_edge(Edge(blog['name'], str(published_post['id']), "PUBLISHED"))
        except KeyError as error:
            print(error)
            print(published_posts_raw)

        return graph

    def fetch_liked_posts(
        self,
        graph,
        blog_name,
        limit=20,
        offset=0,
        before=0,
        after=0
    ):
        """
            Fetches posts liked by the blog with the identifier "blog_name"

            nodes:
                - blog
                - post
            edges:
                - LIKED
        """
        liked_posts_raw = self.tumblr.blog_likes(blog_name, limit=limit, offset=offset, before=before, after=after)

        try:
            liked_posts = liked_posts_raw['liked_posts']
            blog = self.tumblr.blog_info(blog_name)['blog']

            # Create a node for the blog
            blog_node = Blog(blog)
            graph.create_node(blog_node)
            # Create a node for each post
            for liked_post in liked_posts:
                post_node = Post(liked_post)
                graph.create_node(post_node)
                graph.create_edge(Edge(blog_node.get_id(), str(post_node.get_id()), "LIKED"))
        except KeyError as error:
            print(error)
            print(liked_posts_raw)

        return graph

    def fetch_posts_tagged(
        self,
        graph,
        tag,
        limit=20,
        before=0,
        filter=""
    ):
        """
            Fetches posts and their publishers (blogs) with a given tag

            nodes:
                - blog
                - post
            edges:
                - PUBLISHED
        """
        posts_tagged = self.tumblr.tagged(tag=tag, limit=limit, before=before, filter=filter)

        # Create a pair of nodes for each post-blog pair
        for post_tagged in posts_tagged:
            graph.create_node(Post(post_tagged))
            blog = self.tumblr.blog_info(post_tagged['blog_name'])['blog']
            graph.create_node(Blog(blog))
            graph.create_edge(Edge(blog['name'], str(post_tagged['id']), "PUBLISHED"))

        return graph


class Blog (Node):
    """Tumblr's users are identified as Blogs"""

    def __init__(
        self,
        blog
    ):
        Node.__init__(self, blog['name'], blog['title'], "blog")
        self.name = blog['name']
        self.title = blog['title']
        self.description = blog['description']
        self.url = blog['url']
        self.uuid = blog['uuid']
        self.updated = blog['updated']


class Post (Node):
    """Posts are published by/within Blogs"""

    def __init__(
        self,
        post
    ):
        # print(post)
        Node.__init__(self, str(post['id']), str(post['id']), "post")

        self.type = post['type']  # Any one from text, photo, quote, link, chat, video, answer
        self.blog_name = post['blog_name']
        self.post_url = post['post_url']
        self.slug = post['slug']  # Short text summary to the end of the post URL
        self.date = post['date']  # The GMT date and time of the post, as a string
        self.timestamp = post['timestamp']  # The time of the post, in seconds since the epoch
        self.state = post['state']   # Indicates the current state of the post
        self.format = post['format']  # String The post format: html or markdown
        self.reblog_key = post["reblog_key"]  # The key used to reblog this post
        self.tags = post['tags']  # Array(string) Tags applied to the post
        self.short_url = post['short_url']
        self.summary = post['summary']
        self.is_blocks_post_format = post['is_blocks_post_format']
        self.recommended_source = post['recommended_source']
        self.recommended_color = post['recommended_color']
        self.followed = post['followed']
        self.liked = post['liked']
        self.note_count = post['note_count']
        self.can_like = post['can_like']
        self.can_reblog = post['can_reblog']
        self.can_send_in_message = post['can_send_in_message']
        self.can_reply = post['can_reply']
        self.display_avatar = post['display_avatar']

        try:
            if "text" in self.type:
                self.title = post['title']
                self.body = post['body']
                self.trail = post['trail']
                self.reblog = post['reblog']
            elif "photo" in self.type:
                self.caption = post['caption']
                self.photos = post['photos']
                self.trail = post['trail']
                self.reblog = post['reblog']
            elif "quote" in self.type:
                self.text = post['text']
                self.source = post['source']
                self.reblog = post['reblog']
            elif "link" in self.type:
                self.title = post['title']
                self.url = post['url']
                self.link_author = post['link_author']
                self.excerpt = post['excerpt']
                self.publisher = post['publisher']
                self.description = post['description']
                self.trail = post['trail']
                self.reblog = post['reblog']
            elif "chat" in self.type:
                self.title = post['title']
                self.body = post['body']
                self.dialogue = post['dialogue']
            elif "audio" in self.type:
                self.id3_title = post['id3_title']
                self.caption = post['caption']
                self.embed = post['embed']
                self.plays = post['plays']
                self.trail = post['trail']
                self.reblog = post['reblog']
            elif "video" in self.type:
                self.caption = post['caption']
                if 'permalink_url' in post:
                    self.permalink_url = post['permalink_url']
                if 'video_url' in post:
                    self.video_url = post['video_url']
                self.html5_capable = post['html5_capable']
                self.thumbnail_url = post['thumbnail_url']
                self.thumbnail_width = post['thumbnail_width']
                self.thumbnail_height = post['thumbnail_height']
                if 'duration' in post:
                    self.duration = post['duration']
                self.video_type = post['video_type']
                self.player = post['player']
                self.trail = post['trail']
                self.reblog = post['reblog']
            elif "answer" in self.type:
                self.asking_name = post['asking_name']
                self.asking_url = post['asking_name']
                self.question = post['question']
                self.answer = post['answer']
                self.trail = post['trail']
                self.reblog = post['reblog']
        except KeyError as error:
            print(error)
            print(post)







