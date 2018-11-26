#!/usr/bin/env python

import os
import datetime
import logging
from math import floor
logger = logging.getLogger(__name__)

from get_web_element import ChromeDriver

def get_time_str(date_and_time):
    return date_and_time.strftime('%y%m%d_%H%M%S')

def scan_option_activity(raw_data):
    option_activity_list = []
    num_pages = 0
    main_table_started = False
    new_activity = ''
    item_count = 0
    for line in raw_data:
        line = line.rstrip()
        if 'Showing 1-100' in line:
            num_activities = line.split()[-1]
            num_pages = floor((int(num_activities) + 99) / 100)
        if main_table_started:
            if 'Last Volume Open Int' in line:
                main_table_started = False
            else:
                new_activity += (' ' + line)
                item_count += 1
                # TODO: make this robust with format changes
                if item_count == 15:
                    option_activity_list.append(new_activity)
                    new_activity = ''
                    item_count = 0
        else:
            if 'Last Volume Open Int' in line:
                main_table_started = True 
    return (option_activity_list, num_pages)

def parse_option_activity(infile):
    try:
        logger.info('lookup file %s to parse option activity' % (infile))
        fin = open(infile, 'r')
    except:
        logger.info('error reading %s' % (infile))
        return ([''], 0)
    (option_activity_list, num_pages) = scan_option_activity(fin.readlines())
    return (option_activity_list, num_pages)

def lookup_option_activity(page_idx):
    # read web data
    url = 'https://www.barchart.com/options/unusual-activity/stocks?page=%u' % page_idx
    eid = 'main-content-column'
    chrome_driver = ChromeDriver(height=3240)
    web_data = chrome_driver.download_data(url=url, element_id=eid)
    chrome_driver.close()
    # lookup
    return scan_option_activity(web_data.splitlines())

def get_option_activity(save_file=False):
    # first get total number of pages
    (option_activity_list, num_pages) = lookup_option_activity(page_idx=1)
    # FIXME: specifying page index in the URL does not work
    num_pages = 1
    # TODO: should parallelize the work
    for page_idx in range(2, num_pages+1):
        (oa, num) = lookup_option_activity(page_idx=page_idx)
        option_activity_list.extend(oa)
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, 'logs')
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_time_str = get_time_str(datetime.datetime.now())
        filename = os.path.join(meta_data_dir, 'OA_%s.txt' % (today_time_str))
        with open(filename, 'w') as fout:
            fout.write('\n'.join(option_activity_list))
        logger.info('save option activity to %s' % (filename))
    return (option_activity_list, num_pages)

if __name__ == '__main__':
    root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    # test from local copy
#    infile = os.path.join(root_dir, 'temp', 'data_option_activity.txt')
#    (option_activity_list, num_pages) = parse_option_activity(infile)
#    print ('\n'.join(option_activity_list))
    # test from lookup
    (option_activity_list, num_pages) = get_option_activity(save_file=True)
