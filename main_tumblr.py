from tumblr_api import Tumblr


class USDE:
    def __init__(self, api):
        tumblr_api = api["tumblr"]
        self.tumblr = Tumblr(tumblr_api)

    def get_tumblr(self):
        return self.tumblr


api = {
    "tumblr": {
        "consumer_key": ' ',
        "consumer_secret": ' ',
        "oauth_token": ' ',
        "oauth_secret": ' '
    }
}

usde = USDE(api)
tumblr = usde.get_tumblr()
#tumblr.fetch_tumblr_posts_tagged(tag='trump')
#tumblr.fetch_tumblr_blog_following('azspot')
#tumblr.fetch_tumblr_blog_followers('azspot')
tumblr.fetch_tumblr_posts_published('azspot')