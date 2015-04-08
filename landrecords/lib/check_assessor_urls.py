# -*- coding: utf-8 -*-

import urllib2
import re
import time
import random
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from landrecords.lib.log import Log
from landrecords import (
    config,
    db
)


class Assessor(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('assessor').logger

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        self.engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

        rows = self.get_rows_with_neighborhood()
        clean_rows = self.clean_rows(rows)
        self.commit_rows(clean_rows)

        rows = self.get_rows_without_neighborhood()
        clean_rows = self.clean_rows(rows)
        self.commit_rows(clean_rows)

    def check_assessor_links(self, initial_date=None, until_date=None):
        q = self.session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.document_recorded >= '%s' % (initial_date)
        ).filter(
            db.Cleaned.document_recorded <= '%s' % (until_date)
        ).filter(
            db.Cleaned.assessor_publish == '0'
        ).all()

        error_html = self.get_error_page_html(
            "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=7724-"
            "BURTHESTt")

        num_records = len(q)
        print '%d records to check.' % num_records

        for u in q:
            print '%d records left.' % num_records
            num_records = num_records - 1
            address = u.address
            location_info = u.location_info
            instrument_no = u.instrument_no
            url_param = self.check_assessor_urls.formAssessorURL(
                address, location_info)

            if url_param is None:
                '''
                session.query(
                    db.Cleaned.instrument_no,
                    db.Cleaned.assessor_publish
                ).filter(
                    db.Cleaned.instrument_no == '%s' % (instrument_no)
                ).update({
                    "assessor_publish": "0"
                })

                session.commit()
                '''
                continue

            assessor_url = """
                http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s
                """ % (url_param)

            response = self.test_url(assessor_url, error_html)

            if response is None:  # No error page
                self.session.query(
                    db.Cleaned.instrument_no,
                    db.Cleaned.assessor_publish
                ).filter(
                    db.Cleaned.instrument_no == '%s' % (instrument_no)
                ).update({
                    "assessor_publish": "1"
                })

                self.session.commit()
            '''
            else:#Error page
                session.query(
                    db.Cleaned.instrument_no,
                    db.Cleaned.assessor_publish
                ).filter(
                    db.Cleaned.instrument_no == '%s' % (instrument_no)
                ).update({
                    "assessor_publish": "0"
                })

                session.commit()
            '''

            time.sleep(random.randint(1, 2) + random.uniform(1.0, 2.0))

    def form_assessor_url(self, address, location_info):
        # todo: what if multiple addresses.
        # which to use to form assessor's link?
        # todo: need to account for N/S/E/W designations.
        # Ex: S. Saratoga St. has
        # url_param = 2617-SSARATOGAST. Maybe need to ignore the cardinal
        # direction? Seems like it is always necessary if present though.

        print 'address:', address
        print 'location_info:', location_info

        address = address.strip()
        address = address.upper()
        address = address.split(';')[0]

        location_info = location_info.strip()
        location_info = location_info.upper()
        address = address.split(';')[0]

        address_number = re.match(r"[^ \-]*", address).group(0)

        if address_number == 'UNIT:':
            return None

        print 'address_number:', address_number

        street = re.match(r"\S+\s([^\,]*)", address)

        if street is not None:
            street = street.group(1)
        else:
            return None

        street = street.replace('.', '')
        street = street.replace('FKA', '')

        print 'street:', street

        '''
        street_direction = street.split(' ')[0]

        if street_direction == "N."
        or street_direction == "S."
        or street_direction == "E."
        or street_direction == "W.":
            street_direction = street_direction[0]
        else:
            street_direction = ''

        print 'street_direction:', street_direction
        '''

        street_type = street.split(' ')[-1]

        # Taken from:
        # http://en.wikipedia.org/wiki/Street_or_road_name#Street_type_designations
        abbreviations = [
            # Major roads
            ['HIGHWAY', 'HW'],
            ['FREEWAY', ''],
            ['AUTOROUTE', ''],
            ['AUTOBAHN', ''],
            ['EXPRESSWAY', ''],
            ['AUTOSTRASSE', ''],
            ['AUTOSTRADA', ''],
            ['BYWAY', ''],
            ['AUTO-ESTRADA', ''],
            ['MOTORWAY', ''],
            ['PIKE', ''],
            ['AVENUE', 'AV'],
            ['BOULEVARD', 'BL'],
            ['ROAD', 'RD'],
            ['STREET', 'ST'],
            # Small roads
            ['ALLEY', ''],
            ['BAY', ''],
            ['BEND', ''],
            ['DRIVE', 'DR'],
            ['FAIRWAY', ''],
            ['GARDENS', ''],
            ['GATE', ''],
            ['GROVE', ''],
            ['HEIGHTS', ''],
            ['HIGHLANDS', ''],
            ['KNOLL', ''],
            ['LANE', 'LN'],
            ['MANOR', ''],
            ['MEWS', ''],
            ['PATHWAY', ''],
            ['TERRACE', ''],
            ['TRAIL', ''],
            ['VALE', ''],
            ['VIEW', ''],
            ['WALK', ''],
            ['WAY', ''],
            ['WYND', ''],
            # Culs-de-sac
            ['CLOSE', ''],
            ['COURT', 'CT'],
            ['PLACE', 'PL'],
            ['COVE', ''],
            # Shapes
            ['CIRCLE', ''],
            ['CRESCENT', ''],
            ['DIAGONAL', ''],
            ['LOOP', ''],
            ['QUADRANT', ''],
            ['SQUARE', ''],
            # Geographic attributes
            ['HILL', ''],
            ['GRADE', ''],
            ['CAUSEWAY', ''],
            ['CANYON', ''],
            ['RIDGE', ''],
            ['PARKWAY', 'PW'],
            # Functions
            ['ESPLANADE', ''],
            ['APPROACH', ''],
            ['FRONTAGE', ''],
            ['PARADE', ''],
            ['PARK', ''],
            ['PLAZA', ''],
            ['PROMENADE', ''],
            ['QUAY', ''],
            ['BYPASS', ''],
            ['STRAVENUE', ''],

            # Post cleanup
            ['AVE.', 'AV'],
            ['BLVD.', 'BL'],
            ['ROAD', 'RD'],
            ['ST.', 'ST'],
            ['DR.', 'DR']
        ]
        street_type_abbr = street_type
        for abbreviation in abbreviations:
            abbr0 = abbreviation[0]
            abbr1 = abbreviation[1]
            street_type_abbr = re.sub(abbr0, abbr1, street_type_abbr)

        unit = re.match(r"^.*UNIT\: (.*)\, CONDO", location_info)
        if unit is not None:
            unit = unit.group(1)
        else:
            unit = ''
        # print 'unit:', unit

        street = " ".join(street.split()[0:-1])

        # Be careful about regex patterns
        assessor_abbreviations = [
            [r"GRAND ROUTE ST\. JOHN", "GRANDRTESTJO"],  # Grand Route St. John
            [r'GENERAL', 'GEN'],  # General xxx
            [r'ST\.', 'ST'],  # St. xxx
            [r"ROUTE", 'RTE']
        ]

        for assessor_abbr in assessor_abbreviations:
            abbr0 = assessor_abbr[0]
            abbr1 = assessor_abbr[1]
            street = re.sub(abbr0, abbr1, street)
        street = "".join(street.split())  # remove spaces

        url_param = address_number + '-' + street + street_type_abbr + unit

        print 'url_param:', url_param
        print '\n'

        return url_param

    def get_error_page_html(self, url):
        error_req = urllib2.Request(
            url,
            headers={
                'User-Agent': '''
                Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 \
                Safari/537.36'''})
        error_con = urllib2.urlopen(error_req)
        error_html = error_con.read()
        error_con.close()

        return error_html

    def test_url(self, url, error_html):
        req = urllib2.Request(
            url,
            headers={
                'User-Agent': '''
                Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) \
                AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'''})
        con = urllib2.urlopen(req)
        html = con.read()
        con.close()

        if html == error_html:
            return url
        else:
            return None

    def get_instrument_numbers(self):
        Base.metadata.create_all(engine)
        sn = sessionmaker(bind=engine)
        session = sn()

        q = session.query(
            db.Cleaned.address,
            db.Cleaned.location_info
        ).all()

        locations = []
        url_params = []
        assessor_urls = []

        print "# of records:", len(q)

        for u in q:
            address = u.address
            location_info = u.location_info
            location = address + ', ' + location_info
            locations.append(location)

        session.close()

        for location in locations:
            url_params.append(self.form_assessor_url(location))

        for url_param in url_params:
            if url_param is None:
                continue
            else:
                assessor_urls.append("""
                    http://qpublic9.qpublic.net/la_orleans_display \
                    .php?KEY=%s""" % (url_param))

        print "# of assessor URLs to check:", len(assessor_urls)

        error_html = self.get_error_page_html("""
            http://qpublic9.qpublic.net/la_orleans_display \
            .php?KEY=7724-BURTHESTt""")

        problem_urls = []

        for i, assessor_url in enumerate(assessor_urls):
            if assessor_url == '':
                print 'this should never print'

                continue
            else:
                response = self.test_url(assessor_url, error_html)
                if response is not None:
                    problem_urls.append(response)

            # if i == 5:
            #     break

            time.sleep(random.randint(3, 5) + random.uniform(1.0, 2.0))

    if __name__ == '__main__':
        get_instrument_numbers()
        # formAssessorURL("7471 Restgate Road, Unit: , Condo: , Weeks: ,
        # Subdivision: Lake Forest No 8 Warwick East, District: 3rd, Square: 7,
        # Lot: 2")
