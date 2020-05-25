#!/usr/bin/env python

import argparse
import pandas as pd
import sqlite3
import sys


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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="DB reader",
    )
    parser.add_argument("-f", "--dbfile", required=True,
                        help="sqlite3 DB filename")

    args = parser.parse_args()
    dump_tables(args.dbfile)
