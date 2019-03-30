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

def print_option_effect(filename):
    from analysis.option_effect import OptionEffect
    option_effect = OptionEffect()
    oe_filename = None
    rel_filename = filename.split('/')[-1]
    if rel_filename.startswith('Act'):
        from analysis.option_activity import OptionActivity
        option_activity = OptionActivity()
        try:
            option_activity.unserialize(filename)
        except Exception as e:
            logger.error('error unserializing %s: %s' % (filename, e))
        from analysis.option_effect import OptionEffectFactory
        oe_filename = OptionEffectFactory.get_record_file(option_activity)
    elif rel_filename.startswith('Eff'):
        oe_filename = filename
    else:
        return

    if oe_filename:
        try:
            option_effect.unserialize(oe_filename)
            print (option_effect.get_display_str())
        except Exception as e:
            logger.error('error unserializing %s: %s' % (oe_filename, e))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', '-f', nargs='+', required=True,
            help='option effect files to display')

    args = parser.parse_args()
    for item in args.infile:
        print_option_effect(item)

