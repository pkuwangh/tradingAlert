#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import sys
import time
import random
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)
from utils.datetime_string import *
from utils.file_rdwr import *

class ChromeDriver:
    # class members
    binary_path = '/usr/bin/google-chrome'
    driver_path = '/usr/local/bin/chromedriver'

    def __init__(self, width=1920, height=1080):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--window-size=1920,3240')
        self.chrome_options.binary_location = ChromeDriver.binary_path
        num_retry = 0
        retry_timeout = 4
        while num_retry < retry_timeout:
            try:
                self.driver = webdriver.Chrome(executable_path=ChromeDriver.driver_path,
                        options=self.chrome_options)
                if num_retry > 0:
                    logger.info('finally succeed after retrying %d times' % (num_retry))
                break
            except Exception as e:
                logger.warning('error when init driver: %s (retry=%d)' % (e, num_retry))
                time.sleep(10)
                num_retry += 1
                continue
        if num_retry >= retry_timeout:
            raise

    def download_data(self, url, button_css_sel=None, element_id=None, element_class_name=None, outfile=None):
        logger.info('%s download data from %s' % (get_time_log(), url))
        num_retry = 0
        element = None
        while num_retry < 8:
            num_retry += 1
            # access the url
            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning('error when accessing url=%s: %s (retry=%d)'
                        % (url, e, num_retry))
                time.sleep(10)
                continue
            time.sleep(5*random.random())
            # click a button if needed
            if button_css_sel:
                try:
                    button = self.driver.find_element_by_css_selector(button_css_sel).click()
                except Exception as e:
                    logger.warning('error when getting button=%s: %s (retry=%d)'
                            % (button_css_sel, e, num_retry))
                    if num_retry < 4:
                        time.sleep(10)
                        continue
            # get the target element
            if element_id:
                try:
                    element = self.driver.find_element_by_id(element_id)
                except Exception as e:
                    logger.warning('error when getting element=%s: %s (retry=%d)'
                            % (element_id, e, num_retry))
                    time.sleep(10)
                    continue
            elif element_class_name:
                try:
                    element = self.driver.find_element_by_class_name(element_class_name)
                except Exception as e:
                    logger.warning('error when getting class=%s: %s (retry=%d)'
                            % (element_class_name, e, num_retry))
                    time.sleep(10)
                    continue
            else:
                logger.error('Do not know how to find element')
            # done if found element
            if element and element.text:
                break
            else:
                logger.warning('did not get the element? (retry=%u)' % (num_retry))
                time.sleep(30)
                continue
        # output & return
        if element:
            if outfile:
                with openw(outfile, 'wt') as fout:
                    fout.write(element.text)
            return element.text
        else:
            logger.error('%s failed to get element from %s' % (get_time_log(), url))
            raise

    def close(self):
        self.driver.close()

if __name__ == '__main__':
    import os
    import os.path
    root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
    temp_dir = os.path.join(root_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    log_file = os.path.join(temp_dir, 'log.' + __name__)
    import sys
    logging.basicConfig(filename=log_file, filemode='w')
    logging.getLogger().addHandler(logging.StreamHandler())
    # create chrome driver
    chrome_driver = ChromeDriver(height=3240)
    # option chain
    url = 'https://finance.yahoo.com/quote/MSFT/options?date=1542326400'
    eid = 'Col1-1-OptionContracts-Proxy'
    outfile = os.path.join(temp_dir, 'data_msft_option_chain.txt')
    data = chrome_driver.download_data(url=url, element_id=eid, outfile=outfile)
    print (data)
    # option activity
    url = 'https://www.barchart.com/options/unusual-activity/stocks'
    eid = 'main-content-column'
    outfile = os.path.join(temp_dir, 'data_option_activity.txt')
    data = chrome_driver.download_data(url=url, element_id=eid, outfile=outfile)
    print (data)
    chrome_driver.close()

