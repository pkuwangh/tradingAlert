#!/usr/bin/env python

import datetime
import pandas_market_calendars as mcal
from typing import List


def is_market_open(date_str=None):
    if not date_str:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
    nyse = mcal.get_calendar('NYSE')
    return (len(nyse.valid_days(start_date=date_str, end_date=date_str)) > 0)


def get_raw_number_str(number_str: str, remove_list: List[str]) -> str:
    number = number_str.replace(',', '')
    for x in remove_list:
        number = number.replace(x, '')
    return number


def convert_int(number_str: str, remove_list: List[str]=[]) -> int:
    return int(get_raw_number_str(number_str, remove_list))


def convert_float(number_str: str, remove_list: List[str]=[]) -> float:
    return float(get_raw_number_str(number_str, remove_list))


if __name__ == '__main__':
    print(is_market_open())
    print(is_market_open('2020-01-20'))