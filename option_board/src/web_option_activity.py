#!/usr/bin/env python

import json
import logging
import os
import random
import sys
import time

from utils_datetime import get_time_log, get_date_str, get_datetime_str
from utils_file import openw
from utils_logging import setup_metadata_dir, setup_logger
from web_chrome_driver import ChromeDriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_option_activity(web_data):
    option_activity_list = []
    main_table_started = False
    new_activity = ''
    for idx, line in enumerate(web_data):
        line = line.rstrip()
        if main_table_started:
            if 'Last Volume Open Int' in line:
                main_table_started = False
            else:
                if (line.isupper() and
                    (idx+2) < len(web_data) and
                    ('Call' in web_data[idx+2] or 'Put' in web_data[idx+2])):
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


def read_option_activity(browser, save_file=False, folder='logs'):
    retry_timeout = 4
    url = 'https://www.barchart.com/options/unusual-activity/stocks?page=all'
    eid = 'main-content-column'
    #buttons = ['a.show-all']
    buttons = None
    num_retry = 0
    while num_retry < retry_timeout:
        num_retry += 1
        try:
            web_data = browser.download_data(
                url=url, wait_base=2 * num_retry,
                button_css=buttons, element_id=eid)
        except Exception as e:
            logger.error(f'error {str(e)} (retry={num_retry}/{retry_timeout})')
            time.sleep(num_retry)
            continue
        else:
            option_activity_list = parse_option_activity(web_data.splitlines())
            if len(option_activity_list) > 0:
                logger.info('retrieved option activity list: # items={:d}'.format(
                    len(option_activity_list)))
                break
            else:
                logger.warning('option activity list empty? retry={}/{}'.format(
                    num_retry, retry_timeout))
                time.sleep(num_retry)
                continue
    if num_retry >= retry_timeout:
        raise sys.exc_info()[1]
    # save a copy
    if save_file:
        # try to remove duplicates
        today_str = get_date_str()
        for item in os.listdir(folder):
            if item.startswith('OA_%s' % (today_str)):
                os.remove(os.path.join(folder, item))
        # write new one
        filename = os.path.join(folder, f'OA_{get_datetime_str()}.txt.gz')
        with openw(filename, 'wt') as fout:
            fout.write('\n'.join(option_activity_list))
        logger.info(f'{get_time_log()} save option activity to {filename}')
    return option_activity_list


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('web_chrome_driver').setLevel(logging.DEBUG)
    with ChromeDriver() as browser:
        option_activity_list = read_option_activity(browser, True, metadata_dir)
        print(json.dumps(option_activity_list, indent=4))
