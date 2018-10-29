#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class ChromeDriver:
    # class members
    binary_path = '/usr/bin/google-chrome'
    driver_path = '/usr/local/bin/chromedriver'

    def __init__(self, width=1920, height=3240):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--window-size=1920,3240')
        self.chrome_options.binary_location = ChromeDriver.binary_path
        self.driver = webdriver.Chrome(executable_path=ChromeDriver.driver_path,
                                       options=self.chrome_options)

    def download_data(self, url, element_id=None, class_name=None, outfile=None):
        logger.info('%s download data from %s'
                % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), url))
        # access the url
        self.driver.get(url)
        # get the target element
        if element_id:
            element = self.driver.find_element_by_id(element_id)
        elif class_name:
            element = self.driver.find_element_by_class_name(class_name)
        else:
            logger.error('Do not know how to find element')
            raise
        # output & return
        if outfile:
            with open(outfile, 'w') as fout:
                fout.write(element.text)
        return element.text

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
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode='w')
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
    url = 'https://www.barchart.com/options/unusual-activity/stocks?orderBy=tradeTime&orderDir=desc&page=1'
    eid = 'main-content-column'
    outfile = os.path.join(temp_dir, 'data_option_activity.txt')
    data = chrome_driver.download_data(url=url, element_id=eid, outfile=outfile)
    print (data)
    chrome_driver.close()

