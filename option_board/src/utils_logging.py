#!/usr/bin/env python

import logging
import os


def setup_metadata_dir():
    root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
    metadata_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
    return metadata_dir


def setup_logger(module_name, mode='w', level=logging.DEBUG):
    metadata_dir = setup_metadata_dir()
    log_file = os.path.join(metadata_dir, 'log.{:s}'.format(module_name))
    logging.basicConfig(filename=log_file, filemode=mode)
    logging.getLogger().addHandler(logging.StreamHandler())
