#!/usr/bin/env python

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.file_rdwr import *

def add_note(activity_in, comment):
    activity_key = activity_in.split('/')[-1].rstrip('.txt.gz')
    import json
    note_json = os.path.join(root_dir, 'records', 'manual_track', 'note.json')
    try:
        with openw(note_json, 'rt') as fp:
            json_dict = json.load(fp)
        with openw(note_json, 'wt') as fp:
            json_dict[activity_key] = comment
            json.dump(json_dict, fp, indent=4, sort_keys=True)
    except:
        print('failed to add note to %s' % (activity_in))
        pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--activity', '-a', required=True,
            help='option activity file to add mark')
    parser.add_argument('--note', '-n', required=True,
            help='note to add')

    args = parser.parse_args()
    add_note(args.activity, args.note)

