#!/usr/bin/env python

import logging
import os
from typing import List

from data_packet import DailyOptionInfo
from store_dbms import DBMS, execute_sql
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_sql import sql_cols

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def del_invalid_daily_option_info(db: DBMS):
    with db.get_conn() as conn:
        cursor = conn.cursor()
        # step 1, find invalid rows
        where_term = " AND ".join(
            [f"{x} = 0" for x in DailyOptionInfo.value_fields()])
        sql_str = "SELECT * FROM {} WHERE {}".format(
            DailyOptionInfo.name,
            where_term
        )
        if len(execute_sql(cursor, sql_str)) > 0:
            sql_str = "DELETE FROM {} WHERE {}".format(
                DailyOptionInfo.name,
                where_term
            )
            execute_sql(cursor, sql_str)


def deduplicate_daily_option_info(db: DBMS, symbol: str=''):
    with db.get_conn() as conn:
        cursor = conn.cursor()
        # step 1, find which symbol & date need de-duplicate
        keys = 'symbol, date'
        sql_str = "SELECT {}, COUNT(1) FROM {} {} GROUP BY {}".format(
            keys,
            DailyOptionInfo.name,
            f"WHERE symbol='{symbol}'" if symbol else "",
            keys,
        )
        duplicate_counts = execute_sql(cursor, sql_str)
        for (x_symbol, x_date, x_count) in duplicate_counts:
            if x_count > 1:
                # step 2, save the row we want to keep
                fields = list(DailyOptionInfo.fields.keys())
                sql_str = "SELECT {} FROM {} WHERE {} ORDER BY {} DESC LIMIT 1".format(
                    sql_cols(fields),
                    DailyOptionInfo.name,
                    f"symbol='{x_symbol}' AND date='{x_date}'",
                    "(call_vol+put_vol)",
                )
                backup_row = execute_sql(cursor, sql_str)
                backup_pkt = DailyOptionInfo(x_symbol, x_date)
                for idx in range(len(fields[0])):
                    backup_pkt.set(fields[idx], backup_row[0][idx])
                # step 3, remove all
                sql_str = "DELETE FROM {} WHERE {}".format(
                    DailyOptionInfo.name,
                    f"symbol='{x_symbol}' AND date='{x_date}'",
                )
                execute_sql(cursor, sql_str)
                # step 4, write the backup one back
                db.write_row(DailyOptionInfo.name, backup_pkt)


if __name__ == '__main__':
    root_dir = get_root_dir()
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('store_dbms').setLevel(logging.DEBUG)
    db_file = os.path.join(root_dir, 'database.sqlite3')
    with DBMS(db_file) as db:
        deduplicate_daily_option_info(db)
        del_invalid_daily_option_info(db)