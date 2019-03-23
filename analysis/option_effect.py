#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from analysis.option_activity import OptionActivity
from utils.datetime_string import *
from utils.file_rdwr import *

class OptionEffect:
    def __init__(self, option_activity=None):
        self.__values = {}
        self.__values['effect'] = {}
        if option_activity:
            self.__values['symbol'] = option_activity.get('symbol')
            self.__values['exp_date'] = option_activity.get('exp_date')
            self.__values['option_type'] = 'C' if 'Call' in option_activity.get('option_type') else 'P'
            self.__values['strike_price'] = option_activity.get('strike_price')
            self.__values['volume'] = option_activity.get('volume')
            self.__values['signature'] = option_activity.get_signature()
            self.__values['display_str'] = option_activity.get_ext_display_str()
            self.__values['oi_init'] = option_activity.get('volume') / option_activity.get('vol_oi')
            self.__values['price_init'] = option_activity.get('ref_price')

    def get(self, key):
        if key not in self.__values: raise
        return self.__values[key]

    @staticmethod
    def calc_record_name(signature):
        return 'Eff' + signature[3:]

    def get_record_name(self):
        return OptionEffect.calc_record_name(self.__values['signature'])

    def track_change(self, folder='logs'):
        exp_date = self.get('exp_date')
        symbol = self.get('symbol')
        logger.info('track changes in OI & price for %s' % (symbol))
        from data_source.parse_yahoo_option import lookup_option_chain_info
        from data_source.parse_yahoo_quote  import lookup_quote_summary
        # 1. lookup oi change
        (found1, oi) = lookup_option_chain_info(
                symbol, get_date(exp_date),
                self.get('option_type'), self.get('strike_price'),
                save_file=True, folder=folder)
        if found1:
            # 2. lookup price change
            (found2, quote_info) = lookup_quote_summary(
                    symbol,
                    save_file=True, folder=folder)
            if found2:
                if self.get('option_type') == 'C': price = quote_info['price_high']
                else: price = quote_info['price_low']
                self.__values['effect'][exp_date] = (oi, price)
            else:
                logger.error('%s error quote for %s not found'
                        % (get_time_log(), symbol))
        else:
            logger.error('%s error OI for %s exp=%s not found'
                    % (get_time_log(), symbol, exp_date))
        return (found1 and found2)

    def unserialize(self, filename):
        import json
        try:
            with openw(filename, 'rt') as fp:
                json_dict = json.load(fp)
            for k in json_dict:
                if k == 'effect':
                    for tk in json_dict[k]:
                        self.__values[k][tk] = json_dict[k][tk]
                else:
                    self.__values[k] = json_dict[k]
        except Exception as e:
            logger.error('error processing %s: %s' % (filename, e))

    def serialize(self, folder='records'):
        file_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = '/'.join(file_dir.split('/')[:-1])
        meta_data_dir = os.path.join(root_dir, folder)
        if not os.path.exists(meta_data_dir):
            os.makedirs(meta_data_dir)
        filename = os.path.join(meta_data_dir, self.get_record_name()+'.txt.gz')
        logger.info('%s save %4s option effect to %s'
                % (get_time_log(), self.get('symbol'), filename))
        import json
        with openw(filename, 'wt') as fp:
            json.dump(self.__values, fp, indent=4)


class OptionEffectFactory:
    # class members
    folder = 'records/auto_track'
    # factory creator
    @classmethod
    def create(cls, option_activity):
        record_name = OptionEffect.calc_record_name(option_activity.get_signature())
        filename = os.path.join(root_dir, cls.folder, record_name+'.txt.gz')
        if os.path.exists(filename):
            # already being tracked
            option_effect = OptionEffect()
            option_effect.unserialize(filename)
        else:
            # new activity
            option_effect = OptionEffect(option_activity)
        # return an option-effect object
        return option_effect


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', '-f', action='store', required=True,
            help='option activity files to display')

    args = parser.parse_args()
    option_activity = OptionActivity()
    option_activity.unserialize(args.infile)
    option_effect = OptionEffectFactory.create(option_activity)
    option_effect.track_change()
    option_effect.serialize(OptionEffectFactory.folder)

