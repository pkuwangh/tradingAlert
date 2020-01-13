#!/usr/bin/env python

import logging
import os


def get_root_dir():
    return '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])


def setup_metadata_dir():
    root_dir = get_root_dir()
    metadata_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
    return metadata_dir


def setup_logger(pyfile, mode='w'):
    module_name = pyfile.split('/')[-1]
    if len(module_name) > 3 and module_name[-3:] == '.py':
        module_name = module_name[0:-3]
    metadata_dir = setup_metadata_dir()
    log_file = os.path.join(metadata_dir, 'log.{:s}'.format(module_name))
    logging.basicConfig(filename=log_file, filemode=mode)
    logging.getLogger().addHandler(logging.StreamHandler())
