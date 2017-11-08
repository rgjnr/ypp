#!/usr/bin/env python

import os
import sys
import json
import argparse
import httplib2
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

def process_arguments():
    parser = argparse.ArgumentParser(description="YouTube Playlist Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[argparser])

    retrieval_method = parser.add_mutually_exclusive_group()
    retrieval_method.add_argument("-i", "--id", help="Retrieve playlists using channel ID")
    retrieval_method.add_argument("-u", "--username", help="Retrieve playlists using legacy YouTube username")
    parser.add_argument("-r", "--related", help="Also retrieve related playlists (likes, history, etc.)",
                        action="store_true")

    return parser.parse_args()

# Checks playlists for missing videos (deleted or private) using the provided request
def patch_playlists(playlists_request):
    email_message = ""

    try:
        with open('videos_dict.json', 'r') as f:
        #with open('videos_dict.json', 'a+') as f:
            try:
                videos_dict = json.load(f)

                #print json.dumps(videos_dict, indent=4, separators=(',',':'))

                if videos_dict is not None:
                    VIDEOS_DICT_EXISTS = True

                f.closed
            except:
                videos_dict = {}
                VIDEOS_DICT_EXISTS = False
    except:
        videos_dict = {}
        VIDEOS_DICT_EXISTS = False

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
                    # Check videos in response
                    for i, video in enumerate(playlist_items_response["items"], start=1):
                        # Check if video deleted or private in response AND if video already in videos_dict
                        if (video["status"]["privacyStatus"].encode("utf-8") == "private" or video["snippet"]["title"].encode("utf-8") == "Deleted video") and video["snippet"]["resourceId"]["videoId"] in videos_dict:
                            print "Found bad video with record"
                            print "{} missing from {}".format(videos_dict[video["snippet"]["resourceId"]["videoId"]], playlist["snippet"]["title"].encode("utf-8"))

                            bad_video_message = "{} missing from {}".format(videos_dict[video["snippet"]["resourceId"]["videoId"]], playlist["snippet"]["title"].encode("utf-8"))

                            # add to email message
                            email_message += bad_video_message

                            #replace_video(videos_dict[video["snippet"]["resourceId"]["videoId"]], playlist["id"])
#
#                            # remove old bad entry
#                            del videos_dict[video["snippet"]["resourceId"]["videoId"]]
                else:
                    # Check videos in response
                    for i, video in enumerate(playlist_items_response["items"], start=1):
                        # Create entries for videos in videos dictionary that are not deleted or private
                        if not (video["status"]["privacyStatus"].encode("utf-8") == "private" or video["snippet"]["title"].encode("utf-8") == "Deleted video"):
                            videos_dict[video["snippet"]["resourceId"]["videoId"]] = video["snippet"]["title"].encode("utf-8")

                # Request next page of videos
                playlist_items_request = create_next_page_request("playlistItem", playlist_items_request, playlist_items_response)

        # Request next page of playlists
        playlists_request = create_next_page_request("playlist", playlists_request, playlists_response)

    # send email notification
    msg = MIMEText(email_message)
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    s = smtplib.SMTP(host=HOST, port=PORT)
    s.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
    s.quit()

    #print json.dumps(videos_dict, indent=4, separators=(',',':'))

#    with open("videos_dict.json", "w") as f:
#        json.dump(videos_dict, f)
#
#    f.closed

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
