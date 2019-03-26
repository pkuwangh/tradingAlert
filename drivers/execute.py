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

def execute():
    # hunt for unusual activity
    from drivers.hunter import hunt
    hunted_list = hunt()
    # send email to my beloved followers
    from utils.send_email import MailMan
    mail_man = MailMan()
    subject = 'Option activity on %s' % (get_datetime_str())
    text = ''
    for item in hunted_list:
        text += (item.get_ext_display_str() + '\n')
    text += '\n'
    mail_man.send(subject=subject, content=text)


if __name__ == '__main__':
    meta_data_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(meta_data_dir):
        os.makedirs(meta_data_dir)
    log_file = os.path.join(meta_data_dir, 'log.' + __name__)
    logging.basicConfig(filename=log_file, filemode='a')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)
    # execute all
    execute()

