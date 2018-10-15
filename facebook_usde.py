from facebook_api import Facebook


class USDE:
    def __init__(self, api):
        facebook_api = api["facebook"]
        self.facebook = Facebook(facebook_api)

    def get_facebook(self):
        return self.facebook


api = {
    "facebook": {
        "access_token": 'EAAcuifsRNJUBAK8iBFcHjhAFl9isPnC3rD47JOSuyZAGjR4JQgBieMvzYLthm9jnQaxlisxkGgRrnAjqyhW7LtwKPArmYN8BUxn3X5avZA0eghEXW5La68g7YWUEbO48wgn4eZCiFZBh1m7FW11fAH6SehlPEQkyFUiksnz32Xyh6cHaHzpjtGoWIdeWZBQr0dCMjHpaFUgZDZD',
        "id": 'me'
    }
}

usde = USDE(api)
facebook = usde.get_facebook()
user_graph = facebook.fetch_facebook_user_info('me')
user_post_graph = facebook.fetch_Facebook_user_created_post('me')
user_liked_page_graph = facebook.fetch_facebook_user_liked_pages('me')
# # user_community_graph = facebook.fetch_facebook_user_friends('me')
comment_post_graph = facebook.fetch_facebook_post_comments('1543600752452807_1367858056693745')

user_graph.export_all_CSV("facebook_user_graph")

user_post_graph.export_all_CSV("facebook_user_post_graph")

user_liked_page_graph.export_all_CSV("facebook_user_liked_page")

comment_post_graph.export_all_CSV("facebook_comment_post")

# node_opt = {"post"}
# edge_opt = {}
# user_post_graph.export_CSV("user_post", node_opt, edge_opt)
