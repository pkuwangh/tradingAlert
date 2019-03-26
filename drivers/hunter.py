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

def filter_base(new_option_activity, option_volume_cache):
    # parameters
    thd_vol_oi = 2
    thd_tot_cost = 200
    thd_ext_value = 100
    thd_d2e_min = 2
    thd_d2e_max = 60
    thd_vol_spike = 2
    thd_vol_dist = 0.6
    # stage 1: simple filtering
    # ----------------------------------------------------------------
    # volume/open interest: first blood ?
    if new_option_activity.get('vol_oi') < thd_vol_oi:
        return False
    # total cost: serious money ?
    if new_option_activity.get('total_cost') < thd_tot_cost:
        return False
    # extrinsic value: real money in risk ?
    if new_option_activity.get('ext_value') < thd_ext_value:
        return False
    # day to exp: not too-long term ?
    if new_option_activity.get('day_to_exp') < thd_d2e_min:
        return False
    if new_option_activity.get('day_to_exp') > thd_d2e_max:
        return False
    # volume/average volume: volume spike ?
    volume_folder = 'records/raw_option_volume'
    (found, option_info) = option_volume_cache.lookup(symbol=new_option_activity.get('symbol'), avg_only=True, folder=volume_folder)
    if found:
        if new_option_activity.get('volume') < option_info['vol_3mon'] * thd_vol_spike:
            return False
    else:
        logger.error('%s cannot find avg. option volume info for %s' % (get_time_log(), new_option_activity.get('symbol')))
        return False
    # stage 2: more detailed analysis
    # ----------------------------------------------------------------
    # volume/today's volume: dominating trade ?
    (found, option_info) = option_volume_cache.lookup(symbol=new_option_activity.get('symbol'), avg_only=False, folder=volume_folder)
    if found:
        if new_option_activity.get('volume') < option_info['vol_today'] * thd_vol_dist:
            return False
    else:
        logger.error('%s cannot find total option volume info for %s' % (get_time_log(), new_option_activity.get('symbol')))
        return False
    # stage 3: got a candidate
    new_option_activity.set_option_quote(option_info['vol_today'], option_info['vol_3mon'])
    logger.info('candidate: %s' % (new_option_activity.get_ext_display_str()))
    return True


def filter_detail(new_option_activity, option_volume_cache):
    # it should be extreme in some aspect(s)
    mid_vol_oi  = (new_option_activity.get('vol_oi') > 5)
    high_vol_oi = (new_option_activity.get('vol_oi') > 20)
    high_cost = (new_option_activity.get('total_cost') > 1000)
    high_ext_value = (new_option_activity.get('ext_value') > 500)
    mid_volume_spike  = (new_option_activity.get('volume') > new_option_activity.get('avg_option_volume') * 3)
    high_volume_spike = (new_option_activity.get('volume') > new_option_activity.get('avg_option_volume') * 6)
    mid_volume_domin  = (new_option_activity.get('volume') > new_option_activity.get('option_volume') * 0.75)
    high_volume_domin = (new_option_activity.get('volume') > new_option_activity.get('option_volume') * 0.9)
    # types of unusual activity
    big_money  = ((high_cost or high_ext_value) and (mid_vol_oi or mid_volume_spike or mid_volume_domin))
    big_volume = (high_vol_oi or high_volume_spike or high_volume_domin)
    # final round
    if big_money or big_volume:
        # my lucky guy
        return True
    return False


def filter(new_option_activity, option_volume_cache):
    if filter_base(new_option_activity, option_volume_cache):
        if filter_detail(new_option_activity, option_volume_cache):
            return True
    return False


def hunt():
    logger.info('================================================================')
    logger.info('%s the hunter started! Hunt or to be hunted!' % (get_time_log()))
    # init volume cache
    from analysis.option_volume import OptionVolumeCache
    option_volume_cache = OptionVolumeCache(filename=os.path.join(root_dir, 'records', 'cache', 'option_volume.db'))
    # pull option activity list
    from data_source.parse_barchart_activity import get_option_activity
    from analysis.option_activity import OptionActivity
    option_activity_list = get_option_activity(save_file=True, folder='records/raw_option_activity')
#    infile = os.path.join(root_dir, 'records', 'raw_option_activity', 'OA_190321_010414.txt.gz')
#    fin = openw(infile, 'rt')
#    option_activity_list = fin.readlines()
    # look into each one
    filtered_list = []
    for line in option_activity_list:
        new_option_activity = OptionActivity()
        new_option_activity.from_activity_str(line)
        if new_option_activity.is_inited():
            if filter(new_option_activity, option_volume_cache):
                filtered_list.append(new_option_activity)
                new_option_activity.serialize('records/option_activity_live')
        else:
            logger.error('error while init-ing line: %s' % (line))
    filtered_list.sort()
    # dump cache
    option_volume_cache.close()
    # return a list of option-activity objects
    return filtered_list


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)
    filtered_list = hunt()
    for item in filtered_list:
        print (item.get_ext_display_str())

