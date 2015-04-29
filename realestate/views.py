# -*- coding: utf-8 -*-

'''Renders the views.'''

# from flask.ext.cache import Cache
from flask import (
    render_template,
    jsonify,
    make_response
)
from realestate.lib.utils import Utils
from realestate import (
    log,
    JS,
    INDEX_JS,
    SEARCH_JS,
    SEARCH_AREA_JS,
    SALE_JS,
    MAP_JS,
    LENS_CSS,
    REALESTATE_CSS,
    TABLE_CSS,
    BANNER_CSS,
    JS_APP_ROUTING
)


class Views(object):

    '''Methods for each page in the app.'''

    def __init__(self):
        '''Commonly accessed static files.'''

        self.js = JS
        self.index_js = INDEX_JS
        self.search_js = SEARCH_JS
        self.search_area_js = SEARCH_AREA_JS
        self.sale_js = SALE_JS
        self.map_js = MAP_JS
        self.lens_css = LENS_CSS
        self.realestate_css = REALESTATE_CSS
        self.banner_css = BANNER_CSS
        self.table_css = TABLE_CSS
        self.js_app_routing = JS_APP_ROUTING
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
                realestate_css=self.realestate_css,
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
                realestate_css=self.realestate_css,
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
                realestate_css=self.realestate_css,
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
