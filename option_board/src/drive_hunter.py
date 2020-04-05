#!/usr/bin/env python

import logging
import multiprocessing as mp
import os
import sys
import time

from data_option_activity import OptionActivity
from data_packet import DailyOptionInfo, AvgOptionInfo
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


def evaluate_option_activity(in_queue: mp.Queue, out_queue: mp.Queue):
    pname = mp.current_process().name
    num_items = 0
    logger.info(f"OA evaluation worker-{pname} starting")
    with ChromeDriver() as browser:
        while True:
            try:
                raw_data = in_queue.get(block=True, timeout=120)
            except Exception as e:
                logger.warning(f"Unexpected exception: {str(e)}")
                break
            if raw_data == None:
                time.sleep(1)
                in_queue.put(None)
                break
            num_items += 1
            symbol: str = raw_data[0]
            option_activity: OptionActivity = raw_data[1]
            avg_option_info: AvgOptionInfo = raw_data[2]
            if avg_option_info.get("count") == 0:
                # lookup daily option info
                daily_option_info = read_daily_option_info(browser, symbol)
                avg_option_info.set(
                    "avg_call_oi", daily_option_info.get("call_oi")
                )
                avg_option_info.set(
                    "avg_put_oi", daily_option_info.get("put_vol")
                )
            # filtering
            print(option_activity.get_display_str())
    logger.info(f"OA evaluation worker-{pname} processed {num_items} items")


def hunt(option_activity_file: str=None):
    logger.info('================================================')
    logger.info(f'{get_time_log()} Hunt or to be hunted !!!')
    # synchronized queues
    raw_oa_queue = mp.Queue(maxsize=1000)
    filtered_oa_queue = mp.Queue(maxsize=1000)
    # pull option activity list
    option_activity_list = []
    if option_activity_file is None:
        with ChromeDriver() as browser:
            option_activity_list = read_option_activity(
                browser,
                save_file=False, folder='records/raw_option_activity',
            )
    else:
        with openw(option_activity_file, "rt") as fp:
            option_activity_list = fp.readlines()
    # launch down-stream workers
    procs = [mp.Process(
        target=evaluate_option_activity,
        args=(raw_oa_queue, filtered_oa_queue),
        name=f"P{idx}",
    ) for idx in range(mp.cpu_count())]
    _ = [p.start() for p in procs]
    # scan UOA list and enqueue candidates
    with DBMS(get_db_file()) as db:
        for line in option_activity_list:
            option_activity = OptionActivity()
            option_activity.from_activity_str(line)
            # lookup volume info
            symbol = option_activity.get('symbol')
            avg_option_info = read_avg_option_info(db, symbol)
            if avg_option_info.get("count") == 0:
                # add to tracking list
                add_to_symbol_table(db, symbol)
            # add to queue for processing
            raw_oa_queue.put(
                [symbol, option_activity, avg_option_info], block=True,
            )
        raw_oa_queue.put(None)
    _ = [p.join() for p in procs]
    logger.info("Hunting done !!!")


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('web_chrome_driver').setLevel(logging.INFO)
    hunt(os.path.join(metadata_dir, "OA_200405_012638.txt.gz"))
