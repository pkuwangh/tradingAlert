#!/usr/bin/env python

import logging
import os
import sqlite3
import sys

from data_option_activity import OptionActivity
from data_packet import DailyOptionInfo
from utils_datetime import get_time_log
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir
from utils_sql import sql_schema, sql_cols, sql_slots, sql_values
from web_chrome_driver import ChromeDriver
from web_option_volume import read_daily_option_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
            for sql_str in sqls:
                logger.info(f'{get_time_log()} SQL: {sql_str}')
                cursor.execute(sql_str)

    def write_table(self, table_name, data_pkt):
        with self.conn:
            cursor = self.conn.cursor()
            sql_str = 'INSERT INTO {}({}) VALUES({})'.format(
                table_name,
                sql_cols(data_pkt.fields.keys()),
                sql_slots(data_pkt.fields.keys())
            )
            values = sql_values(data_pkt)
            logger.info(f'{get_time_log()} SQL: {sql_str}')
            cursor.execute(sql_str, values)

    def read_table(self, table_name, keys):
        with self.conn:
            cursor = self.conn.cursor()
            sql_str = 'SELECT {} FROM {}'.format(
                sql_cols(keys), table_name
            )
            logger.info(f'{get_time_log()} SQL: {sql_str}')
            cursor.execute(sql_str)
            return cursor.fetchall()


if __name__ == '__main__':
    root_dir = get_root_dir()
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    db_file = os.path.join(root_dir, 'database.sqlite3')
    with DBMS(db_file) as db:
        with ChromeDriver() as browser:
            option_info = read_daily_option_info(browser, 'ASHR')
            db.write_table(DailyOptionInfo.name, option_info)
        x = db.read_table(DailyOptionInfo.name, DailyOptionInfo.fields.keys())
        print(x)