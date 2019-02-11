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

def scan_quote_summary(symbol, quote_summary_table):
    quote_info = {}
    logger.info('%s lookup %s quote summary' % (get_time_log(), symbol))
    quote_info['market_cap'] = 0
    quote_info['open_price'] = 0
    quote_info['avg_volumn'] = 0
    return (True, quote_info)

def parse_option_summary(symbol, infile):
    try:
        fin = open(infile, 'r')
        logger.info('%s lookup file %s for %s'
                % (get_time_log(), infile, symbol))
    except:
        logger.error('%s error reading %s' % (get_time_log(), infile))
        return (False, None)
    quote_summary_table = fin.readlines()
    return scan_quote_summary(symbol, quote_summary_table)

def lookup_quote_summary(symbol, save_file=False, folder='logs'):
    # read web data
    url = 'https://finance.yahoo.com/quote/%s' % (symbol)
    eid = 'quote-summary'
    try:
        chrome_driver = ChromeDriver(height=1080)
        web_data = chrome_driver.download_data(url=url, element_id=eid)
    except:
        web_data = None
    try:
        chrome_driver.close()
    except:
        pass
    # something wrong
    if web_data is None:
        return (False, None)
    # lookup
    (found, quote_info) = \
            scan_quote_summary(symbol, web_data.splitlines())
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_date_str = get_date_str(datetime.datetime.today())
        filename = os.path.join(meta_data_dir, symbol + '_' + today_date_str + '.txt')
        with open(filename, 'w') as fout:
            fout.write(web_data)
        logger.info('%s save %s quote summary to %s' % (get_time_log(), symbol, filename))
    return (found, quote_info)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    (found, quote_info) = lookup_quote_summary('NVDA', save_file=True)
    print ('%s market_cap=%d open_price=%d avg_volumn=%d'
            % ('NVDA',
                quote_info['market_cap'],
                quote_info['open_price'],
                quote_info['avg_volumn']))
