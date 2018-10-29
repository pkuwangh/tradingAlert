#!/usr/bin/env python

import os
import datetime
import logging
logger = logging.getLogger(__name__)

from get_web_element import ChromeDriver

def get_date_in_url(exp_date):
    # convert a datetime object into the special date string used in url
    ep = datetime.datetime(1970,1,1,0,0,0)
    return (int)((exp_date - ep).total_seconds())

def get_exp_date(date_str):
    # convert a regular date string into datetime object
    return datetime.datetime.strptime(date_str, '%y%m%d')

def get_date_str(exp_date):
    # convert a datetime object into regular date string
    return exp_date.strftime('%y%m%d')

def extract_contract_info(contract):
    option_items = contract.split()
    option_interest = (int)(option_items[-2])
    return (option_interest)

def scan_option_chain(symbol, exp_date, option_type, strike, option_chain):
    open_interest = -1
    exp_date_str = get_date_str(exp_date)
    strike_str = '%08d' % (strike * 1000)
    contract_name = symbol + exp_date_str + option_type + strike_str
    logger.info('lookup %s exp=%s %s at %.1f'
            % (symbol, exp_date_str, option_type, strike))
    for contract in option_chain:
        if contract.startswith(contract_name):
            open_interest = extract_contract_info(contract)
            logger.info('got OI=%d from {%s}' % (open_interest, contract))
            break
    return (contract_name, open_interest >= 0, open_interest)

def parse_option_info(symbol, exp_date, option_type, strike, infile):
    try:
        fin = open(infile, 'r')
    except:
        logger.debug('error reading %s' % (infile))
        return (False, 0)
    print ('check')
    option_chain = fin.readlines()
    (contract_name, found, open_interest) = \
            scan_option_chain(symbol, exp_date, option_type, strike, option_chain)
    return (found, open_interest)

def lookup_option_info(symbol, exp_date, option_type, strike, save_file=False):
    # read web data
    url = 'https://finance.yahoo.com/quote/%s/options?date=%s' \
            % (symbol, get_date_in_url(exp_date))
    eid = 'Col1-1-OptionContracts-Proxy'
    chrome_driver = ChromeDriver(height=3240)
    web_data = chrome_driver.download_data(url=url, element_id=eid)
    chrome_driver.close()
    # lookup
    (contract_name, found, open_interest) = \
            scan_option_chain(symbol, exp_date, option_type, strike, web_data.splitlines())
    # save a copy
    if save_file:
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, 'logs')
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        today_date_str = get_date_str(datetime.datetime.today())
        filename = os.path.join(meta_data_dir, contract_name + '_' + today_date_str + '.txt')
        with open(filename, 'w') as fout:
            fout.write(web_data)
    return (found, open_interest)

if __name__ == '__main__':
    root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode='w')
    logging.getLogger().addHandler(logging.StreamHandler())
    exp_date = datetime.datetime(2018,11,16)
    #(found, open_interest) = lookup_option_info('MSFT', exp_date, 'C', 70, True)
    #print ('open interest is %d' % (open_interest))
    infile = os.path.join(root_dir, 'temp', 'data_msft_option_chain.txt')
    (found, open_interest) = parse_option_info('MSFT', exp_date, 'C', 70, infile)
    print ('open interest is %d' % (open_interest))

