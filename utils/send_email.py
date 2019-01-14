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

class MailMan:
    def __init__(self):
        self.__status_good = True
        try:
            self.msg = MIMEMultipart()
            import json
            # sender
            sender_json = os.path.join(root_dir, 'email', 'sender.json')
            with open(sender_json, 'r') as fp:
                sender_dict = json.load(fp)
            self.__sender = list(sender_dict.keys())[-1]
            self.__password = sender_dict[self.__sender]
            self.msg['From'] = self.__sender
            # receivers
            receiver_json = os.path.join(root_dir, 'email', 'receiver.json')
            with open(receiver_json, 'r') as fp:
                receiver_dict = json.load(fp)
            receivers = [v for v in receiver_dict.values()]
            self.msg['To'] = ','.join(receivers)
        except Exception as e:
            logger.error('error when initing MailMan: %s' % (e))
            self.__status_good = False

    def send(self, subject, content):
        if self.__status_good:
            self.msg['Subject'] = subject
            main_text = MIMEText(content, 'plain')
            self.msg.attach(main_text)
            # send
            try:
                server = smtplib.SMTP('{}:{}'.format('smtp.gmail.com', 587))
                server.starttls()
                server.login(self.__sender, self.__password)
                server.send_message(self.msg)
                server.quit()
                logger.info('sent email to subscribers')
            except Exception as e:
                logger.error('error when sending email: %s' % (e))
        else:
            pass

if __name__ == '__main__':
    subject = 'Option activity on %s' % get_datetime_str(datetime.datetime.now())
    with open(os.path.join(root_dir, 'notes.txt'), 'r') as fp:
        text = fp.read()
    # create a MailMan object
    mail_man = MailMan()
    mail_man.send(subject=subject, content=text)
