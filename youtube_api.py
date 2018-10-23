#!/usr/bin/python
import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from googleapiclient.discovery import build

from graph import Node, Edge, Graph


def get_comments(youtube, video_id, channel_id):
    results = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        channelId=channel_id,
        textFormat="plainText"
    ).execute()
    return results["items"]


class ChannelNode(Node):
    def __init__(self, channel):
        if 'channelId' not in channel['id']:
            channel_id = channel['id']
        else:
            channel_id = channel['id']['channelId']

        # initialize the channel node with node id & Label
        Node.__init__(self, channel_id, channel['snippet']['title'], "channel")

        self.description = channel['snippet']['description']
        self.published_at = channel['snippet']['publishedAt']
        self.view_count = channel['statistics']['viewCount']
        self.comment_count = channel['statistics']['commentCount']
        self.hidden_subscriber_count = channel['statistics']['hiddenSubscriberCount']
        self.video_count = channel['statistics']['videoCount']

        if not channel['statistics']['hiddenSubscriberCount']:
            self.subscriber_count = channel['statistics']['subscriberCount']
        if 'customUrl' in channel:
            self.custom_url = channel['snippet']['customUrl']


class VideoNode(Node):
    def __init__(self, video):
        if 'videoId' not in video['id']:
            video_id = video['id']
        else:
            video_id = video['id']['videoId']
        # initialize the video node with video id & label
        Node.__init__(self, video_id, video['snippet']['title'], "video")
        self.published_at = video['snippet']['publishedAt']
        self.description = video['snippet']['description']


class PlaylistNode(Node):
    def __init__(self, playlist):
        if 'playlistId' not in playlist['id']:
            playlist_id = playlist['id']
        else:
            playlist_id = playlist['id']['playlistId']
        Node.__init__(self, playlist_id, playlist['snippet']['title'], "playlist")

        self.published_at = playlist['snippet']['publishedAt']
        self.description = playlist['snippet']['description']


class CommentNode(Node):
    def __init__(self, comment):
        Node.__init__(self, comment['id'], comment['snippet']['textDisplay'], "comment")

        # Attributes:
        self.updated_at = comment['snippet']['updatedAt']
        self.published_at = comment['snippet']['publishedAt']
        self.view_rating = comment['snippet']['viewerRating']
        self.can_rate = comment['snippet']['canRate']
        self.text_original = comment['snippet']['textOriginal']
        self.like_count = comment['snippet']['likeCount']


class Youtube:
    def __init__(self, api, option="pandas"):
        self.YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'
        self.DEVELOPER_KEY = api["api_key"]
        self.CLIENT_SECRET_FILE = api["client_secret"]
        # This variable defines a message to display if the CLIENT_SECRETS_FILE is
        # missing.
        self.MISSING_CLIENT_SECRET_MESSAGE = """
        WARNING: Please configure OAuth 2.0
        
        To make this sample run you will need to populate the client_secrets.json file
        found at:
           %s
        with information from the APIs Console
        https://console.developers.google.com
        
        For more information about the client_secrets.json file format, please visit:
        https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        """ % os.path.abspath(os.path.join(os.path.dirname(__file__), self.CLIENT_SECRET_FILE))

        self.option = option

        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                             developerKey=self.DEVELOPER_KEY)
        self.get_authenticated_service()

    # Authorize the request and store authorization credentials.
    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRET_FILE, scope=self.YOUTUBE_READ_WRITE_SSL_SCOPE,
                                       message=self.MISSING_CLIENT_SECRET_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        # Trusted testers can download this discovery document from the developers page
        # and it should be in the same directory with the code.
        with open("youtube-v3-discoverydocument.json", "r") as f:
            doc = f.read()
            return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

    def create_node_by_channel_id(self, channel_id):
        response = self.youtube.channels().list(
            id=channel_id,
            part='snippet,contentDetails,statistics'
        ).execute()

        channel_node = ChannelNode(response['items'][0])
        return channel_node

    def create_node_by_video_id(self, video_id):
        response = self.youtube.videos().list(
            id=video_id,
            part='snippet,contentDetails,statistics'
        )
        video_node = VideoNode(response['items'][0])
        return video_node

    def fetch_channel_by_id(self, channel_id):
        graph = Graph(option=self.option)
        graph.create_node(self.create_node_by_channel_id(channel_id))
        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_videos_by_topic(self, topic, maxResult=25):
        search_response = self.youtube.search().list(
            q=topic,
            type='video',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

        graph = Graph(option=self.option)

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                channel_id = search_result['snippet']['channelId']
                video_id = search_result['id']['videoId']
                graph.create_node(VideoNode(search_result))
                graph.create_node(self.create_node_by_channel_id(channel_id))
                graph.create_edge(Edge(channel_id, video_id, "createVideo"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_playlistItems_by_playlist_id(self, playlist_id):
        graph = Graph(option=self.option)
        response = self.youtube.playlistItems().list(
            part='snippet,contentDetails',
            maxResults=25,
            playlistId=playlist_id
        ).execute()

        # TODO finish this

        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            video_node = self.create_node_by_video_id(video_id)

            graph.create_node(video_node)
            graph.create_node()



    # Fetches video with its comments
    def fetch_video_by_id_with_comments(self, video_id):
        graph = Graph(option=self.option)
        response = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        # Add video node to the graph
        graph.create_node(VideoNode(response['items'][0]))

        # Add its author
        channel_id = response['items'][0]['snippet']['channelId']
        graph.create_node(self.create_node_by_channel_id(channel_id))
        graph.create_edge(Edge(channel_id, video_id, "createVideo"))

        # fetch its comments
        comment_threads = get_comments(self.youtube, video_id, None)

        for comment_thread in comment_threads:
            top_level_comment = comment_thread['snippet']['topLevelComment']
            top_level_comment_id = top_level_comment['id']
            top_level_channel_id = top_level_comment['snippet']['authorChannelId']['value']

            graph.create_node(self.create_node_by_channel_id(top_level_channel_id))
            graph.create_node(CommentNode(top_level_comment))
            graph.create_edge(Edge(top_level_channel_id, top_level_comment_id, "comment"))
            graph.create_edge(Edge(top_level_comment_id, video_id, "comment"))

            if 'replies' in comment_thread:
                replies = comment_thread['replies']['comments']
                for reply in replies:
                    reply_id = reply['id']
                    reply_channel_id = reply['snippet']['authorChannelId']['value']

                    # connect reply to comment
                    graph.create_node(CommentNode(reply))
                    graph.create_edge(Edge(reply_id, top_level_comment_id, "comment"))
                    # connect user to reply
                    graph.create_node(self.create_node_by_channel_id(reply_channel_id))
                    graph.create_edge(Edge(reply_channel_id, reply_id, "comment"))
                    graph.create_edge(Edge(reply_id, video_id, "comment"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_channels_by_topic(self, topic, maxResult=25):
        search_response = self.youtube.search().list(
            q=topic,
            type='channel',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

        graph = Graph(option=self.option)

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#channel':
                channel_id = search_result['snippet']['channelId']
                graph.create_node(self.create_node_by_channel_id(channel_id))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_playlists_by_topic(self, topic, maxResult=25):
        search_response = self.youtube.search().list(
            q=topic,
            type='playlist',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

        graph = Graph(option=self.option)

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#playlist':
                playlist_id = search_result['id']['playlistId']
                graph.create_node(PlaylistNode(search_result))

                channel_id = search_result['snippet']['channelId']
                graph.create_node(self.create_node_by_channel_id(channel_id))
                graph.create_edge(Edge(channel_id, playlist_id, "createPlaylist"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph
