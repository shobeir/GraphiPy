import pytumblr

from usde.graph.graph_base import BaseGraph as Graph, BaseNode as Node, BaseEdge as Edge


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
        except KeyError:
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
        except KeyError:
            print(followers_raw)

        return graph

    def fetch_published_posts(
        self,
        graph,
        blog_name,
        type="text",
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
        except KeyError:
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
            graph.create_node(Blog(blog))
            # Create a node for each post
            for liked_post in liked_posts:
                graph.create_node(Post(liked_post))
                graph.create_edge(Edge(blog['name'], str(liked_post['id']), "LIKED"))
        except KeyError:
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
            Fetches posts with a given tag and their publishers (blogs)

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
        Node.__init__(self, post['id'], post['id'], "post")
        self.type = post['type']  # Any one from text, photo, quote, link, chat, audio
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
        self.reblog = post['reblog']
        self.trail = post['trail']
        self.can_like = post['can_like']
        self.can_reblog = post['can_reblog']
        self.can_send_in_message = post['can_send_in_message']
        self.can_reply = post['can_reply']
        self.display_avatar = post['display_avatar']
        self.title = None  # Special field for text, link, chat posts
        self.body = None  # Special field for text, chat posts
        self.caption = None  # Special field for photo, chat, video posts
        self.image_permalink = None  # Special field for photo posts
        self.photos = None  # Special field for photo, link posts
        self.source_url = None  # Special field for quote, audio, video posts
        self.source_title = None  # Special field for quote, audio, video posts
        self.text = None  # Special field for quote posts
        self.source = None  # Special field for quote posts
        self.url = None  # Special field for link posts
        self.link_author = None  # Special field for link posts
        self.excerpt = None  # Special field for link posts
        self.publisher = None  # Special field for link posts
        self.description = None  # Special field for link posts
        self.dialogue = None  # Special field for chat posts
        self.id3_title = None  # Special field for audio posts
        self.embed = None  # Special field for audio posts
        self.plays = None  # Special field for audio posts
        self.player = None  # Special field for video posts
        self.asking_name = None  # Special field for answer posts
        self.asking_url = None  # Special field for answer posts
        self.question = None  # Special field for question posts
        self.answer = None  # Special field for answer posts

        try:
            if "text" in self.type:
                self.title = post['title']
                self.body = post['body']
            elif "photo" in self.type:
                self.caption = post['caption']
                self.image_permalink = post['image_permalink']
                self.photos = post['photos']
            elif "quote" in self.type:
                print(post)
                self.source_url = post['source_url']
                self.source_title = post['source_title']
                self.text = post['text']
                self.source = post['source']
            elif "link" in self.type:
                self.title = post['title']
                self.url = post['url']
                self.link_author = post['link_author']
                self.excerpt = post['excerpt']
                self.publisher = post['publisher']
                self.photos = post['photos']
                self.description = post['description']
            elif "chat" in self.type:
                print(post)
                self.title = post['title']
                self.body = post['body']
                self.dialogue = post['dialogue']
                self.source_url = post['source_url']
                self.source_title = post['source_title']
                self.id3_title = post['id3_title']
                self.caption = post['caption']
                self.embed = post['embed']
                self.plays = post['plays']
            elif "video" in self.type:
                print(post)
                self.source_url = post['source_url']
                self.source_title = post['source_title']
                self.caption = post['caption']
                self.player = post['player']
            elif "answer" in self.type:
                print(post)
                self.asking_name = post['asking_name']
                self.asking_url = post['asking_name']
                self.question = post['question']
                self.answer = post['answer']
        except KeyError:
            print("KeyError")
            print(post)







