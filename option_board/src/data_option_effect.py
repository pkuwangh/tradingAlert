#!/usr/bin/env python

import json
import os
import logging
from typing import List

from data_packet import BaseDataPacket, DailyStockQuote, DailyOptionQuote
from utils_datetime import get_date_str, get_date
from utils_logging import setup_metadata_dir, setup_logger
from web_chrome_driver import ChromeDriver
from web_option_volume import read_daily_option_quote
from web_stock_quote import read_stock_quote

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OptionEffect(BaseDataPacket):
    name = "option_effect"
    fields = {
        "symbol": "TEXT",
        "option_type": "TEXT",
        "strike_price": "REAL",
        "exp_date": "INTEGER",
        "date": "INTEGER",
        "option_interest": "INTEGER",
        "option_price": "REAL",
        "contract_volume": "INTEGER",
        "market_cap": "REAL",
        "price_high": "REAL",
        "price_low": "REAL",
        "volume": "INTEGER",
        "avg_volume": "INTEGER",
    }

    def __init__(
        self,
        values: List=None,
        daily_stock_quote: DailyStockQuote=None,
        daily_option_quote: DailyOptionQuote=None,
    ):
        super(OptionEffect, self).__init__()
        for k in OptionEffect.fields:
            self._values[k] = None
        if values:
            for idx, key in enumerate(OptionEffect.fields.keys()):
                v = values[idx]
                self.__set(key, v)
        if daily_option_quote:
            for k in DailyOptionQuote.fields.keys():
                if k in OptionEffect.fields:
                    self.__set(k, daily_option_quote.get(k))
        if daily_stock_quote:
            for k in DailyStockQuote.fields.keys():
                if k in OptionEffect.fields:
                    self.__set(k, daily_stock_quote.get(k))


    def set(self, key, value):
        raise RuntimeError("Should not be used")

    def __set(self, key, value):
        if key not in OptionEffect.fields:
            raise KeyError(f"Invalid key={key}")
        self._values[key] = value



if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger("web_chrome_driver").setLevel(logging.DEBUG)
    # test from online reading
    with ChromeDriver() as browser:
        option_quote = read_daily_option_quote(
            browser, "AMD", "Call", 60.0, 20220121, use_barchart=True)
        stock_quote = read_stock_quote(
            browser, "AMD")
        option_effect = OptionEffect(
            daily_option_quote=option_quote, daily_stock_quote=stock_quote)
        print(json.dumps(option_effect.__dict__, indent=4))