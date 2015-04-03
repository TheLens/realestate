# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import logging
import logging.handlers
from flask.ext.cache import Cache
from flask import (
    # Flask,
    render_template,
    jsonify,
    # request,
    # Response
)

from landrecords import config
from landrecords.lib.utils import Utils


def initialize_log(name):
    if os.path.isfile('%s/%s.log' % (config.LOG_DIR, name)):
        os.remove('%s/%s.log' % (config.LOG_DIR, name))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler('%s/%s.log' % (config.LOG_DIR, name))
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(funcName)s - '
        '%(levelname)s - %(lineno)d - %(message)s')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)

    return logger


class Views(object):

    def __init__(self):
        self.logger = initialize_log('views')

    def get_home(self, data):
        return render_template(
            'index.html',
            yesterday_date=data['yesterday_date'],
            js=config.JS,
            indexjs=config.INDEX_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            js_app_routing=config.JS_APP_ROUTING,
            css=config.CSS,
            neighborhoods=data['neighborhoods'],
            zip_codes=Utils().zip_codes
        )

    def get_search(self, data, newrows, jsdata, parameters):
        return render_template(
            'search.html',
            yesterday_date=data['yesterday_date'],
            js=config.JS,
            searchjs=config.SEARCH_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            mapjs=config.MAP_JS,
            css=config.CSS,
            js_app_routing=config.JS_APP_ROUTING,
            newrows=newrows,
            jsdata=jsdata,
            results_css_display=data['results_css_display'],
            results_language=data['results_language'],
            page=data['page'],
            totalpages=data['totalpages'],
            pagelength=data['pagelength'],
            parameters=parameters,
            neighborhoods=data['neighborhoods'],
            zip_codes=Utils().zip_codes
        )

    def post_search(self, data, newrows, jsdata):
        # For mapquery_db. May differ once add geoquery feature.

        tabletemplate = render_template(
            'table.html',
            newrows=newrows
        )

        return jsonify(
            tabletemplate=tabletemplate,
            yesterday_date=data['yesterday_date'],
            jsdata=jsdata,
            results_language=data['results_language'],
            results_css_display=data['results_css_display'],
            page=data['page'],
            totalpages=data['totalpages'],
            pagelength=data['pagelength']
        )

    def get_sale(self, data, jsdata, q):
        return render_template(
            'sale.html',
            yesterday_date=data['yesterday_date'],
            js=config.JS,
            salejs=config.SALE_JS,
            css=config.CSS,
            newrows=q,
            assessor=data['assessor'],
            jsdata=jsdata
        )







    def get_dashboard(self):
        return render_template(
            'search.html',
            yesterday_date=yesterday_date,
            js=config.JS,
            searchjs=config.SEARCH_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            mapjs=config.MAP_JS,
            css=config.CSS,
            js_app_routing=config.JS_APP_ROUTING,
            newrows=newrows,
            jsdata=jsdata,
            results_css_display=results_css_display,
            results_language=results_language,
            page=page,
            totalpages=totalpages,
            pagelength=PAGE_LENGTH,
            parameters=parameters,
            neighborhoods=neighborhoods,
            zip_codes=Utils().zip_codes
        )

    def post_dashboard(self):
        return render_template(
            'search.html',
            yesterday_date=yesterday_date,
            js=config.JS,
            searchjs=config.SEARCH_JS,
            searchAreajs=config.SEARCH_AREA_JS,
            mapjs=config.MAP_JS,
            css=config.CSS,
            js_app_routing=config.JS_APP_ROUTING,
            newrows=newrows,
            jsdata=jsdata,
            results_css_display=results_css_display,
            results_language=results_language,
            page=page,
            totalpages=totalpages,
            pagelength=PAGE_LENGTH,
            parameters=parameters,
            neighborhoods=neighborhoods,
            zip_codes=Utils().zip_codes
        )
