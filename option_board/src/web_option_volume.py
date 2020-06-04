#!/usr/bin/env python

import json
import logging
import re
import sys
import time

from data_packet import DailyOptionInfo
from utils_logging import setup_logger
from utils_datetime import get_date_str
from web_chrome_driver import ChromeDriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_dates(web_data):
    return re.findall(r'[\d]{4}-[\d]{2}-[\d]{2}', web_data)


def read_exp_dates(browser, symbol, use_barchart=True, suppress_log=False):
    if use_barchart:
        url = 'https://www.barchart.com/stocks/quotes/'
        url += '{:s}/options'.format(symbol)
        eclass = 'filters'
        web_data = browser.download_data(
            url=url, element_class=eclass, suppress_log=suppress_log
        )
        return extract_dates(web_data)
    else:
        logger.error('other data sources not implemented')
        return []


def parse_daily_option_info(option_info, web_data):
    try:
        for idx in range(len(web_data)):
            line = web_data[idx].lstrip()
            if line.startswith('Put ') or line.startswith('Call '):
                num = int(web_data[idx + 1].replace(',', ''))
                if line.startswith('Call Volume'):
                    option_info.inc('call_vol', num)
                elif line.startswith('Put Volume'):
                    option_info.inc('put_vol', num)
                elif line.startswith('Call Open'):
                    option_info.inc('call_oi', num)
                elif line.startswith('Put Open'):
                    option_info.inc('put_oi', num)
    except Exception as e:
        raise e


def read_daily_option_info(
    browser: ChromeDriver, symbol: str, use_barchart: bool=True,
    suppress_all_log: bool=False, suppress_sub_log: bool=False,
)-> DailyOptionInfo:
    option_info = DailyOptionInfo(symbol, int(get_date_str()))
    if use_barchart:
        all_exp_dates = read_exp_dates(
            browser, symbol,
            suppress_log=suppress_all_log,
        )
        eclass = 'bc-futures-options-quotes-totals'
        pre_eclass = 'bc-datatable'
        for exp_date in all_exp_dates:
            url = 'https://www.barchart.com/stocks/quotes/'
            url += '{:s}/options?expiration={:s}'.format(
                    symbol, exp_date)
            web_data = browser.download_data(
                url=url,
                wait_base=2,
                pre_element_class=pre_eclass,
                element_class=eclass,
                suppress_log=suppress_sub_log,
            )
            parse_daily_option_info(option_info, web_data.splitlines())
        return option_info
    else:
        logger.error('other data sources not implemented')
        raise ValueError('use_barchart={}'.format(use_barchart))


def read_option_contract(
    browser: ChromeDriver,
    symbol: str, exp_date: str, option_type: str, strike:float,
):
    pass


if __name__ == '__main__':
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    with ChromeDriver() as browser:
        option_info = read_daily_option_info(browser, 'ASHR')
        print(json.dumps(option_info.__dict__, indent=4))
