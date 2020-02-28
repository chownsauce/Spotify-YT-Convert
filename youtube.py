import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import re
from datetime import timedelta
from collections import OrderedDict
import isodate
import requests
import pafy
from apiclient.discovery import build
from secrets import get_secret


# ----------INIT----------

# MAYBE SET THESE AS INPUTS LATER?
MAX_RESULTS = 5
TIME_DIFF = 3

# basic initialization stuff
GOOGLE_API = get_secret('GOOGLE_API')
YT_API_SERVICE = 'youtube'
YT_API_VERSION = 'v3'
pafy.set_api_key(GOOGLE_API)
YT = "https://www.youtube.com/watch?v="
CLIENT_SECRET = "client_secret.json"

# simple http requests - doesn't use api
# returns youtube search results as list
# returns a lot of entries, can't control how many
def search_youtube(trackname):
    '''
    Uses HTTP requests (requests lib) w/o using the YouTube API
    This can possibly save some quota information, but could be unreliable.

    Parameters:
    trackname - name of track

    Returns:
    search_results - list of videos as video id's
    '''
    search_str = 'https://www.youtube.com/results?search_query=' + trackname
    req = requests.get(search_str)
    html_content = req.text
    # uses regular expressions to search the search result html
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
    # compiles results into OrderedDict to remove duplicates
    search_results = OrderedDict((x, True) for x in search_results).keys()
    return list(search_results)

# uses youtube api - more control, use if possible
# returns youtube search results as list
# ripped almost directly from google
def youtube_search(search, max_results):
    # Call the search.list method to retrieve results matching the specified
    # query term.
    youtube = build(YT_API_SERVICE, YT_API_VERSION, developerKey=GOOGLE_API)
    search_response = youtube.search().list(
        q=search,
        part="id,snippet",
        maxResults=max_results
    ).execute()
    # add all video items to list of video id's
    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % (search_result["id"]["videoId"]))
    # returns list of video id's for search term
    return videos


def get_result_duration(videos):
    '''
    Helper method to query the YouTube API for returned video id's in one call.

    Parameters:
    videos - list of video id's to find duration of
    '''
    # parse list of videos into a comma seperated string
    video_ids = ','.join(map(str, videos))
    
    # setup an API client
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        YT_API_SERVICE, YT_API_VERSION, credentials=credentials)
    

    # make query for contentDetails
    request = youtube.videos().list(
        part="contentDetails",
        id=video_ids
    )
    response = request.execute()

    # lots more todo here
    return response





def yt_duration(video):
    '''
    Helper method to parse video duration from a pafy video object

    Parameters:
    video - pafy video object

    Returns:
    delta.seconds - duration of video in seconds
    '''
    time = (video.duration).split(':')
    delta = timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
    return delta.seconds

# TODO - check all possible video lengths in one API call
def check_match(spotify, youtube_id, max_time):
    '''
    Helper method to determine if video duration is close enough to spotify song duration.

    Parameters:
    spotify - spotify song information
    youtube_id - video id of particular video
    max_time - maximum time difference

    Returns:
    True if matching, otherwise False
    '''
    # create object to hold possible video
    vid = pafy.new(youtube_id, basic=False, gdata=False, size=False)
    # get duration of vid
    y_time = (yt_duration(vid))
    # calc difference between spotify length and vid duration
    delta = abs(y_time - spotify[2])
    # if difference is greater than max return FALSE
    if delta > max_time:
        return False
    # otherwise return TRUE
    return True

# only handles ONE track(tuple with title, artist name, length)
def find_tracks_p(track):
    # create a track string, and execute search
    search = str(track[0]) + " - " + str(track[1])
    possible = youtube_search(search, MAX_RESULTS)
    for v_id in possible:
        if check_match(track, v_id, TIME_DIFF):
            # vid_data(v_id).title
            # don't need vid title???
            return (True, v_id)
    return (False, search)

# checks accuracy of found songs
def check_accuracy(good_match, no_match):
    total = len(good_match) + len(no_match)
    percent = (len(good_match) / total) * 100
    return (len(good_match), total, (str(percent) + '%'))


def get_yt_playlist():
    playlist_str = input('Enter a youtube playlist link or id: ')
    if '/' in playlist_str:
        from urllib.parse import urlparse
        query = urlparse(playlist_str).query
        query = query.split('&')
        query = [i for i in query if 'list=' in i]
        playlist_id = query[0].split('list=')[1]
        return playlist_id

# parses results into list divided list
def parse_result_list(input_list):
    good = []
    bad = []
    for i in input_list:
        if i[0] == True:
            good.append(i[1])
        else:
            bad.append(i[1])
    return (good, bad)
