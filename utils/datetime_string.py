#!/usr/bin/env python

import datetime

def get_time_diff(date_str):
    if len(date_str) == 6 and date_str.isdigit():
        ref_date = datetime.datetime.strptime(date_str, '%y%m%d')
        delta = datetime.datetime.now() - ref_date
        return delta.days
    return 99999

# return a datetime object
def get_date(date_str):
    # convert a regular date string into datetime object
    if len(date_str) == 8 and date_str[2] == '/' and date_str[5] == '/':
        return datetime.datetime.strptime(date_str, '%m/%d/%y')
    elif len(date_str) == 6 and date_str.isdigit():
        return datetime.datetime.strptime(date_str, '%y%m%d')
    else:
        return datetime.datetime.now()

# return a datetime string
def get_date_str(datetime_obj=None):
    # convert a datetime object into regular date string
    if datetime_obj is None:
        datetime_obj = datetime.datetime.now()
    return datetime_obj.strftime('%y%m%d')

def get_datetime_str(datetime_obj=None):
    # convert a datetime object
    if datetime_obj is None:
        datetime_obj = datetime.datetime.now()
    return datetime_obj.strftime('%y%m%d_%H%M%S')

def get_time_log():
    return '[%s]' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

