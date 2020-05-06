#!/usr/bin/env python

import os
import sys
import logging

from data_packet import BaseDataPacket
from utils_datetime import get_time_log, get_date_str, get_date
from utils_file import openw
from utils_logging import setup_metadata_dir, setup_logger
from web_chrome_driver import ChromeDriver
from web_option_activity import read_option_activity

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OptionActivity(BaseDataPacket):
    name = 'option_activity'
    fields = {
        'symbol': 'TEXT',              # basic info
        'ref_stock_price': 'REAL',
        'option_type': 'TEXT',
        'strike_price': 'REAL',
        'exp_date': 'INTEGER',
        'day_to_exp': 'INTEGER',
        'option_price': 'REAL',
        'contract_vol': 'INTEGER',
        'contract_oi': 'INTEGER',
        'deal_time': 'INTEGER',
        'total_cost': 'INTEGER',       # derived info
        'extrinsic_value': 'INTEGER',
        'avg_option_vol': 'INTEGER',   # separate lookup
        'avg_total_oi': 'INTEGER',
    }

    def __init__(self):
        super(OptionActivity, self).__init__()
        self.__inited = False
        for k in OptionActivity.fields:
            self._values[k] = None

    def is_inited(self):
        return self.__inited

    def __lt__(self, other):
        return self._values['deal_time'] < other._values['deal_time']

    def get_basic_display_str(self):
        return '{:<4s} {:<4s} {:6d}->{:6d} {:5.1f}->{:<5.1f} {:5.1f}%'.format(
            self.__peek('symbol', is_str=True),
            self.__peek('option_type', is_str=True),
            self.__peek('deal_time'),
            self.__peek('exp_date'),
            self.__peek('ref_stock_price'),
            self.__peek('strike_price'),
            self.get_otm())

    def get_display_str(self):
        outstr = self.get_basic_display_str()
        outstr += ' days={:<2d} vol/oi={:<2.0f} cost={:.1f}M ext={:.1f}M'.format(
            self.__peek('day_to_exp'),
            self.get_contract_vol_oi(),
            self.__peek('total_cost')/1000.0,
            self.__peek('extrinsic_value')/1000.0)
        outstr += ' vol(k)={:<4.1f}'.format(
            self.__peek('contract_vol')/1000.0)
        outstr += ' avg_vol={:<4.1f} vol/avg={:<4.1f}'.format(
            self.__peek('avg_option_vol')/1000.0,
            self.get_contract_vol_avg_vol())
        outstr += ' tot_oi={:<4.1f} vol/tot_oi={:<4.1f}%'.format(
            self.__peek('avg_total_oi')/1000.0,
            self.get_contract_vol_avg_tot_oi()*100)
        return outstr

    def get_contract_vol_oi(self):
        return self.__peek('contract_vol') / (self.__peek('contract_oi')+0.1)

    def get_contract_vol_avg_vol(self):
        return self.__peek('contract_vol') / (self.__peek('avg_option_vol') + 0.1)

    def get_contract_vol_avg_tot_oi(self):
        return self.__peek('contract_vol') / (self.__peek('avg_total_oi') + 0.1)

    def get_signature(self):
        if not self.__inited:
            raise sys.exc_info()[1]
        return 'Act' + \
            str(self._values['deal_time']) + \
            self._values['symbol'] + \
            str(self._values['exp_date']) + \
            self._values['option_type'] + \
            str(int(self._values['strike_price'] * 100))

    def get_otm(self):
        l_x = 100 * self.get('strike_price') / (self.get('ref_stock_price') + 0.001)
        if self.is_call():
            return (l_x - 100)
        else:
            return (100 - l_x)

    def get(self, key):
        if key not in OptionActivity.fields: raise sys.exc_info()[1]
        if not self.__inited: raise sys.exc_info()[1]
        if self._values[key] is None: raise sys.exc_info()[1]
        return self._values[key]

    def __peek(self, key, is_str=False):
        if key in self._values and self._values[key] is not None:
            return self._values[key]
        else:
            if is_str: return 'Null'
            else: return 0

    def is_call(self):
        return ('Call' in self.get('option_type'))

    def is_put(self):
        return (not self.is_call())

    def set(self, key, value):
        raise sys.exc_info()[1]

    def __set(self, key, value):
        if key not in OptionActivity.fields:
            raise sys.exc_info()[1]
        self._values[key] = value

    def set_option_info(self, avg_option_volume, avg_total_oi):
        self.__set('avg_option_vol', avg_option_volume)
        self.__set('avg_total_oi', avg_total_oi)

    def __derive(self):
        in_money_call = self.is_call() and \
            self.get('strike_price') < self.get('ref_stock_price')
        in_money_put = self.is_put() and \
            self.get('strike_price') > self.get('ref_stock_price')
        in_money = in_money_call or in_money_put
        if in_money:
            int_price = abs(self.get('strike_price') - self.get('ref_stock_price'))
            pure_price = self.get('option_price') - int_price
        else:
            pure_price = self.get('option_price')
        # extrinsic value
        extrinsic_value = int(self.get('contract_vol') * pure_price / 10)
        self.__set('extrinsic_value', extrinsic_value)
        # total cost
        total_cost = int(self.get('contract_vol') * self.get('option_price') / 10)
        self.__set('total_cost', total_cost)

    def from_activity_str(self, option_activity_str):
        try:
            items = option_activity_str.split()
            self.__set('symbol', items[0])
            self.__set('ref_stock_price', float(items[1].replace(',', '')))
            self.__set('option_type', items[2])
            self.__set('strike_price', float(items[3].replace(',', '').replace('*','')))
            self.__set('exp_date', int(get_date_str(get_date(items[4]))))
            self.__set('day_to_exp', int(items[5]))
            self.__set('option_price', float(items[9].replace(',', '')))
            self.__set('contract_vol', int(items[10].replace(',', '')))
            self.__set('contract_oi', int(items[11].replace(',', '')))
            self.__set('deal_time', int(get_date_str(get_date(items[14]))))
            self.__inited = True
            self.__derive()
        except Exception as e:
            logger.error('error processing %s: %s' % (option_activity_str.rstrip(), e))


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    # test from online reading
    with ChromeDriver() as browser:
        option_activity_list = read_option_activity(browser, True, metadata_dir)
        filtered_list = []
        for line in option_activity_list:
            option_activity = OptionActivity()
            option_activity.from_activity_str(line)
            if option_activity.is_inited():
                vol = option_activity.get('contract_vol')
                oi = option_activity.get('contract_oi')
                ratio = (vol/oi > 5)
                ext = (option_activity.get('extrinsic_value') > 200)
                cost = (option_activity.get('total_cost') > 500)
                if ratio and ext and cost:
                    filtered_list.append(option_activity.get_display_str())
        filtered_list.sort()
        for item in filtered_list:
            print(item)
