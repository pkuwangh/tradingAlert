#!/usr/bin/env python

import json
import logging
from typing import List

from data_packet import DailyStockQuote
from utils_logging import setup_logger
from utils_datetime import get_date_str, get_time_log
from web_chrome_driver import ChromeDriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_stock_quote(stock_quote: DailyStockQuote, web_data: List[str]):
    logger.debug("{} lookup {} quote summary".format(
        get_time_log(), stock_quote.get("symbol")))
    status_bad = False
    for line in web_data:
        items = line.split()
        if "Market Cap" in line or "Net Assets" in line:
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
                stock_quote.set("market_cap", value / 1e9)
            except:
                status_bad = True
        elif "Range" in line and "Day" in line:
            try:
                stock_quote.set("price_high", float(items[-1].replace(',', '')))
                stock_quote.set("price_low", float(items[-3].replace(',', '')))
            except:
                status_bad = True
        elif "Volume" in line and "Avg" not in line:
            try:
                stock_quote.set('volume', int(items[-1].replace(',', '')))
            except:
                status_bad = True
        elif "Avg. Volume" in line:
            try:
                stock_quote.set("avg_volume", int(items[-1].replace(',', '')))
            except:
                status_bad = True
    if status_bad:
        logger.error(
            "{} error parsing {} quote; cap={} high={} low={} vol={} avg_vol={}".format(
                get_time_log(), stock_quote.get("symbol"),
                stock_quote.get("market_cap"),
                stock_quote.get("price_high"), stock_quote.get("price_low"),
                stock_quote.get("volume"), stock_quote.get("avg_volume"),
            )
        )


def read_stock_quote(
    browser: ChromeDriver, symbol: str,
    suppress_log: bool=False,
)-> DailyStockQuote:
    stock_quote = DailyStockQuote(symbol, int(get_date_str()))
    url = f"https://finance.yahoo.com/quote/{symbol}"
    eid = "quote-summary"
    web_data = browser.download_data(
        url=url,
        element_id=eid,
        suppress_log=suppress_log,
    )
    parse_stock_quote(stock_quote, web_data.splitlines())
    return stock_quote


if __name__ == "__main__":
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger("web_chrome_driver").setLevel(logging.DEBUG)
    with ChromeDriver() as browser:
        stock_quote = read_stock_quote(browser, "ASHR")
        print(json.dumps(stock_quote.__dict__, indent=4))