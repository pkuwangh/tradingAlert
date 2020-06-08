#!/usr/bin/env python

import logging
import multiprocessing as mp
import os
import typing

from data_option_activity import OptionActivity
from data_packet import DailyOptionInfo, AvgOptionInfo
from store_dbms import DBMS
from store_proxy import (
    get_db_file,
    add_to_symbol_table,
    write_option_activity,
    query_avg_option_info,
)
from utils_datetime import get_time_log
from utils_file import openw
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_symbol import is_in_black_list, hash_symbol
from web_chrome_driver import ChromeDriver
from web_option_activity import read_option_activity
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def filter(
    new_option_activity: OptionActivity,
    avg_option_info: AvgOptionInfo,
    browser: ChromeDriver,
    cache: typing.Mapping[str, DailyOptionInfo],
):
    symbol = new_option_activity.get("symbol")
    if is_in_black_list(symbol):
        return False
    # parameters
    thd_vol_oi = 1
    thd_tot_cost = 200
    thd_ext_value = 100
    thd_d2e_min = 2
    thd_d2e_max = 91
    thd_otm = 20
    thd_vol_spike = 4
    thd_oi_spike = 0.15
    # stage 1: simple filtering
    if new_option_activity.get_contract_vol_oi() < thd_vol_oi:
        return False
    if new_option_activity.get('total_cost') < thd_tot_cost:
        return False
    if new_option_activity.get('extrinsic_value') < thd_ext_value:
        return False
    if new_option_activity.get('day_to_exp') < thd_d2e_min:
        return False
    if new_option_activity.get('day_to_exp') > thd_d2e_max:
        return False
    if new_option_activity.get_otm() > thd_otm:
        return False
    # use daily option info if no history found
    if avg_option_info.get("count") == 0:
        if symbol not in cache:
            cache[symbol] = read_daily_option_info(
                browser, symbol,
                suppress_all_log=True, suppress_sub_log=True,
            )
        daily_option_info = cache[symbol]
        avg_option_info.set("avg_call_oi", daily_option_info.get("call_oi"))
        avg_option_info.set("avg_put_oi", daily_option_info.get("put_oi"))
        avg_option_info.set("avg_call_vol", avg_option_info.get("avg_call_oi"))
        avg_option_info.set("avg_put_vol", avg_option_info.get("avg_put_oi"))
        if avg_option_info.get_avg_oi() == 0:
            logger.warning(f"DailyOptionInfo for {symbol} returns all 0s")
            return False
    # volume spike ?
    if avg_option_info.get("count") > 5:
        if (new_option_activity.get("contract_vol")
            < avg_option_info.get_avg_vol() * thd_vol_spike):
            return False
    else:
        if (new_option_activity.get("contract_vol")
            < avg_option_info.get_avg_oi() * thd_oi_spike):
            return False
    # got a candidate
    new_option_activity.set_option_info(
        avg_option_info.get_avg_vol(), avg_option_info.get_avg_oi())
    logger.info(f"candidate: {new_option_activity.get_display_str()}")
    return filter_detail(new_option_activity, avg_option_info)


def filter_detail(
    new_option_activity: OptionActivity,
    avg_option_info: AvgOptionInfo,
):
    # it should be extreme in some aspect(s)
    # volume on the contract
    mid_vol_oi = (new_option_activity.get_contract_vol_oi() > 10)
    high_vol_oi = (new_option_activity.get_contract_vol_oi() > 20)
    # volume spike
    if avg_option_info.get("count") > 5:
        ratio = new_option_activity.get_contract_vol_avg_vol()
        mid_volume_spike = (ratio > 4)
        high_volume_spike = (ratio > 8)
    else:
        ratio = new_option_activity.get_contract_vol_avg_tot_oi()
        mid_volume_spike = (ratio > 0.40)
        high_volume_spike = (ratio > 0.80)
    # reference price
    ntm = (new_option_activity.get_otm() < 8)
    atm = (new_option_activity.get_otm() < 3)
    # 1. very high volume spike
    big_volume = ((high_volume_spike) and (high_vol_oi or ntm))
    # 2. typical straightforward pattern
    typical_pattern = ((atm) and (mid_vol_oi) and (mid_volume_spike))
    # final round
    return (big_volume or typical_pattern)


