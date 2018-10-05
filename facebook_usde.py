from facebook_api import Facebook


class USDE:
    def __init__(self, api):
        facebook_api = api["facebook"]
        self.facebook = Facebook(facebook_api)

    def get_facebook(self):
        return self.facebook


api = {
    "facebook": {
        "access_token": 'EAAcuifsRNJUBAIpJZBhhSZBZBSUm6onGL2ML3TnLZBXAccqPvJdbg0IZAS7zm00KqsWRRdgzjDw0y6DskDkMgP1c2NFJRQXTuf0vkg5WbM99kVpQ4vKB8EnJd2l2eVNGNrOtiiBwQtj5VL4pGphfZC0eTmrnesSyxkciFos0X1MlvYZBlGNTvhye3zEkTw3WkOjuFL6xfWh9wZDZD',
        "id": 'me'
    }
}

usde = USDE(api)
facebook = usde.get_facebook()
facebook.fetch_facebook_user_info('me')
facebook.fetch_Facebook_user_created_post('me')
facebook.fetch_facebook_user_liked_pages('me')
facebook.fetch_facebook_user_friends('me')
facebook.fetch_facebook_post_comments('1543600752452807_1367858056693745')
