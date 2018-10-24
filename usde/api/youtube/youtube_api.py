# !/usr/bin/python
import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from googleapiclient.discovery import build

from usde.graph.graph_base import BaseNode as Node, BaseEdge as Edge, BaseGraph as Graph


class ChannelNode(Node):
    """
    This class is the channel node class which inherits from the BaseNode class
    The channel node has following attribute:
        Id
        Title (Label for Gephi)
        Description
        View Count
        Comment Count
        Hidden Subscriber Count (Bool)
        Video Count
        Subscriber Count
        Custom Url
    """

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
    """
    This class is the video node class which inherits from the BaseNode class
    The video node has following attribute:
        Id
        Title (Label for Gephi)
        Description
        Published At
    """

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
    """
    This class is the playlist node class which inherits from the BaseNode class
    The playlist node has following attribute:
        Id
        Title (Label for Gephi)
        Description
        Published At
    """

    def __init__(self, playlist):
        if 'playlistId' not in playlist['id']:
            playlist_id = playlist['id']
        else:
            playlist_id = playlist['id']['playlistId']
        Node.__init__(self, playlist_id,
                      playlist['snippet']['title'], "playlist")

        self.published_at = playlist['snippet']['publishedAt']
        self.description = playlist['snippet']['description']


class CommentNode(Node):
    """
    This class is the comment node class which inherits from the BaseNode class
    The comment node has following attribute:
        Id
        Text Display (Label for Gephi)
        Updated At
        Viewer Rating
        canRate (Bool)
        Text Original
        likeCount
    """

    def __init__(self, comment):
        Node.__init__(self, comment['id'],
                      comment['snippet']['textDisplay'], "comment")

        # Attributes:
        self.updated_at = comment['snippet']['updatedAt']
        self.published_at = comment['snippet']['publishedAt']
        self.view_rating = comment['snippet']['viewerRating']
        self.can_rate = comment['snippet']['canRate']
        self.text_original = comment['snippet']['textOriginal']
        self.like_count = comment['snippet']['likeCount']


