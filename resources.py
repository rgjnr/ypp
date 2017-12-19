import sys
import json
import argparse
import smtplib
from youtube import *
from config import *
from email.mime.text import MIMEText
from oauth2client.tools import argparser

class Options():
    def __init__(self):
        self.id_config = False
        self.username_config = False
        self.id = None
        self.username = None
        self.related = None
        self.region_check = False

    def process_options(self, arguments):
        # Check for mutual exclusion of config options
        try:
            if (CHANNELID and USERNAME):
                sys.exit("May only specify either CHANNELID or USERNAME")
        except NameError:
            pass

        # Process config options
        try:
            if CHANNELID:
                self.id_config = True
        except NameError:
            self.id_config = False

        try:
            if USERNAME:
                self.username_config = True
        except NameError:
            self.username_config = False

        # Process commandline arguments
        # Check args first, then config options if specified
        try:
            self.id = arguments.id if (arguments.id) else CHANNELID
        except NameError:
            self.id = None

        try:
            self.username = arguments.username if (arguments.username) else USERNAME
        except NameError:
            self.username = None

        try:
            self.related = arguments.related if (arguments.related) else RELATED
        except NameError:
            self.related = None

        if arguments.country:
            self.region_check = True
        else:
            self.region_check = False

def process_arguments():
    parser = argparse.ArgumentParser(description="YouTube Playlist Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[argparser])

    retrieval_method = parser.add_mutually_exclusive_group()
    retrieval_method.add_argument("-i", "--id", help="Retrieve playlists using channel ID")
    retrieval_method.add_argument("-u", "--username", help="Retrieve playlists using legacy YouTube username")
    parser.add_argument("-r", "--related", help="Also retrieve related playlists (likes, history, etc.)",
                        action="store_true")
    parser.add_argument("-c", "--country", help="Check for country restrictions", action="store_true")

    return parser.parse_args()

# open videos_dict.json file and deserialize videos dictionary
def open_videos_dict(vd):
    try:
        with open('videos_dict.json', 'r') as f:
            try:
                # use update method of dict object to force updating original
                # dict object passed from process_request()
                vd.update(json.load(f))

                if vd is not None:
                    VIDEOS_DICT_EXISTS = True

                f.closed
            except:
                VIDEOS_DICT_EXISTS = False
    except:
        VIDEOS_DICT_EXISTS = False

    return VIDEOS_DICT_EXISTS

# serialze videos dictionary and write to videos_dict.json file
def write_videos_dict(vd):
    with open("videos_dict.json", "w") as f:
        json.dump(vd, f)

    f.closed

def check_region_restrictions(pl, plir):
    video_ids = ""
    playlist_title = pl["snippet"]["title"].encode("utf-8")

    for video in plir["items"]:
        video_id = video["snippet"]["resourceId"]["videoId"]
        video_ids += "{},".format(video_id)

    video_list_request = create_video_list_request(video_ids)
    video_list_response = video_list_request.execute()

    for item in video_list_response["items"]:
        video_title = item["snippet"]["title"].encode("utf-8")

        try:
            if "US" in item["contentDetails"]["regionRestriction"]["blocked"]:
                print "{} in playlist {} blocked in US".format(video_title, playlist_title)

                #replace_video()
        except (IndexError, TypeError, KeyError):
            pass

        try:
            if "US" not in item["contentDetails"]["regionRestriction"]["allowed"]:
                print "{} in playlist {} not allowed in US".format(video_title, playlist_title)

                #replace_video()
        except (IndexError, TypeError, KeyError):
            pass

# Analyze videos_dict and playlist responses for determining unavailaable videos
def patch_playlists(vd, pl, plir, opt):
    bad_video_message = ""

    # Check videos in response
    for i, video in enumerate(plir["items"], start=1):
        video_privacy_status = video["status"]["privacyStatus"].encode("utf-8")
        video_title = video["snippet"]["title"].encode("utf-8")
        video_id = video["snippet"]["resourceId"]["videoId"]
        playlist_title = pl["snippet"]["title"].encode("utf-8")

        # Check if video deleted or private in response AND if video already in videos_dict
        if (video_privacy_status == "private" or video_title == "Deleted video") and video_id in vd:
            print "Found bad video with record"
            print "{} missing from {}".format(vd[video_id], playlist_title)

            bad_video_message += "{} missing from {}".format(vd[video_id], playlist_title)

            #replace_video(vd[video_id], pl["id"])

            # remove old bad entry
            #del vd[video_id]

    if opt.region_check:
        check_region_restrictions(pl, plir)

    return bad_video_message

def create_videos_dict(vd, plir):
    # Check videos in response
    for i, video in enumerate(plir["items"], start=1):
        video_privacy_status = video["status"]["privacyStatus"].encode("utf-8")
        video_title = video["snippet"]["title"].encode("utf-8")
        video_id = video["snippet"]["resourceId"]["videoId"]

    # Create entries for videos in videos dictionary that are not deleted or private
    if not (video_privacy_status == "private" or video_title == "Deleted video"):
        vd.update(video_id=video_title)

def send_email_notification(message):
    msg = MIMEText(message)
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    s = smtplib.SMTP(host=HOST, port=PORT)
    s.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
    s.quit()

# Main entry point for beginning checking of user's playlists using supplied request
def process_request(playlists_request, opt):
    videos_dict = {}
    email_message = ""

    VIDEOS_DICT_EXISTS = open_videos_dict(videos_dict)

    # Fetch pages of playlists until end
    while playlists_request:
        playlists_response = playlists_request.execute()

        for playlist in playlists_response["items"]:
            # Assemble request for videos in each playlist
            playlist_items_request = create_playlist_items_request(playlist["id"])

            # Fetch pages of videos until end
            while playlist_items_request:
                playlist_items_response = playlist_items_request.execute()

                if VIDEOS_DICT_EXISTS:
                    email_message += patch_playlists(videos_dict, playlist, playlist_items_response, opt)
                else:
                    create_videos_dict(videos_dict, playlist_items_response)

                # Request next page of videos
                playlist_items_request = create_next_page_request("playlistItem", playlist_items_request, playlist_items_response)

        # Request next page of playlists
        playlists_request = create_next_page_request("playlist", playlists_request, playlists_response)

    send_email_notification(email_message)

    #write_videos_dict(videos_dict)

def replace_video(video_title, playlist_id):
    video_search_request = create_video_search_request(video_title)

    video_search_response = video_search_request.execute()

    print json.dumps(video_search_response, indent=4, separators=(',',':'))

    try:
        new_video_id = video_search_response["items"][0]["id"]["videoId"]
    except:
        print "blah"

    try:
        new_video_title = video_search_response["items"][0]["snippet"]["title"]
    except:
        print "blah"

    print new_video_id
    print new_video_title

    video_search_request = create_playlist_items_insert_request(playlist_id, position, new_video_id)

    # remove bad vidoe from playlist
    # create playlistitems delete request
    #video_search_request = youtube.playlistItems().delete()
