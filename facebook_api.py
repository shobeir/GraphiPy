import os
import json
import facebook
import pandas as pd

class Facebook:
	def __init__(self,api):
		token = api["access_token"]
		id = api["id"]
		self.graph = facebook.GraphAPI(token)


	def fetch_facebook_user_info(
		self,
		id

	): 
		profile = self.graph.get_object(id,fields='name,id,gender,birthday,hometown')
		print(json.dumps(profile,indent=4))
		#user = User(profile)




	def fetch_Facebook_user_created_post(
		self,
		id
	):
		result =  self.graph.get_object(id,fields='name,posts')
		post_data = result['posts']['data']
		user_node = {'id': result['id'],
		'name':result['name']
		}
		# print(json.dumps(post_data,indent=4))
		post_nodes = []
		post_user_edges = []
		for post in post_data:
			post_node = {'id': post['id'],
			 'created_time': post['created_time']
			 # ,
			 # 'message':post['message']
			 }

			post_nodes.append(post_node)
			post_user_edges.append({'Source': post['id'],
									'Target':user_node['id']
									})

		post_nodes_df = pd.DataFrame(post_nodes)
		post_user_edges_df = pd.DataFrame(post_user_edges)
		post_nodes_df.to_csv("post_nodes.csv", encoding='UTF-8', index=False)
		post_user_edges_df.to_csv("post_user_edges.csv", encoding='UTF-8', index=False)
		

	def fetch_facebook_user_liked_pages(
		self,
		id,
		limit = 20
	):
		result = self.graph.get_object(id,fields='name,likes')
		like_data = result['likes']['data']
		user_node = {'id': result['id'],
		'name':result['name']
		}
		like_nodes = []
		like_user_edges = []
		# print(json.dumps(like_data,indent=4))
		for like in like_data:
			like_node = {'id':like['id'],
			'created_time': like['created_time'],
			'name': like['name']
			}

			like_nodes.append(like_node)
			like_user_edges.append({'Source': like['id'],
									'Target':user_node['id']
									})

		like_nodes_df = pd.DataFrame(like_nodes)
		like_user_edges_df = pd.DataFrame(like_user_edges)
		like_nodes_df.to_csv("like_nodes.csv", encoding='UTF-8', index=False)
		like_user_edges_df.to_csv("like_user_edges.csv", encoding='UTF-8', index=False)

	def fetch_facebook_user_friends(
		self,
		id
	):
		profile = self.graph.get_object(id,fields='friends{name,id}')
		# print(json.dumps(profile,indent=4))
		# for friend in profile.friend:
		# 	f = User(friends)


	def fetch_facebook_post_comments(
		self,
		post_id
	):
		result = self.graph.get_object(post_id,fields='comments')
		comment_data = result['comments']['data']
		post_node ={'id':result['id']}
		comment_nodes = []
		comment_post_edges = []
		for comment in comment_data:
			comment_node = {'id':comment['id'],
			'created_time': comment['created_time'],
			'message': comment['message'],
			'author': comment['from']['name']
			}

			comment_nodes.append(comment_node)
			comment_post_edges.append({'Source': comment['id'],
									'Target':post_node['id']})


		# print(json.dumps(result,indent=4))
		comment_nodes_df = pd.DataFrame(comment_nodes)
		comment_post_edges_df = pd.DataFrame(comment_post_edges)
		comment_nodes_df.to_csv("comment_nodes.csv", encoding='UTF-8', index=False)
		comment_post_edges_df.to_csv("comment_post_edges.csv", encoding='UTF-8', index=False)


	def fetch_facebook_community_info(
		self,
		id
	):
		profile = self.graph.get_object(id,fields='about,category,id,created_time,member_count,creator_id')
		# print(json.dumps(profile,indent=4))
		# community = Community(profile)

	def fetch_facebook_community_feed(
		self,
		id
	):
		result =  self.graph.get_object(id,fields='feeds')
		feed_data = result['feeds']['data']
		community_node = {'id': result['id'],
		'name':result['name']
		}
		feed_nodes = []
		feed_community_edges = []
		# print(json.dumps(result,indent=4))
		for feed in feed_data:
			feed_node= {'id': post['id'],
			 'created_time': post['created_time']
			 # ,
			 # 'message':post['message']
			}
			feed_nodes.append(feed_node)
			feed_community_edges.append({'Source': feed['id'],
									'Target':community_node['id']
									})
		feed_nodes_df = pd.DataFrame(feed_nodes)
		feed_community_edges_df = pd.DataFrame(feed_community_edges)
		feed_nodes_df.to_csv("feed_nodes.csv", encoding='UTF-8', index=False)
		feed_community_edges_df.to_csv("feed_community_edges.csv", encoding='UTF-8', index=False)

	def fetch_facebook_event_info(
		self,
		id
	):
		result = self.graph.get_object(id,fields='about,name,id')
		# print(json.dumps(result,indent=4))
		# event = Event(profile)


# class User:
# 	def __init__(self, profile):
# 		self.user_id = profile.id
# 		self.name = profile.name
# 		self.gender = profile.gender
# 		self.birthday = profile.birthday
# 		self.hometown = profile.hometown
# 		self.friends_count = profile.friends.summary.total_count

# class Post:
# 	def __init__(self, post, creator_id):
# 		self.post_id = post.id
# 		self.created_time = post.created_time
# 		self.message = post.message
# 		self.creator_id = post.creator_id
# 		if post.full_picture:
# 			self.picture = post.full_picture
# 		else:
# 			self.picture = None

# 		if post.caption:
# 			self.caption = post.caption
# 		else:
# 			self.caption = None

# class Community:
# 	def __init__(self, profile):
# 		self.community_id = profile.id
# 		self.description = profile.about
# 		self.category = profile.category
# 		self.created_time = profile.created_time
# 		self.member_count: profile.member_count
# 		self.creator_id = profile.creator_id


# class Event:
# 	def __init__(self, profile):
# 		self.event_id = profile.id
# 		self.event_name = profile.name
# 		self.description = profile.about
# 		self.attending_count = profile.attending_count
# 		self.declined_count = profile.declined_count
# 		self.start_time: profile.start_time
# 		self.end_time: profile.end_time
# 		self.is_canceled = profile.is_canceled
# 		self.interested_count = profile.interested_count
# 		self.maybe_count: profile.maybe_count
# 		self.noreply_count = profile.noreply_count




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
