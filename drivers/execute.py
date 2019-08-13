#!/usr/bin/env python

import os
import sys
from multiprocessing import Pool
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

def run_track():
    # track past unusual activity
    from drivers.tracker import track
    (hold_list, watch_list, live_list) = track()
    logger.info('%s tracking done!' % (get_time_log()))
    return (hold_list, watch_list, live_list)

def run_hunt():
    # hunt for unusual activity
    from drivers.hunter import hunt
    hunted_list = hunt()
    logger.info('%s hunting done!' % (get_time_log()))
    return hunted_list


def execute(send_regular=False, send_prime=False):
    work_pool = Pool(processes = 2)
    res1 = work_pool.apply_async(run_track, ())
    res2 = work_pool.apply_async(run_hunt, ())
    work_pool.close()
    work_pool.join()
    (hold_list, watch_list, live_list) = res1.get()
    hunted_list = res2.get()
    # send email or print to terminal ?
    if not (send_regular or send_prime):
        user_input = input('send above results to subscribers? (yes/no/prime): ')
        if 'yes' in user_input:
            send_regular = True
        if 'prime' in user_input:
            send_prime = True
    term_print = (not (send_regular or send_prime))
    # prepare output
    text = ""
    text += "======== Today's Unusual Option Activity (UOA) ========\n"
    for item in hunted_list:
        text += (item.get_ext_display_str(color=term_print) + "\n")
    text += "\n"
    text += "======== Current Holdings ========\n"
    for item in hold_list:
        text += (item.get_display_str(color=term_print) + "\n")
    text += "\n"
    text += "======== Candidate Watch ========\n"
    for item in watch_list:
        text += (item.get_display_str(color=term_print) + "\n")
    text += "\n"
    text += "======== Live-Tracked UOA Effect ========\n"
    for item in live_list:
        text += (item.get_display_str(color=term_print) + "\n")
    text += "\n"
    print (text)
    # send email to my beloved followers
    if send_regular or send_prime:
        from utils.send_email import MailMan
        mail_man = MailMan()
        subject = 'Option activity on %s' % (get_datetime_str())
        mail_man.send(subject=subject, content=text, prime=send_prime)


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
    parser.add_argument('--send-regular', '-r', action='store_true',
            help='send out result to regular users')
    parser.add_argument('--send-prime', '-p', action='store_true',
            help='send out result to prime users')

    args = parser.parse_args()
    # execute all
    execute(args.send_regular, args.send_prime)

