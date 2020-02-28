import time
import multiprocessing
import pprint
from joblib import Parallel, delayed
from tqdm import tqdm
from spotify import *
from youtube import *
from add_to_playlist import *

###------------INIT/SETTINGS------------###
# change these if you want
MATCH_FN = 'matches.txt'
NOMATCH_FN = 'no_matches.txt'
# set to false to not display full link in saved file
FULL_LINK = True

# wouldn't change these
SAVE_TO_FILE = 'Do you want to save to a file? '
FULL_YT_LINK = 'Do you want the results stored with a full youtube link? '
YT = 'https://www.youtube.com/watch?v='
MAX_JOBS = (multiprocessing.cpu_count() * 2)


###------------ALL - FUNCTIONS------------###

# prints accuracy of findings
def print_accuracy(tracks):
    accuracy = check_accuracy(tracks[0], tracks[1])
    pprint.pprint('Found ' + str(accuracy[0]) + ' / ' + str(accuracy[1]))
    pprint.pprint(str(accuracy[2]))

# full process flow (WORKS!!)
# returns sorted[0](list of video_ids of matches)
# returns sorted[1](list of all titles of no match)


def spot_to_yt():
    # prompt for playlist
    info = select_playlist()
    # if select playlist returns error
    if 'ERROR' in info:
        pprint.pprint('Error: Could not find playlist.')
        pprint.pprint('Playlist must be public.')
        return None
    # print playlist info
    pprint.pprint('Name: ' + str(info[3]))
    pprint.pprint('Followers: ' + str(info[4]))
    pprint.pprint('Number of songs: ' + str(info[2]))
    # start timer
    overall = time.time()
    # get song list stuff from spotify
    song_list = get_songs(info)
    if song_list == 'failed':
        pprint.pprint('Could not find playlist')
    found = (info[2], len(song_list))

    # accuracy/timer information from spotify scrape
    found_percent = ' (' + str((found[0] / found[1]) * 100) + '%)'
    pprint.pprint('Finished scraping playlist')
    pprint.pprint('Found ' + str(found[0]) + '/' + str(found[1]) + found_percent)
    end_time = time.time()
    spotify_time = round((end_time - overall), 2)
    pprint.pprint('Spotify search took: ' + str(spotify_time) + '(s)')

    # prompt for how many processes to run while searching for video

    jobs_str = str(MAX_JOBS)
    pprint.pprint('You have ( ' + jobs_str + ' ) available.')
    try:
        jobs = int(input('How many jobs do you want? Max (' + jobs_str + '): '))
    except ValueError:
        print("This is not a valid input.")
    # incase out of allowed range
    if jobs > MAX_JOBS:
        pprint.pprint('Out of range, using default of (' + jobs_str + ')')
        jobs = MAX_JOBS

    # start search on youtube
    start_yt = time.time()
    delay_time = start_yt - end_time
    pprint.pprint('Searching for tracks on youtube - may take a while...')
    pprint.pprint('Will lag at the end.')
    matched = Parallel(n_jobs=jobs)(delayed(find_tracks_p)(i)
                                    for i in tqdm(song_list[:], ascii=True, unit='videos', smoothing=0.05))
    sorted_list = parse_result_list(matched)
    # final timer information and results display
    end_time = time.time()
    yt_time = round((end_time-start_yt), 2)
    end_time = round(((end_time - overall) - delay_time), 2)
    pprint.pprint('Youtube search took: ' + str(yt_time) + '(s)')
    pprint.pprint('Took a total time of ' + str(end_time) + '(s)')
    print_accuracy(sorted_list)
    return sorted_list


def prompt_save(item_list):
    if item_list == None:
        return
    if yes_or_no(SAVE_TO_FILE):
        with open(MATCH_FN, 'w') as output_file:
            for item in item_list[0]:
                if FULL_LINK:
                    item = YT + item
                output_file.write("%s\n" % item)
        with open(NOMATCH_FN, 'w') as output_file:
            for item in item_list[1]:
                output_file.write("%s\n" % item)
        pprint.pprint('wrote all matches to ' + MATCH_FN + ' in current dirrectory.')
        pprint.pprint('wrote all non-matches to ' + NOMATCH_FN + ' in current dirrectory.')

# helper yes or no function
# returns bool (true if yes, false if no)


def yes_or_no(question):
    answer = input(question + "(y/n): ").lower().strip()
    print("")
    while not(answer == "y" or answer == "yes" or
              answer == "n" or answer == "no"):
        print("Input yes or no")
        answer = input(question + "(y/n):").lower().strip()
        print("")
    if answer[0] == "y":
        return True
    return False

# read file


def read_file(filename):
    with open('./' + filename) as f:
        lines = f.read().splitlines()
        return lines


def add_to_playlist(service, playlist, playlist_id):
    Parallel(n_jobs=12)(delayed(add_video_to_playlist(service, link_id, playlist_id))
                        for link_id in tqdm(playlist, ascii=True, unit='vid_added', smoothing=0.05))

###-------------END FUNCTIONS-------------###
###------------------------###

# ALL CALLS BELOW THIS LINE


fileread = read_file('matches_nourl.txt')


PLAYLIST_ID = get_yt_playlist()
MY_YT = get_service()
pprint.pprint('If api token returned was valid, following process *should* work')
pprint.pprint('...as long as this doesn\'t take an hour')
# try:
add_to_playlist(MY_YT, fileread, PLAYLIST_ID)
