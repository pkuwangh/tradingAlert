#!/usr/bin/env python


class LiveSymbol:
    name = 'live_symbol'
    fields = {
        'symbol': 'TEXT PRIMARY KEY',
    }

    def __init__(self, symbol):
        self.__values = {}
        self.__values['symbol'] = symbol

    def get(self, key):
        return self.__values[key]


class DailyOptionInfo:
    name = 'daily_option_info'
    fields = {
        'symbol': 'TEXT',
        'date': 'INTEGER',
        'call_vol': 'INTEGER',
        'call_oi': 'INTEGER',
        'put_vol': 'INTEGER',
        'put_oi': 'INTEGER',
    }

    def __init__(self, symbol=None, date=None):
        self.__values = {}
        self.__values['symbol'] = symbol
        self.__values['date'] = date
        for k in DailyOptionInfo.fields:
            if k not in self.__values.keys():
                self.__values[k] = 0

    def set(self, key, value):
        self.__values[key] = value

    def inc(self, key, value):
        self.__values[key] += value

    def get(self, key):
        return self.__values[key]