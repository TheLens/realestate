# -*- coding: utf-8 -*-

"""Get the data."""

import math
import urllib
# from flask.ext.cache import Cache

from flask import jsonify
from sqlalchemy import desc

from www.db import Cleaned, Neighborhood
from www.results_language import ResultsLanguage
from www.utils import get_num_with_curr_sign, ymd_to_full_date
from www import log, TODAY_DAY, SESSION


class Models(object):
    """Gather data from particular requests."""

    def __init__(self, initial_date=None, until_date=None):
        """
        Initialize self variables and establishes connection to database.

        :param initial_date: string. YYYY-MM-DD. Default is None.
        :type initial_date: string
        :param until_date: string. YYYY-MM-DD. Default is None.
        :type until_date: string
        """
        self.initial_date = initial_date
        self.until_date = until_date

    def get_home(self):
        """
        Get data for the homepage (/realestate/).

        :returns: Data for the homepage, such as date the app was last updated
        and a list of neighborhoods for the dropdown.
        """
        update_date = self.get_last_updated_date()
        log.info(update_date)

        neighborhoods = self.get_neighborhoods()

        data = {'update_date': update_date,
                'neighborhoods': neighborhoods}
        log.info(data)

        return data

    def query_search_term_limit_3(self, table, term):
        """
        Get the top three results for autocomplete dropdown.

        :param table: string. The database to query.
        :type table: string
        :param term: string. The autocomplete term entered in search box.
        :type term: string
        :returns: A SQLAlchemy query result for three matches, at most.
        """
        query = SESSION.query(
            getattr(Cleaned, table)
        ).filter(
            getattr(Cleaned, table).ilike('%%{}%%'.format(term))
        ).distinct().limit(3).all()

        SESSION.close()
        return query

    def searchbar_input(self, term):
        """
        Receive the autocomplete term from the search input.

        Return a JSON with three suggestions for each of the following
        categories: neighborhoods, ZIP codes, locations, buyers and
        sellers.

        :param term: string. The autocomplete term entered in search box.
        :type term: string
        :returns: A JSON with at most three suggestions for each
        category.
        """
        log.debug('searchbar_input')

        term = urllib.parse.unquote(term)  # .decode('utf8')

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

        log.debug(response)

        for row in query_zip:
            response.append({"label": row.zip_code, "category": "ZIP codes"})

        log.debug(response)

        for row in query_locations:
            response.append({"label": row.address, "category": "Addresses"})

        log.debug(response)

        for row in query_buyers:
            response.append({"label": row.buyers, "category": "Buyers"})

        log.debug(response)

        for row in query_sellers:
            response.append({"label": row.sellers, "category": "Sellers"})

        log.debug(response)

        return jsonify(response=response)

    @staticmethod
    def parse_query_string(request):
        """
        Receive URL query string parameters and returns as dict.

        :param request: A (Flask object?) containing query string.
        :returns: A dict with the query string parameters.
        """
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
        """
        Receive data dict and return with additional information about pager.

        Includes number of records, page length, number
        of pages, current page and page offset and URL query string
        parameters and returns as dict.

        :param data: The response's data dict.
        :type data: dict
        :returns: The dict with additional pager information.
        """
        query = self.find_all_publishable_rows_fitting_criteria(data)

        data['number_of_records'] = len(query)
        data['page_length'] = 10
        data['number_of_pages'] = int(math.ceil(
            float(data['number_of_records']) / float(data['page_length'])))
        data['current_page'] = 1
        data['page_offset'] = (data['current_page'] - 1) * data['page_length']

        return data

    def get_search(self, request):
        """
        GET call for /realestate/search.

        :param request: The request object(?).
        :returns: A data dict, SQL query result and JS data.
        """
        data = self.parse_query_string(request)
        data = self.decode_data(data)
        data = self.convert_entries_to_db_friendly(data)

        data['update_date'] = self.get_last_updated_date()
        data['neighborhoods'] = self.get_neighborhoods()

        data = self.determine_pages(data)

        query = self.find_page_of_publishable_rows_fitting_criteria(data)

        for row in query:
            row.amount = get_num_with_curr_sign(row.amount)
            row.document_date = ymd_to_full_date(
                (row.document_date).strftime('%Y-%m-%d'),
                no_day=True)

        features = self.build_features_json(query)

        jsdata = {
            "type": "FeatureCollection",
            "features": features}

        data['results_css_display'] = 'none'

        if data['number_of_records'] == 0:
            data['current_page'] = 0
            data['results_css_display'] = 'block'

        data = self.revert_entries(data)

        data['map_button_state'] = False

        data['results_language'] = ResultsLanguage(data).main()

        log.debug('data')

        return data, query, jsdata

    def post_search(self, data):
        """Process incoming POST data."""
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
        """TODO."""
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
        """Use map bounds to filter results."""
        query = self.map_query_length(data)
        data['number_of_records'] = len(query)  # number of records
        # total number of pages:
        data['number_of_pages'] = int(math.ceil(
            float(data['number_of_records']) / float(data['page_length'])))

        data = self.update_pager(data)

        query = self.query_with_map_boundaries(data)

        return query

    def do_not_filter_by_map(self, data):
        """TODO."""
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
        """TODO."""
        data['bounds'] = [
            data['bounds']['_northEast']['lat'],
            data['bounds']['_northEast']['lng'],
            data['bounds']['_southWest']['lat'],
            data['bounds']['_southWest']['lng']
        ]

        data['update_date'] = self.get_last_updated_date()

        log.debug('map_button_state')

        if data['map_button_state']:  # map filtering is on
            query = self.filter_by_map(data)  # TODO: was defined elsewhere
        else:  # map filtering is off
            query = self.do_not_filter_by_map(data)

        for row in query:
            row.amount = get_num_with_curr_sign(row.amount)
            row.document_date = ymd_to_full_date(
                (row.document_date).strftime('%Y-%m-%d'), no_day=True)

        features = self.build_features_json(query)

        jsdata = {
            "type": "FeatureCollection",
            "features": features}

        if data['number_of_records'] == 0:
            data['current_page'] = 0
            data['results_css_display'] = 'block'
        else:
            data['results_css_display'] = 'none'

        data = self.revert_entries(data)

        data['results_language'] = ResultsLanguage(data).main()

        log.debug('data returned:')
        log.debug(data)

        return data, query, jsdata

    def get_sale(self, instrument_no):
        """TODO."""
        data = {}
        data['update_date'] = self.get_last_updated_date()

        query = SESSION.query(
            Cleaned
        ).filter(
            Cleaned.instrument_no == '%s' % (instrument_no)
        ).filter(
            Cleaned.detail_publish.is_(True)  # Only publish trusted data
        ).all()

        for row in query:
            row.amount = get_num_with_curr_sign(row.amount)
            row.document_date = ymd_to_full_date(
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

        SESSION.close()

        if len(query) == 0:
            return None, None, None
        else:
            return data, jsdata, query

    def map_query_length(self, data):
        """TODO."""
        query = SESSION.query(
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

        SESSION.close()

        return query

    # For when map filtering is turned on
    def query_with_map_boundaries(self, data):
        """TODO."""
        query = SESSION.query(
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

        SESSION.close()

        return query

    def find_all_publishable_rows_fitting_criteria(self, data):
        """TODO."""
        # log.debug(data)

        query = SESSION.query(
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

        SESSION.close()

        return query

    def find_page_of_publishable_rows_fitting_criteria(self, data):
        """TODO."""
        # log.debug(data)

        query = SESSION.query(
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

        SESSION.close()

        return query

    @staticmethod
    def convert_entries_to_db_friendly(data):
        """Convert front-end format to database format."""
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
        """Convert database-friendly data back to front-end."""
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
        """TODO."""
        log.debug(len(query))
        features = []
        features_dict = {}
        for row in query:
            # log.debug(row.buyers)
            if not row.location_publish:
                row.document_date = row.document_date + "*"

            if not row.permanent_flag:
                row.document_date = row.document_date + u"\u2020"

            features_dict = {
                "type": "Feature",
                "properties": {
                    "document_date": row.document_date,
                    "address": row.address,
                    "location_info": row.location_info,
                    "amount": row.amount,
                    "buyers": row.buyers,
                    "sellers": row.sellers,
                    "instrument_no": row.instrument_no,
                    "location_publish": row.location_publish,
                    "permanent_flag": row.permanent_flag
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
        """TODO."""
        search_term = data['name_address']
        data['name_address'] = urllib.parse.unquote(search_term)
        # .decode('utf8')

        neighborhood = data['neighborhood']
        data['neighborhood'] = urllib.parse.unquote(neighborhood)
        # .decode('utf8')

        return data

    def get_last_updated_date(self):
        """TODO."""
        query = SESSION.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish.is_(True)
        ).order_by(
            desc(Cleaned.document_recorded)
        ).limit(1).all()

        log.info(query)

        updated_date = ''

        for row in query:
            updated_date = ymd_to_full_date(
                (row.document_recorded).strftime('%Y-%m-%d'), no_day=True)

        log.info(updated_date)

        SESSION.close()

        return updated_date

    def get_neighborhoods(self):
        """TODO."""
        query = SESSION.query(Neighborhood.gnocdc_lab).all()

        neighborhoods = []

        for neighborhood in query:
            neighborhoods.append(
                (neighborhood.gnocdc_lab).title().replace('Mcd', 'McD'))

        neighborhoods.sort()

        SESSION.close()

        return neighborhoods
