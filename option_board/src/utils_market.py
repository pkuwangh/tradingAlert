#!/usr/bin/env python

import datetime
import pandas_market_calendars as mcal


def is_market_open(date_str=None):
    if not date_str:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
    nyse = mcal.get_calendar('NYSE')
    return (len(nyse.valid_days(start_date=date_str, end_date=date_str)) > 0)


if __name__ == '__main__':
    print(is_market_open())
    print(is_market_open('2020-01-20'))