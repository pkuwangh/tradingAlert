#!/usr/bin/env python


black_list = [
    "AAPL",
    "AMD",
    "AMZN",
    "FB",
    "GOOG",
    "MSFT",
    "NFLX",
    "NVDA",
    "TSLA",
]

def is_in_black_list(symbol: str) -> bool:
    return (symbol in black_list)


def hash_symbol(symbol: str) -> int:
    return sum([ord(x) for x in symbol])