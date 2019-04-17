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

def print_option_activity(fileset):
    from analysis.option_activity import OptionActivity
    oa_list = []
    for filename in fileset:
        rel_filename = filename.split('/')[-1]
        if rel_filename.startswith('Act'):
            option_activity = OptionActivity()
            try:
                option_activity.unserialize(filename)
                oa_list.append(option_activity)
            except Exception as e:
                logger.error('error displaying %s: %s' % (filename, e))
    oa_list.sort()
    for item in oa_list:
        print (item.get_ext_display_str(color=True))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', '-f', nargs='+', required=True,
            help='option activity files to display')

    args = parser.parse_args()
    print_option_activity(args.infile)

