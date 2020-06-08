#!/usr/bin/env python


class BaseDataPacket:
    def __init__(self):
        self._values = {}

    def __str__(self):
        return "({})".format(
            ", ".join([f"{k}: {v}" for k, v in self._values.items()])
        )

    def get(self, key):
        return self._values[key]

    def set(self, key, value):
        self._values[key] = value

    def inc(self, key, value):
        self._values[key] += value


class LiveSymbol(BaseDataPacket):
    name = "live_symbol"
    fields = {
        "symbol": "TEXT PRIMARY KEY",
    }

    def __init__(self, symbol):
        BaseDataPacket.__init__(self)
        self._values["symbol"] = symbol


class DailyStockQuote(BaseDataPacket):
    name = "daily_stock_quote"
    fields = {
        "symbol": "TEXT",
        "date": "INTEGER",
        "market_cap": "REAL",
        "price_high": "REAL",
        "price_low": "REAL",
        "volume": "INTEGER",
        "avg_volume": "INTEGER",
    }

    def __init__(self, symbol=None, date=None):
        BaseDataPacket.__init__(self)
        self._values["symbol"] = symbol
        self._values["date"] = date
        for k in DailyStockQuote.fields:
            if k not in self._values.keys():
                self._values[k] = 0


class DailyOptionQuote(BaseDataPacket):
    name = "daily_option_quote"
    fields = {
        "symbol": "TEXT",
        "option_type": "TEXT",
        "strike_price": "REAL",
        "exp_date": "INTEGER",
        "date": "INTEGER",
        "option_interest": "INTEGER",
        "option_price": "REAL",
        "contract_volume": "INTEGER",
    }

    def __init__(
        self, symbol=None, option_type=None, strike_price=None, exp_date=None,
        date=None,
    ):
        BaseDataPacket.__init__(self)
        self._values["symbol"] = symbol
        self._values["option_type"] = option_type
        self._values["strike_price"] = strike_price
        self._values["exp_date"] = exp_date
        self._values["date"] = date
        for k in DailyOptionQuote.fields:
            if k not in self._values.keys():
                self._values[k] = 0


class DailyOptionInfo(BaseDataPacket):
    name = "daily_option_info"
    fields = {
        "symbol": "TEXT",
        "date": "INTEGER",
        "call_vol": "INTEGER",
        "call_oi": "INTEGER",
        "put_vol": "INTEGER",
        "put_oi": "INTEGER",
    }

    def __init__(self, symbol=None, date=None):
        BaseDataPacket.__init__(self)
        self._values["symbol"] = symbol
        self._values["date"] = date
        for k in DailyOptionInfo.fields:
            if k not in self._values.keys():
                self._values[k] = 0


class AvgOptionInfo(BaseDataPacket):
    name = "AvgOptionInfo"
    fields = {
        "avg_call_vol": "AVG(call_vol)",
        "avg_put_vol": "AVG(put_vol)",
        "avg_call_oi": "AVG(call_oi)",
        "avg_put_oi": "AVG(put_oi)",
        "count": "COUNT(1)",
    }

    def __init__(self, values):
        BaseDataPacket.__init__(self)
        for idx, key in enumerate(AvgOptionInfo.fields.keys()):
            v = values[idx]
            self.set(
                key,
                int(v) if type(v) is float else v,
            )

    def get_avg_vol(self):
        return self.get("avg_call_vol") + self.get("avg_put_vol")

    def get_avg_oi(self):
        return self.get("avg_call_oi") + self.get("avg_put_oi")