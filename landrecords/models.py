# -*- coding: utf-8 -*-

from __future__ import absolute_import

import math
import urllib
from datetime import datetime

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

from landrecords import config, db
from landrecords.lib import check_assessor_urls
from landrecords.lib.log import Log
from landrecords.lib.utils import Utils


class Models(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('models').logger

        self.initial_date = initial_date
        self.until_date = until_date

        self.PAGE_LENGTH = 10  # todo: determine this via front end.
        # May want to let users change in future. Also just for consistency.

        base = declarative_base()
        engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    def get_home(self):
        session = self.sn()

        update_date = self.get_last_updated_date()
        neighborhoods = self.get_neighborhoods()

        data = {'update_date': update_date,
                'neighborhoods': neighborhoods}

        session.close()
        return data

    def query_search_term_limit_3(self, table, term):
        session = self.sn()

        q = session.query(
            getattr(db.Cleaned, table)
        ).filter(
            getattr(db.Cleaned, table).ilike('%%%s%%' % term)
        ).distinct().limit(3).all()

        session.close()
        return q

    def searchbar_input(self, term):
        term = urllib.unquote(term).decode('utf8')

        q_neighborhoods = self.query_search_term_limit_3('neighborhood', term)
        q_zip = self.query_search_term_limit_3('zip_code', term)
        q_locations = self.query_search_term_limit_3('address', term)
        q_buyers = self.query_search_term_limit_3('buyers', term)
        q_sellers = self.query_search_term_limit_3('sellers', term)

        response = []

        for i, u in enumerate(q_neighborhoods):
            response.append({
                "label": (u.neighborhood).title().replace('Mcd', 'McD'),
                "category": "Neighborhoods"})

        for i, u in enumerate(q_zip):
            response.append({"label": u.zip_code, "category": "ZIP codes"})

        for i, u in enumerate(q_locations):
            response.append({"label": u.address, "category": "Addresses"})

        for i, u in enumerate(q_buyers):
            response.append({"label": u.buyers, "category": "Buyers"})

        for i, u in enumerate(q_sellers):
            response.append({"label": u.sellers, "category": "Sellers"})

        return jsonify(
            response=response
        )

    def get_search(self, request):
        data = {}
        data['name_address'] = request.args.get('q')
        data['amountlow'] = request.args.get('a1')
        data['amounthigh'] = request.args.get('a2')
        data['begindate'] = request.args.get('d1')
        data['enddate'] = request.args.get('d2')
        data['neighborhood'] = request.args.get('nbhd')
        data['zip_code'] = request.args.get('zip')

        # Change any missing parameters to 0-length string
        for key in data:
            if data[key] is None:
                data[key] = ''

        data = self.decode_data(data)
        data = self.convert_entries_to_db_friendly(data)

        data['update_date'] = self.get_last_updated_date()
        data['neighborhoods'] = self.get_neighborhoods()

        q = self.find_all_publishable_rows_fitting_criteria(data)

        data['qlength'] = len(q)  # number of records
        data['pagelength'] = self.PAGE_LENGTH
        # total number of pages:
        data['totalpages'] = int(math.ceil(float(data['qlength']) / float(
            data['pagelength'])))
        data['page'] = 1  # start on first page
        # Page 1 offsets 0:
        data['recordsoffset'] = (data['page'] - 1) * data['pagelength']

        q = self.find_page_of_publishable_rows_fitting_criteria(data)

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(
                (u.document_date).strftime('%Y-%m-%d'), no_day=True)

        features = self.build_features_json(q)

        newrows = q  # todo: remove?

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        data['results_css_display'] = 'none'

        if data['qlength'] == 0:
            data['page'] = 0
            data['results_css_display'] = 'block'

        data = self.revert_entries(data)

        data['mapbuttonstate'] = False

        data['results_language'] = self.construct_results_language(data)

        return data, newrows, jsdata

    def post_search(self, data):
        data = self.decode_data(data)
        data = self.convert_entries_to_db_friendly(data)

        # If a geo query (search near me). Not yet a feature.
        # if 'latitude' in data and 'longitude' in data:
        #     response = self.geoquery_db(data)
        # else:
        response = self.mapquery_db(data)

        return response

    def update_pager(self, data):
        cond = (data['direction'] == 'back' or
                data['direction'] == 'forward')

        if data['direction'] is None:
            data['page'] = 1
            data['recordsoffset'] = (data['page'] - 1) * data['pagelength']
        elif cond:
            if data['direction'] == 'forward':
                data['page'] = int(data['page']) + 1

            if data['qlength'] == 0:
                data['page'] = 0

            if data['page'] == 0:
                data['recordsoffset'] = 0
            else:
                if data['direction'] == 'back':
                    data['page'] = int(data['page']) - 1
                data['recordsoffset'] = (
                    (data['page'] - 1) * data['pagelength'])
                data['pagelength'] = data['pagelength']

        return data

    def filter_by_map(self, data):
        q = self.map_query_length(data)
        data['qlength'] = len(q)  # number of records
        # total number of pages:
        data['totalpages'] = int(math.ceil(
            float(data['qlength']) / float(data['pagelength'])))

        data = self.update_pager(data)

        q = self.query_with_map_boundaries(data)

        return q

    def do_not_filter_by_map(self, data):
        q = self.find_all_publishable_rows_fitting_criteria(data)
        data['pagelength'] = self.PAGE_LENGTH
        data['qlength'] = len(q)  # number of records
        # total number of pages:
        data['totalpages'] = int(math.ceil(
            float(data['qlength']) / float(data['pagelength'])))

        data = self.update_pager(data)

        q = self.find_page_of_publishable_rows_fitting_criteria(data)

        return q

    def mapquery_db(self, data):
        data['bounds'] = [
            data['bounds']['_northEast']['lat'],
            data['bounds']['_northEast']['lng'],
            data['bounds']['_southWest']['lat'],
            data['bounds']['_southWest']['lng']
        ]

        data['update_date'] = self.get_last_updated_date()

        if data['mapbuttonstate'] is True:  # map filtering is on
            q = self.filter_by_map(data)

        if data['mapbuttonstate'] is False:  # map filtering is off
            q = self.do_not_filter_by_map(data)

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(
                (u.document_date).strftime('%Y-%m-%d'), no_day=True)

        features = self.build_features_json(q)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        if data['qlength'] == 0:
            data['page'] = 0
            data['results_css_display'] = 'block'
        else:
            data['results_css_display'] = 'none'

        data = self.revert_entries(data)

        data['results_language'] = self.construct_results_language(data)

        newrows = q
        # todo: remove?
        # Or necessary because it might change when the session is closed

        return data, newrows, jsdata

    def get_sale(self, instrument_no):
        session = self.sn()

        data = {}
        data['update_date'] = self.get_last_updated_date()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.instrument_no == '%s' % (instrument_no)
        ).all()

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(
                (u.document_date).strftime('%Y-%m-%d'), no_day=True)
            address = u.address
            location_info = u.location_info
            data['assessor_publish'] = u.assessor_publish

        newrows = q

        features = self.build_features_json(q)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        conds = (data['assessor_publish'] == '0' or
                 data['assessor_publish'] is None or
                 data['assessor_publish'] == '')

        if conds:
            data['assessor'] = (
                "Could not find this property on the Orleans Parish" +
                "Assessor's Office site. <a href='http://www.qpublic" +
                ".net/la/orleans/search1.html' target='_blank'>" +
                "Search based on other criteria.</a>")
        else:
            url_param = check_assessor_urls().form_assessor_url(
                address, location_info)
            data['assessor_url'] = "http://qpublic9.qpublic.net/" + \
                "la_orleans_display" + \
                ".php?KEY=%s" % (url_param)
            data['assessor'] = "<a href='%s' target='_blank'>Read more " + \
                "about this property on the Assessor's Office's" + \
                "website.</a>" % (data['assessor_url'])

        if len(q) == 0:
            session.close()
            return None, None, None
        else:
            self.session.close()
            return data, jsdata, newrows

    def map_query_length(self, data):
        session = self.sn()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            (db.Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            db.Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            db.Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            db.Cleaned.document_date >= '%s' % data['begindate']
        ).filter(
            db.Cleaned.document_date <= '%s' % data['enddate']
        ).filter(
            db.Cleaned.amount >= '%s' % data['amountlow']
        ).filter(
            db.Cleaned.amount <= '%s' % data['amounthigh']
        ).filter(
            (db.Cleaned.latitude <= data['bounds'][0]) &
            (db.Cleaned.latitude >= data['bounds'][2]) &
            (db.Cleaned.longitude <= data['bounds'][1]) &
            (db.Cleaned.longitude >= data['bounds'][3])
        ).all()

        session.close()

        return q

    # For when map filtering is turned on
    def query_with_map_boundaries(self, data):
        session = self.sn()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            (db.Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            db.Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            db.Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            db.Cleaned.document_date >= '%s' % data['begindate']
        ).filter(
            db.Cleaned.document_date <= '%s' % data['enddate']
        ).filter(
            db.Cleaned.amount >= '%s' % data['amountlow']
        ).filter(
            db.Cleaned.amount <= '%s' % data['amounthigh']
        ).filter(
            (db.Cleaned.latitude <= data['bounds'][0]) &
            (db.Cleaned.latitude >= data['bounds'][2]) &
            (db.Cleaned.longitude <= data['bounds'][1]) &
            (db.Cleaned.longitude >= data['bounds'][3])
        ).order_by(
            desc(db.Cleaned.document_date)
        ).offset(
            '%d' % data['recordsoffset']
        ).limit(
            '%d' % data['pagelength']
        ).all()

        session.close()

        return q

    def find_all_publishable_rows_fitting_criteria(self, data):
        session = self.sn()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            (db.Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            db.Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            db.Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            db.Cleaned.document_date >= '%s' % data['begindate']
        ).filter(
            db.Cleaned.document_date <= '%s' % data['enddate']
        ).filter(
            db.Cleaned.amount >= '%s' % data['amountlow']
        ).filter(
            db.Cleaned.amount <= '%s' % data['amounthigh']
        ).all()

        session.close()

        return q

    def find_page_of_publishable_rows_fitting_criteria(self, data):
        session = self.sn()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            (db.Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
            (db.Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
        ).filter(
            db.Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
        ).filter(
            db.Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
        ).filter(
            db.Cleaned.document_date >= '%s' % data['begindate']
        ).filter(
            db.Cleaned.document_date <= '%s' % data['enddate']
        ).filter(
            db.Cleaned.amount >= '%s' % data['amountlow']
        ).filter(
            db.Cleaned.amount <= '%s' % data['amounthigh']
        ).order_by(
            desc(db.Cleaned.document_date)
        ).offset(
            '%d' % data['recordsoffset']
        ).limit(
            '%d' % data['pagelength']
        ).all()

        session.close()

        return q

    def convert_entries_to_db_friendly(self, data):
        if data['amountlow'] == '':
            data['amountlow'] = 0
        if data['amounthigh'] == '':
            data['amounthigh'] = 9999999999999
        if data['begindate'] == '':
            data['begindate'] = "1900-01-01"
        if data['enddate'] == '':
            data['enddate'] = (datetime.today()).strftime('%Y-%m-%d')

        return data

    def revert_entries(self, data):
        if data['amountlow'] == 0:
            data['amountlow'] = ''
        if data['amounthigh'] == 9999999999999:
            data['amounthigh'] = ''
        if data['begindate'] == '1900-01-01':
            data['begindate'] = ''
        if data['enddate'] == (datetime.today()).strftime('%Y-%m-%d'):
            data['enddate'] = ''

        return data

    def build_features_json(self, q):
        self.log.debug(len(q))
        features = []
        features_dict = {}
        for u in q:
            self.log.debug(u.buyers)
            if u.location_publish == "0":
                u.document_date = u.document_date + "*"
                continue
            if u.permanent_flag is False:
                u.document_date = u.document_date + u"\u2020"
                # continue
            features_dict = {
                "type": "Feature",
                "properties": {
                    "document_date": u.document_date,
                    "address": u.address,
                    "location_info": u.location_info,
                    "amount": u.amount,
                    "buyers": u.buyers,
                    "sellers": u.sellers,
                    "instrument_no": u.instrument_no
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [u.longitude, u.latitude]
                }
            }
            features.append(features_dict)

        return features

    def decode_data(self, data):
        search_term = data['name_address']
        data['name_address'] = urllib.unquote(search_term).decode('utf8')

        neighborhood = data['neighborhood']
        data['neighborhood'] = urllib.unquote(neighborhood).decode('utf8')

        return data

    def get_last_updated_date(self):
        session = self.sn()

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).order_by(
            desc(db.Cleaned.document_recorded)
        ).limit(1).all()

        updated_date = ''

        for u in q:
            updated_date = Utils().ymd_to_full_date(
                (u.document_recorded).strftime('%Y-%m-%d'), no_day=True)

        session.close()

        return updated_date

    def get_neighborhoods(self):
        session = self.sn()

        q = session.query(db.Neighborhood.gnocdc_lab).all()

        neighborhoods = []

        for hood in q:
            neighborhoods.append(
                (hood.gnocdc_lab).title().replace('Mcd', 'McD'))

        neighborhoods.sort()

        session.close()

        return neighborhoods

    def plural_or_not(self, data):
        if data['qlength'] == 1:
            plural_or_not = "sale"
        else:
            plural_or_not = "sales"

        return plural_or_not

    def add_keyword_language(self, final_sentence, data):
        if data['name_address'] != '':
            if len(data['name_address'].split()) > 1:
                final_sentence += ' for key phrase "' + \
                    data['name_address'] + '"'
                # for 'keyword'
            else:
                final_sentence += ' for keyword "' + \
                    data['name_address'] + '"'
                # for 'keyword'

        return final_sentence

    def add_nbhd_zip_language(self, final_sentence, data):
        if data['neighborhood'] != '':
            if data['zip_code'] != '':
                final_sentence += " in the " + data['neighborhood'] + \
                    " neighborhood and " + data['zip_code']
                # in the Mid-City neighborhood and 70119
            else:
                final_sentence += " in the " + data['neighborhood'] + \
                    " neighborhood"
                # in the Mid-City neighborhood
        elif data['zip_code'] != '':
            final_sentence += " in ZIP code " + data['zip_code']
            # in ZIP code 70119

        return final_sentence

    def add_amount_language(self, final_sentence, data):
        if data['amountlow'] != '':
            if data['amounthigh'] != '':
                final_sentence += " where the price was between " + \
                    Utils().get_num_with_curr_sign(data['amountlow']) + \
                    + " and " + \
                    Utils().get_num_with_curr_sign(data['amounthigh'])
                # where the amount is between $10 and $20
            else:
                final_sentence += " where the price was greater than " + \
                    Utils().get_num_with_curr_sign(data['amountlow'])
                # where the amount is greater than $10
        elif data['amounthigh'] != '':
            final_sentence += " where the price was less than " + \
                Utils().get_num_with_curr_sign(data['amounthigh'])
            # where the amount is less than $20

        return final_sentence

    def add_date_language(self, final_sentence, data):
        if data['begindate'] != '':
            if data['enddate'] != '':
                final_sentence += " between " + \
                    Utils().ymd_to_full_date(
                        data['begindate'],
                        no_day=True) + \
                    ", and " + \
                    Utils().ymd_to_full_date(
                        data['enddate'],
                        no_day=True)
                # between Feb. 10, 2014, and Feb. 12, 2014
            else:
                final_sentence += " after " + \
                    Utils().ymd_to_full_date(
                        data['begindate'],
                        no_day=True)
                # after Feb. 10, 2014.
        elif data['enddate'] != '':
            final_sentence += " before " + \
                Utils().ymd_to_full_date(
                    data['enddate'],
                    no_day=True)
            # before Feb. 20, 2014.

        return final_sentence

    def add_map_filtering_language(self, final_sentence, data):
        if data['mapbuttonstate'] is True:
            final_sentence += ' in the current map view'

        return final_sentence

    def add_final_sentence_language(self, final_sentence, data):
        # Punctuation comes before quotation marks

        if final_sentence[-1] == "'" or final_sentence[-1] == '"':
            last_character = final_sentence[-1]
            l = list(final_sentence)
            l[-1] = '.'
            l.append(last_character)
            final_sentence = ''.join(l)
        else:
            final_sentence += '.'

        return final_sentence

    def add_initial_language(self, plural_or_not, data):
        final_sentence = str(Utils().get_number_with_commas(
            data['qlength'])) + ' ' + plural_or_not + ' found'

        return final_sentence

    def construct_results_language(self, data):
        plural_or_not = self.plural_or_not(data)

        final_sentence = self.add_initial_language(plural_or_not, data)

        final_sentence = self.add_keyword_language(final_sentence, data)

        final_sentence = self.add_nbhd_zip_language(final_sentence, data)

        final_sentence = self.add_amount_language(final_sentence, data)

        final_sentence = self.add_date_language(final_sentence, data)

        final_sentence = self.add_map_filtering_language(final_sentence, data)

        final_sentence = self.add_final_sentence_language(final_sentence, data)

        return final_sentence

    # def dashboard_get(self):
    # session = self.sn()
    #
    #     q = session.query(
    #         db.Cleaned
    #     ).filter(
    #         (db.Cleaned.detail_publish == '0') |
    #         (db.Cleaned.location_publish == '0')
    #     ).order_by(
    #         db.Cleaned.document_recorded.desc()
    #     ).all()

    #     num_results = len(q)

    #     for u in q:
    #         u.amount = Utils().get_num_with_curr_sign(u.amount)
    #         u.document_date = Utils().ymd_to_full_date(
    #     (u.document_date).strftime('%Y-%m-%d'))
    #         u.document_recorded = Utils().ymd_to_full_date(
    # (u.document_date).strftime('%Y-%m-%d'))
    #         u.detail_publish = Utils().binary_to_english(u.detail_publish)
    #         u.location_publish = Utils().binary_to_english(
    # u.location_publish)

    #     rows = []
    #     for row in q:
    #         row_dict = {}
    #         row_dict['detail_publish'] = row.detail_publish
    #         row_dict['location_publish'] = row.location_publish
    #         row_dict['latitude'] = row.latitude
    #         row_dict['longitude'] = row.longitude
    #         row_dict['amount'] = row.amount
    #         row_dict['document_recorded'] = row.document_recorded
    #         row_dict['document_date'] = row.document_date

    #         rows.append(row_dict)

    #     session.close()
    #     return render_template(
    #         'dashboard.html',
    #         js=config.JS,
    #         dashboardjs=config.DASHBOARD_JS,
    #         neighborhoodstopo=config.NEIGHBORHOODS_TOPO,
    #         squarestopo=config.SQUARES_TOPO,
    #         css=config.CSS,
    #         num_results=num_results,
    #         js_app_routing=config.JS_APP_ROUTING,
    #         newrows=q,
    #         jsrows=rows,
    #         number_of_indexes=len(q)
    #     )

    # def dashboard_post(self, data):
    #     # User submitted a change through dashboard

    #     for key in data:
    #         data[key] = data[key].strip()

    #     # Set fixed to false
    #     data['fixed'] = False

    #     doc_rec_date = data['document_recorded']
    #     doc_rec_date = doc_rec_date.replace('March', 'Mar.')
    #     doc_rec_date = doc_rec_date.replace('April', 'Apr.')
    #     doc_rec_date = doc_rec_date.replace('May', 'May.')
    #     doc_rec_date = doc_rec_date.replace('June', 'Jun.')
    #     doc_rec_date = doc_rec_date.replace('July', 'Jul.')
    #     doc_rec_date = datetime.strptime(doc_rec_date, '%A, %b. %d, %Y')
    #     doc_rec_date = doc_rec_date.strftime('%Y-%m-%d')
    #     data['document_recorded'] = doc_rec_date

    #     doc_rec_date = data['document_date']
    #     doc_rec_date = doc_rec_date.replace('March', 'Mar.')
    #     doc_rec_date = doc_rec_date.replace('April', 'Apr.')
    #     doc_rec_date = doc_rec_date.replace('May', 'May.')
    #     doc_rec_date = doc_rec_date.replace('June', 'Jun.')
    #     doc_rec_date = doc_rec_date.replace('July', 'Jul.')
    #     doc_rec_date = datetime.strptime(doc_rec_date, '%A, %b. %d, %Y')
    #     doc_rec_date = doc_rec_date.strftime('%Y-%m-%d')
    #     data['document_date'] = doc_rec_date

    #     '''
    #     Insert/update dashboard log table
    #     '''
    #     session = self.sn()
    #     q = session.query(
    #         db.Dashboard.instrument_no
    #     ).filter(
    #         db.Dashboard.instrument_no == '%s' % (data['instrument_no'])
    #     ).all()

    #     input_length = len(q)

    #     if input_length == 0:
    #         # This sale has not been entered into dashboard table yet
    #         i = insert(db.Dashboard)
    #         i = i.values(data)
    #         session.execute(i)
    #         session.commit()
    #     else:
    #         # This sale has already been entered into dashboard table
    #         u = update(db.Dashboard)
    #         u = u.values(data)
    #         u = u.where(db.Dashboard.instrument_no == '%s' % (
    #             data['instrument_no']))

    #         session.execute(u)
    #         session.commit()

    #     # Update changes in Cleaned table
    #     self.update_cleaned()

    #     session.close()
    #     return 'hi'

    # def geoquery_db(self, data):
    #     session = self.sn()
    #
    #     q = self.find_all_publishable_rows_fitting_criteria(data)

    #     data['qlength'] = len(q)  # number of records
    #     data['pagelength'] = self.PAGE_LENGTH
    #     # total number of pages:
    #     data['totalpages'] = int(math.ceil(
    #         float(data['qlength']) / float(data['pagelength'])))
    #     data['page'] = 1  # start on first page
    #     # Page 1 offsets 0:
    #     data['recordsoffset'] = (data['page'] - 1) * data['pagelength']

    #     # Near me query
    #     q = session.query(
    #         db.Cleaned
    #     ).filter(
    #         func.ST_Distance_Sphere(
    #             db.Cleaned.geom,
    #             func.ST_MakePoint(
    #                 '%f' % data['longitude'],
    #                 '%f' % data['latitude'])
    #         ) <= 1 * 1609.34
    #     ).filter(
    #         db.Cleaned.detail_publish == '1'
    #     ).filter(
    #         (db.Cleaned.sellers.ilike('%%%s%%' % data['name_address'])) |
    #         (db.Cleaned.buyers.ilike('%%%s%%' % data['name_address'])) |
    #         (db.Cleaned.address.ilike('%%%s%%' % data['name_address'])) |
    #         (db.Cleaned.instrument_no.ilike('%%%s%%' % data['name_address']))
    #     ).filter(
    #         db.Cleaned.neighborhood.ilike('%%%s%%' % data['neighborhood'])
    #     ).filter(
    #         db.Cleaned.zip_code.ilike('%%%s%%' % data['zip_code'])
    #     ).filter(
    #         db.Cleaned.document_date >= '%s' % data['databegindate']
    #     ).filter(
    #         db.Cleaned.document_date <= '%s' % data['enddate']
    #     ).filter(
    #         db.Cleaned.amount >= '%s' % data['amountlow']
    #     ).filter(
    #         db.Cleaned.amount <= '%s' % data['amounthigh']
    #     ).order_by(
    #         desc(db.Cleaned.document_date)
    #     ).offset(
    #         '%d' % data['recordsoffset']
    #     ).limit(
    #         '%d' % data['pagelength']
    #     ).all()

    #     for u in q:
    #         u.amount = Utils().get_num_with_curr_sign(u.amount)
    #         u.document_date = Utils().ymd_to_full_date(
    #             (u.document_date).strftime('%Y-%m-%d'), no_day=True)

    #     features = self.build_features_json(q)

    #     jsdata = {
    #         "type": "FeatureCollection",
    #         "features": features
    #     }

    #     if data['qlength'] == 0:
    #         data['page'] = 0

    #     tabletemplate = render_template(
    #         'table.html',
    #         newrows=q
    #     )

    #     data = self.revert_entries(data)

    #     data['results_language'] = self.construct_results_language(data)

    #     session.close()
    #     return jsonify(
    #         tabletemplate=tabletemplate,
    #         update_date=data['update_date'],
    #         jsdata=jsdata,
    #         results_language=data['results_language'],
    #         page=data['page'],
    #         totalpages=data['totalpages'],
    #         pagelength=data['pagelength']
    #     )

    # def update_cleaned(self):
    #     session = self.sn()
    #
    #     q = session.query(
    #         db.Dashboard
    #     ).filter(
    #         db.Dashboard.fixed is False
    #     ).all()

    #     rows = []
    #     for row in q:
    #         row_dict = {}
    #         row_dict['instrument_no'] = row.instrument_no
    #         row_dict['detail_publish'] = row.detail_publish
    #         row_dict['location_publish'] = row.location_publish
    #         row_dict['document_date'] = row.document_date
    #         row_dict['amount'] = row.amount
    #         row_dict['address'] = row.address
    #         row_dict['location_info'] = row.location_info
    #         row_dict['sellers'] = row.sellers
    #         row_dict['buyers'] = row.buyers
    #         row_dict['document_recorded'] = row.document_recorded
    #         row_dict['latitude'] = row.latitude
    #         row_dict['longitude'] = row.longitude
    #         row_dict['zip_code'] = row.zip_code
    #         row_dict['neighborhood'] = row.neighborhood

    #         rows.append(row_dict)

    #     for row in rows:
    #         # This sale has already been entered into dashboard table
    #         u = update(db.Cleaned)
    #         u = u.values(row)
    #         u = u.where(
    #             db.Cleaned.instrument_no == '%s' % row['instrument_no'])
    #         session.execute(u)
    #         session.commit()

    #         # This sale has already been entered into dashboard table
    #         u = update(db.Dashboard)
    #         u = u.values({"fixed": True})
    #         u = u.where(
    #             db.Dashboard.instrument_no == '%s' % row['instrument_no'])
    #         session.execute(u)
    #         session.commit()
    #
    #     session.close()
