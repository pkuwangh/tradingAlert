#!/usr/bin/env python

import os
import sys
import datetime
import logging
logger = logging.getLogger(__name__)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from data_source.get_web_element import ChromeDriver

def scan_option_breakdown(symbol, option_total_table, option_info):
    logger.info('%s lookup %s option volume breakdown' % (get_time_log(), symbol))
    status_good = True
    return status_good

def lookup_option_breakdown(symbol, save_file=False, folder='logs'):
    # read web data
    url = 'https://marketchameleon.com/Overview/%s/OptionSummary/' % (symbol)
    eid = 'symov_main_content'
    try:
        chrome_driver = ChromeDriver(height=1080)
        web_data = chrome_driver.download_data(url=url, element_id=eid)
    except:
        web_data = None
    try:
        chrome_driver.close()
    except:
        pass
    # resulting info
    option_info = {}
    option_info['call_vol'] = 0
    option_info['put_vol'] = 0
    option_info['call_oi'] = 0
    option_info['put_oi'] = 0
    # something wrong
    if web_data is None:
        return (False, option_info)
    # lookup
    found = scan_option_breakdown(symbol, web_data.splitlines(), option_info)
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_date_str = get_date_str(datetime.datetime.today())
        filename = os.path.join(meta_data_dir, symbol + '_putcall_' + today_date_str + '.txt')
        with open(filename, 'w') as fout:
            fout.write(web_data)
        logger.info('%s save %s option breakdown to %s' % (get_time_log(), symbol, filename))
    return (found, option_info)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    (found, option_callput_info) = lookup_option_breakdown('NVDA', save_file=True)
    print ('%s call_vol=%d put_vol=%d call_oi=%d put_oi=%d' %
            ('NVDA',
                option_callput_info['call_vol'], option_callput_info['put_vol'],
                option_callput_info['call_oi'], option_callput_info['put_oi']))

#    https://marketchameleon.com/Overview/TSS/
