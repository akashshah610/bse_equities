#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  settings.py
#
#  Created by Akash Shah on 25/06/19.
#
import os

from dotenv import load_dotenv

DEFAULT_DATE_STRING = "%d-%m-%Y"
BSE_FILE_DATE_FORMAT = "%d%m%y"
BSE_EQ_FILE_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{as_of_date}_CSV.ZIP"

REDIS_EQ_RECORD_KEY = "bse:{code}"
REDIS_EQ_NAME_MAP_KEY = "bse:{name}"
REDIS_ALL_EQ = "bse_all_eq"
REDIS_ALL_EQ_NAME = "bse_all_eq_name"

load_dotenv()
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
