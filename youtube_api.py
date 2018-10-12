#!/usr/bin/python
import json
from Queue import Queue

import httplib2
import os
import sys
import pandas as pd

from apiclient.discovery import build_from_document
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from graph import Node, Edge


def get_comments(youtube, video_id, channel_id):
    results = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        channelId=channel_id,
        textFormat="plainText"
    ).execute()
    return results["items"]


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource


def print_response(response):
    print(response)


class ChannelNode(Node):
    def __init__(self, channel):
        # initialize the channel node with node id
        Node.__init__(self, channel['id']['channelId'])
        # this is the channel label
        self.channel_title = channel['snippet']['title']

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

    def to_dic(self):
        return {"Id": self.get_id(),
                "Label": self.channel_title,
                "description": self.description,
                "published_at": self.published_at,
                "view_count": self.view_count,
                "comment_count": self.comment_count,
                "hidden_subscriber_count": self.hidden_subscriber_count,
                "video_count": self.video_count,
                "custom_url": self.custom_url,
                "subscriber_count": self.subscriber_count}


class VideoNode(Node):
    def __init__(self, video):
        # initialize the video node with video id
        Node.__init__(self, video['id']['videoId'])
        # label is the title
        self.title = video['snippet']['title']

        self.published_at = video['snippet']['publishedAt']
        self.description = video['snippet']['description']

    def to_dic(self):
        return {'Id': self.get_id(),
                'Label': self.title,
                'description': self.description,
                'published_at': self.published_at}


class PlaylistNode(Node):
    def __init__(self, playlist):
        if 'playlistId' not in playlist['id']:
            self.playlist_id = playlist['id']
        else:
            self.playlist_id = playlist['id']['playlistId']
        Node.__init__(self, self.playlist_id)

        self.published_at = playlist['snippet']['publishedAt']
        self.title = playlist['snippet']['title']
        self.description = playlist['snippet']['description']


class Comment(Node):
    def __init__(self, comment):
        # id:
        Node.__init__(self, comment['id'])
        # label:
        self.text_display = comment['snippet']['textDisplay']

        # Attributes:
        self.updated_at = comment['snippet']['updatedAt']
        self.published_at = comment['snippet']['publishedAt']
        self.view_rating = comment['snippet']['viewerRating']
        self.can_rate = comment['snippet']['canRate']
        self.text_original = comment['snippet']['textOriginal']
        self.like_count = comment['snippet']['likeCount']

    def to_dic(self):
        return {'Id': self.get_id(),
                'Label': self.text_display,
                'updated_at': self.updated_at,
                'published_at': self.published_at,
                'view_rating': self.view_rating,
                'can_rate': self.can_rate,
                'text_original': self.text_original,
                'like_count': self.like_count}


def parse_comment_to_node(comment):
    return {'updated_at': comment['snippet']['updatedAt'],
            'published_at': comment['snippet']['publishedAt'],
            'view_rating': comment['snippet']['viewerRating'],
            'can_rate': comment['snippet']['canRate'],
            'text_original': comment['snippet']['textOriginal'],
            # text_display is the label
            'Label': comment['snippet']['textDisplay'],
            'like_count': comment['snippet']['likeCount'],
            'Id': comment['id']}


