#!/usr/bin/env python

import gzip


def openw(filename, mode):
    if filename.endswith('gz'):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)
