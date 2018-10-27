#!/home/wangh/anaconda3/bin/python

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
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    chrome_driver = ChromeDriver(height=3240)
    url = 'https://finance.yahoo.com/quote/MSFT/options?date=1542326400';
    eid = 'Col1-1-OptionContracts-Proxy'
    data = chrome_driver.download_data(url=url, element_id=eid)
    print (data)
    chrome_driver.close()

