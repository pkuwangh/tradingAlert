#!/usr/bin/env python

import logging
import platform
import os
import random
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils_datetime import get_time_log
from utils_file import openw
from utils_logging import setup_logger, setup_metadata_dir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger(
    "selenium.webdriver.remote.remote_connection"
).setLevel(logging.WARNING)


class ChromeDriver:
    def __init__(self, width=1920, height=1080):
        self.driver = None
        if platform.system() == "Darwin":
            self.path = "/Users/haowang3/workspace/downloads/chromedriver"
        else:
            self.path = "/usr/local/bin/chromedriver"
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument(f"--window-size={width},{height}")
        self.options.add_argument("--no-proxy-server")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )

    def __enter__(self):
        logger.debug("ChromeDriver entering")
        num_retry = 0
        retry_timeout = 4
        while num_retry < retry_timeout:
            num_retry += 1
            try:
                self.driver = webdriver.Chrome(
                        executable_path=self.path,
                        options=self.options)
                break
            except Exception as e:
                logger.warning("error {} init driver (retry={}/{})".format(
                    str(e), num_retry, retry_timeout,
                ))
                time.sleep(5 * num_retry)
                continue
        return self

    def __exit__(self, *args):
        logger.debug("ChromeDriver exiting")
        if self.driver:
            self.driver.close()
            self.driver.quit()

    def download_data(
        self,
        url,
        wait_base=1,
        button_css=None,
        pre_element_id=None,
        pre_element_class=None,
        element_id=None,
        element_class=None,
        outfile=None,
        suppress_log=False,
    ):
        if not suppress_log:
            logger.info(f"{get_time_log()} download data from {url}")
        num_retry = 0
        retry_timeout = 4
        element = None
        while num_retry < retry_timeout:
            num_retry += 1
            # access the url
            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning(
                    "error {} accessing url={} (retry={}/{})".format(
                        str(e), url, num_retry, retry_timeout,
                    )
                )
                if self.driver is None:
                    break
                else:
                    time.sleep(5 * num_retry)
                    continue
            time.sleep(wait_base * (random.random() + 1))
            # click a button if needed
            if button_css:
                all_seq_good = True
                for button in button_css:
                    try:
                        self.driver.find_element_by_css_selector(
                            button).click()
                        time.sleep(wait_base * (random.random() + 1))
                    except Exception as e:
                        logger.warning(
                            "error {} getting button={} (retry={}/{})".format(
                                str(e), button, num_retry, retry_timeout,
                            )
                        )
                        all_seq_good = False
                        time.sleep(5 * num_retry)
                        break
                if not all_seq_good:
                    continue
            # get the target element
            try:
                # touch the pre-req element
                if pre_element_id:
                    self.driver.find_element_by_id(pre_element_id)
                if pre_element_class:
                    self.driver.find_element_by_class_name(pre_element_class)
                # read actual target element
                if element_id:
                    element = self.driver.find_element_by_id(element_id)
                elif element_class:
                    element = self.driver.find_element_by_class_name(
                        element_class)
                else:
                    logger.error("Do not know how to find element")
            except Exception as e:
                logger.warning(
                    "error {} when getting element (retry={}/{})".format(
                        str(e), num_retry, retry_timeout,
                    )
                )
                time.sleep(5 * num_retry)
                continue
            # done if found element
            if element and element.text and len(element.text) > 1:
                break
            else:
                logger.warning(
                    "failed get element={} text={} len(text)={} (retry={}/{})"
                    .format(
                        1 if element else 0,
                        1 if element and element.text else 0,
                        len(element.text) if element and element.text else 0,
                        num_retry, retry_timeout,
                    )
                )
                time.sleep(5 * num_retry)
                continue
        # output & return
        if element:
            if outfile:
                with openw(outfile, "wt") as fout:
                    fout.write(element.text)
            return element.text
        else:
            logger.error(f"{get_time_log()} failed to get element from {url}")
            raise sys.exc_info()[1]


if __name__ == "__main__":
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    # testing
    with ChromeDriver() as browser:
        url = "https://finance.yahoo.com/quote/AMD/options"
        eid = "Col1-1-OptionContracts-Proxy"
        outfile = os.path.join(
            metadata_dir, "data_amd_yahoo_option_chain.txt"
        )
        print(browser.download_data(
            url=url, element_id=eid, outfile=outfile
        ))
        url = "https://www.barchart.com/stocks/quotes/AMD/options"
        eclass = "filters"
        outfile = os.path.join(
            metadata_dir, "data_amd_barchart_option_date.txt"
        )
        print(browser.download_data(
            url=url, element_class=eclass, outfile=outfile
        ))
        url = ("https://www.barchart.com/stocks/quotes/AMD/options"
               "?moneyness=allRows&expiration=2020-01-17")
        eclass = "bc-futures-options-quotes-totals"
        outfile = os.path.join(
            metadata_dir, "data_amd_barchart_option_volume.txt"
        )
        print(browser.download_data(
            url=url, element_class=eclass, outfile=outfile)
        )