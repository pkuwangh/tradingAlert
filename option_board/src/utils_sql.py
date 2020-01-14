#!/usr/bin/env python


def sql_schema(fields):
    decorated_fileds = [f'{k} {v}' for k, v in fields.items()]
    return ', '.join(decorated_fileds)


def sql_cols(keys):
    return ', '.join(keys)


def sql_slots(keys):
    return ', '.join(['?' for x in keys])


def sql_values(data_pkt):
    return [data_pkt.get(k) for k in data_pkt.fields]