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
    LENS_JS,
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

        # self.home_assets = {
        #     'js': LENS_JS,
        #     'css': LENS_CSS,
        #     'index_js': INDEX_JS,
        #     'search_area_js': SEARCH_AREA_JS,
        #     'js_app_routing': JS_APP_ROUTING,
        #     'zip_codes': Utils().zip_codes
        # }
        # self.search_assets = {
        #     'js': LENS_JS,
        #     'search_js': SEARCH_JS,
        #     'search_area_js': SEARCH_AREA_JS,
        #     'map_js': MAP_JS,
        #     'css': LENS_CSS,
        #     'js_app_routing': JS_APP_ROUTING,
        #     'zip_codes': Utils().zip_codes
        # }
        # self.sale_assets = {
        #     'js': LENS_JS,
        #     'css': LENS_CSS,
        #     'salejs': SALE_JS
        # }

    def get_home(self, data):
        '''Return view for /realestate/'''

        log.debug('get_home')

        response = make_response(
            render_template(
                'index.html',
                data=data,
                # home_assets=self.home_assets
                lens_js=LENS_JS,
                lens_css=LENS_CSS,
                realestate_css=REALESTATE_CSS,
                banner_css=BANNER_CSS,
                table_css=TABLE_CSS,
                index_js=INDEX_JS,
                search_area_js=SEARCH_AREA_JS,
                js_app_routing=JS_APP_ROUTING,
                zip_codes=Utils().zip_codes
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
                lens_js=LENS_JS,
                search_js=SEARCH_JS,
                search_area_js=SEARCH_AREA_JS,
                map_js=MAP_JS,
                lens_css=LENS_CSS,
                realestate_css=REALESTATE_CSS,
                banner_css=BANNER_CSS,
                table_css=TABLE_CSS,
                js_app_routing=JS_APP_ROUTING,
                zip_codes=Utils().zip_codes
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
                lens_js=LENS_JS,
                lens_css=LENS_CSS,
                realestate_css=REALESTATE_CSS,
                banner_css=BANNER_CSS,
                table_css=TABLE_CSS,
                sale_js=SALE_JS
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
                lens_js=LENS_JS,
                search_js=SEARCH_JS,
                search_area_js=SEARCH_AREA_JS,
                map_js=MAP_JS,
                lens_css=LENS_CSS,
                js_app_routing=JS_APP_ROUTING,
                zip_codes=Utils().zip_codes
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
                lens_js=LENS_JS,
                search_js=SEARCH_JS,
                search_area_js=SEARCH_AREA_JS,
                map_js=MAP_JS,
                lens_css=LENS_CSS,  # todo
                js_app_routing=JS_APP_ROUTING,
                zip_codes=Utils().zip_codes
            )
        )

        return response

    def get_error_page(self):
        '''Return 404 error page.'''

        response = make_response(
            render_template(
                '404.html',
                lens_css=LENS_CSS,  # todo
                lens_js=LENS_JS,
                index_js=INDEX_JS
            )
        )

        return response, 404


if __name__ == '__main__':
    pass
