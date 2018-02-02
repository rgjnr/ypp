# ypp
YouTube Playlist Patcher - Automatically replace missing videos from YouTube playlists

## SYNOPSIS
ypp.py<br>
ypp.py [-h]<br>
ypp.py [-i ID | -u USERNAME] [-r] [-d] [-p] [-c] [-cc COUNTRY_CODE]

## DESCRIPTION
ypp is a Python script that automatically replaces missing videos from
user's YouTube playlists due to copyright infringement, private status, etc.
Missing videos are replaced with alternate videos based on title
information.

Note ypp will not replace videos that have been unavailable before using
ypp. These videos will have to be manually replaced by the channel owner.
ypp will only replace videos that become unavailable after subsequently
using it.

## OPTIONS
-h, --help<br>
Show the help message and exit.

i, --id<br>
Retrieve public playlists for the supplied YouTube channel ID. No
authentication is required. The channel ID is embedded in the URL when
accessing channel-related content, e.g. youtube.com/channel/CHANNELID.
It may also be viewed via My Channel or by accessing YouTube settings
-> Advanced -> Account Information.

-u, --username<br>
Retrieve public playlists for the supplied legacy YouTube username. No
authentication is required. Usernames were used by YouTube before it
was acquired by Google, although they are still supported for older
accounts. Usernames should not be confused with display names, which
do not uniquely identify a channel.

-r, --related<br>
Retrieve related playlists in addition to standard playlists. Related
playlists record metadata associated with a channel. These include
likes, favorites, uploads, watch later and history. The watch later
and history playlists may only be retrieved via authenticated
requests.

-d, --deleted<br>
Check for deleted videos

-p, --private<br>
Check for private videos

-c, --country<br>
Check for country restrictions, default is US

-cc COUNTRY_CODE, --country-code COUNTRY_CODE<br>
ISO 3166 alpha-2 country code used for checking country restrictions

## CREDENTIALS
To communicate with YouTube Data API the script requires proper
authorization credentials. Since the keys and files required for
authorization are not provided, it is up to the user to obtain them. For
authenticated requests, the client-secrets.json file is required. For
non-authenticated requests, an API key is required. Please see
[Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application)
for more information regarding authorization credentials.

## DEPENDENCIES
* [Python 2.7](https://www.python.org/download)
* [google-api-python-client](https://github.com/google/google-api-python-client)
* [youtube-data-api-library](https://github.com/rgjnr/youtube-data-api-library)

## FILES
config.py<br>
Configuration file for email notifications.

resources.py<br>
Module containing class and function definitions.

client-secrets.json<br>
Required for authenticated requests. See CREDENTIALS.

ypp.py-oauth2.json<br>
Created during authenticated requests. See CREDENTIALS.

videos_dict.json<br>
File containing dictionary of videos added to user's playlists. Used
for determination of outdated video references.

## AUTHOR
Roberto Gomez, Jr.
