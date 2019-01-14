#!/usr/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import sys
import logging
logger = logging.getLogger(__name__)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *

if __name__ == '__main__':
    # create the container email message
    msg = MIMEMultipart();
    msg['Subject'] = 'Option activity on %s' % get_datetime_str(datetime.datetime.now())
    import json
    # sender
    sender_json = os.path.join(root_dir, 'email', 'sender.json')
    with open(sender_json, 'r') as fp:
        sender_dict = json.load(fp)
    sender = list(sender_dict.keys())[-1]
    password = sender_dict[sender]
    msg['From'] = sender
    # receivers
    receiver_json = os.path.join(root_dir, 'email', 'receiver.json')
    with open(receiver_json, 'r') as fp:
        receiver_dict = json.load(fp)
    receivers = [v for v in receiver_dict.values()]
    msg['To'] = ','.join(receivers)
    # main content
    with open(os.path.join(root_dir, 'notes.txt'), 'r') as fp:
        text = fp.read()
    main_text = MIMEText(text, 'plain')
    msg.attach(main_text)
    # send
    server = smtplib.SMTP('{}:{}'.format('smtp.gmail.com', 587))
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
