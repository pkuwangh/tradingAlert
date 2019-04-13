#!/usr/bin/env python

import os
import sys
import pickledb
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *

class OptionVolumeCache:
    expire_threshold = 15   # in days
    def __init__(self, filename=None, init_dump=False):
        if filename is None:
            filename = os.path.join(root_dir, 'records', 'cache', 'option_volume.db')
        self.__cache = pickledb.load(filename, auto_dump=init_dump)

    def lookup(self, symbol, avg_only, folder='records'):
        hit = self.__cache.exists(symbol)
        logger.debug('%s lookup option volume info for %s: cache-hit=%d' % (get_time_log(), symbol, hit))
        # lookup the cache
        if self.__cache.exists(symbol):
            # hit
            (option_info, update_date) = self.__cache.get(symbol)
            # check if cache data expired
            elapsed_days = get_time_diff(update_date)
            logger.debug('%s %s from cache: avg_vol=%d today_vol=%d cache_date=%s elapsed=%d'
                    % (get_time_log(), symbol, option_info['vol_3mon'], option_info['vol_today'], update_date, elapsed_days))
            if avg_only:
                if elapsed_days < OptionVolumeCache.expire_threshold:
                    return (True, option_info)
            else:
                if elapsed_days == 0:
                    return (True, option_info)
        # lookup from web
        from data_source.parse_chameleon_option_info import lookup_option_volume
        (found, option_info) = lookup_option_volume(symbol, save_file=False, folder=folder)
        if found:
            # install into the cache
            self.__cache.set(symbol, (option_info, get_date_str()))
        return (found, option_info)

    def dump(self):
        self.__cache.dump()

    def close(self):
        logger.info('%s dump volume cache data to persistent storage', get_time_log())
        self.__cache.dump()

if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    option_volume_cache = OptionVolumeCache()
    (found, option_volume_info) = option_volume_cache.lookup('ECA', avg_only=False)
    print ('%s found=%d vol_today=%d vol_3mon=%d' %
            ('ECA', found, option_volume_info['vol_today'], option_volume_info['vol_3mon']))
    option_volume_cache.close()

