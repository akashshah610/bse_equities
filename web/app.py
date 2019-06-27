#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  equity_view.py
#
#  Created by Akash Shah on 25/06/19.
#
import os
from datetime import datetime, timedelta

import cherrypy
import redis
from jinja2 import Template

from config import settings
from scripts.refresh_equity_price import process_equity_price


class EquityListView(object):
    @cherrypy.expose
    def index(self):
        """
        Returns equity home page.
        :return:
        """
        with open("web/templates/equity_list.html") as fp:
            template = Template(fp.read())
        return template.render()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def equity_list(self, start=1, length=10, **kwargs):
        """
        Equity list returns equity price data, default it returns 10 data, sorted by close price desc.
        :param start: starting cursor position
        :param length: how many data should be included in response
        :param kwargs:
        :return:
        """
        start = int(start)
        length = int(length)
        r = redis.from_url(settings.REDIS_URL)
        total_eq = r.scard(settings.REDIS_ALL_EQ)
        response = {"data": [], "recordsTotal": total_eq, "recordsFiltered": total_eq}
        name = kwargs.get("search[value]", None)
        if name:
            pattern = settings.REDIS_EQ_NAME_MAP_KEY.format(name=name.strip()).lower() + "*"
            matched_name_keys = r.keys(pattern)[:length]
            keys = []
            for key in matched_name_keys:
                keys += r.smembers(key)
            response["recordsFiltered"] = len(keys)
        else:
            keys = r.sort(settings.REDIS_ALL_EQ, by="*->close", start=start, num=length, desc=True)
        for key in keys:
            response["data"].append(r.hgetall(key))
        return response

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def equity_update(self, date=None, **kwargs):
        """
        Equity update API updates security price data. Default it will update price with yesterday's date.
        :param date: Date argument in DD-MM-YYYY format
        :param kwargs:
        :return:
        """
        try:
            as_of_date = datetime.strptime(date, settings.DEFAULT_DATE_STRING) if date else (
                    datetime.today() - timedelta(1))
        except ValueError:
            raise ValueError("Incorrect data format, should be {fmt}".format(fmt=settings.DEFAULT_DATE_STRING))
        process_equity_price(as_of_date)
        return {"success": True}


if __name__ == '__main__':
    config = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 8080)),
        }
    }

    cherrypy.quickstart(EquityListView(), "/", config=config)
