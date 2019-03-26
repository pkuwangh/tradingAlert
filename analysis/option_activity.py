#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

class OptionActivity:
    __keys = ['activity_str',       # initial string
            'symbol',               # basic info
            'ref_price',
            'option_type',
            'strike_price',
            'exp_date',
            'day_to_exp',
            'option_price',
            'volume',
            'vol_oi',
            'deal_time',
            'total_cost',           # derived
            'ext_value',
            'option_volume',        # separate lookup
            'avg_option_volume',
            'stock_volume',
            'avg_stock_volume',
            'market_cap']

    def __init__(self):
        self.__inited = False
        self.__values = {}
        for k in OptionActivity.__keys:
            self.__values[k] = None

    def is_inited(self):
        return self.__inited

    def __lt__(self, other):
        return self.__values['symbol'] < other.__values['symbol']

    def get_basic_display_str(self):
        return '%-4s %-4s %s->%s %5.1f->%5.1f' % \
                (self.__peek('symbol', is_str=True), self.__peek('option_type', is_str=True),
                        self.__peek('deal_time', is_str=True), self.__peek('exp_date', is_str=True),
                        self.__peek('ref_price'), self.__peek('strike_price'))

    def get_display_str(self):
        return self.get_basic_display_str() + ' vol/oi=%-2.0f cost=%.1fM ext=%.1fM days=%-2d vol(k)=%-4.1f' % \
                (self.__peek('vol_oi'),
                        self.__peek('total_cost')/1e3,
                        self.__peek('ext_value')/1e3,
                        self.__peek('day_to_exp'),
                        self.__peek('volume')/1000)

    def get_ext_display_str(self):
        return self.get_display_str() + ' tot_vol=%-4.1f avg_vol=%-4.1f vol/avg=%-4.1f' % \
                (self.__peek('option_volume')/1000, self.__peek('avg_option_volume')/1000,
                        self.__peek('volume')/(self.__peek('avg_option_volume')+0.1))

    def get_signature(self):
        if not self.__inited:
            raise
        return 'Act' + self.__values['deal_time'] + \
                self.__values['symbol'] + \
                self.__values['exp_date'] + \
                self.__values['option_type'] + \
                str(int(self.__values['strike_price'] * 100))

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

    def set_option_quote(self, option_volume, avg_option_volume):
        self.__set('option_volume', option_volume)
        self.__set('avg_option_volume', avg_option_volume)

    def set_stock_quote(self, stock_volume, avg_stock_volume, market_cap):
        self.__set('stock_volume', stock_volume)
        self.__set('avg_stock_volume', avg_stock_volume)
        self.__set('market_cap', market_cap)

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
        ext_value = int(self.get('volume') * pure_price * 100 / 1000)
        self.__set('ext_value', ext_value)
        # total cost
        total_cost = int(self.get('volume') * self.get('option_price') * 100 / 1000)
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
            self.__set('volume', int(items[10].replace(',', '')))
            self.__set('vol_oi', float(items[12].replace(',', '')))
            self.__set('deal_time', get_date_str(get_date(items[14])))
            self.__inited = True
            self.__derive()
        except Exception as e:
            logger.error('error processing %s: %s' % (option_activity_str.rstrip(), e))

    def from_json_file(self, filename):
        import json
        try:
            with openw(filename, 'rt') as fp:
                json_dict = json.load(fp)
            for k in json_dict:
                try:
                    self.__set(k, json_dict[k])
                except Exception as e:
                    logger.error('error setting %s from %s: %s' % (k, filename, e))
            self.__inited = True
        except Exception as e:
            logger.error('error processing %s: %s' % (filename, e))

    def unserialize(self, filename):
        self.from_json_file(filename)

    def serialize(self, folder='records'):
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        filename = os.path.join(meta_data_dir, self.get_signature()+'.txt.gz')
        logger.info('%s save %4s option activity to %s'
                % (get_time_log(), self.get('symbol'), filename))
        import json
        with openw(filename, 'wt') as fp:
            json.dump(self.__values, fp, indent=4)

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    # test from local copy
#    from data_source.parse_barchart_activity import parse_option_activity
#    infile = os.path.join(root_dir, 'temp', 'data_option_activity.txt')
#    option_activity_list = parse_option_activity(infile)
    # test from online reading
    from data_source.parse_barchart_activity import get_option_activity
    option_activity_list = get_option_activity(save_file=True, folder='logs')
    # test from formatted file
#    infile = os.path.join(root_dir, 'logs', 'OA_190130_150731.txt')
#    fin = openw(infile, 'rt')
#    option_activity_list = fin.readlines()

    filtered_list = []
    for line in option_activity_list:
        option_activity = OptionActivity()
        option_activity.from_activity_str(line)
        if option_activity.is_inited():
            mid_ratio = (option_activity.get('vol_oi') > 5)
            high_ratio = (option_activity.get('vol_oi') > 40)
            mid_ext = (option_activity.get('ext_value') > 100)
            high_ext = (option_activity.get('ext_value') > 500)
            high_cost = (option_activity.get('total_cost') > 1000)
            if (mid_ratio and high_ext and high_cost) or (high_ratio and mid_ext):
#                option_activity.serialize()
                filtered_list.append(option_activity.get_display_str())
    filtered_list.sort()
    for item in filtered_list:
        print (item)
    # send email
    #subject = 'Option activity on %s' % get_datetime_str(datetime.datetime.now())
    #text = '\n'.join(filtered_list)
    #from utils.send_email import MailMan
    #mail_man = MailMan()
    #mail_man.send(subject=subject, content=text)
