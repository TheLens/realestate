# -*- coding: utf-8 -*-

from __future__ import absolute_import

import math
import os
import urllib
import logging
import logging.handlers
from datetime import datetime

# from flask.ext.cache import Cache
from flask import (
    # request,
    render_template,
    jsonify
)
from sqlalchemy import (
    create_engine,
    desc,
    insert,
    update
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib import check_assessor_urls
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


class Models(object):

    def __init__(self, initial_date=None, until_date=None):
        self.initial_date = initial_date
        self.until_date = until_date
        self.logger = initialize_log('models')

        self.PAGE_LENGTH = 10  # todo: determine this via front end.
        # May want to let users change in future. Also just for consistency.

        base = declarative_base()
        self.engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    def get_home(self):
        yesterday_date = self.get_last_updated_date()
        neighborhoods = self.get_neighborhoods()

        data = {'yesterday_date': yesterday_date,
                'neighborhoods': neighborhoods}

        self.session.close()
        return data

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

        data = self.assign_data(data)
        data = self.check_entry(data)

        # query_db all below:
        data['yesterday_date'] = self.get_last_updated_date()
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
                u.document_date, no_day=True)

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

        parameters = {}
        parameters['name_address'] = data['name_address']
        parameters['amountlow'] = data['amountlow']
        parameters['amounthigh'] = data['amounthigh']
        parameters['begindate'] = data['begindate']
        parameters['enddate'] = data['enddate']
        parameters['neighborhood'] = data['neighborhood']
        parameters['zip_code'] = data['zip_code']

        self.session.close()

        return data, newrows, jsdata, parameters

    def post_search(self, data):
        data = self.assign_data(data)
        data = self.check_entry(data)

        # If a geo query (search near me). Not yet a feature.
        # if 'latitude' in data and 'longitude' in data:
        #     response = self.geoquery_db(data)
        # else:
        response = self.mapquery_db(data)

        self.session.close()

        return response

    def mapquery_db(self, data):
        data['bounds'] = [
            data['bounds']['_northEast']['lat'],
            data['bounds']['_northEast']['lng'],
            data['bounds']['_southWest']['lat'],
            data['bounds']['_southWest']['lng']
        ]

        data['yesterday_date'] = self.get_last_updated_date()

        if data['mapbuttonstate'] is True:  # map filtering is on
            q = self.map_query_length(data)
            data['qlength'] = len(q)  # number of records
            # total number of pages:
            data['totalpages'] = int(math.ceil(
                float(data['qlength']) / float(data['pagelength'])))

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

            q = self.map_query1(data)

        if data['mapbuttonstate'] is False:  # map filtering is off
            q = self.find_all_publishable_rows_fitting_criteria(data)
            data['pagelength'] = self.PAGE_LENGTH
            data['qlength'] = len(q)  # number of records
            # total number of pages:
            data['totalpages'] = int(math.ceil(
                float(data['qlength']) / float(data['pagelength'])))

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

            q = self.find_page_of_publishable_rows_fitting_criteria(data)

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(
                u.document_date, no_day=True)

        features = self.build_features_json(q)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        data['results_css_display'] = 'none'

        if data['qlength'] == 0:
            data['page'] = 0
            data['results_css_display'] = 'block'

        data = self.revert_entries(data)

        data['results_language'] = self.construct_results_language(data)

        newrows = q
        # todo: remove?
        # Or necessary because it might change when the session is closed

        self.session.close()

        return data, newrows, jsdata

    def dashboard_get(self):
        q = self.session.query(
            db.Cleaned
        ).filter(
            (db.Cleaned.detail_publish == '0') |
            (db.Cleaned.location_publish == '0')
        ).order_by(
            db.Cleaned.document_recorded.desc()
        ).all()

        num_results = len(q)

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(u.document_date)
            u.document_recorded = Utils().ymd_to_full_date(u.document_recorded)
            u.detail_publish = Utils().binary_to_english(u.detail_publish)
            u.location_publish = Utils().binary_to_english(u.location_publish)

        rows = []
        for row in q:
            row_dict = {}
            row_dict['detail_publish'] = row.detail_publish
            row_dict['location_publish'] = row.location_publish
            row_dict['latitude'] = row.latitude
            row_dict['longitude'] = row.longitude
            row_dict['amount'] = row.amount
            row_dict['document_recorded'] = row.document_recorded
            row_dict['document_date'] = row.document_date

            rows.append(row_dict)

        self.session.close()
        return render_template(
            'dashboard.html',
            js=config.JS,
            dashboardjs=config.DASHBOARD_JS,
            neighborhoodstopo=config.NEIGHBORHOODS_TOPO,
            squarestopo=config.SQUARES_TOPO,
            css=config.CSS,
            num_results=num_results,
            js_app_routing=config.JS_APP_ROUTING,
            newrows=q,
            jsrows=rows,
            number_of_indexes=len(q)
        )

    def dashboard_post(self, data):
        # User submitted a change through dashboard

        for key in data:
            data[key] = data[key].strip()

        # Set fixed to false
        data['fixed'] = False

        doc_rec_date = data['document_recorded']
        doc_rec_date = doc_rec_date.replace('March', 'Mar.')
        doc_rec_date = doc_rec_date.replace('April', 'Apr.')
        doc_rec_date = doc_rec_date.replace('May', 'May.')
        doc_rec_date = doc_rec_date.replace('June', 'Jun.')
        doc_rec_date = doc_rec_date.replace('July', 'Jul.')
        doc_rec_date = datetime.strptime(doc_rec_date, '%A, %b. %d, %Y')
        doc_rec_date = doc_rec_date.strftime('%Y-%m-%d')
        data['document_recorded'] = doc_rec_date

        doc_rec_date = data['document_date']
        doc_rec_date = doc_rec_date.replace('March', 'Mar.')
        doc_rec_date = doc_rec_date.replace('April', 'Apr.')
        doc_rec_date = doc_rec_date.replace('May', 'May.')
        doc_rec_date = doc_rec_date.replace('June', 'Jun.')
        doc_rec_date = doc_rec_date.replace('July', 'Jul.')
        doc_rec_date = datetime.strptime(doc_rec_date, '%A, %b. %d, %Y')
        doc_rec_date = doc_rec_date.strftime('%Y-%m-%d')
        data['document_date'] = doc_rec_date

        '''
        Insert/update dashboard log table
        '''

        q = self.session.query(
            db.Dashboard.instrument_no
        ).filter(
            db.Dashboard.instrument_no == '%s' % (data['instrument_no'])
        ).all()

        input_length = len(q)

        if input_length == 0:
            # This sale has not been entered into dashboard table yet
            i = insert(db.Dashboard)
            i = i.values(data)
            self.session.execute(i)
            self.session.commit()
        else:
            # This sale has already been entered into dashboard table
            u = update(db.Dashboard)
            u = u.values(data)
            u = u.where(db.Dashboard.instrument_no == '%s' % (
                data['instrument_no']))

            self.session.execute(u)
            self.session.commit()

        # Update changes in Cleaned table
        self.update_cleaned()

        self.session.close()
        return 'hi'

    def get_sale(self, instrument_no):
        data = {}
        data['yesterday_date'] = self.get_last_updated_date()

        q = self.session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.instrument_no == '%s' % (instrument_no)
        ).all()

        for u in q:
            u.amount = Utils().get_num_with_curr_sign(u.amount)
            u.document_date = Utils().ymd_to_full_date(
                u.document_date, no_day=True)
            address = u.address
            location_info = u.location_info
            data['assessor_publish'] = u.assessor_publish

        features = self.build_features_json(q)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        conds = (data['assessor_publish'] == '0' or
                 data['assessor_publish'] is None or
                 data['assessor_publish'] == '')

        if conds:
            data['assessor'] = """
                Could not find this property on the Orleans Parish
                Assessor's Office site. <a href='http://www.qpublic
                .net/la/orleans/search1.html' target='_blank'>"
                Search based on other criteria.</a>"""
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
            self.session.close()
            return None, None, None
        else:
            self.session.close()
            return data, jsdata, q

    def map_query_length(self, data):
        q = self.session.query(
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

        return q

    # For when map filtering is turned on
    def map_query1(self, data):
        q = self.session.query(
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

        return q

    def find_all_publishable_rows_fitting_criteria(self, data):
        q = self.session.query(
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

        return q

    def find_page_of_publishable_rows_fitting_criteria(self, data):
        q = self.session.query(
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

        return q

    def check_entry(self, data):
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
        features = []
        features_dict = {}
        for u in q:
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

    def assign_data(self, data):
        search_term = data['name_address']
        data['name_address'] = urllib.unquote(search_term).decode('utf8')

        neighborhood = data['neighborhood']
        data['neighborhood'] = urllib.unquote(neighborhood).decode('utf8')

        return data

    def get_last_updated_date(self):
        q = self.session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).order_by(
            desc(db.Cleaned.document_recorded)
        ).limit(1).all()

        updated_date = ''

        for u in q:
            updated_date = Utils().ymd_to_full_date(
                u.document_recorded, no_day=True)

        return updated_date

    def get_neighborhoods(self):
        q = self.session.query(db.Neighborhood.gnocdc_lab).all()

        neighborhoods = []

        for hood in q:
            neighborhoods.append(
                (hood.gnocdc_lab).title().replace('Mcd', 'McD'))

        neighborhoods.sort()

        return neighborhoods

    def update_cleaned(self):
        q = self.session.query(
            db.Dashboard
        ).filter(
            db.Dashboard.fixed is False
        ).all()

        rows = []
        for row in q:
            row_dict = {}
            row_dict['instrument_no'] = row.instrument_no
            row_dict['detail_publish'] = row.detail_publish
            row_dict['location_publish'] = row.location_publish
            row_dict['document_date'] = row.document_date
            row_dict['amount'] = row.amount
            row_dict['address'] = row.address
            row_dict['location_info'] = row.location_info
            row_dict['sellers'] = row.sellers
            row_dict['buyers'] = row.buyers
            row_dict['document_recorded'] = row.document_recorded
            row_dict['latitude'] = row.latitude
            row_dict['longitude'] = row.longitude
            row_dict['zip_code'] = row.zip_code
            row_dict['neighborhood'] = row.neighborhood

            rows.append(row_dict)

        for row in rows:
            # This sale has already been entered into dashboard table
            u = update(db.Cleaned)
            u = u.values(row)
            u = u.where(
                db.Cleaned.instrument_no == '%s' % row['instrument_no'])
            self.session.execute(u)
            self.session.commit()

            # This sale has already been entered into dashboard table
            u = update(db.Dashboard)
            u = u.values({"fixed": True})
            u = u.where(
                db.Dashboard.instrument_no == '%s' % row['instrument_no'])
            self.session.execute(u)
            self.session.commit()

    def searchbar_input(self, term):
        search_term = urllib.unquote(term).decode('utf8')

        q_neighborhoods = self.session.query(
            db.Cleaned.neighborhood
        ).filter(
            db.Cleaned.neighborhood.ilike('%%%s%%' % search_term)
        ).distinct().limit(3).all()

        q_zip = self.session.query(
            db.Cleaned.zip_code
        ).filter(
            db.Cleaned.zip_code.ilike('%%%s%%' % search_term)
        ).distinct().limit(3).all()

        q_locations = self.session.query(
            db.Cleaned.detail_publish,
            db.Cleaned.address
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.address.ilike('%%%s%%' % search_term)
        ).limit(3).all()

        q_buyers = self.session.query(
            db.Cleaned.detail_publish,
            db.Cleaned.buyers
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.buyers.ilike('%%%s%%' % search_term)
        ).limit(3).all()

        q_sellers = self.session.query(
            db.Cleaned.detail_publish,
            db.Cleaned.sellers
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.sellers.ilike('%%%s%%' % search_term)
        ).limit(3).all()

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

    def construct_results_language(self, data):
        if data['qlength'] == 1:
            plural_or_not = "sale"
        else:
            plural_or_not = "sales"

        final_sentence = str(Utils().get_number_with_commas(data['qlength'])) + \
            ' ' + str(plural_or_not) + ' found'
        # 10 records found

        conds = (data['name_address'] == '' and
                 data['amountlow'] == '' and
                 data['amounthigh'] == '' and
                 data['begindate'] == '' and
                 data['enddate'] == '' and
                 data['neighborhood'] == '' and
                 data['zip_code'] == '')
        if conds:
            if data['mapbuttonstate'] is True:
                final_sentence += ' in the current map view.'
                # 10 records found.
            else:
                final_sentence += '.'  # 10 records found.
        else:
            if data['name_address'] != '':
                if len(data['name_address'].split()) > 1:
                    final_sentence += ' for key phrase "' + \
                        data['name_address'] + '"'
                    # 10 records found for 'keyword'
                else:
                    final_sentence += ' for keyword "' + \
                        data['name_address'] + '"'
                    # 10 records found for 'keyword'

            if data['neighborhood'] != '':
                if data['zip_code'] != '':
                    final_sentence += " in the " + data['neighborhood'] + \
                        " neighborhood and " + data['zip_code']
                    # 10 records found for 'keyword' in Mid-City and 70119
                else:
                    final_sentence += " in the " + data['neighborhood'] + \
                        " neighborhood"
                    # 10 records found for 'keyword' in Mid-City
            elif data['zip_code'] != '':
                final_sentence += " in ZIP code " + data['zip_code']
                # 10 records found for 'keyword' in 70119

            if data['amountlow'] != '':
                if data['amounthigh'] != '':
                    final_sentence += " where the price was between " + \
                        Utils().get_num_with_curr_sign(data['amountlow']) + \
                        + " and " + \
                        Utils().get_num_with_curr_sign(data['amounthigh'])
                    # 10 records found for 'keyword' in Mid-City, where the
                    # amount is between $10 and $20
                else:
                    final_sentence += " where the price was greater than " + \
                        Utils().get_num_with_curr_sign(data['amountlow'])
                    # 10 records found for 'keyword' in Mid-City, where the
                    # amount is greater than $10
            elif data['amounthigh'] != '':
                final_sentence += " where the price was less than " + \
                    Utils().get_num_with_curr_sign(data['amounthigh'])
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is less than $20

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
                    # 10 records found for 'keyword' in Mid-City, where the
                    # amount is between $10 and $20, between Feb. 10, 2014,
                    # and Feb. 12, 2014
                else:
                    final_sentence += " after " + \
                        Utils().ymd_to_full_date(
                            data['begindate'],
                            no_day=True)
                    # 10 records found for 'keyword' in Mid-City, where the
                    # amount is greater than $10, after Feb. 10, 2014.
            elif data['enddate'] != '':
                final_sentence += " before " + \
                    Utils().ymd_to_full_date(
                        data['enddate'],
                        no_day=True)
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is less than $20, before Feb. 20, 2014.

            if data['mapbuttonstate'] is True:
                final_sentence += " in the current map view"

            if final_sentence[-1] == "'" or final_sentence[-1] == '"':
                last_character = final_sentence[-1]
                l = list(final_sentence)
                l[-1] = '.'
                l.append(last_character)
                final_sentence = ''.join(l)
            else:
                final_sentence += '.'

        return final_sentence

    # def geoquery_db(self, data):
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
    #     q = self.session.query(
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
    #             u.document_date, no_day=True)

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

    #     self.session.close()
    #     return jsonify(
    #         tabletemplate=tabletemplate,
    #         yesterday_date=data['yesterday_date'],
    #         jsdata=jsdata,
    #         results_language=data['results_language'],
    #         page=data['page'],
    #         totalpages=data['totalpages'],
    #         pagelength=data['pagelength']
    #     )
