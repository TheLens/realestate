# -*- coding: utf-8 -*-

'''Gets the data.'''

import os
import math
import urllib
# from flask.ext.cache import Cache
from flask import (
    # request,
    jsonify
)
from sqlalchemy import (
    create_engine,
    desc
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from realestate.db import (
    Cleaned,
    Neighborhood
)
# from realestate.lib.check_assessor_urls import Assessor
from realestate.lib.results_language import ResultsLanguage
from realestate.lib.utils import Utils
from realestate import log, TODAY_DAY


class Models(object):

    '''Gathers data from particular requests.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        log.debug('1')

        self.initial_date = initial_date
        log.debug('2')

        self.until_date = until_date
        log.debug('3')

        base = declarative_base()
        log.debug('4')

        en = os.environ.get('REAL_ESTATE_SERVER_ENGINE')
        log.debug(en)

        try:
            engine = create_engine(en)
            log.debug(engine)
        except Exception, error:
            log.debug(error, exc_info=True)

        base.metadata.create_all(engine)
        log.debug('6')

        self.sn = sessionmaker(bind=engine)
        log.debug('7')

    def get_home(self):
        '''Gets data for the homepage (/).'''

        log.debug('get_home')

        session = self.sn()

        log.debug(session)

        update_date = self.get_last_updated_date()
        log.debug(update_date)

        neighborhoods = self.get_neighborhoods()
        log.debug(neighborhoods)

        data = {'update_date': update_date,
                'neighborhoods': neighborhoods}

        log.debug(data)

        session.close()
        log.debug('session.close()')

        return data

    def query_search_term_limit_3(self, table, term):
        '''Gets the top three results for autocomplete dropdown.'''

        session = self.sn()

        query = session.query(
            getattr(Cleaned, table)
        ).filter(
            getattr(Cleaned, table).ilike('%%%s%%' % term)
        ).distinct().limit(3).all()

        session.close()
        return query

    def searchbar_input(self, term):
        '''docstring'''

        term = urllib.unquote(term).decode('utf8')

        query_neighborhoods = self.query_search_term_limit_3(
            'neighborhood', term)
        query_zip = self.query_search_term_limit_3('zip_code', term)
        query_locations = self.query_search_term_limit_3('address', term)
        query_buyers = self.query_search_term_limit_3('buyers', term)
        query_sellers = self.query_search_term_limit_3('sellers', term)

        response = []

        for row in query_neighborhoods:
            response.append({
                "label": (row.neighborhood).title().replace('Mcd', 'McD'),
                "category": "Neighborhoods"})

        for row in query_zip:
            response.append({"label": row.zip_code, "category": "ZIP codes"})

        for row in query_locations:
            response.append({"label": row.address, "category": "Addresses"})

        for row in query_buyers:
            response.append({"label": row.buyers, "category": "Buyers"})

        for row in query_sellers:
            response.append({"label": row.sellers, "category": "Sellers"})

        return jsonify(
            response=response
        )

    @staticmethod
    def parse_query_string(request):
        '''Parses URL query string parameters.'''

        data = {}
        data['name_address'] = request.args.get('q')
        data['amount_low'] = request.args.get('a1')
        data['amount_high'] = request.args.get('a2')
        data['begin_date'] = request.args.get('d1')
        data['end_date'] = request.args.get('d2')
        data['neighborhood'] = request.args.get('nbhd')
        data['zip_code'] = request.args.get('zip')

        # Change any missing parameters to 0-length string
        for key in data:
            if data[key] is None:
                data[key] = ''

        return data

    def determine_pages(self, data):
        '''docstring'''

        query = self.find_all_publishable_rows_fitting_criteria(data)

        data['number_of_records'] = len(query)
        data['page_length'] = 10
        data['number_of_pages'] = int(math.ceil(
            float(data['number_of_records']) / float(data['page_length'])))
        data['current_page'] = 1
        data['page_offset'] = (data['current_page'] - 1) * data['page_length']

        return data

    def get_search(self, request):
        '''GET call to /realestate/search.'''

        data = self.parse_query_string(request)
        data = self.decode_data(data)
        data = self.convert_entries_to_db_friendly(data)

        data['update_date'] = self.get_last_updated_date()
        data['neighborhoods'] = self.get_neighborhoods()

        data = self.determine_pages(data)

        query = self.find_page_of_publishable_rows_fitting_criteria(data)

        for row in query:
            row.amount = Utils().get_num_with_curr_sign(row.amount)
            row.document_date = Utils().ymd_to_full_date(
                (row.document_date).strftime('%Y-%m-%d'), no_day=True)

        features = self.build_features_json(query)

        # newrows = query  # todo: remove?

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        data['results_css_display'] = 'none'

        if data['number_of_records'] == 0:
            data['current_page'] = 0
            data['results_css_display'] = 'block'

        data = self.revert_entries(data)

        data['map_button_state'] = False

        data['results_language'] = ResultsLanguage(data).main()

        log.debug('data')
        # log.debug(data)

        return data, query, jsdata

    def post_search(self, data):
        '''Process incoming POST data.'''

        log.debug('post_search')

        data = self.decode_data(data)
        data = self.convert_entries_to_db_friendly(data)

        log.debug(data)

        # If a geo query (search near me). Not yet a feature.
        # if 'latitude' in data and 'longitude' in data:
        #     response = self.geoquery_db(data)
        # else:
        response = self.mapquery_db(data)

        return response

    @staticmethod
    def update_pager(data):
        '''docstring'''

        cond = (data['direction'] == 'back' or
                data['direction'] == 'forward')

        if data['direction'] is None:
            data['current_page'] = 1
            data['page_offset'] = (
                (data['current_page'] - 1) * data['page_length'])
        elif cond:
            if data['direction'] == 'forward':
                data['current_page'] = int(data['current_page']) + 1

            if data['number_of_records'] == 0:
                data['current_page'] = 0

            if data['current_page'] == 0:
                data['page_offset'] = 0
            else:
                if data['direction'] == 'back':
                    data['current_page'] = int(data['current_page']) - 1
                data['page_offset'] = (
                    (data['current_page'] - 1) * data['page_length'])
                data['page_length'] = data['page_length']

        return data

    def filter_by_map(self, data):
        '''docstring'''

        query = self.map_query_length(data)
        data['number_of_records'] = len(query)  # number of records
        # total number of pages:
        data['number_of_pages'] = int(math.ceil(
            float(data['number_of_records']) / float(data['page_length'])))

        data = self.update_pager(data)

        query = self.query_with_map_boundaries(data)

        return query

    def do_not_filter_by_map(self, data):
        '''docstring'''

        query = self.find_all_publishable_rows_fitting_criteria(data)
        # data['page_length'] = self.PAGE_LENGTH
        data['number_of_records'] = len(query)  # number of records
        # total number of pages:
        data['number_of_pages'] = int(math.ceil(
            float(data['number_of_records']) / float(data['page_length'])))

        data = self.update_pager(data)

        query = self.find_page_of_publishable_rows_fitting_criteria(data)

        log.debug(query)

        return query

    def mapquery_db(self, data):
        '''docstring'''

        data['bounds'] = [
            data['bounds']['_northEast']['lat'],
            data['bounds']['_northEast']['lng'],
            data['bounds']['_southWest']['lat'],
            data['bounds']['_southWest']['lng']
        ]

        data['update_date'] = self.get_last_updated_date()

        log.debug('map_button_state')

        if data['map_button_state'] is True:  # map filtering is on
            query = self.filter_by_map(data)  # todo: was defined elsewhere

        if data['map_button_state'] is False:  # map filtering is off
            query = self.do_not_filter_by_map(data)

        for row in query:
            row.amount = Utils().get_num_with_curr_sign(row.amount)
            row.document_date = Utils().ymd_to_full_date(
                (row.document_date).strftime('%Y-%m-%d'), no_day=True)

        features = self.build_features_json(query)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        if data['number_of_records'] == 0:
            data['current_page'] = 0
            data['results_css_display'] = 'block'
        else:
            data['results_css_display'] = 'none'

        data = self.revert_entries(data)

        data['results_language'] = ResultsLanguage(data).main()

        log.debug('data returned:')
        log.debug(data)

        # newrows = q
        # todo: remove?
        # Or necessary because it might change when the session is closed

        return data, query, jsdata

    def get_sale(self, instrument_no):
        '''docstring'''

        session = self.sn()

        data = {}
        data['update_date'] = self.get_last_updated_date()

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.instrument_no == '%s' % (instrument_no)
        ).filter(
            Cleaned.detail_publish.is_(True)  # Only publish trusted data
        ).all()

        for row in query:
            row.amount = Utils().get_num_with_curr_sign(row.amount)
            row.document_date = Utils().ymd_to_full_date(
                (row.document_date).strftime('%Y-%m-%d'), no_day=True)
            # address = row.address
            # location_info = row.location_info
            data['assessor_publish'] = row.assessor_publish

        # newrows = query

        features = self.build_features_json(query)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        # conds = (data['assessor_publish'] is False or
        #          data['assessor_publish'] is None or
        #          data['assessor_publish'] == '')

        # if conds:
        #     data['assessor'] = (
        #         "Could not find this property on the Orleans Parish" +
        #         "Assessor's Office site. <a href='http://www.qpublic" +
        #         ".net/la/orleans/search1.html' target='_blank'>" +
        #         "Search based on other criteria.</a>")
        # else:
        #     url_param = Assessor().form_assessor_url(
        #         address, location_info)
        #     data['assessor_url'] = "http://qpublic9.qpublic.net/" + \
        #         "la_orleans_display" + \
        #         ".php?KEY=%s" % (url_param)
        #     data['assessor'] = "<a href='%s' target='_blank'>Read more " + \
        #         "about this property on the Assessor's Office's" + \
        #         "website.</a>" % (data['assessor_url'])

        if len(query) == 0:
            session.close()
            return None, None, None
        else:
            session.close()
            return data, jsdata, query

    def map_query_length(self, data):
        '''docstring'''

        session = self.sn()

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            Cleaned.document_date >= '%s' % data['begin_date']
        ).filter(
            Cleaned.document_date <= '%s' % data['end_date']
        ).filter(
            Cleaned.amount >= '%s' % data['amount_low']
        ).filter(
            Cleaned.amount <= '%s' % data['amount_high']
        ).filter(
            (Cleaned.latitude <= data['bounds'][0]) &
            (Cleaned.latitude >= data['bounds'][2]) &
            (Cleaned.longitude <= data['bounds'][1]) &
            (Cleaned.longitude >= data['bounds'][3])
        ).all()

        session.close()

        return query

    # For when map filtering is turned on
    def query_with_map_boundaries(self, data):
        '''docstring'''

        session = self.sn()

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            Cleaned.document_date >= '%s' % data['begin_date']
        ).filter(
            Cleaned.document_date <= '%s' % data['end_date']
        ).filter(
            Cleaned.amount >= '%s' % data['amount_low']
        ).filter(
            Cleaned.amount <= '%s' % data['amount_high']
        ).filter(
            (Cleaned.latitude <= data['bounds'][0]) &
            (Cleaned.latitude >= data['bounds'][2]) &
            (Cleaned.longitude <= data['bounds'][1]) &
            (Cleaned.longitude >= data['bounds'][3])
        ).order_by(
            desc(Cleaned.document_date)
        ).offset(
            '%d' % data['page_offset']
        ).limit(
            '%d' % data['page_length']
        ).all()

        session.close()

        return query

    def find_all_publishable_rows_fitting_criteria(self, data):
        '''docstring'''

        session = self.sn()

        # log.debug(data)

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            Cleaned.document_date >= '%s' % data['begin_date']
        ).filter(
            Cleaned.document_date <= '%s' % data['end_date']
        ).filter(
            Cleaned.amount >= '%s' % data['amount_low']
        ).filter(
            Cleaned.amount <= '%s' % data['amount_high']
        ).all()

        # log.debug(query)

        session.close()

        return query

    def find_page_of_publishable_rows_fitting_criteria(self, data):
        '''docstring'''

        session = self.sn()

        # log.debug(data)

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            Cleaned.document_date >= '%s' % data['begin_date']
        ).filter(
            Cleaned.document_date <= '%s' % data['end_date']
        ).filter(
            Cleaned.amount >= '%s' % data['amount_low']
        ).filter(
            Cleaned.amount <= '%s' % data['amount_high']
        ).order_by(
            desc(Cleaned.document_date)
        ).offset(
            '%d' % int(data['page_offset'])  # convert unicode to int
        ).limit(
            '%d' % int(data['page_length'])
        ).all()

        # log.debug(query)

        session.close()

        return query

    @staticmethod
    def convert_entries_to_db_friendly(data):
        '''docstring'''

        if data['amount_low'] == '':
            data['amount_low'] = 0
        if data['amount_high'] == '':
            data['amount_high'] = 9999999999999
        if data['begin_date'] == '':
            data['begin_date'] = "1900-01-01"
        if data['end_date'] == '':
            data['end_date'] = TODAY_DAY

        return data

    @staticmethod
    def revert_entries(data):
        '''docstring'''

        if data['amount_low'] == 0:
            data['amount_low'] = ''
        if data['amount_high'] == 9999999999999:
            data['amount_high'] = ''
        if data['begin_date'] == '1900-01-01':
            data['begin_date'] = ''
        if data['end_date'] == TODAY_DAY:
            data['end_date'] = ''

        return data

    @staticmethod
    def build_features_json(query):
        '''docstring'''

        log.debug(len(query))
        features = []
        features_dict = {}
        for row in query:
            # log.debug(row.buyers)
            if row.location_publish is False:
                row.document_date = row.document_date + "*"
                continue
            if row.permanent_flag is False:
                row.document_date = row.document_date + u"\u2020"
                # continue
            features_dict = {
                "type": "Feature",
                "properties": {
                    "document_date": row.document_date,
                    "address": row.address,
                    "location_info": row.location_info,
                    "amount": row.amount,
                    "buyers": row.buyers,
                    "sellers": row.sellers,
                    "instrument_no": row.instrument_no
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row.longitude, row.latitude]
                }
            }
            features.append(features_dict)

        return features

    @staticmethod
    def decode_data(data):
        '''docstring'''

        search_term = data['name_address']
        data['name_address'] = urllib.unquote(search_term).decode('utf8')

        neighborhood = data['neighborhood']
        data['neighborhood'] = urllib.unquote(neighborhood).decode('utf8')

        return data

    def get_last_updated_date(self):
        '''docstring'''

        session = self.sn()

        query = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).order_by(
            desc(Cleaned.document_recorded)
        ).limit(1).all()

        updated_date = ''

        for row in query:
            updated_date = Utils().ymd_to_full_date(
                (row.document_recorded).strftime('%Y-%m-%d'), no_day=True)

        session.close()

        return updated_date

    def get_neighborhoods(self):
        '''docstring'''

        session = self.sn()

        query = session.query(Neighborhood.gnocdc_lab).all()

        neighborhoods = []

        for hood in query:
            neighborhoods.append(
                (hood.gnocdc_lab).title().replace('Mcd', 'McD'))

        neighborhoods.sort()

        session.close()

        return neighborhoods


if __name__ == '__main__':
    pass
