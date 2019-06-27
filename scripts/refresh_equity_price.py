#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  equity_price.py
#
#  Created by Akash Shah on 25/06/19.
#
import csv
import io
import zipfile
from StringIO import StringIO
from datetime import datetime
from os import sys

import redis
import requests
from box import BoxList
from requests import status_codes

from config import settings


def nfloat(n):
    return float(n) if n is not None else None


def download_zipfile(url):
    response = requests.get(url)
    assert response.status_code == status_codes.codes.OK, \
        "Couldn't download file. URL - {}, Response status code - {}".format(url, response.status_code)
    zip = zipfile.ZipFile(io.BytesIO(response.content))
    return zip


def get_equity_data(as_of_date):
    """
    Retrieves equity price data from BSE server and return List object.
    :param as_of_date:
    :return:
    """
    data = []
    url = settings.BSE_EQ_FILE_URL.format(as_of_date=as_of_date.strftime(settings.BSE_FILE_DATE_FORMAT))
    zip = download_zipfile(url)
    file_list = zip.filelist
    assert len(file_list) == 1, "zip file must have 1 file, got {}".format(len(file_list))
    csvfile = StringIO(zip.read(file_list[0]))
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)
    csvfile.close()
    return BoxList(data)


def update_equity_data(data):
    """

    :param data:
    :return:
    """
    r = redis.from_url(settings.REDIS_URL)
    for row in data:
        record_key = settings.REDIS_EQ_RECORD_KEY.format(code=row.SC_CODE)
        record = dict(sc_code=row.SC_CODE, sc_name=row.SC_NAME.strip(), high=nfloat(row.HIGH),
                      low=nfloat(row.LOW), close=nfloat(row.CLOSE))
        r.hmset(record_key, record)
        # for search using name, added name mapping
        r.sadd(settings.REDIS_EQ_NAME_MAP_KEY.format(name=record['sc_name']).lower(), record_key)
        # For sorting added in all equity items key
        r.sadd(settings.REDIS_ALL_EQ, record_key)
        r.sadd(settings.REDIS_ALL_EQ_NAME, record_key)


def process_equity_price(as_of_date):
    """
    Function download BSE equity price file and updates equity price data in redis server
    :param as_of_date: Date, process price data for specific date
    :return:
    """
    data = get_equity_data(as_of_date)
    update_equity_data(data)


def main(args):
    try:
        as_of_date = datetime.strptime(args[0], settings.DEFAULT_DATE_STRING) if args else datetime.today()
    except ValueError:
        raise ValueError("Incorrect data format, should be {fmt}".format(fmt=settings.DEFAULT_DATE_STRING))

    process_equity_price(as_of_date)


if __name__ == "__main__":
    main(sys.argv[1:])
