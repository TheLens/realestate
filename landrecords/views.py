# -*- coding: utf-8 -*-

from __future__ import absolute_import

# from flask.ext.cache import Cache
from flask import (
    render_template,
    jsonify,
)

from landrecords import config
from landrecords.lib.log import Log
from landrecords.lib.utils import Utils


class Views(object):

    def __init__(self):
        self.log = Log('views').logger

    def get_home(self, data):
        return render_template(
            'index.html',
            data=data,
            js=config.JS,
            indexjs=config.INDEX_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            js_app_routing=config.JS_APP_ROUTING,
            css=config.CSS,
            zip_codes=Utils().zip_codes
        )

    def get_search(self, data, newrows, jsdata):
        return render_template(
            'search.html',
            data=data,
            newrows=newrows,
            jsdata=jsdata,
            js=config.JS,
            searchjs=config.SEARCH_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            mapjs=config.MAP_JS,
            css=config.CSS,
            js_app_routing=config.JS_APP_ROUTING,
            zip_codes=Utils().zip_codes
        )

    def post_search(self, data, newrows, jsdata):
        tabletemplate = render_template(
            'table.html',
            newrows=newrows
        )

        return jsonify(
            tabletemplate=tabletemplate,
            jsdata=jsdata,
            data=data
        )

    def get_sale(self, data, jsdata, newrows):
        return render_template(
            'sale.html',
            data=data,
            newrows=newrows,
            jsdata=jsdata,
            js=config.JS,
            salejs=config.SALE_JS,
            css=config.CSS
        )

    # def get_dashboard(self, data, newrows, jsdata, parameters):
    #     return render_template(
    #         'search.html',
    #         data=data,
    #         newrows=newrows,
    #         jsdata=jsdata,
    #         parameters=parameters,
    #         js=config.JS,
    #         searchjs=config.SEARCH_JS,
    #         searchAreajs=config.SEARCH_AREA_JS,
    #         mapjs=config.MAP_JS,
    #         css=config.CSS,
    #         js_app_routing=config.JS_APP_ROUTING,
    #         zip_codes=Utils().zip_codes
    #     )

    # def post_dashboard(self, data, newrows, jsdata, parameters):
    #     return render_template(
    #         'search.html',
    #         data=data,
    #         newrows=newrows,
    #         jsdata=jsdata,
    #         parameters=parameters,
    #         js=config.JS,
    #         searchjs=config.SEARCH_JS,
    #         searchAreajs=config.SEARCH_AREA_JS,
    #         mapjs=config.MAP_JS,
    #         css=config.CSS,
    #         js_app_routing=config.JS_APP_ROUTING,
    #         zip_codes=Utils().zip_codes
    #     )
