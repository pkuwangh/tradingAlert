#!/usr/bin/env python

import json
import logging
import multiprocessing as mp

from data_packet import DailyOptionQuote, DailyStockQuote
from data_option_activity import OptionActivity
from data_option_effect import OptionEffect
from store_dbms import DBMS
from store_proxy import (
    get_db_file,
    write_option_effect,
    query_option_activity,
)
from utils_datetime import get_time_log, get_date_str
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from web_chrome_driver import ChromeDriver
from web_option_volume import read_daily_option_quote
from web_stock_quote import read_stock_quote

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def track_effect(
    oa_queue: mp.Queue,
    effect_queue: mp.Queue,
):
    with ChromeDriver() as browser:
        while True:
            try:
                option_activity = oa_queue.get(block=True, timeout=600)
            except Exception as e:
                logger.warning(f"Unexpected expcetion on get: {str(e)}")
                break
            if option_activity is None:
                oa_queue.put(None, block=True, timeout=60)
                break 
            option_quote = read_daily_option_quote(
                browser,
                option_activity.get("symbol"),
                option_activity.get("option_type"),
                option_activity.get("strike_price"),
                option_activity.get("exp_date"),
                use_barchart=True,
                suppress_log=False,
            )
            stock_quote = read_stock_quote(
                browser, option_activity.get("symbol"), suppress_log=False,
            )
            option_effect = OptionEffect(
                daily_option_quote=option_quote, daily_stock_quote=stock_quote)
            effect_queue.put(option_effect, block=True, timeout=600)
        effect_queue.put(None, block=True, timeout=600)


def persist_effect(
    effect_queue: mp.Queue,
    num_workers: int,
):
    effect_list = []
    while num_workers > 0:
        try:
            option_effect = effect_queue.get(block=True, timeout=3600)
        except Exception as e:
            logger.warning(f"Unexpected exception on get: {str(e)}")
            break
        if option_effect is None:
            num_workers -= 1
            continue
        effect_list.append(option_effect)
    logger.info(f"Option effect retrieved today: {len(effect_list)}")
    _ = [print(json.dumps(effect.__dict__)) for effect in effect_list]
    with DBMS(get_db_file()) as db:
        _ = [write_option_effect(db, effect) for effect in effect_list]


def track_option_effect() -> None:
    logger.info("================================================")
    logger.info(f"{get_time_log()}  !!!")
    # synchronized queues
    oa_queue = mp.Queue(maxsize=1000)
    effect_queue = mp.Queue(maxsize=1000)
    num_workers = 1
    # get live option activity list
    with DBMS(get_db_file()) as db:
        option_activity_list = query_option_activity(db, get_date_str())
    # enqueue candidate
    for option_activity in option_activity_list:
        oa_queue.put(option_activity, block=True, timeout=600)
    oa_queue.put(None, block=True, timeout=600)
    track_effect(oa_queue, effect_queue) 
    persist_effect(effect_queue, num_workers)


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('store_dbms').setLevel(logging.DEBUG)
    track_option_effect()