def evaluate_option_activity(
    in_queue: mp.Queue,
    out_queue: mp.Queue,
    cache_queue: mp.Queue,
):
    pname = mp.current_process().name
    logger.info(f"OA evaluation worker-{pname} starting")
    cache = {}
    num_items = 0
    with ChromeDriver() as browser:
        while True:
            try:
                raw_data = in_queue.get(block=True, timeout=600)
            except Exception as e:
                logger.warning(f"Unexpected exception: {str(e)}")
                break
            if raw_data is None:
                break
            num_items += 1
            option_activity: OptionActivity = raw_data[0]
            avg_option_info: AvgOptionInfo = raw_data[1]
            # filtering
            if filter(option_activity, avg_option_info, browser, cache):
                out_queue.put(option_activity)
    out_queue.put(None)
    cache_queue.put(cache)
    logger.info(f"OA evaluation worker-{pname} processed {num_items} items")


def process_unusual_option_activity(
    in_queue: mp.Queue,
    cache_queue: mp.Queue,
    num_workers: int,
    db: DBMS,
) -> typing.Mapping[str, DailyOptionInfo]:
    oa_list = []
    while num_workers > 0:
        try:
            raw_data = in_queue.get(block=True, timeout=3600)
        except Exception as e:
            logger.warning(f"Unexpected exception: {str(e)}")
            break
        if raw_data is None:
            num_workers -= 1
            continue
        oa_list.append(raw_data)
    # persist
    _ = [write_option_activity(db, oa) for oa in oa_list]
    logger.info(f"Option activity captured today:")
    for oa in oa_list:
        logger.info(f"\t{oa.get_display_str()}")
    # return the cache
    aggregated_cache = {}
    while True:
        try:
            cache = cache_queue.get(block=False)
        except:
            break
        else:
            for symbol in cache:
                aggregated_cache[symbol] = cache[symbol]
    return aggregated_cache


def hunt_option_activity(
    max_oa: int=0,
    option_activity_file: str=None,
) -> typing.Mapping[str, DailyOptionInfo]:
    logger.info("================================================")
    logger.info(f"{get_time_log()} Hunt or to be hunted !!!")
    # synchronized queues
    raw_oa_queues = [mp.Queue(maxsize=1000) for _ in range(mp.cpu_count())]
    filtered_oa_queue = mp.Queue(maxsize=1000)
    info_cache_queue = mp.Queue(maxsize=100)
    # pull option activity list
    option_activity_list = []
    if option_activity_file is None:
        with ChromeDriver() as browser:
            option_activity_list = read_option_activity(
                browser,
                save_file=False, folder="records/raw_option_activity",
            )
    else:
        with openw(option_activity_file, "rt") as fp:
            option_activity_list = fp.readlines()
    if max_oa > 0 and max_oa < len(option_activity_list):
        option_activity_list = option_activity_list[0 : max_oa]
    # launch down-stream workers
    worker_procs = [mp.Process(
        target=evaluate_option_activity,
        args=(raw_oa_queues[idx], filtered_oa_queue, info_cache_queue,),
        name=f"ProcWorker{idx}",
    ) for idx in range(len(raw_oa_queues))]
    _ = [p.start() for p in worker_procs]
    # scan UOA list and enqueue candidates
    with DBMS(get_db_file()) as db:
        for line in option_activity_list:
            option_activity = OptionActivity()
            option_activity.from_activity_str(line)
            # lookup volume info
            symbol = option_activity.get('symbol')
            avg_option_info = query_avg_option_info(db, symbol)
            if avg_option_info.get("count") == 0:
                # add to tracking list
                add_to_symbol_table(db, symbol)
            # add to queue for processing
            worker_idx = hash_symbol(symbol) % len(raw_oa_queues)
            raw_oa_queues[worker_idx].put(
                [option_activity, avg_option_info], block=True,
            )
        _ = [x.put(None) for x in raw_oa_queues]
        _ = [p.join() for p in worker_procs]
        logger.info("Hunting done !!!")
        return process_unusual_option_activity(
            filtered_oa_queue, info_cache_queue, len(raw_oa_queues), db)
    return {}


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    #logging.getLogger('store_dbms').setLevel(logging.DEBUG)
    #hunt_option_activity(os.path.join(metadata_dir, "OA_200405_012638.txt.gz"))
    cache = hunt_option_activity(max_oa=4)
    print(len(cache))
