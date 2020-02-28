import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
from secrets import get_secret

C_ID = get_secret("C_ID")
C_SCT = get_secret("C_SCT")


# prompts for playlist id as input, displays number of songs
def select_playlist():
    """
    Prompts for playlist id.

    Returns:
    basic_playlist_info - information from get_basic_playlist_info()
    """
    playlist = input("Enter a spotify playlist id: ")
    # check if url, handle if necessary
    if "/" in playlist:
        from urllib.parse import urlparse

        parsed = urlparse(playlist).path.split("/")
        if "playlist" in parsed:
            playlist = parsed[parsed.index("playlist") + 1]
        else:
            return "ERROR"
    basic_playlist_info = get_basic_playlist_info(playlist)
    # if returns an error code as int
    if isinstance(basic_playlist_info, int):
        return "ERROR"
    # otherwise, assume success
    return basic_playlist_info


def get_basic_playlist_info(playlist_id):
    """
    Helper method to return basic playlist info.

    Parameters:
    playlist_id - id of playlist

    Returns:
    basic_info - tuple of basic playlist info
        [0] - owner_id
        [1] - playlist_id (redudant)
        [2] - total_tracks (number of tracks in playlist)
        [3] - name of playlist
        [4] - number of playlist followers
    """
    token = {
        "Authorization": "Bearer "
        + SpotifyClientCredentials(
            client_id=C_ID, client_secret=C_SCT
        ).get_access_token()
    }
    # basic header for web api request
    header = {"Accept": "application/json", "Content-Type": "application/json"}
    header.update(token)
    result = requests.get(
        "https://api.spotify.com/v1/playlists/" + playlist_id, headers=header
    )
    status = result.status_code
    # if status code is not 200 then returns error and status code
    if not status == 200:
        raise Exception()
        print("Recieved status code of " + str(status))
        return status

    # get result as json
    playlist = result.json()
    name = playlist["name"]
    followers = playlist["followers"]["total"]
    owner_id = playlist["owner"]["id"]
    total_tracks = playlist["tracks"]["total"]
    playlist_id = playlist["id"]
    basic_info = (owner_id, playlist_id, total_tracks, name, followers)
    return basic_info


def get_more_playlist_info(owner_id, playlist_id, limit, offset):
    """ 
    Returns object containing all track info.
    Uses spotipy lib
    
    Parameters:
    owner_id: id of playlist owner (found using get_basic_playlist_info())
    playlist_id: id of playlist
    limit: how many results to return in each request
    offset: offset of results (for multiple pages)

    Returns:
    results: object of all items in playlist
    """

    # get basic auth and create spotify object
    client_credentials_manager = SpotifyClientCredentials(
        client_id=C_ID, client_secret=C_SCT
    )
    sp_cl = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager
    )
    # get results
    result = sp_cl.user_playlist_tracks(
        user=owner_id, playlist_id=playlist_id, limit=limit, offset=offset
    )
    results = result["items"]
    return results


# returns string of track information
# use return_tracks as input
def parse_track(track_info):
    """
    Helper method to concatenate track information into a song.
    Returns:
    track_str: string in format "Song Title - Artist Name"

    UNUSED
    """
    track_str = str(track_info[0]) + " - " + str(track_info[1])
    return track_str


def return_tracks(item):
    """
    Helper method to create a list of track information to iterate over.

    Parameters:
    item: playlist object (returned from get_more_playlist_info())

    Returns:
    track_list: list of tuples
        [0] - track name
        [1] - artist(s)
        [2] - length of song in seconds

    """
    # create empty track_list
    track_list = []
    # iterate over all items in track_list
    for tracks in item:
        # get length, conver to seconds and round to nearest whole num
        # convert duration_ms into seconds and round to nearest second
        length = tracks["track"]["duration_ms"] / 1000
        length = int(round(length))
        # create track name var
        track_name = "" + tracks["track"]["name"]
        artist = ""
        # create track artists by looping over all artists
        for artists in tracks["track"]["artists"]:
            artist += artists["name"] + ", "
        artist = artist[:-2]
        track_info = (track_name, artist, length)
        track_list.append(track_info)
    # return list of track name, artist (comma sep), and length (in s)
    return track_list


# returns list of songs from spotify (each item is song name, artist(s) name, song length)
def get_songs(basic_info):
    """
    Aggregates song information into a list of tuples.

    Parameters:
    basic_info - returned from get_basic_playlist_info()

    Returns:
    song_items - list of all songs found in spotify playlist
    """
    # init stuff
    offset = 0
    tracks = []
    length = basic_info[2]
    # if basic_info returned error, print message and return
    if basic_info == "failed":
        return basic_info
    # prompt for step size, calculate iterations and last amount
    step = (int(input("How many songs per page (max 100): "))) or 100
    iterations = length // step
    if not length % step == 0:
        iterations += 1
    # iterate through all items in spotify playlist
    if step > 100:
        step = 100
    for i in range(0, iterations):
        stuff = return_tracks(
            get_more_playlist_info(basic_info[0], basic_info[1], step, offset)
        )
        offset += step
        tracks.append(stuff)
    # create song_items list and get all songs into one list
    song_items = []
    for info in tracks:
        for song_info in info:
            song_items.append(song_info)
    return song_items
