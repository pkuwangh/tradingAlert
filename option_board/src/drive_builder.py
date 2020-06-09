#!/usr/bin/env python

import json
import logging
import multiprocessing as mp

from data_packet import LiveSymbol, DailyOptionInfo
from store_dbms import DBMS
from store_proxy import (
    get_db_file,
    write_daily_option_volume,
)
from utils_datetime import get_time_log
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_symbol import is_in_black_list
from web_chrome_driver import ChromeDriver
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_info(
    symbol_queue: mp.Queue,
    info_queue: mp.Queue,
):
    pname = mp.current_process().name
    logger.info(f"History builder worker-{pname} starting")
    num_items = 0
    with ChromeDriver() as browser:
        while True:
            try:
                symbol = symbol_queue.get(block=True, timeout=600)
            except Exception as e:
                logger.warning(f"Unexpected expcetion: {str(e)}")
                break
            if symbol is None:
                symbol_queue.put(None, block=True, timeout=60)
                break
            num_items += 1
            daily_option_info = read_daily_option_info(
                browser, symbol,
                suppress_all_log=True, suppress_sub_log=True,
            )
            info_queue.put(daily_option_info)
    info_queue.put(None)
    logger.info(f"History builder worker-{pname} processed {num_items} items")


def persist_info(
    info_queue: mp.Queue,
    num_workers: int,
):
    pname = mp.current_process().name
    logger.info(f"Info writer-{pname} starting")
    info_list = []
    while num_workers > 0:
        try:
            daily_option_info = info_queue.get(block=True, timeout=3600)
        except Exception as e:
            logger.warning(f"Unexpected exception: {str(e)}")
            break
        if daily_option_info is None:
            num_workers -= 1
            continue
        info_list.append(daily_option_info)
    logger.info(f"Daily option info retrieved today: {len(info_list)}")
    #_ = [print(json.dumps(info.__dict__)) for info in info_list]
    with DBMS(get_db_file()) as db:
        _ = [write_daily_option_volume(db, info) for info in info_list]


def build_history(max_symbols: int=0)-> None:
    logger.info("================================================")
    logger.info(f"{get_time_log()} Let's build history !!!")
    # synchronized queues
    symbol_queue = mp.Queue(maxsize=100)
    info_queue = mp.Queue(maxsize=100)
    # launch down-stream workers
    num_workers = 4
    worker_procs = [mp.Process(
        target=read_info,
        args=(symbol_queue, info_queue,),
        name=f"ProcWorker{idx}",
    ) for idx in range(num_workers)]
    _ = [p.start() for p in worker_procs]
    # launch writer
    writer_proc = mp.Process(
        target=persist_info,
        args=(info_queue, num_workers,),
        name=f"ProcWriter",
    )
    writer_proc.start()
    # get live-symbol list
    with DBMS(get_db_file()) as db:
        live_symbols = db.read_table(LiveSymbol.name, LiveSymbol.fields.keys())
    # enqueue candidate
    num_symbols = max_symbols if max_symbols > 0 else len(live_symbols)
    for x in list(live_symbols["symbol"])[0:num_symbols]:
        if is_in_black_list(x):
            continue
        symbol_queue.put(x, block=True, timeout=1200)
    symbol_queue.put(None, block=True, timeout=1200)
    _ = [p.join() for p in worker_procs]
    writer_proc.join()
    logger.info(f"Option history builder done.")


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('store_dbms').setLevel(logging.DEBUG)
    build_history(max_symbols=4)
