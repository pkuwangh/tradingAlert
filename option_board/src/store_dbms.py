#!/usr/bin/env python

import logging
import os
import pandas
import sqlite3
import sys

from data_option_activity import OptionActivity
from data_packet import LiveSymbol, DailyOptionInfo
from utils_datetime import get_time_log
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_sql import sql_schema, sql_cols, sql_slots, sql_values
from web_chrome_driver import ChromeDriver
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def execute_sql(cursor, sql_str, values=None):
    logger.debug(f'{get_time_log()} SQL: {sql_str}')
    if values:
        cursor.execute(sql_str, values)
    else:
        cursor.execute(sql_str)
    if sql_str.lstrip().startswith("SELECT"):
        return cursor.fetchall()
    else:
        return None


class DBMS:
    def __init__(self, db_file):
        logger.info(f'Connecting {db_file}')
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def __enter__(self):
        logger.debug('DMBS entering')
        return self

    def __exit__(self, *args):
        logger.debug('DBMS exiting')
        try:
            self.conn.close()
        except:
            logger.warning('error closing sqlite3 connection')

    def get_conn(self):
        return self.conn

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            base_sql = 'CREATE TABLE IF NOT EXISTS'
            sqls = []
            sqls.append('{} {} ({})'.format(
                base_sql, OptionActivity.name, sql_schema(OptionActivity.fields)
            ))
            sqls.append('{} {} ({})'.format(
                base_sql, DailyOptionInfo.name, sql_schema(DailyOptionInfo.fields)
            ))
            sqls.append('{} {} ({})'.format(
                base_sql, LiveSymbol.name, sql_schema(LiveSymbol.fields)
            ))
            sqls.append('{} {} ({})'.format(
                base_sql, DailyOptionInfo.name, sql_schema(DailyOptionInfo.fields)
            ))
            for sql_str in sqls:
                execute_sql(cursor, sql_str)

    def write_row(self, table_name, data_pkt, insert_unique=False):
        with self.conn:
            cursor = self.conn.cursor()
            sql_str = 'INSERT {} INTO {}({}) VALUES({})'.format(
                'OR IGNORE' if insert_unique else '',
                table_name,
                sql_cols(data_pkt.fields.keys()),
                sql_slots(data_pkt.fields.keys()),
            )
            values = sql_values(data_pkt)
            execute_sql(cursor, sql_str, values)

    def read_table(self, table_name, keys)-> pandas.DataFrame:
        with self.conn:
            cursor = self.conn.cursor()
            sql_str = 'SELECT {} FROM {}'.format(
                sql_cols(keys), table_name,
            )
            raw_data = execute_sql(cursor, sql_str)
            return pandas.DataFrame(
                raw_data,
                columns=keys,
            )


if __name__ == '__main__':
    root_dir = get_root_dir()
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    db_file = os.path.join(root_dir, 'database.sqlite3')
    with DBMS(db_file) as db:
        with ChromeDriver() as browser:
            option_info = read_daily_option_info(browser, 'ASHR')
            db.write_row(DailyOptionInfo.name, option_info)
        x = db.read_table(DailyOptionInfo.name, DailyOptionInfo.fields.keys())
        print(x)