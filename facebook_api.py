import os
import json
import facebook
import pandas as pd
from graph import Graph, Node, Edge


class Facebook:
    def __init__(self, api):
        token = api["access_token"]
        id = api["id"]
        self.graph = facebook.GraphAPI(token)

    def fetch_facebook_user_info(
            self,
            id

    ):
        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')
        # print(json.dumps(user,indent=4))
        # user = User(profile)

        graph = Graph()
        graph.create_node(User(user))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_Facebook_user_created_post(
            self,
            id
    ):
        result = self.graph.get_object(id, fields='name,posts{full_picture,message,caption,created_time}')

        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')

        graph = Graph()
        user_node = User(user)
        graph.create_node(user_node)

        post_data = result['posts']['data']

        for post in post_data:
            post_node = Post(post)
            graph.create_node(post_node)
            graph.create_edge(Edge(user_node.get_id(), post_node.get_id(), "created_post"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_facebook_user_liked_pages(
            self,
            id,
            limit=20
    ):
        result = self.graph.get_object(id, fields='name,likes{about,id,created_time,name,description,category,website}')
        user = self.graph.get_object(id, fields='name,id,gender,birthday,hometown,email')

        graph = Graph()
        user_node = User(user)
        graph.create_node(user_node)

        like_data = result['likes']['data']

        for community in like_data:
            community_node = Community(community)
            graph.create_node(community_node)
            graph.create_edge(Edge(user_node.get_id(), community_node.get_id(), "liked_page"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_facebook_user_friends(
            self,
            id
    ):
        profile = self.graph.get_object(id, fields='friends{name,id}')

    # print(json.dumps(profile,indent=4))
    # for friend in profile.friend:
    # 	f = User(friends)

    def fetch_facebook_post_comments(
            self,
            post_id
    ):
        post = self.graph.get_object(post_id,
                                     fields='full_picture,message,caption,created_time,comments{id,from,message,created_time}')
        comment_data = post['comments']['data']

        graph = Graph()
        post_node = Post(post)
        graph.create_node(post_node)

        for comment in comment_data:
            comment_node = Comment(comment)
            graph.create_node(comment_node)
            graph.create_edge(Edge(comment_node.get_id(), post_node.get_id(), "comment"))

            user = {'id': comment_node.get_creator_id(), 'name': comment_node.get_creator_name()}
            user_node = User(user)
            graph.create_node(user_node)
            graph.create_edge(Edge(user_node.get_id(), comment_node.get_id(), "comment"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_facebook_community_info(
            self,
            id
    ):
        community = self.graph.get_object(id, fields='about,id,created_time,name,description,category,website')
        graph = Graph()
        community_node = Community(community)
        graph.create_node(community_node)

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_facebook_community_feed(
            self,
            id
    ):
        result = self.graph.get_object(id, fields='feeds')
        feed_data = result['feeds']['data']
        community_node = {'id': result['id'],
                          'name': result['name']
                          }
        feed_nodes = []
        feed_community_edges = []
        # print(json.dumps(result,indent=4))
        for feed in feed_data:
            feed_node = {'id': post['id'],
                         'created_time': post['created_time']
                         # ,
                         # 'message':post['message']
                         }
            feed_nodes.append(feed_node)
            feed_community_edges.append({'Source': feed['id'],
                                         'Target': community_node['id']
                                         })

    def fetch_facebook_event_info(
            self,
            id
    ):
        result = self.graph.get_object(id, fields='about,name,id')
# print(json.dumps(result,indent=4))
# event = Event(profile)


class User(Node):
    def __init__(
            self,
            user
    ):
        Node.__init__(self, user['id'], user['name'], "user")
        # self.label_attribute="user"
        self.name = user['name']

        if 'email' in user:
            self.email = user['email']
        # print(user['email'])
        else:
            self.email = None

        if 'gender' in user:
            self.gender = user['gender']
        # print(post['gender'])
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

# self.friends_count = user.friends.summary.total_count


class Post(Node):
    def __init__(
            self,
            post
    ):
        Node.__init__(self, post['id'], "post_" + post['id'], "post")
        # self.label_attribute="post"
        self.created_time = post['created_time']
        self.creator_id = post['id'].split('_')[0]
        # print(self.creator_id)

        if 'message' in post:
            self.message = post['message']
        # print(post['message'])
        else:
            self.message = None

        if 'full_picture' in post:
            self.picture = post['full_picture']
        # print(post['full_picture'])
        else:
            self.picture = None

        if 'caption' in post:
            self.caption = post['caption']
        # print(post['caption'])
        else:
            self.caption = None


class Community(Node):
    def __init__(
            self,
            community
    ):
        Node.__init__(self, community['id'], community['name'], "community")
        # self.label_attribute="community"
        # print(community['name'])

        if 'about' in community:
            self.about = community['about']
        # print(community['about'])
        else:
            self.about = None

        if 'description' in community:
            self.description = community['description']
        # print(community['description'])
        else:
            self.description = None

        if 'category' in community:
            self.category = community['category']
        # print(community['category'])
        else:
            self.category = None

        if 'website' in community:
            self.website = community['website']
        # print(community['website'])
        else:
            self.website = None

# self.created_time = community['created_time']

# self.member_count: community['member_count']
# self.creator_id = community['creator_id']


# class Event (Node):
# 	def __init__(
# 		self,
# 		event
# 	):
# 		Node.__init__(self, event.id, event.name)
# 		self.label_attribute="event"
# 		self.event_id = event['id']
# 		self.event_name = event['name']
# 		self.description = event['about']
# 		self.attending_count = event['attending_count']
# 		self.declined_count = event['declined_count']
# 		self.start_time: event['start_time']
# 		self.end_time: event['end_time']
# 		self.is_canceled = event['is_canceled']
# 		self.interested_count = event['interested_count']
# 		self.maybe_count: event['maybe_count']
# 		self.noreply_count = event['noreply_count']

class Comment(Node):
    def __init__(
            self,
            comment
    ):
        Node.__init__(self, comment['id'], comment['id'], "comment")
        # self.label_attribute="comment"

        self.created_time = comment['created_time']
        self.creator_id = comment['from']['id']
        self.creator_name = comment['from']['name']
        # print(self.creator_id)

        if 'message' in comment:
            self.message = comment['message']
        # print(post['message'])
        else:
            self.message = None

    def get_creator_name(self):
        return self.creator_name

    def get_creator_id(self):
        return self.creator_id

# if __name__ == '__main__':
# 	token = os.environ.get('FACEBOOK_TEMP_TOKEN')

# 	graph = facebook.GraphAPI(token)
# 	profile = graph.get_object('me',fields='name,id,posts')

# 	print(json.dumps(profile,indent=4))
# 	data = profile['posts']['data'];
# 	for item in data:
# 		if 'message' not in item:
# 			continue
# 		print(item['message'])
