#!/usr/bin/env python

import os
import sys
import datetime
import logging
logger = logging.getLogger(__name__)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *
from data_source.get_web_element import ChromeDriver

def scan_quote_summary(symbol, quote_summary_table):
    quote_info = {}
    logger.debug('%s lookup %s quote summary' % (get_time_log(), symbol))
    quote_info['market_cap'] = -1
    quote_info['open_price'] = -1
    quote_info['avg_volume'] = -1
    quote_info['volume']     = -1
    status_bad = False
    for line in quote_summary_table:
        items = line.split()
        if 'Market Cap' in line:
            try:
                value_str = items[-1].replace(',', '')
                if value_str[-1] == 'T':
                    value = float(value_str[:-1]) * 1e12
                elif value_str[-1] == 'B':
                    value = float(value_str[:-1]) * 1e9
                elif value_str[-1] == 'M':
                    value = float(value_str[:-1]) * 1e6
                elif value_str[-1] == 'K':
                    value = float(value_str[:-1]) * 1e3
                else:
                    value = float(value_str)
                quote_info['market_cap'] = value
            except:
                status_bad = True
        elif 'Open' in line:
            try:
                quote_info['open_price'] = float(items[-1].replace(',', ''))
            except:
                status_bad = True
        elif 'Avg. Volume' in line:
            try:
                quote_info['avg_volume'] = int(items[-1].replace(',', ''))
            except:
                status_bad = True
        elif 'Volume' in line:
            try:
                quote_info['volume'] = int(items[-1].replace(',', ''))
            except:
                status_bad = True
    if status_bad:
        logger.error('%s error scanning %s quote; resulting cap=%d open=%d avg_vol=%d vol=%d\n'
                % (get_time_log(), symbol,
                    quote_info['market_cap'], quote_info['open_price'],
                    quote_info['avg_volume'], quote_info['volume']))
    all_found = (min(quote_info.values()) >= 0)
    return (all_found, quote_info)


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
        filename = os.path.join(meta_data_dir, symbol + '_quote_' + today_date_str + '.txt.gz')
        with openw(filename, 'wt') as fout:
            fout.write(web_data)
        logger.debug('%s save %s quote summary to %s' % (get_time_log(), symbol, filename))
    return (found, quote_info)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    (found, quote_info) = lookup_quote_summary('NVDA', save_file=True)
    print ('%s market_cap=%d open_price=%d avg_volume=%d volume=%d'
            % ('NVDA',
                quote_info['market_cap'],
                quote_info['open_price'],
                quote_info['avg_volume'],
                quote_info['volume']))
