#!/usr/bin/env python

import sys
import sqlite3
import pandas as pd


def dump_tables(db_filename):
    conn = sqlite3.connect(db_filename)
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
            print('================ {} ================'.format(table_name))
            print(table.to_string())
            input('...')
        cursor.close()
    conn.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: {} <sqlite3 DB filename>'.format(sys.argv[0]))
        sys.exit(1)
    dump_tables(sys.argv[1])