#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import platform
import sys
import time
import random
import logging

from utils_file import *
from utils_datetime import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

root_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(root_dir)


class ChromeDriver:
    def __init__(self, width=1920, height=1080):
        self.driver = None
        if platform.system() == 'Darwin':
            self.driver_path = '/Users/haowang3/workspace/downloads/chromedriver'
        else:
            self.driver_path = '/usr/local/bin/chromedriver'
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--window-size=%u,%u' % (width, height))
        self.chrome_options.add_argument('--no-proxy-server')
        self.chrome_options.add_argument("--proxy-server='direct://'")
        self.chrome_options.add_argument("--proxy-bypass-list=*")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])


    def __enter__(self):
        logger.debug('ChromeDriver entering')
        num_retry = 0
        retry_timeout = 4
        while num_retry < retry_timeout:
            num_retry += 1
            try:
                self.driver = webdriver.Chrome(
                        executable_path=self.driver_path,
                        options=self.chrome_options)
            except Exception as e:
                logger.warning('error %s when init driver (retry=%d/%d)'
                        % (str(e), num_retry, retry_timeout))
                time.sleep(5)
                continue
        return self


    def __exit__(self, *args):
        logger.debug('ChromeDriver exiting')
        if self.driver:
            self.driver.close()
            self.driver.quit()


    def download_data(self, url, \
            button_css=None, element_id=None, element_class=None, \
            outfile=None):
        logger.info('%s download data from %s' % (get_time_log(), url))
        num_retry = 0
        retry_timeout = 4
        element = None
        while num_retry < retry_timeout:
            num_retry += 1
            # access the url
            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning('error %s when accessing url=%s (retry=%d/%d)'
                        % (str(e), url, num_retry, retry_timeout))
                if self.driver is None:
                    break
                else:
                    time.sleep(5)
                    continue
            time.sleep(1*random.random())
            # click a button if needed
            if button_css:
                all_seq_good = True
                for button in button_css:
                    try:
                        button = self.driver.find_element_by_css_selector(button).click()
                        time.sleep(1*random.random())
                    except Exception as e:
                        logger.warning('error %s when getting button=%s (retry=%d/%d)'
                                % (str(e), button, num_retry, retry_timeout))
                        all_seq_good = False
                        time.sleep(5)
                        break
                if not all_seq_good:
                    continue
            time.sleep(1*random.random())
            # get the target element
            if element_id:
                try:
                    element = self.driver.find_element_by_id(element_id)
                except Exception as e:
                    logger.warning('error %s when getting element=%s (retry=%d/%d)'
                            % (str(e), element_id, num_retry, retry_timeout))
                    time.sleep(5)
                    continue
            elif element_class:
                try:
                    element = self.driver.find_element_by_class_name(element_class)
                except Exception as e:
                    logger.warning('error %s when getting class=%s (retry=%d/%d)'
                            % (str(e), element_class, num_retry, retry_timeout))
                    time.sleep(5)
                    continue
            else:
                logger.error('Do not know how to find element')
            # done if found element
            if element and element.text and len(element.text) > 1:
                break
            else:
                logger.warning('failed get element=%d text=%d len(text)=%d (retry=%d/%d)'
                        % ( (1 if element else 0),
                            (1 if element and element.text else 0),
                            (len(element.text) if element and element.text else 0),
                            (num_retry, retry_timeout) )
                        )
                time.sleep(10)
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


if __name__ == '__main__':
    metadata_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
    log_file = os.path.join(metadata_dir, 'log.' + __file__.split('/')[-1])
    logging.basicConfig(filename=log_file, filemode='w')
    logging.getLogger().addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    # testing
    with ChromeDriver() as driver:
        url = 'https://finance.yahoo.com/quote/AMD/options'
        eid = 'Col1-1-OptionContracts-Proxy'
        outfile = os.path.join(metadata_dir, 'data_amd_option_chain.txt')
        try:
            data = driver.download_data(url=url, element_id=eid, outfile=outfile)
        except:
            pass
        else:
            print(data)
