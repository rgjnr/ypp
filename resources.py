import sys
import json
import argparse
from youtube import *
from config import *
from oauth2client.tools import argparser

class Options():
    def __init__(self):
        self.id_config = False
        self.username_config = False
        self.id = None
        self.username = None
        self.related = None
        self.deleted = False
        self.private = False
        self.country = False
        self.country_code = "US"

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

        if arguments.deleted:
            self.deleted = True

        if arguments.private:
            self.private = True

        if arguments.country:
            self.country = True

        if arguments.country_code:
            self.country = True
            self.country_code = arguments.country_code

        # Default usage, perform all checks when none specified
        if (not arguments.deleted and not arguments.private
        and not arguments.country and not arguments.country_code):
            self.deleted = True
            self.private = True
            self.country = True

def process_arguments():
    parser = argparse.ArgumentParser(
        description="YouTube Playlist Patcher - Maintain YouTube playlists by \
            replacing missing videos with alternates",
        parents=[argparser])

    retrieval_method = parser.add_mutually_exclusive_group()
    retrieval_method.add_argument("-i", "--id", help="Retrieve playlists using channel ID")
    retrieval_method.add_argument("-u", "--username", help="Retrieve playlists using legacy YouTube username")
    parser.add_argument("-r", "--related", help="Also retrieve related playlists (likes, history, etc.)",
                        action="store_true")
    parser.add_argument("-d", "--deleted", help="Check for deleted videos", action="store_true")
    parser.add_argument("-p", "--private", help="Check for private videos", action="store_true")
    parser.add_argument("-c", "--country", help="Check for country restrictions, default is US", action="store_true")
    parser.add_argument("-cc", "--country-code", help="ISO 3166 alpha-2 country code used for checking country restrictions")

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

def check_country_restrictions(pl, plir, opt):
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
            if opt.country_code in item["contentDetails"]["regionRestriction"]["blocked"]:
                print "{} in {} blocked in {}".format(video_title, playlist_title, opt.country_code)

                replace_video(video_title, pl["id"], playlist_item_id)

        except (IndexError, TypeError, KeyError):
            pass

        try:
            if opt.country_code not in item["contentDetails"]["regionRestriction"]["allowed"]:
                print "{} in {} not allowed in {}".format(video_title, playlist_title, opt.country_code)

                replace_video(video_title, pl["id"])

        except (IndexError, TypeError, KeyError):
            pass

# Analyze videos_dict and playlist responses for determining unavailaable videos
def patch_playlists(vd, pl, plir, opt):
    # Check videos in response
    for i, video in enumerate(plir["items"], start=1):
        video_privacy_status = video["status"]["privacyStatus"].encode("utf-8")
        video_title = video["snippet"]["title"].encode("utf-8")
        video_id = video["snippet"]["resourceId"]["videoId"]
        playlist_title = pl["snippet"]["title"].encode("utf-8")
        video_playlist_position = video["snippet"]["position"]
        playlist_item_id = video["id"]

        if opt.deleted:
            if video_title == "Deleted video" and video_id in vd:
                print "{} deleted from {}".format(vd[video_id], playlist_title)

                replace_video(vd[video_id], pl["id"], video_playlist_position, playlist_item_id)

                # remove old bad entry
                del vd[video_id]

        if opt.private:
            if video_privacy_status == "private" and video_id in vd:
                print "{} made private in {}".format(vd[video_id], playlist_title)

                replace_video(vd[video_id], pl["id"], video_playlist_position, playlist_item_id)

                # remove old bad entry
                del vd[video_id]

def create_videos_dict(vd, plir):
    # Check videos in response
    for i, video in enumerate(plir["items"], start=1):
        video_privacy_status = video["status"]["privacyStatus"].encode("utf-8")
        video_title = video["snippet"]["title"].encode("utf-8")
        video_id = video["snippet"]["resourceId"]["videoId"]

    # Create entries for videos in videos dictionary that are not deleted or private
    if not (video_privacy_status == "private" or video_title == "Deleted video"):
        vd.update(video_id=video_title)

# Main entry point for beginning checking of user's playlists using supplied request
def process_request(playlists_request, opt):
    videos_dict = {}

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
                    patch_playlists(videos_dict, playlist, playlist_items_response, opt)
                else:
                    create_videos_dict(videos_dict, playlist_items_response)

                if opt.country:
                    check_country_restrictions(playlist, playlist_items_response, opt)

                # Request next page of videos
                playlist_items_request = create_next_page_request("playlistItem", playlist_items_request, playlist_items_response)

        # Request next page of playlists
        playlists_request = create_next_page_request("playlist", playlists_request, playlists_response)

    write_videos_dict(videos_dict)

def replace_video(video_title, playlist_id, position, playlist_item_id):
    video_search_request = create_video_search_request(video_title)
    video_search_response = video_search_request.execute()

    try:
        new_video_id = video_search_response["items"][0]["id"]["videoId"]
    except:
        print "No alternate video found for {}".format(video_title)

    try:
        new_video_title = video_search_response["items"][0]["snippet"]["title"]
    except:
        print "No alternate video found for {}".format(video_title)

    if new_video_id:
        playlist_items_insert_request = create_playlist_items_insert_request(playlist_id, position, new_video_id)

        try:
            playlist_items_insert_response = playlist_items_insert_request.execute()
        except Exception as e:
            print(e)
            return

        # Remove missing video from playlist
        playlist_items_delete_request = create_playlist_items_delete_request(playlist_item_id)

        try:
            playlist_items_delete_response = playlist_items_delete_request.execute()
        except Exception as e:
            print(e)
            return

        print "{} replaced with {}".format(video_title, new_video_title)
    else:
        print "{} not replaced".format(video_title)