class Youtube:
    """
    This is the youtube class
    It has several fetch functionality:
        fetch_videos_by_topic
        fetch_channels_by_topic
        fetch_playlists_by_topic
        fetch_video_by_id_with_comments
        fetch_channel_by_id
        fetch_playlists_by_channel_id
        fetch_playlistItems_by_playlist_id
    """

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

    def get_authenticated_service(self):
        """
        This method Authorize the request and store authorization credentials.
        """
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
        """
        This method takes a channel id then return the ChannelNode object
        :param channel_id: String of channel id
        :return: the Channel Node object
        """
        response = self.youtube.channels().list(
            id=channel_id,
            part='snippet,contentDetails,statistics'
        ).execute()

        channel_node = ChannelNode(response['items'][0])
        return channel_node

    def create_node_by_video_id(self, video_id):
        """
        This method takes a video id then return the VideoNode object
        :param video_id: String of video id
        :return: the VideoNode object
        """
        response = self.youtube.videos().list(
            id=video_id,
            part='snippet,contentDetails,statistics'
        )
        video_node = VideoNode(response['items'][0])
        return video_node

    def fetch_channel_by_id(self, graph, channel_id):
        """
        This method grabs a channel Id and a graph and add the corresponding channelNode to it
        :param graph: The graph we are passing in
        :param channel_id: The id of channel
        :return: The resulting graph (which adds one ChannelNode)
        """
        graph.create_node(self.create_node_by_channel_id(channel_id))
        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_videos_by_topic(self, graph, topic, maxResult=25):
        """
        This method grabs videos about a certain topic and their corresponding creator (channel)
        and add to the graph
        :param graph: The graph we are passing in
        :param topic: The keyword for query
        :param maxResult: Max result for query, default 25
        :return: The resulting graph
        """
        search_response = self.youtube.search().list(
            q=topic,
            type='video',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

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

    def fetch_video_by_id_with_comments(self, graph, video_id):
        """
        This method fetches a video with its comments and its creator (channel node)
        and also all the creator (channel node) for the comments
        And then add to the graph
        :param graph: The graph we are passing in
        :param video_id: The id of the video
        :return: The resulting graph
        """
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
        comments_results = self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            channelId=channel_id,
            textFormat="plainText"
        ).execute()

        comment_threads = comments_results["items"]

        for comment_thread in comment_threads:
            top_level_comment = comment_thread['snippet']['topLevelComment']
            top_level_comment_id = top_level_comment['id']
            top_level_channel_id = top_level_comment['snippet']['authorChannelId']['value']

            graph.create_node(
                self.create_node_by_channel_id(top_level_channel_id))
            graph.create_node(CommentNode(top_level_comment))
            graph.create_edge(
                Edge(top_level_channel_id, top_level_comment_id, "comment"))
            graph.create_edge(Edge(top_level_comment_id, video_id, "comment"))

            if 'replies' in comment_thread:
                replies = comment_thread['replies']['comments']
                for reply in replies:
                    reply_id = reply['id']
                    reply_channel_id = reply['snippet']['authorChannelId']['value']

                    # connect reply to comment
                    graph.create_node(CommentNode(reply))
                    graph.create_edge(
                        Edge(reply_id, top_level_comment_id, "comment"))
                    # connect user to reply
                    graph.create_node(
                        self.create_node_by_channel_id(reply_channel_id))
                    graph.create_edge(
                        Edge(reply_channel_id, reply_id, "comment"))
                    graph.create_edge(Edge(reply_id, video_id, "comment"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_channels_by_topic(self, graph, topic, maxResult=25):
        """
        This method fetches channels with a given topic
        returning a disconnected graph
        :param graph: The graph we are passing in
        :param topic: The query topic
        :param maxResult: The max result number, default 25
        :return: The resulting graph
        """
        search_response = self.youtube.search().list(
            q=topic,
            type='channel',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#channel':
                channel_id = search_result['snippet']['channelId']
                graph.create_node(self.create_node_by_channel_id(channel_id))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_playlists_by_topic(self, graph, topic, maxResult=25):
        """
        This method fetches playlists with a given topic and all their creators
        :param graph: The graph we are passing in
        :param topic: The query topic
        :param maxResult: The max result number, default 25
        :return: The resulting graph
        """
        search_response = self.youtube.search().list(
            q=topic,
            type='playlist',
            part='id,snippet',
            maxResults=maxResult
        ).execute()

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#playlist':
                playlist_id = search_result['id']['playlistId']
                graph.create_node(PlaylistNode(search_result))

                channel_id = search_result['snippet']['channelId']
                graph.create_node(self.create_node_by_channel_id(channel_id))
                graph.create_edge(
                    Edge(channel_id, playlist_id, "createPlaylist"))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_playlists_by_channel_id(self, graph, channel_id):
        """
        This method fetches the playlists a channel has
        :param graph: The graph we are passing in
        :param channel_id: The channel id
        :return: The resulting graph
        """
        graph.create_node(self.create_node_by_channel_id(channel_id))
        response = self.youtube.playlist().list(
            part='snippet',
            channelId=channel_id,
            maxResults=25
        )

        for item in response.get('items', []):
            playlist_id = item['id']
            graph.create_node(PlaylistNode(item))
            graph.create_edge(channel_id, playlist_id, "createPlaylist")

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph

    def fetch_playlistItems_by_playlist_id(self, graph, playlist_id):
        """
        This method lists all the video (playlistItems) for a playlist
        :param graph: The graph we are passing in
        :param playlist_id: The playlist id
        :return: The resulting graph
        """
        response = self.youtube.playlistItems().list(
            part='snippet',
            maxResults=25,
            playlistId=playlist_id
        ).execute()

        for item in response.get('items', []):
            graph.create_node(VideoNode(item))

        graph.generate_df("node")
        graph.generate_df("edge")
        return graph
