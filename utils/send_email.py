#!/usr/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

class MailMan:
    def __init__(self):
        self.__status_good = True
        try:
            self.msg = MIMEMultipart()
            import json
            # sender
            sender_json = os.path.join(root_dir, 'email', 'sender.json')
            with openw(sender_json, 'rt') as fp:
                sender_dict = json.load(fp)
            self.__sender = list(sender_dict.keys())[-1]
            self.__password = sender_dict[self.__sender]
            self.msg['From'] = self.__sender
            # receivers
            # regular users
            receiver_json = os.path.join(root_dir, 'email', 'receiver.json')
            with openw(receiver_json, 'rt') as fp:
                receiver_dict = json.load(fp)
            self.receivers = [v for v in receiver_dict.values()]
            # prime users
            prime_json = os.path.join(root_dir, 'email', 'prime.json')
            with openw(prime_json, 'rt') as fp:
                prime_dict = json.load(fp)
            self.prime_users = [v for v in prime_dict.values()]
        except Exception as e:
            logger.error('error when initing MailMan: %s' % (e))
            self.__status_good = False

    def send(self, subject, content, prime=False):
        if self.__status_good:
            if prime:
                self.msg['To'] = ','.join(self.prime_users)
                self.msg['Subject'] = 'Prime: ' + subject
            else:
                self.msg['To'] = ','.join(self.receivers)
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
    with openw(os.path.join(root_dir, 'notes.txt'), 'rt') as fp:
        text = fp.read()
    # create a MailMan object
    mail_man = MailMan()
    mail_man.send(subject=subject, content=text)
