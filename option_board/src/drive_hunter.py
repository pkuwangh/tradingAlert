#!/usr/bin/env python

import logging
import sys
from multiprocessing import Queue

from data_option_activity import OptionActivity
from data_packet import DailyOptionInfo
from store_proxy import read_avg_option_volume
from store_proxy import write_daily_option_volume, write_option_activity
from utils_datetime import get_time_log
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from web_chrome_driver import ChromeDriver
from web_option_activity import read_option_activity
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def hunt():
    logger.info('================================================')
    logger.info('{] Hunt or to be hunted !!!')
    # pull option activity list
    with ChromeDriver() as browser:
        option_activity_list = read_option_activity(
            browser, save_file=False, folder='records/raw_option_activity'
        )
        for line in option_activity_list:
            symbol = line.split()[0]
            # lookup volume info
            # track list
            print(symbol)


if __name__ == '__main__':
    hunt()