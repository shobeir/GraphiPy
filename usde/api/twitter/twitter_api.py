import httplib2
import json
import base64
import urllib
from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge

class Twitter:
	def __init__(self, api):
		self.consumer_key = api["consumer_key"]
		self.consumer_secret = api["consumer_secret"]
		self.access_token = api["access_token"]
		self.token_secret = api["token_secret"]

		bearer_token_credentials = self.consumer_key+':'+self.consumer_secret
		
		encoded_credentials = base64.b64encode(bearer_token_credentials.encode('utf-8')).decode('utf-8')
		headers = {
			'Authorization': 'Basic ' + encoded_credentials,
			'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
		}
		url = "https://api.twitter.com/oauth2/token/?grant_type=client_credentials" 
		http = httplib2.Http()
		response, content = http.request(url, method="POST", headers=headers)
		content = json.loads(content.decode("utf-8"))
		self.bearer_token = content["access_token"]
	
	def get_single_user_by_screenname(self, graph, screenname):
		url = "https://api.twitter.com/1.1/users/show.json?screen_name=" + screenname
		http = httplib2.Http()
		headers = {
			'Authorization': 'Bearer ' + self.bearer_token
		}
		response, content = http.request(url, method="GET", headers=headers)
		result = json.loads(content.decode())
		user = TwitterUser(result)
		return user

	def fetch_tweets_by_topic(self, graph, keyword, limit=15):
		url = "https://api.twitter.com/1.1/search/tweets.json?q=" + keyword + "&count=" + str(limit)
		http = httplib2.Http()
		headers = {
			'Authorization': 'Bearer ' + self.bearer_token
		}
		response, content = http.request(url, method="GET", headers=headers)
		result = json.loads(content.decode())
		for tweet in result["statuses"]:
			single_tweet = TwitterTweet(tweet)
			graph.create_node(single_tweet)
			creator = TwitterUser(tweet["user"])
			graph.create_node(creator)
			graph.create_edge(Edge(single_tweet.get_id(), creator.get_id(), "CREATED_BY"))
			graph.create_edge(Edge(creator.get_id(), single_tweet.get_id(), "CREATED"))
			if 'retweeted_status' in tweet:
				original_tweet = TwitterTweet(tweet["retweeted_status"])
				graph.create_node(original_tweet)
				graph.create_edge(Edge(single_tweet.get_id(), original_tweet.get_id(), "RETWEET"))
				graph.create_edge(Edge(original_tweet.get_id(), single_tweet.get_id(), "RETWEETED BY"))
			if 'quoted_status' in tweet:
				original_tweet = TwitterTweet(tweet["quoted_status"])
				graph.create_node(original_tweet)
				graph.create_edge(Edge(single_tweet.get_id(), original_tweet.get_id(), "QUOTE"))
				graph.create_edge(Edge(original_tweet.get_id(), single_tweet.get_id(), "QUOTED BY"))
		return graph

	def fetch_tweet_by_id(self, graph, id):
		url = "https://api.twitter.com/1.1/statuses/show.json?id=" + str(id)
		http = httplib2.Http()
		headers = {
			'Authorization': 'Bearer ' + self.bearer_token
		}
		response, content = http.request(url, method="GET", headers=headers)
		result = json.loads(content.decode())
		tweet = TwitterTweet(result)
		graph.create_node(tweet)
		creator = TwitterUser(result["user"])
		graph.create_node(creator)
		graph.create_edge(Edge(tweet.get_id(), creator.get_id(), "CREATED_BY"))
		graph.create_edge(Edge(creator.get_id(), tweet.get_id(), "CREATED"))
		return graph

	def fetch_user_by_screenname(self, graph, screenname):
		user = self.get_single_user_by_screenname(graph, screenname)
		graph.create_node(user) 
		return graph

	def fecth_followers_by_screenname(self, graph, screenname, limit=15):
		user = self.get_single_user_by_screenname(graph, screenname)
		graph.create_node(user) 

		url = "https://api.twitter.com/1.1/followers/list.json?screen_name=" + screenname + "&count=" + str(limit)
		http = httplib2.Http()
		headers = {
			'Authorization': 'Bearer ' + self.bearer_token
		}
		response, content = http.request(url, method="GET", headers=headers)
		result = json.loads(content.decode())

		for follower in result["users"]:
			single_follower = TwitterUser(follower)
			graph.create_node(single_follower)
			graph.create_edge(Edge(single_follower.get_id(), user.get_id(), "FOLLOW"))
			graph.create_edge(Edge(user.get_id(), single_follower.get_id(), "FOLLOWED BY"))
		return graph

	def fecth_friends_by_screenname(self, graph, screenname, limit=15):
		user = self.get_single_user_by_screenname(graph, screenname)
		graph.create_node(user) 

		url = "https://api.twitter.com/1.1/friends/list.json?screen_name=" + screenname + "&count=" + str(limit)
		http = httplib2.Http()
		headers = {
			'Authorization': 'Bearer ' + self.bearer_token
		}
		response, content = http.request(url, method="GET", headers=headers)
		result = json.loads(content.decode())

		for friend in result["users"]:
			single_friend = TwitterUser(friend)
			graph.create_node(single_friend)
			graph.create_edge(Edge(single_friend.get_id(), user.get_id(), "FRIEND WITH"))
			graph.create_edge(Edge(user.get_id(), single_friend.get_id(), "FRIEND WITH"))
		return graph

class TwitterTweet(Node):
	def __init__(self, result):
		Node.__init__(self, str(result["id"]), "tweet_" + str(result["id"]), "tweet")
		self.created_at = result["created_at"]
		self.text = result["text"]
		self.source = result["source"]
		self.truncated = result["truncated"]
		self.is_quote_status = result["is_quote_status"]
		self.retweet_count = result["retweet_count"]
		self.favorite_count = result["favorite_count"]
		self.lang = result["lang"]
		entities = result["entities"]
		hashtags_list = []
		for hashtag in entities["hashtags"]:
			hashtags_list.append(hashtag["text"])
		self.hashtags = hashtags_list
		urls_list = []
		for url in entities["urls"]:
			urls_list.append(url["url"])
		self.urls = urls_list
		media_list = {}
		if 'media' in entities:
			for media in entities["media"]:
				media_list[media["type"]] = media["url"]
		self.media = media_list
		user_mentions_list = []
		for user_mention in entities["user_mentions"]:
			user_mentions_list.append(user_mention["screen_name"])
		self.user_mentions = user_mentions_list

class TwitterUser(Node):
	def __init__(self, result):
		self.name = result["name"]
		Node.__init__(self, str(result["id"]), self.name, "user")
		self.screen_name = result["screen_name"]
		self.location = result["location"]
		self.url = result["url"]
		self.description = result["description"]
		self.protected = result["protected"]
		self.verified = result["verified"]
		self.followers_count = result["followers_count"]
		self.friends_count = result["friends_count"]
		self.listed_count = result["listed_count"]
		self.favourites_count = result["favourites_count"]
		self.statuses_count = result["statuses_count"]
		self.created_at = result["created_at"]
		self.geo_enabled = result["geo_enabled"]
		self.lang = result["lang"]
		self.profile_background_color = result["profile_background_color"]
		self.profile_background_image_url = result["profile_background_image_url"]
		self.profile_image_url = result["profile_image_url"]
		self.profile_link_color = result["profile_link_color"]
		self.profile_text_color = result["profile_text_color"]
    