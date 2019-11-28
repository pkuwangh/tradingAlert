#!/usr/bin/env python

import sys
import sqlite3
import pandas as pd

def dump_tables(db_filename):
    db = sqlite3.connect(db_filename)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        print('================ %s ================' % table_name)
        print(table.to_string())
        input('...')
    cursor.close()
    db.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <sqlite3 DB filename>' % sys.argv[0])
        sys.exit(1)
    dump_tables(sys.argv[1])
