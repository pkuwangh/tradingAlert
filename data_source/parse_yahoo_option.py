#!/usr/bin/env python

import os
import sys
import datetime
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *
from data_source.get_web_element import ChromeDriver

def get_date_in_url(exp_date):
    # convert a datetime object into the special date string used in url
    ep = datetime.datetime(1970,1,1,0,0,0)
    return (int)((exp_date - ep).total_seconds())

def extract_contract_info(contract):
    option_items = contract.split()
    option_interest = (int)(option_items[-2].replace(',', ''))
    option_price = (float)(option_items[-8].replace(',', ''))
    option_volume = (int)(option_items[-3].replace(',', ''))
    return (option_interest, option_price, option_volume)

def scan_option_chain(symbol, exp_date, option_type, strike, option_chain):
    open_interest = -1
    option_price = 0
    option_volume = 0
    exp_date_str = get_date_str(exp_date)
    strike_str = '%08d' % (strike * 1000)
    contract_name = symbol + exp_date_str + option_type + strike_str
    logger.debug('%s lookup %s exp=%s %s at %.1f'
            % (get_time_log(), symbol, exp_date_str, option_type, strike))
    for contract in option_chain:
        if contract.startswith(contract_name):
            (open_interest, option_price, option_volume) = extract_contract_info(contract)
            logger.info('%s got OI=%d value=%.2f volume=%d for %s exp=%s from {%s}'
                    % (get_time_log(), open_interest, option_price, option_volume,
                        symbol, exp_date_str, contract.rstrip()))
            break
    return (contract_name, open_interest >= 0, open_interest, option_price, option_volume)

def lookup_option_chain_info(symbol, exp_date, option_type, strike, save_file=False, folder='logs'):
    # read web data
    url = 'https://finance.yahoo.com/quote/%s/options?date=%s' \
            % (symbol, get_date_in_url(exp_date))
    eid = 'Col1-1-OptionContracts-Proxy'
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
        return (False, 0)
    # lookup
    (contract_name, found, open_interest, option_price, option_volume) = \
            scan_option_chain(symbol, exp_date, option_type, strike, web_data.splitlines())
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_date_str = get_date_str(datetime.datetime.today())
        filename = os.path.join(meta_data_dir, contract_name + '_' + today_date_str + '.txt.gz')
        with openw(filename, 'wt') as fout:
            fout.write(web_data)
        logger.debug('%s save %s option chain to %s' % (get_time_log(), symbol, filename))
    return (found, open_interest, option_price, option_volume)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())

    exp_date = datetime.datetime(2019,5,17)
    (found, open_interest, option_price, option_volume) = lookup_option_chain_info('WBT', exp_date, 'P', 15, True)
    print ('open interest is %d; value is %.2f' % (open_interest, option_price))

