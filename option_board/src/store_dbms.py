#!/usr/bin/env python

import logging
import os
import sqlite3
import sys

from data_option_activity import OptionActivity
from utils_datetime import get_time_log
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DBMS:
    def __init__(self, db_file):
        logger.info(f'Connecting {db_file}')
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def __enter__(self):
        logger.debug('DMBS entering')
        return self.conn

    def __exit__(self, *args):
        logger.debug('DBMS exiting')
        try:
            self.conn.close()
        except:
            logger.warning('error closing sqlite3 connection')

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            sql_str = 'CREATE TABLE IF NOT EXISTS option_activity ('
            for k, v in OptionActivity.fields.items():
                sql_str += '{} {}, '.format(k, v)
            sql_str = sql_str.rstrip().rstrip(',') + ')'
            logger.info(f'{get_time_log()} SQL: {sql_str}')
            cursor.execute(sql_str)


if __name__ == '__main__':
    root_dir = get_root_dir()
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.DEBUG)
    db_file = os.path.join(root_dir, 'database.sqlite3')
    with DBMS(db_file) as conn:
        pass