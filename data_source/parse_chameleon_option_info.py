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
    #logger.info('%s lookup %s option volume breakdown' % (get_time_log(), symbol))
    status_bad = False
    all_found = True
    return all_found


def scan_option_volume(symbol, option_total_table, option_info):
    #logger.info('%s lookup %s option volume summary' % (get_time_log(), symbol))
    status_bad = False
    started = False
    for line in option_total_table:
        items = line.split()
        if 'Volume' in line:
            started = True
        if started:
            if 'Today' in line:
                try:
                    option_info['vol_today'] = int(items[-1].replace(',', ''))
                except:
                    status_bad = True
            elif '3 Month' in line:
                try:
                    option_info['vol_3mon'] = int(items[-1].replace(',', ''))
                except:
                    status_bad = True
    if status_bad:
        logger.error('%s error scanning %s option; resulting vol_today=%d vol_3mon=%d\n'
                % (get_time_log(), symbol,
                    option_info['vol_today'], option_info['vol_3mon']))
    all_found = (min(option_info.values()) >= 0)
    return all_found


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
    option_info['call_vol'] = -1
    option_info['put_vol'] = -1
    option_info['call_oi'] = -1
    option_info['put_oi'] = -1
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


def lookup_option_volume(symbol, save_file=False, folder='logs'):
    # read web data
    url = 'https://marketchameleon.com/Overview/%s/' % (symbol)
    eid = 'daily_chart_extended_stats_div'
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
    option_info['vol_today'] = -1
    option_info['vol_3mon'] = -1
    # something wrong
    if web_data is None:
        return (False, option_info)
    # lookup
    found = scan_option_volume(symbol, web_data.splitlines(), option_info)
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_date_str = get_date_str(datetime.datetime.today())
        filename = os.path.join(meta_data_dir, symbol + '_option_' + today_date_str + '.txt')
        with open(filename, 'w') as fout:
            fout.write(web_data)
        logger.info('%s save %s option volume to %s' % (get_time_log(), symbol, filename))
    return (found, option_info)


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
#    (found, option_callput_info) = lookup_option_breakdown('NVDA', save_file=True)
#    print ('%s call_vol=%d put_vol=%d call_oi=%d put_oi=%d' %
#            ('NVDA',
#                option_callput_info['call_vol'], option_callput_info['put_vol'],
#                option_callput_info['call_oi'], option_callput_info['put_oi']))

    (found, option_volume_info) = lookup_option_volume('NVDA', save_file=True)
    print ('%s vol_today=%d vol_3mon=%d' %
            ('NVDA',
                option_volume_info['vol_today'], option_volume_info['vol_3mon']))
