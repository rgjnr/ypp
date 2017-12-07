#!/usr/bin/env python

from youtube import *
from resources import *
from apiclient.errors import HttpError

if __name__ == "__main__":
    args = process_arguments()

    opt = Options()
    opt.process_options(args)

    try:
        youtube = create_resource_object(opt.id, opt.username, args)

        if (args.id or opt.id_config and args.username is None):
            req = create_id_request(opt.id)
            ch_req = create_id_channel_request(opt.id)
        elif (args.username or opt.username_config and args.id is None):
            req = create_username_request(opt.username)
            ch_req = create_username_channel_request(opt.username)
        else:
            req = create_private_request()
            ch_req = create_private_channel_request()

        process_request(req)

        if (opt.related):
            req = create_related_request(ch_req)
            process_request(req)

    except HttpError as e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
