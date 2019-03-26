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

def track():
    logger.info('================================================================')
    logger.info('%s the tracker started! 24/7 continuous tracking!' % (get_time_log()))
    # find live-tracked activity
    from analysis.option_activity import OptionActivity
    from analysis.option_effect   import OptionEffectFactory
    from analysis.option_effect   import OptionEffect
    live_activity_dir = os.path.join(root_dir, 'records', 'option_activity_live')
    send_notification = False
    for item in os.listdir(live_activity_dir):
        if item.startswith('Act'):
            src_file = os.path.join(live_activity_dir, item)
            option_activity = OptionActivity()
            option_activity.unserialize(src_file)
            option_effect = OptionEffectFactory.create(option_activity)
            (found, price_change, oi_change) = option_effect.track_change()
            if found:
                option_effect.serialize(OptionEffectFactory.folder)
                num_days = option_effect.get_days()
                if price_change or oi_change or num_days%7 == 0 or num_days < 4:
                    send_notification = True
                print (option_effect.get_display_str())


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)
    track()
