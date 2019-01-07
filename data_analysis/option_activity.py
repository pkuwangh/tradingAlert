#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from util.datetime_string import *

class OptionActivity:
    __keys = ['activity_str',       # initial string
            'symbol',               # basic info
            'ref_price',
            'option_type',
            'strike_price',
            'exp_date',
            'day_to_exp',
            'option_price',
            'volumn',
            'vol_oi',
            'deal_time',
            'total_cost',           # derived
            'ext_value']

    def __init__(self):
        self.__inited = False
        self.__values = {}
        for k in OptionActivity.__keys:
            self.__values[k] = None

    def get_display_str(self):
        return '%s ratio=%.0f cost=%.0fK ext=%.0fK from [%s]' % \
                (self.get('symbol'), self.get('vol_oi'), \
                self.get('total_cost'), self.get('ext_value'), \
                self.get('activity_str'))

    def is_inited(self):
        return self.__inited

    def get(self, key):
        if key not in OptionActivity.__keys: raise
        if not self.__inited: raise
        if self.__values[key] is None: raise
        return self.__values[key]

    def is_call(self):
        return ('Call' in self.get('option_type'))

    def is_put(self):
        return (not self.is_call())

    def __set(self, key, value):
        if key not in OptionActivity.__keys:
            raise
        self.__values[key] = value

    def __derive(self):
        in_money_call = self.is_call() and self.get('strike_price') < self.get('ref_price')
        in_money_put = self.is_put() and self.get('strike_price') <= self.get('ref_price')
        in_money = in_money_call and in_money_put
        if in_money:
            int_price = abs(self.get('strike_price') - self.get('ref_price'))
            pure_price = self.get('option_price') - int_price
        else:
            pure_price = self.get('option_price')
        # extrinsic value
        ext_value = self.get('volumn') * pure_price / 1000
        self.__set('ext_value', ext_value)
        # total cost
        total_cost = self.get('volumn') * self.get('option_price') / 1000
        self.__set('total_cost', total_cost)

    def from_activity_str(self, option_activity_str):
        self.__set('activity_str', option_activity_str);
        try:
            items = option_activity_str.split()
            self.__set('symbol', items[0])
            self.__set('ref_price', float(items[1]))
            self.__set('option_type', items[2])
            self.__set('strike_price', float(items[3]))
            self.__set('exp_date', get_date(items[4]))
            self.__set('day_to_exp', int(items[5]))
            self.__set('option_price', float(items[9].replace(',', '')))
            self.__set('volumn', int(items[10].replace(',', '')))
            self.__set('vol_oi', float(items[12]))
            self.__set('deal_time', get_date(items[14]))
        except:
            logger.error('error processing %s', option_activity_str)
        self.__inited = True 
        self.__derive()

    def from_json_entry(self, json_filename, json_dict):
        for k in json_dict:
            try:
                self.__set(k, json_dict[k])
            except:
                logger.error('error processing %s from %s', k, json_filename)
        self.__inited = True
        self.__derive()

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    # test from local copy
#    from data_retrieve.parse_barchart_activity import parse_option_activity
#    infile = os.path.join(root_dir, 'temp', 'data_option_activity.txt')
#    (option_activity_list, num_pages) = parse_option_activity(infile)
    from data_retrieve.parse_barchart_activity import get_option_activity
    (option_activity_list, num_pages) = get_option_activity(save_file=True)
    for line in option_activity_list:
        option_activity = OptionActivity()
        option_activity.from_activity_str(line)
        if option_activity.get('vol_oi') > 100 or \
                option_activity.get('ext_value') > 20 or \
                option_activity.get('total_cost') > 200:
            print (option_activity.get_display_str())

