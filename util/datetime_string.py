#!/usr/bin/env python

import datetime

def get_date(date_str):
    # convert a regular date string into datetime object
    if len(date_str) == 8 and date_str[2] == '/' and date_str[5] == '/':
        return datetime.datetime.strptime(date_str, '%m/%d/%y')
    else:
        return datetime.datetime.now()

def get_date_str(exp_date):
    # convert a datetime object into regular date string
    return exp_date.strftime('%y%m%d')

def get_datetime_str(date_and_time):
    # convert a datetime object
    return date_and_time.strftime('%y%m%d_%H%M%S')

def get_time_log():
    return '[%s]' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

