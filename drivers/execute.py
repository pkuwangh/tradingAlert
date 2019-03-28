#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

def execute(send_out=False):
    # track past unusual activity
    from drivers.tracker import track
    (hold_list, live_list) = track()
    # hunt for unusual activity
    from drivers.hunter import hunt
    hunted_list = hunt()
    # prepare output
    text = ""
    text += "======== Today's Unusual Option Activity (UOA) ========\n"
    for item in hunted_list:
        text += (item.get_ext_display_str() + "\n")
    text += "\n"
    text += "======== Current Holdings ========\n"
    for item in hold_list:
        text += (item.get_display_str() + "\n")
    text += "\n"
    text += "======== Live-Tracked UOA Effect ========\n"
    for item in live_list:
        text += (item.get_display_str() + "\n")
    text += "\n"
    print (text)
    # send email to my beloved followers
    send_now = send_out
    if not send_now:
        user_input = input('send above results to subscribers? (yes/no): ')
        if 'yes' in user_input:
            send_now = True
    if send_now:
        from utils.send_email import MailMan
        mail_man = MailMan()
        subject = 'Option activity on %s' % (get_datetime_str())
        mail_man.send(subject=subject, content=text)


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--send-out', '-s', action='store_true',
            help='send out result')

    args = parser.parse_args()
    # execute all
    execute(args.send_out)

