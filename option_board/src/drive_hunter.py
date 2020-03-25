#!/usr/bin/env python

import logging
import os
import sys
from multiprocessing import Queue

from data_option_activity import OptionActivity
from data_packet import DailyOptionInfo
from store_dbms import DBMS
from store_proxy import (
    get_db_file,
    add_to_symbol_table,
    write_daily_option_volume, write_option_activity, read_avg_option_info,
)
from utils_datetime import get_time_log
from utils_file import openw
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from web_chrome_driver import ChromeDriver
from web_option_activity import read_option_activity
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def hunt(option_activity_file: str=None):
    logger.info('================================================')
    logger.info(f'{get_time_log()} Hunt or to be hunted !!!')
    # pull option activity list
    option_activity_list = []
    if option_activity_file is None:
        with ChromeDriver() as browser:
            option_activity_list = read_option_activity(
                browser, save_file=False, folder='records/raw_option_activity'
            )
    else:
        with openw(option_activity_file, "rt") as fp:
            option_activity_list = fp.readlines()
    with DBMS(get_db_file()) as db:
        for line in option_activity_list:
            option_activity = OptionActivity()
            option_activity.from_activity_str(line)
            # lookup volume info
            symbol = option_activity.get('symbol')
            avg_option_info = read_avg_option_info(db, symbol)
            if avg_option_info.count > 0:
                # take it
                pass
            else:
                # add to tracking list
                add_to_symbol_table(db, symbol)
            break


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('web_chrome_driver').setLevel(logging.DEBUG)
    hunt(os.path.join(metadata_dir, "OA_200324_235751.txt.gz"))