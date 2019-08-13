#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

def print_option_effect(fileset):
    from analysis.option_activity import OptionActivity
    from analysis.option_effect import OptionEffect
    from analysis.option_effect import OptionEffectFactory
    oe_list = []
    for filename in fileset:
        option_effect = OptionEffect()
        oe_filename = None
        rel_filename = filename.split('/')[-1]
        if rel_filename.startswith('Act'):
            option_activity = OptionActivity()
            try:
                option_activity.unserialize(filename)
            except Exception as e:
                logger.error('error unserializing %s: %s' % (filename, e))
            oe_filename = OptionEffectFactory.get_record_file(option_activity)
        elif rel_filename.startswith('Eff'):
            oe_filename = filename
        else:
            continue

        if oe_filename and os.path.exists(oe_filename):
            try:
                option_effect.unserialize(oe_filename)
                oe_list.append(option_effect)
            except Exception as e:
                logger.error('error unserializing %s: %s' % (oe_filename, e))
    oe_list.sort()
    total_profit = 0
    for item in oe_list:
        (found, sell_date, profit, sell_note) = item.get_transaction_note()
        if found:
            total_profit += profit
        print (item.get_display_str(color=True))
    print ('total profit: %d\n' % (total_profit))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', '-f', nargs='+', required=True,
            help='option effect files to display')

    args = parser.parse_args()
    print_option_effect(args.infile)