class Youtube:
    def __init__(self, api):
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

        self.videos = []
        self.channels = []
        self.playlists = []
        self.video_comments = []
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

        channel = response['items'][0]
        channel_node = {"Id": channel_id,
                        "Label": channel['snippet']['title'],
                        "description": channel['snippet']['description'],
                        "published_at": channel['snippet']['publishedAt'],
                        "view_count": channel['statistics']['viewCount'],
                        "comment_count": channel['statistics']['commentCount'],
                        "hidden_subscriber_count": channel['statistics']['hiddenSubscriberCount'],
                        "video_count": channel['statistics']['videoCount']}

        if not channel['statistics']['hiddenSubscriberCount']:
            channel_node["subscriber_count"] = channel['statistics']['subscriberCount']
        if 'customUrl' in channel:
            channel_node["custom_url"] = channel['snippet']['customUrl']
        return channel_node

    def fetch_video(self, options):
        search_response = self.youtube.search().list(
            q=options.q,
            part='id,snippet',
            maxResults=options.max_results
        ).execute()

        video_nodes = []
        video_edges = []
        channel_nodes = []

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_node = VideoNode(search_result)
                video_nodes.append(video_node)

                # creating a channel to video edge
                channel_video_edge = Edge(search_result['snippet']['channelId'], video_id)
                video_edges.append({'Source': search_result['snippet']['channelId'],
                                    'Target': video_id})

                # channel id is Id, title is Label
                channel_node = self.create_node_by_channel_id(search_result['snippet']['channelId'])
                channel_nodes.append(channel_node)

        video_nodes_df = pd.DataFrame(video_nodes)
        video_edges_df = pd.DataFrame(video_edges)
        channel_nodes_df = pd.DataFrame(channel_nodes)

        return {"video_nodes_df": video_nodes_df,
                "video_edges_df": video_edges_df,
                "channel_nodes_df": channel_nodes_df}

    def fetch_video_comments(self, video_id):
        comment_nodes = []
        comment_user_edges = []
        comment_reply_edges = []
        comment_video_edges = []
        channel_nodes = []
        comment_threads = get_comments(self.youtube, video_id, None)
        for comment_thread in comment_threads:
            top_level_comment = comment_thread['snippet']['topLevelComment']
            # Source is channel Id, target is comment Id
            comment_user_edge = {'Target': top_level_comment['id'],
                                 'Source': top_level_comment['snippet']['authorChannelId']['value']}
            comment_user_edges.append(comment_user_edge)
            channel_nodes.append(
                self.create_node_by_channel_id(top_level_comment['snippet']['authorChannelId']['value']))

            top_level_comment_node = parse_comment_to_node(top_level_comment)
            comment_nodes.append(top_level_comment_node)

            comment_video_edges.append({'Target': video_id,
                                        'Source': top_level_comment['id']})

            if 'replies' in comment_thread:
                replies = comment_thread['replies']['comments']
                for reply in replies:
                    # Add reply (to top level comment) nodes
                    comment_nodes.append(parse_comment_to_node(reply))
                    # Add Edge
                    comment_reply_edge = {'Target': reply['snippet']['parentId'],
                                          'Source': reply['id']}
                    reply_user_edge = {'Target': reply['id'],
                                       'Source': reply['snippet']['authorChannelId']['value'],
                                       'channel_url': reply['snippet']['authorChannelUrl'],
                                       'author_display_name': reply['snippet']['authorDisplayName']}
                    comment_reply_edges.append(comment_reply_edge)
                    comment_user_edges.append(reply_user_edge)

        comment_nodes_df = pd.DataFrame(comment_nodes)
        channel_nodes_df = pd.DataFrame(channel_nodes)
        comment_user_edges_df = pd.DataFrame(comment_user_edges)
        comment_reply_edges_df = pd.DataFrame(comment_reply_edges)
        comment_video_edges_df = pd.DataFrame(comment_video_edges)

        print comment_nodes_df
        print channel_nodes_df
        print comment_user_edges_df
        print comment_reply_edges_df
        print comment_video_edges_df

        return {'comment_nodes_df': comment_nodes_df,
                'channel_nodes_df': channel_nodes_df,
                'comment_user_edges_df': comment_user_edges_df,
                'comment_reply_edges_df': comment_reply_edges_df,
                'comment_video_edges_df': comment_video_edges_df}

    def fetch_channel(self, options):
        search_response = self.youtube.search().list(
            q=options.q,
            part='id,snippet',
            maxResults=options.max_results
        ).execute()

    def youtube_search(self, options):

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = self.youtube.search().list(
            q=options.q,
            part='id,snippet',
            maxResults=options.max_results
        ).execute()

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        try:
            for search_result in search_response.get('items', []):

                if search_result['id']['kind'] == 'youtube#video':
                    self.videos.append(VideoNode(search_result))
                    comments = get_comments(self.youtube, search_result['id']['videoId'], None)
                    for item in comments:
                        topLevelComment = item["snippet"]["topLevelComment"]
                        comment = Comment(topLevelComment)
                        comment.videoId = search_result['id']['videoId']
                        self.video_comments.append(comment)


                elif search_result['id']['kind'] == 'youtube#channel':
                    self.channels.append(ChannelNode(search_result))
                    comments = get_comments(self.youtube, None, search_result['id']['channelId'])
                    for item in comments:
                        comment = item["snippet"]["topLevelComment"]
                        self.video_comments.append(Comment(comment))

                elif search_result['id']['kind'] == 'youtube#playlist':
                    playlistId = search_result['id']['playlistId']
                    self.playlists.append(PlaylistNode(search_result))
                    self.playlist_items_list_by_playlist_id(part='snippet,contentDetails',
                                                            maxResults=25,
                                                            playlistId=playlistId)

        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    # Build a resource based on a list of properties given as key-value pairs.
    # Leave properties with empty values out of the inserted resource.

    def playlist_items_list_by_playlist_id(self, **kwargs):
        # See full sample for function
        kwargs = remove_empty_kwargs(**kwargs)

        response = self.youtube.playlistItems().list(
            **kwargs
        ).execute()

        for item in response['items']:
            self.playlists.append(PlaylistNode(item))

    def pretty_print(self):
        print('Videos:')
        for video in self.videos:
            print("\tvideoId: " + video.video_id.encode("utf-8"))
            print("\ttitle: " + video.title.encode("utf-8"))
            print("\tdescription: " + video.description.encode("utf-8"))
            print("\tpublished at: " + video.published_at.encode("utf-8"))
            print

        print('Channels:')
        for channel in self.channels:
            print("\tchannelId: " + channel.channel_id.encode("utf-8"))
            print("\ttitle: " + channel.channel_title.encode("utf-8"))
            print("\tdescription: " + channel.description.encode("utf-8"))
            print

        print('Playlist:')
        for playlist in self.playlists:
            print("\tplaylistId: " + playlist.playlist_id.encode("utf-8"))
            print("\ttitle: " + playlist.title.encode("utf-8"))
            print("\tdescription: " + playlist.description.encode("utf-8"))
            print("\tpublished at: " + playlist.published_at.encode("utf-8"))
            print

        print('Comments:\n')
        for comment in self.video_comments:
            if comment.video_id is not None:
                print("\tvideoId: " + comment.video_id.encode("utf-8"))
            print("\tupdated_at: " + comment.updated_at.encode("utf-8"))
            print("\tpublished_at: " + comment.published_at.encode("utf-8"))
            print("\tview rating: " + comment.view_rating.encode("utf-8"))
            print("\tcan rate: " + str(comment.can_rate))
            print("\ttext_original: " + comment.text_original.encode("utf-8"))
            print("\ttext_display: " + comment.text_display.encode("utf-8"))
            print("\tlike count: " + str(comment.like_count))
            print
