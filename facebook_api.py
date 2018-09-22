import os
import json
import facebook

class Facebook:
	def __init__(self,api):
		token = api["FACEBOOK_TEMP_TOKEN"]
		self.graph = facebook.GraphAPI(token)

	def fetch_facebook_user_info(
		self,
		id

	): 
		profile = self.graph.get_object(id,fields='name,id,gender,birthday,hometown,friends')
		user = User(profile)




	def fetch_Facebook_user_created_post(
		self,
		id
	):
		posts =  self.graph.get_object(id,fields='posts')
		for post in posts:
			p = Post(post)
		

	def fetch_facebook_user_liked_pages(
		self,
		id,
		limit = 20
	):
	#	TODO
		pass


	def fetch_facebook_user_friends(
		self,
		id
	):
	#	TODO
		pass

	def fetch_facebook_post_comments(
		self,
		post_id
	):
	#	TODO
		pass



	def fetch_facebook_community_info(
		self,
		id
	):
		profile = self.graph.get_object(id,fields='about,category,id,created_time,member_count,creator_id')
		community = Community(profile)

	def fetch_facebook_community_feed(
		self,
		id
	):
		feeds =  self.graph.get_object(id,fields='feeds')
		for feed in feeds:
			f = Post(feed)


	def fetch_facebook_event_info(
		self,
		id
	):
		pass


class User:
	def __init__(self, profile):
		self.user_id = profile.id
		self.name = profile.name
		self.gender = profile.gender
		self.birthday = profile.birthday
		self.hometown = profile.hometown
		self.friends_count = profile.friends.summary.total_count

class Post:
	def __init__(self, post, creator_id):
		self.post_id = post.id
		self.created_time = post.created_time
		self.message = post.message
		self.creator_id = post.creator_id
		if post.full_picture:
			self.picture = post.full_picture
		else:
			self.picture = None

		if post.caption:
			self.caption = post.caption
		else:
			self.caption = None

class Community:
	def __init__(self, profile):
		self.community_id = profile.id
		self.description = profile.about
		self.category = profile.category
		self.created_time = profile.created_time
		self.member_count: profile.member_count
		self.creator_id = profile.creator_id


class Event:
	def __init__(self, profile):
		self.event_id = profile.id
		self.event_name = profile.name
		self.description = profile.about
		self.attending_count = profile.attending_count
		self.declined_count = profile.declined_count
		self.start_time: profile.start_time
		self.end_time: profile.end_time
		self.is_canceled = profile.is_canceled
		self.interested_count = profile.interested_count
		self.maybe_count: profile.maybe_count
		self.noreply_count = profile.noreply_count




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