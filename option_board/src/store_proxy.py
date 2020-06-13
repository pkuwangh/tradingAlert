#!/usr/bin/env python

import logging
import os
from typing import List

from data_option_activity import OptionActivity
from data_option_effect import OptionEffect
from data_packet import LiveSymbol, DailyOptionInfo, AvgOptionInfo
from store_dbms import DBMS, execute_sql
from utils_datetime import get_date_str
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_sql import sql_cols

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_db_file()-> str:
    return os.path.join(get_root_dir(), 'database.sqlite3')


def add_to_symbol_table(db: DBMS, symbol: str):
    db.write_row(LiveSymbol.name, LiveSymbol(symbol), insert_unique=True)


def write_option_activity(db: DBMS, option_activity: OptionActivity):
    db.delete_row(
        OptionActivity.name, option_activity,
        ["symbol", "option_type", "strike_price", "exp_date", "deal_time"],
    )
    db.write_row(OptionActivity.name, option_activity)


def write_option_effect(db: DBMS, option_effect: OptionEffect):
    db.delete_row(
        OptionEffect.name, option_effect,
        ["symbol", "option_type", "strike_price", "exp_date", "date"],
    )
    db.write_row(OptionEffect.name, option_effect)


def write_daily_option_volume(db: DBMS, option_info: DailyOptionInfo):
    db.delete_row(
        DailyOptionInfo.name, option_info,
        ["symbol", "date"],
    )
    db.write_row(DailyOptionInfo.name, option_info)


def query_avg_option_info(db: DBMS, symbol: str)-> AvgOptionInfo:
    with db.get_conn() as conn:
        cursor = conn.cursor()
        fields = [
            f"{AvgOptionInfo.fields[x]}" for x in AvgOptionInfo.fields.keys()
        ]
        sql_str = "SELECT {} FROM {} WHERE {}='{}'".format(
            ", ".join(fields),
            DailyOptionInfo.name,
            'symbol', symbol,
        )
        raw_data = execute_sql(cursor, sql_str)[0]
        return AvgOptionInfo(raw_data)


def query_option_activity(db: DBMS, exp_date: int)-> List[OptionActivity]:
    with db.get_conn() as conn:
        cursor = conn.cursor()
        fields = list(OptionActivity.fields.keys())
        where_term = f"exp_date >= {exp_date}"
        sql_str = "SELECT {} FROM {} WHERE {}".format(
            ", ".join(fields),
            OptionActivity.name,
            where_term,
        )
        raw_data = execute_sql(cursor, sql_str)
        return [OptionActivity(x) for x in raw_data]


if __name__ == '__main__':
    root_dir = get_root_dir()
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('store_dbms').setLevel(logging.DEBUG)
    db_file = os.path.join(root_dir, 'database.sqlite3')
    with DBMS(db_file) as db:
        print(query_avg_option_info(db, 'ASHR'))
        print(query_avg_option_info(db, 'CO'))
        x = db.read_table(DailyOptionInfo.name, DailyOptionInfo.fields.keys())
        print(x.tail(4))
        for x in query_option_activity(db, get_date_str()):
            print(x.get_display_str())
        x = db.read_table(LiveSymbol.name, LiveSymbol.fields.keys())
        print(x.tail(4))
        print(list(x["symbol"])[0:4])