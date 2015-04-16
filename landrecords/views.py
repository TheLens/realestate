# -*- coding: utf-8 -*-

from __future__ import absolute_import

# from flask.ext.cache import Cache
from flask import (
    render_template,
    jsonify,
    make_response
)

from landrecords.config import Config
from landrecords.lib.log import Log
from landrecords.lib.utils import Utils

log = Log('views').logger


class Views(object):

    def __init__(self):
        self.js = Config().JS
        self.index_js = Config().INDEX_JS
        self.search_js = Config().SEARCH_JS
        self.search_area_js = Config().SEARCH_AREA_JS
        self.sale_js = Config().SALE_JS
        self.map_js = Config().MAP_JS
        self.css = Config().CSS
        self.js_app_routing = Config().JS_APP_ROUTING
        self.zip_codes = Utils().zip_codes

        self.home_assets = {
            'js': self.js,
            'css': self.css,
            'index_js': self.index_js,
            'search_area_js': self.search_area_js,
            'js_app_routing': self.js_app_routing,
            'zip_codes': self.zip_codes
        }
        self.search_assets = {
            'js': self.js,
            'search_js': self.search_js,
            'search_area_js': self.search_area_js,
            'map_js': self.map_js,
            'css': self.css,
            'js_app_routing': self.js_app_routing,
            'zip_codes': self.zip_codes
        }
        self.sale_assets = {
            'js': self.js,
            'css': self.css,
            'salejs': self.sale_js
        }

    def get_home(self, data):
        '''Return view for /realestate/'''

        response = make_response(
            render_template(
                'index.html',
                data=data,
                # home_assets=self.home_assets
                js=self.js,
                css=self.css,
                index_js=self.index_js,
                search_area_js=self.search_area_js,
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    def get_search(self, data, newrows, js_data):
        '''Return GET view for /realestate/search'''

        response = make_response(
            render_template(
                'search.html',
                data=data,
                newrows=newrows,
                js_data=js_data,
                # search_assets=self.search_assets
                js=self.js,
                search_js=self.search_js,
                search_area_js=self.search_area_js,
                map_js=self.map_js,
                css=self.css,
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    def post_search(self, data, newrows, js_data):
        table_template = render_template(
            'table.html',
            newrows=newrows
        )

        return jsonify(
            table_template=table_template,
            js_data=js_data,
            data=data
        )

    def get_sale(self, data, js_data, newrows):
        '''Return GET view for /realestate/sale'''

        response = make_response(
            render_template(
                'sale.html',
                data=data,
                newrows=newrows,
                js_data=js_data,
                # sale_assets=self.sale_assets
                js=self.js,
                css=self.css,
                sale_js=self.sale_js
            )
        )

        return response

    # def get_dashboard(self, data, newrows, js_data, parameters):
    #     '''Return GET view for /realestate/dashboard'''

    #     response = make_response(
    #         render_template(
    #             'search.html',
    #             data=data,
    #             newrows=newrows,
    #             js_data=js_data,
    #             parameters=parameters,
    #             js=Config().JS,
    #             searchjs=Config().SEARCH_JS,
    #             searchAreajs=Config().SEARCH_AREA_JS,
    #             mapjs=Config().MAP_JS,
    #             css=Config().CSS,
    #             js_app_routing=Config().JS_APP_ROUTING,
    #             zip_codes=Utils().zip_codes
    #         )
    #     )

    #     return response

    # def post_dashboard(self, data, newrows, js_data, parameters):
    #     '''Return POST view for /realestate/dashboard'''

    #     response = make_response(
    #         render_template(
    #             'search.html',
    #             data=data,
    #             newrows=newrows,
    #             js_data=js_data,
    #             parameters=parameters,
    #             js=Config().JS,
    #             searchjs=Config().SEARCH_JS,
    #             searchAreajs=Config().SEARCH_AREA_JS,
    #             mapjs=Config().MAP_JS,
    #             css=Config().CSS,
    #             js_app_routing=Config().JS_APP_ROUTING,
    #             zip_codes=Utils().zip_codes
    #         )
    #     )

    #     return response
