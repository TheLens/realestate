# -*- coding: utf-8 -*-

import re
import os
import logging
import logging.handlers
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib.libraries import Library


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


class Clean(object):

    def __init__(self, initial_date=None, until_date=None):
        self.initial_date = initial_date
        self.until_date = until_date
        self.logger = initialize_log('clean')

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

    def get_rows_with_neighborhood(self):
        '''
        All sales (just yesterday or every day, depending)
        '''

        sql = """
            WITH vendee AS (
              SELECT document_id, string_agg(vendee_firstname::text || ' ' ||
               vendee_lastname::text, ', ') AS buyers
              FROM vendees
              GROUP BY document_id
            ), vendor AS (
              SELECT document_id, string_agg(vendor_firstname::text || ' ' ||
                 vendor_lastname::text, ', ') AS sellers
              FROM vendors
              GROUP BY document_id
            ), location AS (
              SELECT document_id,
                     min(location_publish) AS location_publish,
                     string_agg(
                        street_number::text || ' ' ||
                        address::text, '; ') AS address,
                     string_agg(
                        'Unit: ' || unit::text ||
                        ', Condo: ' || condo::text ||
                        ', Weeks: ' || weeks::text ||
                        ', Subdivision: ' || subdivision::text ||
                        ', District: ' || district::text ||
                        ', Square: ' || square::text ||
                        ', Lot: ' || lot::text, '; ') AS location_info,
                     mode() WITHIN GROUP (ORDER BY zip_code) AS zip_code,
                     mode() WITHIN GROUP (ORDER BY latitude) AS latitude,
                     mode() WITHIN GROUP (ORDER BY longitude) AS longitude
              FROM locations
              GROUP BY document_id
            ), hood AS (
              SELECT document_id, longitude, latitude
              FROM locations
            ), neighborhood AS (
              SELECT document_id,
                     mode() WITHIN GROUP (ORDER BY gnocdc_lab) AS neighborhood
              FROM neighborhoods, hood
              WHERE ST_Contains(neighborhoods.geom, ST_SetSRID(ST_Point(
                hood.longitude::float, hood.latitude::float),4326))
              GROUP BY document_id
            )
            SELECT details.amount,
                   details.document_date,
                   details.document_recorded,
                   location.address,
                   location.location_info,
                   vendor.sellers,
                   vendee.buyers,
                   details.instrument_no,
                   location.latitude,
                   location.longitude,
                   location.zip_code,
                   details.detail_publish,
                   details.permanent_flag,
                   location.location_publish,
                   neighborhood.neighborhood
            FROM details
            JOIN location ON details.document_id = location.document_id
            JOIN vendor ON details.document_id = vendor.document_id
            JOIN vendee ON details.document_id = vendee.document_id
            JOIN neighborhood ON details.document_id = neighborhood.document_id
            WHERE document_recorded >= '%s' AND document_recorded <= '%s';
        """ % (self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        rows = []
        for row in result:
            self.logger.debug(row)
            row = dict(row)
            rows.append(row)

        return rows

    def get_rows_without_neighborhood(self):
        '''
        No neighborhood found.
        '''

        sql = """
            WITH vendee AS (
              SELECT document_id, string_agg(vendee_firstname::text || ' ' ||
               vendee_lastname::text, ', ') AS buyers
              FROM vendees
              GROUP BY document_id
            ), vendor AS (
              SELECT document_id, string_agg(vendor_firstname::text || ' ' ||
               vendor_lastname::text, ', ') AS sellers
              FROM vendors
              GROUP BY document_id
            ), location AS (
              SELECT document_id,
                     min(location_publish) AS location_publish,
                     string_agg(
                        street_number::text || ' ' ||
                        address::text, '; ') AS address,
                     string_agg('Unit: ' || unit::text ||
                        ', Condo: ' || condo::text ||
                        ', Weeks: ' || weeks::text ||
                        ', Subdivision: ' || subdivision::text ||
                        ', District: ' || district::text ||
                        ', Square: ' || square::text ||
                        ', Lot: ' || lot::text, '; ') AS location_info,
                     mode() WITHIN GROUP (ORDER BY zip_code) AS zip_code,
                     mode() WITHIN GROUP (ORDER BY latitude) AS latitude,
                     mode() WITHIN GROUP (ORDER BY longitude) AS longitude
              FROM locations
              GROUP BY document_id
            ), hood AS (
              SELECT document_id, longitude, latitude
              FROM locations
            ), neighborhood AS (
              SELECT document_id
              FROM hood, (
                SELECT ST_Union(geom) as geom from neighborhoods
                ) as nbhd
              WHERE NOT ST_Contains(nbhd.geom,
                ST_SetSRID(
                    ST_Point(hood.longitude::float, hood.latitude::float),
                    4326))
              GROUP BY document_id
            )
            SELECT details.amount,
                   details.document_date,
                   details.document_recorded,
                   location.address,
                   location.location_info,
                   vendor.sellers,
                   vendee.buyers,
                   details.instrument_no,
                   location.latitude,
                   location.longitude,
                   location.zip_code,
                   details.detail_publish,
                   details.permanent_flag,
                   location.location_publish
            FROM details
            JOIN location ON details.document_id = location.document_id
            JOIN vendor ON details.document_id = vendor.document_id
            JOIN vendee ON details.document_id = vendee.document_id
            JOIN neighborhood ON details.document_id = neighborhood.document_id
            WHERE document_recorded >= '%s' AND document_recorded <= '%s';
        """ % (self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        rows = []
        for row in result:
            self.logger.debug(row)
            row = dict(row)
            row['neighborhood'] = "None"
            rows.append(row)

        return rows

    def commit_rows(self, rows):
        print 'Cleaning...'
        for row in rows:
            self.logger.debug(row)
            try:
                with self.session.begin_nested():
                    i = insert(db.Cleaned)
                    i = i.values(row)
                    self.session.execute(i)
                    self.session.flush()
            except Exception, e:
                print 'Error!', e
                self.logger.error(e, exc_info=True)
                self.session.rollback()

        self.session.commit()

    def clean_rows(self, rows):
        '''
        This function takes in ALL CAPS and returns clean text.
        '''

        # This loop returns text that is not all-caps, but is still flawed:
        # to standardize upper and lowercases
        for i, row in enumerate(rows):
            # Read this row's values
            sellers = row['sellers']
            buyers = row['buyers']
            address = row['address']
            location_info = row['location_info']
            neighborhood = row['neighborhood']

            # Capitalizes the first letter in each word.
            # Results in words like Llc, Xiv, etc
            sellers = sellers.title()
            buyers = buyers.title()
            address = address.title()
            location_info = location_info.title()
            neighborhood = neighborhood.title()

            # Write over this rows values with newer, cleaner values
            rows[i]['sellers'] = sellers
            rows[i]['buyers'] = buyers
            rows[i]['address'] = address
            rows[i]['location_info'] = location_info
            rows[i]['neighborhood'] = neighborhood

        # This loop scans for the above problem words and replaces them with
        # their substitutes:
        for i, row in enumerate(rows):
            # Read the current rows values
            sellers = row['sellers']
            buyers = row['buyers']
            address = row['address']
            location_info = row['location_info']
            amt = row['amount']
            neighborhood = row['neighborhood']
            # Check for occurences of problematic acronyms
            for acronym in Library().acronyms:
                acronym0 = acronym[0]  # Problem acronym
                acronym1 = acronym[1]  # Solution acronym
                # If find problem acronym (acronym0) in a string,
                # replace with solution acronym (acronym1)
                sellers = re.sub(acronym0, acronym1, sellers)
                buyers = re.sub(acronym0, acronym1, buyers)
                address = re.sub(acronym0, acronym1, address)
                location_info = re.sub(acronym0, acronym1, location_info)
            # Check for occurences of problematic "Mc" names. Corrections
            # assume that the letter after should be capitalized:
            for mcname in Library().mc_names:
                mcname0 = mcname[0]
                mcname1 = mcname[1]
                sellers = re.sub(mcname0, mcname1, sellers)
                buyers = re.sub(mcname0, mcname1, buyers)
                address = re.sub(mcname0, mcname1, address)
                location_info = re.sub(mcname0, mcname1, location_info)
            # Check for problematic abbreviations:
            for abbreviation in Library().abbreviations:
                abbreviation0 = abbreviation[0]
                abbreviation1 = abbreviation[1]
                sellers = re.sub(abbreviation0, abbreviation1, sellers)
                buyers = re.sub(abbreviation0, abbreviation1, buyers)
                address = re.sub(abbreviation0, abbreviation1, address)
                location_info = re.sub(
                    abbreviation0, abbreviation1, location_info)
            # Fix address abbreviations (for AP style purposes)
            for address_abbreviation in Library().streets:
                address0 = address_abbreviation[0]
                address1 = address_abbreviation[1]
                address = re.sub(address0, address1, address)
                location_info = re.sub(address0, address1, location_info)
            for middle_initial in Library().middle_initials:
                middle_initial0 = middle_initial[0]
                middle_initial1 = middle_initial[1]
                sellers = re.sub(middle_initial0, middle_initial1, sellers)
                buyers = re.sub(middle_initial0, middle_initial1, buyers)

            for neighborhood_name in Library().neighborhood_names:
                name0 = neighborhood_name[0]
                name1 = neighborhood_name[1]
                neighborhood = re.sub(name0, name1, neighborhood)

            # Must do regex for "St" and others. Imagine "123 Star St".
            # Scanning for " St" in the above loop would catch the start of
            # the street name here. "St " wouldn't work either.
            # Check for "St" followed by end-of-line character:
            address = re.sub(r"St$", r"St.", address)
            address = re.sub(r"Ave$", r"Ave.", address)
            address = re.sub(r"Dr$", r"Dr.", address)
            address = re.sub(r" N ", r" N. ", address)
            address = re.sub(r" S ", r" S. ", address)
            address = re.sub(r" E ", r" E. ", address)
            address = re.sub(r" W ", r" W. ", address)
            sellers = re.sub(r"Inc$", r"Inc.", sellers)
            buyers = re.sub(r"Inc$", r"Inc.", buyers)
            amt = str(amt)
            amt = re.sub(r'\$', r'', amt)  # remove the $
            amt = re.sub(r',', r'', amt)  # remove the comma
            amt = float(amt)  # change string to a float
            amt = round(amt)  # round to nearest dollar
            amt = int(amt)

            all_addresses_text = ''

            address_list1 = address.split(';')

            for row in address_list1:
                # unit: x, condo: 4, etc.

                address_list2 = row.split(',')

                individiual_address_text = ''

                for l in address_list2:
                    # condo: x

                    try:
                        if l.strip()[-1] != ':':
                            # If first addition:
                            if individiual_address_text == '':
                                individiual_address_text = l.strip()
                            else:  # If second addition or later
                                individiual_address_text = (
                                    individiual_address_text +
                                    ', ' +
                                    l.strip())
                    except Exception, e:
                        self.logger.error(e, exc_info=True)
                        continue

                if all_addresses_text == '':
                    if individiual_address_text != '':
                        all_addresses_text = individiual_address_text.strip()
                else:
                    if individiual_address_text != '':
                        all_addresses_text = (
                            all_addresses_text +
                            '; ' +
                            individiual_address_text.strip())

            # location_info = location_info.replace(';', ',')
            # So can split on commas for both semi-colons and commas

            # To remove district ordinal
            location_info = location_info.replace('1st', '1')
            location_info = location_info.replace('2nd', '2')
            location_info = location_info.replace('3rd', '3')
            location_info = location_info.replace('4th', '4')
            location_info = location_info.replace('5th', '5')
            location_info = location_info.replace('6th', '6')
            location_info = location_info.replace('7th', '7')

            all_locations_text = ''

            list1 = location_info.split(';')

            for row in list1:
                # unit: x, condo: 4, etc.

                list2 = row.split(',')

                individiual_location_text = ''

                for l in list2:
                    # condo: x

                    try:
                        if l.strip()[-1] != ':':
                            # If first addition:
                            if individiual_location_text == '':
                                individiual_location_text = l.strip()
                            else:  # If second addition or later
                                individiual_location_text = (
                                    individiual_location_text +
                                    ', ' +
                                    l.strip())
                    except Exception, e:
                        self.logger.error(e, exc_info=True)
                        print 'Error!', e
                        continue

                    # print 'individiual_location_text:',
                    # individiual_location_text

                if all_locations_text == '':
                    if individiual_location_text != '':
                        all_locations_text = individiual_location_text.strip()
                else:
                    if individiual_location_text != '':
                        all_locations_text = (
                            all_locations_text +
                            '; ' +
                            individiual_location_text.strip())

            # unit = re.match(
            #     r"^.*UNIT\: (.*)\, CONDO", location_info).group(1)

            self.logger.info('Final values:')

            # Write over current row's values with newer, cleaner, smarter,
            # better values
            rows[i]['sellers'] = sellers.strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')
            self.logger.debug(rows[i]['sellers'])

            rows[i]['buyers'] = buyers.strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')
            self.logger.debug(rows[i]['buyers'])

            rows[i]['address'] = all_addresses_text.strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')
            self.logger.debug(rows[i]['address'])

            rows[i]['location_info'] = all_locations_text.strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')
            self.logger.debug(rows[i]['location_info'])

            rows[i]['amount'] = amt
            self.logger.debug(rows[i]['amount'])

            rows[i]['neighborhood'] = neighborhood.replace(
                '  ', ' '
            ).replace(' ,', ',')
            self.logger.debug(rows[i]['neighborhood'])

        return rows
