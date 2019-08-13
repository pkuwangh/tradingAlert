#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)

from analysis.option_activity import OptionActivity
from analysis.option_effect   import OptionEffect

def fix_option_effect(option_activity):
    from analysis.option_effect import OptionEffectFactory
    filename = OptionEffectFactory.get_record_file(option_activity)
    if os.path.exists(filename):
        logger.info('fixing option effect: %s' % (filename))
        # read it in & create a backup
        option_effect = OptionEffect()
        option_effect.unserialize(filename)
#        os.rename(filename, filename[:-6]+'txt.bak.gz')
        # re-initialize
        option_effect.initialize(option_activity)
        # dump
        option_effect.serialize(OptionEffectFactory.folder)
        return True
    else:
        return False


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
    parser.add_argument('--infile', '-f', nargs='+', required=True,
            help='option activity files to display')

    args = parser.parse_args()
    for item in args.infile:
        if item.startswith('Act'):
            option_activity = OptionActivity()
            option_activity.unserialize(item)
            if fix_option_effect(option_activity):
                logger.info('fixed option activity: %s' % (item))
            else:
                logger.info('ignored option activity: %s' % (item))

