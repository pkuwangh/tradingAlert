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
        return '%-4s ratio=%.0f cost=%.0fK ext=%.0fK %s %.1f->%.1f exp=%s days=%d vol=%.1fK date=%s' % \
                (self.__peek('symbol', is_str=True), self.__peek('vol_oi'),
                        self.__peek('total_cost'), self.__peek('ext_value'),
                        self.__peek('option_type', is_str=True),
                        self.__peek('ref_price'), self.__peek('strike_price'),
                        self.__peek('exp_date', is_str=True), self.__peek('day_to_exp'),
                        self.__peek('volumn')/1000,
                        self.__peek('deal_time', is_str=True))

    def is_inited(self):
        return self.__inited

    def get(self, key):
        if key not in OptionActivity.__keys: raise
        if not self.__inited: raise
        if self.__values[key] is None: raise
        return self.__values[key]

    def __peek(self, key, is_str=False):
        if key in self.__values and self.__values[key] is not None:
            return self.__values[key]
        else:
            if is_str: return 'none'
            else: return 0

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
        in_money_put = self.is_put() and self.get('strike_price') > self.get('ref_price')
        in_money = in_money_call or in_money_put
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
        self.__set('activity_str', option_activity_str.rstrip());
        try:
            items = option_activity_str.split()
            self.__set('symbol', items[0])
            self.__set('ref_price', float(items[1].replace(',', '')))
            self.__set('option_type', items[2])
            self.__set('strike_price', float(items[3].replace(',', '').replace('*','')))
            self.__set('exp_date', get_date_str(get_date(items[4])))
            self.__set('day_to_exp', int(items[5]))
            self.__set('option_price', float(items[9].replace(',', '')))
            self.__set('volumn', int(items[10].replace(',', '')))
            self.__set('vol_oi', float(items[12].replace(',', '')))
            self.__set('deal_time', get_date_str(get_date(items[14])))
            self.__inited = True
            self.__derive()
        except Exception as e:
            logger.error('error processing %s: %s', option_activity_str.rstrip(), e)

    def from_json_entry(self, json_filename, json_dict):
        for k in json_dict:
            try:
                self.__set(k, json_dict[k])
            except Exception as e:
                logger.error('error processing %s from %s: %s', k, json_filename, e)
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
#    option_activity_list = parse_option_activity(infile)
    # test from online reading
    from data_retrieve.parse_barchart_activity import get_option_activity
    option_activity_list = get_option_activity(save_file=True)
    # test from formatted file
#    infile = os.path.join(root_dir, 'logs', 'OA_190108_142404.txt')
#    fin = open(infile, 'r')
#    option_activity_list = fin.readlines()

    for line in option_activity_list:
        option_activity = OptionActivity()
        option_activity.from_activity_str(line)
        if option_activity.is_inited():
            if option_activity.get('vol_oi') > 80 or option_activity.get('ext_value') > 20 or option_activity.get('total_cost') > 200:
                print (option_activity.get_display_str())
