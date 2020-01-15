#!/usr/bin/env python

import logging
import os
import sqlite3
import sys

from store_dbms import DBMS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

