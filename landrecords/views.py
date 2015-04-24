# -*- coding: utf-8 -*-

'''Renders the views.'''

from __future__ import absolute_import

# from flask.ext.cache import Cache
from flask import (
    render_template,
    jsonify,
    make_response
)

from landrecords.config import Config
from landrecords import log
from landrecords.lib.utils import Utils


class Views(object):

    '''Methods for each page in the app.'''

    def __init__(self):
        '''Commonly accessed static files.'''

        self.js = Config().JS
        self.index_js = Config().INDEX_JS
        self.search_js = Config().SEARCH_JS
        self.search_area_js = Config().SEARCH_AREA_JS
        self.sale_js = Config().SALE_JS
        self.map_js = Config().MAP_JS
        self.lens_css = Config().LENS_CSS
        self.landrecords_css = Config().LANDRECORDS_CSS
        self.banner_css = Config().BANNER_CSS
        self.table_css = Config().TABLE_CSS
        self.js_app_routing = Config().JS_APP_ROUTING
        self.zip_codes = Utils().zip_codes

        # self.home_assets = {
        #     'js': self.js,
        #     'css': self.css,
        #     'index_js': self.index_js,
        #     'search_area_js': self.search_area_js,
        #     'js_app_routing': self.js_app_routing,
        #     'zip_codes': self.zip_codes
        # }
        # self.search_assets = {
        #     'js': self.js,
        #     'search_js': self.search_js,
        #     'search_area_js': self.search_area_js,
        #     'map_js': self.map_js,
        #     'css': self.css,
        #     'js_app_routing': self.js_app_routing,
        #     'zip_codes': self.zip_codes
        # }
        # self.sale_assets = {
        #     'js': self.js,
        #     'css': self.css,
        #     'salejs': self.sale_js
        # }

    def get_home(self, data):
        '''Return view for /realestate/'''

        log.debug('get_home')

        response = make_response(
            render_template(
                'index.html',
                data=data,
                # home_assets=self.home_assets
                js=self.js,
                lens_css=self.lens_css,
                landrecords_css=self.landrecords_css,
                banner_css=self.banner_css,
                table_css=self.table_css,
                index_js=self.index_js,
                search_area_js=self.search_area_js,
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    def get_search(self, data, newrows, js_data):
        '''Return GET view for /realestate/search'''

        log.debug('get_search')

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
                lens_css=self.lens_css,
                landrecords_css=self.landrecords_css,
                banner_css=self.banner_css,
                table_css=self.table_css,
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    @staticmethod
    def post_search(data, newrows, js_data):
        '''Return updated views for /realestate/search'''

        log.debug('post_search')

        log.debug('returned newrows')
        log.debug(newrows)

        table_template = render_template(
            'table.html',
            newrows=newrows
        )

        log.debug('returned js_data:')
        log.debug(js_data)

        log.debug('returned data')
        log.debug(data)

        return jsonify(
            table_template=table_template,
            js_data=js_data,
            data=data
        )

    def get_sale(self, data, js_data, newrows):
        '''Return GET view for /realestate/sale'''

        log.debug('get_sale')

        response = make_response(
            render_template(
                'sale.html',
                data=data,
                newrows=newrows,
                js_data=js_data,
                # sale_assets=self.sale_assets
                js=self.js,
                lens_css=self.lens_css,
                landrecords_css=self.landrecords_css,
                banner_css=self.banner_css,
                table_css=self.table_css,
                sale_js=self.sale_js
            )
        )

        return response

    # todo
    def get_dashboard(self, data, newrows, js_data, parameters):
        '''Return GET view for /realestate/dashboard'''

        response = make_response(
            render_template(
                'dashboard.html',
                data=data,
                newrows=newrows,
                js_data=js_data,
                parameters=parameters,
                js=self.js,
                search_js=self.search_js,
                search_area_js=self.search_area_js,
                map_js=self.map_js,
                lens_css=self.lens_css,
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    # todo
    def post_dashboard(self, data, newrows, js_data, parameters):
        '''Return POST view for /realestate/dashboard'''

        response = make_response(
            render_template(
                'dashboard.html',
                data=data,
                newrows=newrows,
                js_data=js_data,
                parameters=parameters,
                js=self.js,
                search_js=self.search_js,
                search_area_js=self.search_area_js,
                map_js=self.map_js,
                lens_css=self.lens_css,  # todo
                js_app_routing=self.js_app_routing,
                zip_codes=self.zip_codes
            )
        )

        return response

    def get_error_page(self):
        '''Return 404 error page.'''

        response = make_response(
            render_template(
                '404.html',
                lens_css=self.lens_css,  # todo
                js=self.js,
                index_js=self.index_js
            )
        )

        return response, 404


if __name__ == '__main__':
    pass
