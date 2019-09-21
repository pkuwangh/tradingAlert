#!/usr/bin/env python

import os
import sys
import time
import random
import datetime
import logging
from math import floor
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *
from data_source.get_web_element import ChromeDriver

def scan_option_activity(raw_data):
    option_activity_list = []
    main_table_started = False
    new_activity = ''
    for idx,line in enumerate(raw_data):
        line = line.rstrip()
        if main_table_started:
            if 'Last Volume Open Int' in line:
                main_table_started = False
            else:
                if line.isupper() and (idx+2) < len(raw_data) and ('Call' in raw_data[idx+2] or 'Put' in raw_data[idx+2]):
                    # find the anchor point
                    if new_activity:
                        option_activity_list.append(new_activity)
                        new_activity = ''
                new_activity += (' ' + line)
        else:
            if 'Last Volume Open Int' in line:
                main_table_started = True 
    if new_activity:
        option_activity_list.append(new_activity)
    return option_activity_list

def parse_option_activity(infile):
    try:
        logger.info('%s lookup file %s to parse option activity' % (get_time_log(), infile))
        fin = openw(infile, 'rt')
    except:
        logger.error('%s error reading %s' % (get_time_log(), infile))
        return ([''], 0)
    option_activity_list = scan_option_activity(fin.readlines())
    return option_activity_list

def lookup_option_activity():
    # read web data
    url = 'https://www.barchart.com/options/unusual-activity/stocks'
    eid = 'main-content-column'
#    show_all = 'a.show-all.ng-scope'
    show_all = 'a.show-all'
    buttons = [show_all]
    try:
        chrome_driver = ChromeDriver(width=3840, height=3840)
        outfile = os.path.join(root_dir, 'logs', 'data_option_activity.txt')
        web_data = chrome_driver.download_data(url=url, button_css_sel=buttons, element_id=eid, outfile=outfile)
    except:
        web_data = None
    try:
        chrome_driver.close()
    except:
        pass
    # lookup
    if web_data:
        return scan_option_activity(web_data.splitlines())
    else:
        return []

def get_option_activity(save_file=False, folder='logs'):
    num_retry = 0
    retry_timeout = 4
    while num_retry < retry_timeout:
        option_activity_list = lookup_option_activity()
        if len(option_activity_list) > 0:
            logger.info('retrieved option activity list: # items=%d'
                    % (len(option_activity_list)))
            break
        else:
            logger.warning('option activity list empty? retry=%d' % (num_retry))
            num_retry += 1
            time.sleep(10*random.random())
            continue
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_time_str = get_datetime_str(datetime.datetime.now())
        filename = os.path.join(meta_data_dir, 'OA_%s.txt.gz' % (today_time_str))
        with openw(filename, 'wt') as fout:
            fout.write('\n'.join(option_activity_list))
        logger.info('%s save option activity to %s' % (get_time_log(), filename))
    return option_activity_list

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    # test from local copy
    #infile = os.path.join(root_dir, 'temp', 'data_option_activity.txt')
    #option_activity_list = parse_option_activity(infile)
    # test from lookup
    option_activity_list = get_option_activity(save_file=True)
    print ('\n'.join(option_activity_list))

