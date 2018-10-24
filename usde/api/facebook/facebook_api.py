import os
import json
import facebook
from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge


class Facebook:
    def __init__(self, api):
        token = api["access_token"]
        id = api["id"]
        self.graph = facebook.GraphAPI(token)

    def fetch_facebook_user_info(
            self,
            graph,
            id
    ):
        '''
        Fetches user information based on id

        nodes:
            - user
        edges:
            -
        '''        

        # search a user based on user id 
        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')

        # Create a user node in the graph
        graph.create_node(User(user))


    def fetch_facebook_user_created_post(
            self,
            graph,
            id,
            limit=20
    ):
        '''
        Fetches posts based on user id

        nodes:
            - post
            - user
        edges:
            - post
        '''
        
        # search user's post based on user id
        result = self.graph.get_object(id, fields='name,posts{full_picture,message,caption,created_time}')

        # search a user based on user id 
        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')

        # create an user object
        user_node = User(user)
        # create a new node for user
        graph.create_node(user_node)

        # get the data for array of posts
        post_data = result['posts']['data']

        i = 0

        # create post node for every post the user created
        for post in post_data:
            # check if reach the limit
            if i == limit:
                break
            i += 1

            post_node = Post(post)
            graph.create_node(post_node)
            graph.create_edge(Edge(user_node.get_id(), post_node.get_id(), "POSTED"))



    def fetch_facebook_user_liked_pages(
            self,
            graph,
            id,
            limit=20
    ):
        '''
        Fetches liked pages based on user id

        nodes:
            - pages
            - user
        edges:
            - pages
        '''

        # search user's liked pages based on user id
        result = self.graph.get_object(id, fields='name,likes{about,id,created_time,name,description,category,website}')

        # search a user based on user id 
        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')

        # create an user object
        user_node = User(user)
        # create a new node for user
        graph.create_node(user_node)

        # get the data for array of liked pages
        like_data = result['likes']['data']

        i = 0

        # create community node for every post the user liked
        for community in like_data:
            # check if reach the limit
            if i == limit:
                break
            i += 1

            community_node = Community(community)
            graph.create_node(community_node)
            graph.create_edge(Edge(user_node.get_id(), community_node.get_id(), "LIKED"))

        

    def fetch_facebook_user_friends(
            self,
            id
    ):
        profile = self.graph.get_object(id, fields='friends{name,id}')



    def fetch_facebook_post_comments(
            self,
            graph,
            id,
            limit=20
    ):
        '''
        Fetches comments based on post id

        nodes:
            - comment
            - post
            - user
        edges:
            - comment
        '''

        # search post based on post id
        post = self.graph.get_object(id, fields='full_picture,message,caption,created_time,comments{id,from,message,created_time}')

        # get the data for array of comments
        comment_data = post['comments']['data']

        # create a post object
        post_node = Post(post)

        # create a new node for post
        graph.create_node(post_node)

        i = 0

        for comment in comment_data:
            # check if reach the limit
            if i == limit:
                break
            i += 1

            # create a comment object
            comment_node = Comment(comment)
            # create a new node for comment
            graph.create_node(comment_node)
            # create an edge bewteen comment id and post id
            graph.create_edge(Edge(comment_node.get_id(), post_node.get_id(), "COMMENTED"))

            user = {'id': comment_node.get_creator_id(), 'name': comment_node.get_creator_name()}

            # create an user object
            user_node = User(user)
            # create a new node for user
            graph.create_node(user_node)
            # create an edge bewteen user id and comment id
            graph.create_edge(Edge(user_node.get_id(), comment_node.get_id(), "COMMENTED"))



    def fetch_facebook_community_info(
            self,
            graph,
            id
    ):
        '''
        Fetches community information based on id

        nodes:
            - community
        edges:
            -
        '''   

        # search a community based on  id    
        community = self.graph.get_object(id, fields='about,id,created_time,name,description,category,website')

        # create a community object
        community_node = Community(community)
        # create a node for community
        graph.create_node(community_node)



    def fetch_facebook_community_feed(
            self,
            graph,
            id,
            limit=20
    ):
        '''
        Fetches feeds based on community id

        nodes:
            - post
            - community
        edges:
            - post
        '''
        
        # search user's post based on user id
        result = self.graph.get_object(id, fields='name,feeds{full_picture,message,caption,created_time}')

        # search a community based on community id 
        community = self.graph.get_object(id, fields='about,id,created_time,name,description,category,website')

        # create an community object
        community_node = Community(community)
        # create a new node for user
        graph.create_node(community_node)

        # get the data for array of feeds
        post_data = result['feeds']['data']

        i = 0

        # create post node for every post the user created
        for post in post_data:
            # check if reach the limit
            if i == limit:
                break
            i += 1

            post_node = Post(post)
            graph.create_node(post_node)
            graph.create_edge(Edge(community_node.get_id(), post_node.get_id(), "POSTED"))


    def fetch_facebook_event_info(
            self,
            id
    ):
        result = self.graph.get_object(id, fields='about,name,id')



class User(Node):
    def __init__(
            self,
            user
    ):
        Node.__init__(self, user['id'], user['name'], "user")
        self.name = user['name']

        if 'email' in user:
            self.email = user['email']
        else:
            self.email = None

        if 'gender' in user:
            self.gender = user['gender']
        else:
            self.gender = None

        if 'birthday' in user:
            self.birthday = user['birthday']
        else:
            self.birthday = None

        if 'hometown' in user:
            self.hometown = user['hometown']['name']
        else:
            self.hometown = None


class Post(Node):
    def __init__(
            self,
            post
    ):
        Node.__init__(self, post['id'], "post_" + post['id'], "post")
        self.created_time = post['created_time']
        self.creator_id = post['id'].split('_')[0]

        if 'message' in post:
            self.message = post['message']
        else:
            self.message = None

        if 'full_picture' in post:
            self.picture = post['full_picture']
        else:
            self.picture = None

        if 'caption' in post:
            self.caption = post['caption']
        else:
            self.caption = None


class Community(Node):
    def __init__(
            self,
            community
    ):
        Node.__init__(self, community['id'], community['name'], "community")

        if 'about' in community:
            self.about = community['about']
        else:
            self.about = None

        if 'description' in community:
            self.description = community['description']
        else:
            self.description = None

        if 'category' in community:
            self.category = community['category']
        else:
            self.category = None

        if 'website' in community:
            self.website = community['website']
        else:
            self.website = None



# class Event (Node):
#   def __init__(
#       self,
#       event
#   ):
#       Node.__init__(self, event.id, event.name)
#       self.label_attribute="event"
#       self.event_id = event['id']
#       self.event_name = event['name']
#       self.description = event['about']
#       self.attending_count = event['attending_count']
#       self.declined_count = event['declined_count']
#       self.start_time: event['start_time']
#       self.end_time: event['end_time']
#       self.is_canceled = event['is_canceled']
#       self.interested_count = event['interested_count']
#       self.maybe_count: event['maybe_count']
#       self.noreply_count = event['noreply_count']

class Comment(Node):
    def __init__(
            self,
            comment
    ):
        Node.__init__(self, comment['id'], comment['id'], "comment")

        self.created_time = comment['created_time']
        self.creator_id = comment['from']['id']
        self.creator_name = comment['from']['name']

        if 'message' in comment:
            self.message = comment['message']
        else:
            self.message = None

    def get_creator_name(self):
        return self.creator_name

    def get_creator_id(self):
        return self.creator_id
