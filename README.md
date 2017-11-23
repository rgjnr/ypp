# ypp
    YouTube Playlist Patcher

# SYNOPSIS
    ypp.py
    ypp.py [-h]

# DESCRIPTION
    ypp is a Python script that automatically replaces missing videos from
    user's YouTube playlists due to copyright infringement, private status, etc.
    Missing videos are replaced with alternate videos based on title
    information.

    Note ypp will not replace videos that have been unavailable before using
    ypp. These videos will have to be manually replaced by the channel owner.
    ypp will only replace videos that become unavailable after subsequently
    using it.

# OPTIONS
    -h, --help
        Show the help message and exit.

# CREDENTIALS
    To communicate with YouTube Data API the script requires proper
    authorization credentials. Since the keys and files required for
    authorization are not provided, it is up to the user to obtain them. For
    authenticated requests, the client-secrets.json file is required. For
    non-authenticated requests, an API key is required. Please see
    [Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application)
    for more information regarding authorization credentials.

# DEPENDENCIES
    Python 2.7
    [google-api-python-client](https://github.com/google/google-api-python-client)
    [youtube-data-api-library](https://github.com/rgjnr/youtube-data-api-library)

# FILES
    config.py
        Configuration file for email notifications.

    resources.py
        Module containing class and function definitions.

    client-secrets.json
        Required for authenticated requests. See CREDENTIALS.

    ypp.py-oauth2.json
        Created during authenticated requests. See CREDENTIALS.

    videos_dict.json
        File containing dictionary of videos added to user's playlists. Used
        for determination of outdated video references.

# AUTHOR
    Roberto Gomez, Jr.
