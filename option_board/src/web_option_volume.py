#!/usr/bin/env python

import json
import logging
import re
from typing import List

from data_packet import DailyOptionInfo, DailyOptionQuote
from utils_logging import setup_logger
from utils_datetime import (
    get_time_log, get_date_str, get_date, get_datetime_start)
from utils_market import convert_float, convert_int
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
            url=url,
            wait_base=1,
            element_class=eclass,
            suppress_log=suppress_log,
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
            url = "https://www.barchart.com/stocks/quotes/"
            url += f"{symbol}/options?expiration={str(exp_date)}"
            web_data = browser.download_data(
                url=url,
                wait_base=1,
                pre_element_class=pre_eclass,
                element_class=eclass,
                suppress_log=suppress_sub_log,
            )
            parse_daily_option_info(option_info, web_data.splitlines())
    else:
        logger.error('other data sources not implemented')
        raise ValueError(f"use_barchart={use_barchart}")
    return option_info


def parse_daily_option_quote(
    option_quote: DailyOptionQuote, web_data: List[str],
    symbol: str, option_type: str, strike_price:float, exp_date: int,
    use_barchart: bool=False,
):
    if use_barchart:
        strike_price_str = f"{strike_price:.2f}"
        started = False
        for idx, line in enumerate(web_data):
            if (
                started and
                line.startswith(strike_price_str) and
                ('/' in web_data[idx - 1] or "Strike" in web_data[idx - 1])
            ):
                option_quote.set(
                    "option_interest", convert_int(web_data[idx + 10]))
                option_quote.set(
                    "option_price", convert_float(web_data[idx + 1]))
                option_quote.set(
                    "contract_volume", convert_int(web_data[idx + 9]))
                break
            if line.startswith(option_type):
                started = True
    else:
        exp_date_str = str(exp_date)[-6:]
        strike_str = "%08d" % (strike_price * 1000)
        contract_name = symbol + exp_date_str + option_type[0] + strike_str
        logger.debug("{} lookup {} exp={} {} at {:.1f}".format(
            get_time_log(), symbol, exp_date_str, option_type, strike_price))
        for contract in web_data:
            if contract.startswith(contract_name):
                items = contract.split()
                option_quote.set("option_interest", convert_int(items[-2]))
                option_quote.set("option_price", convert_float(items[-8]))
                option_quote.set("contract_volume", convert_int(items[-3]))


def read_daily_option_quote(
    browser: ChromeDriver,
    symbol: str, option_type: str, strike_price:float, exp_date: int,
    use_barchart: bool=False, suppress_log: bool=False,
)-> DailyOptionQuote:
    option_quote = DailyOptionQuote(
        symbol, option_type, strike_price, exp_date, int(get_date_str()))
    if use_barchart:
        url = "https://www.barchart.com/stocks/quotes/"
        url += f"{symbol}/options?expiration={str(exp_date)}&moneyness=allRows"
        eclass = "bc-options-quotes"
        web_data = browser.download_data(
            url=url,
            wait_base=1,
            element_class=eclass,
            suppress_log=suppress_log,
        )
    else:
        datetime_diff = get_date(str(exp_date)) - get_datetime_start()
        date_url = int(datetime_diff.total_seconds())
        url = f"https://finance.yahoo.com/quote/{symbol}/options?date={date_url}"
        eid = 'Col1-1-OptionContracts-Proxy'
        web_data = browser.download_data(
            url=url,
            wait_base=1,
            element_id=eid,
            suppress_log=suppress_log,
        )
    parse_daily_option_quote(
        option_quote, web_data.splitlines(),
        symbol, option_type, strike_price, exp_date, use_barchart)
    return option_quote


if __name__ == '__main__':
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    with ChromeDriver() as browser:
        option_quote = read_daily_option_quote(
            browser, "ASHR", "Call", 30, 20220121, use_barchart=True)
        print(json.dumps(option_quote.__dict__, indent=4))
        option_info = read_daily_option_info(browser, 'ASHR')
        print(json.dumps(option_info.__dict__, indent=4))
