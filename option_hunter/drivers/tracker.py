#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

def track_from_act(activity_file, notify_list, force_notify):
    from analysis.option_activity import OptionActivity
    from analysis.option_effect   import OptionEffectFactory
    from analysis.option_effect   import OptionEffect
    option_activity = OptionActivity()
    option_activity.unserialize(activity_file)
    option_effect = OptionEffectFactory.create(option_activity)
    if option_effect.get_elapsed_days() < 1:
        logger.warning('%s ignore activity of today: %s'
                % (get_time_log(), option_activity.get_basic_display_str()))
        return
    (found, price_change, oi_change, is_show) = option_effect.track_change()
    if found:
        option_effect.serialize(OptionEffectFactory.folder)
        num_days = option_effect.get_remaining_days()
        if price_change or oi_change or is_show or num_days%7 == 0 or num_days < 4 or force_notify:
            # append is thread safe
            notify_list.append(option_effect)

def track_group(activity_dir, force_notify=False):
    # find live-tracked activity
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        notify_list = []
        for item in os.listdir(activity_dir):
            if item.startswith('Act'):
                src_file = os.path.join(activity_dir, item)
                executor.submit(track_from_act, src_file, notify_list, force_notify)
    notify_list.sort()
    return notify_list

def track():
    logger.info('================================================================')
    logger.info('%s the tracker started! 24/7 continuous tracking!' % (get_time_log()))
    hold_activity_dir = os.path.join(root_dir, 'records', 'option_activity_hold')
    watch_activity_dir = os.path.join(root_dir, 'records', 'option_activity_watch')
    live_activity_dir = os.path.join(root_dir, 'records', 'option_activity_live')
    hold_list = track_group(hold_activity_dir, force_notify=True)
    watch_list = track_group(watch_activity_dir, force_notify=True)
    live_list = track_group(live_activity_dir)
    return (hold_list, watch_list, live_list)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)
    (hold_list, watch_list, live_list) = track()
    print ('current holdings:')
    for item in hold_list:
        print (item.get_display_str())
    print ('candidate watch:')
    for item in watch_list:
        print (item.get_display_str())
    print ('live-tracked:')
    for item in live_list:
        print (item.get_display_str())

