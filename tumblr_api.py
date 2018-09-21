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

    def export_data(
            self,
            format,
            object_type_list,
            file_name,
            options=None
    ):
        pass # TODO: export specified data to


class Blog (BareboneNode):
    def __init__(
            self,
            title,
            hostname,
            num_posts,
            last_time_updated,
            description,
            num_likes
    ):
        self.title = title
        self.hostname = hostname
        self.num_posts = num_posts
        self.last_time_updated = last_time_updated
        self.description = description
        self.num_likes = num_likes


class Post (BareboneNode):
    def __init__(
            self,
            type,
            timestamp,
            date,
            tags,
            limit,
            state,
            liked,
            num_posts,
            creator
    ):
        self.type = type
        self.timestamp = timestamp
        self.date = date
        self.tags = tags
        self.limit = limit
        self.state  = state
        self.liked = liked
        self.limit = limit
        self.state = state
        self.liked = liked
        self.num_posts = num_posts
        self.creator = creator
        #TODO: add methods


class TextPost(Post):
    def __init__(
            self,
            type,
            timestamp,
            date,
            tags,
            limit,
            state,
            liked,
            num_posts,
            creator,
            title,
            body
    ):
        Post.__init__(self, type, timestamp, date, tags, limit, state, liked, num_posts, creator)
        self.title = title
        self.body = body


class PhotoPost(Post):
    def __init__(
            self,
            type,
            timestamp,
            date,
            tags,
            limit,
            state,
            liked,
            num_posts,
            creator,
            photos,
            caption,
            width,
            height
    ):
        Post.__init__(self, type, timestamp, date, tags, limit, state, liked, num_posts, creator)
        self.photos = photos
        self.caption = caption
        self.width = width
        self.height = height


class QuotePost(Post):
    def __init__(
            self,
            type,
            timestamp,
            date,
            tags,
            limit,
            state,
            liked,
            num_posts,
            creator,
            text,
            source
    ):
        Post.__init__(self, type, timestamp, date, tags, limit, state, liked, num_posts, creator)
        self.text = text
        self.source = source


class LinkPost(Post):
    def __init__(
            self,
            type,
            timestamp,
            date,
            tags,
            limit,
            state,
            liked,
            num_posts,
            creator,
            title,
            url,
            author,
            excerpt,
            publisher,
            photos,
            description
    ):
        Post.__init__(self, type, timestamp, date, tags, limit, state, liked, num_posts, creator)
        self.title = title
        self.url = url
        self.author = author
        self.excerpt = excerpt
        self.publisher = publisher
        self.photos = photos
        self.description = description


# TODO: continue with chat, audio, video and answer posts


# TODO: continue with edges
class Like_post(BareboneEdge):
    def __init__(
            self,
            user_id,
            post_id
    ):
        BareboneEdge.__init__(self, user_id, post_id)


class Follow_blog(BareboneEdge):
    def __init__(
            self,
            following_blog_id,
            followed_blog_id
    ):
        BareboneEdge.__init__(self, following_blog_id, followed_blog_id)