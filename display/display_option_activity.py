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

def print_option_activity(filename):
    from analysis.option_activity import OptionActivity
    option_activity = OptionActivity()
    try:
        option_activity.unserialize(filename)
        print (option_activity.get_ext_display_str())
    except Exception as e:
        logger.error('error displaying %s: %s' % (filename, e))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', '-f', nargs='+', required=True,
            help='option activity files to display')

    args = parser.parse_args()
    for item in args.infile:
        print_option_activity(item)

