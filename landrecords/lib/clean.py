# -*- coding: utf-8 -*-

import re
from subprocess import call
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib.libraries import Library
from landrecords.lib.log import Log


class Clean(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('clean').logger

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        self.engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    def update_cleaned_geom(self):
        print 'Updating Cleaned geometry...'
        call(['psql',
              'landrecords',
              '-c',
              'UPDATE cleaned SET geom = ST_SetSRID(' +
              'ST_MakePoint(longitude, latitude), 4326);'])

    def get_rows_with_neighborhood(self):
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
            row = dict(row)
            row['neighborhood'] = "None"
            rows.append(row)

        return rows

    def commit_rows(self, rows):
        for row in rows:
            try:
                with self.session.begin_nested():
                    i = insert(db.Cleaned)
                    i = i.values(row)
                    self.session.execute(i)
                    self.session.flush()
            except Exception, e:
                self.log.exception(e, exc_info=True)
                self.session.rollback()

        self.session.commit()

    def prep_rows(self, rows):
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

        return rows

    def main(self):
        print 'Cleaning...'

        nbhd_rows = self.get_rows_with_neighborhood()
        no_nbhd_rows = self.get_rows_without_neighborhood()

        rows = nbhd_rows + no_nbhd_rows

        prepped_rows = self.prep_rows(rows)
        clean_rows = self.clean_rows(prepped_rows)

        self.commit_rows(clean_rows)

    def check_for_acronyms(self, rows):
        # This loop scans for the above problem words and replaces them with
        # their substitutes:
        for i, row in enumerate(rows):
            # Check for occurences of problematic acronyms
            for acronym in Library().acronyms:
                acronym0 = acronym[0]  # Problem acronym
                acronym1 = acronym[1]  # Solution acronym
                # If find problem acronym (acronym0) in a string,
                # replace with solution acronym (acronym1)
                row['sellers'] = re.sub(acronym0, acronym1, row['sellers'])
                row['buyers'] = re.sub(acronym0, acronym1, row['buyers'])
                row['address'] = re.sub(acronym0, acronym1, row['address'])
                row['location_info'] = re.sub(
                    acronym0, acronym1, row['location_info'])

        return rows

    def check_for_mcnames(self, rows):
        for i, row in enumerate(rows):
            # Check for occurences of problematic "Mc" names. Corrections
            # assume that the letter after should be capitalized:
            for mcname in Library().mc_names:
                mcname0 = mcname[0]
                mcname1 = mcname[1]
                row['sellers'] = re.sub(mcname0, mcname1, row['sellers'])
                row['buyers'] = re.sub(mcname0, mcname1, row['buyers'])
                row['address'] = re.sub(mcname0, mcname1, row['address'])
                row['location_info'] = re.sub(
                    mcname0, mcname1, row['location_info'])

        return rows

    def check_for_abbreviations(self, rows):
        for i, row in enumerate(rows):
            # Check for problematic abbreviations:
            for abbreviation in Library().abbreviations:
                abbreviation0 = abbreviation[0]
                abbreviation1 = abbreviation[1]
                row['sellers'] = re.sub(
                    abbreviation0, abbreviation1, row['sellers'])
                row['buyers'] = re.sub(
                    abbreviation0, abbreviation1, row['buyers'])
                row['address'] = re.sub(
                    abbreviation0, abbreviation1, row['address'])
                row['location_info'] = re.sub(
                    abbreviation0, abbreviation1, row['location_info'])

        return rows

    def check_for_adress_abbreviations(self, rows):
        for i, row in enumerate(rows):
            # Fix address abbreviations (for AP style purposes)
            for address_abbreviation in Library().streets:
                address0 = address_abbreviation[0]
                address1 = address_abbreviation[1]
                row['address'] = re.sub(
                    address0, address1, row['address'])
                row['location_info'] = re.sub(
                    address0, address1, row['location_info'])

        return rows

    def check_for_middle_initials(self, rows):
        for i, row in enumerate(rows):
            for middle_initial in Library().middle_initials:
                middle_initial0 = middle_initial[0]
                middle_initial1 = middle_initial[1]
                row['sellers'] = re.sub(
                    middle_initial0, middle_initial1, row['sellers'])
                row['buyers'] = re.sub(
                    middle_initial0, middle_initial1, row['buyers'])

        return rows

    def check_for_neighborhood_names(self, rows):
        for i, row in enumerate(rows):
            for neighborhood_name in Library().neighborhood_names:
                name0 = neighborhood_name[0]
                name1 = neighborhood_name[1]
                row['neighborhood'] = re.sub(
                    name0, name1, row['neighborhood'])

        return rows

    def misc_subs(self, rows):
        for i, row in enumerate(rows):
            # Must do regex for "St" and others. Imagine "123 Star St".
            # Scanning for " St" in the above loop would catch the start of
            # the street name here. "St " wouldn't work either.
            # Check for "St" followed by end-of-line character:
            row['address'] = re.sub(r"St$", r"St.", row['address'])
            row['address'] = re.sub(r"Ave$", r"Ave.", row['address'])
            row['address'] = re.sub(r"Dr$", r"Dr.", row['address'])
            row['address'] = re.sub(r" N ", r" N. ", row['address'])
            row['address'] = re.sub(r" S ", r" S. ", row['address'])
            row['address'] = re.sub(r" E ", r" E. ", row['address'])
            row['address'] = re.sub(r" W ", r" W. ", row['address'])
            row['sellers'] = re.sub(r"Inc$", r"Inc.", row['sellers'])
            row['buyers'] = re.sub(r"Inc$", r"Inc.", row['buyers'])

        return rows

    def convert_amounts(self, rows):
        for i, row in enumerate(rows):
            row['amount'] = str(row['amount'])
            row['amount'] = re.sub(r'\$', r'', row['amount'])  # remove the $
            row['amount'] = re.sub(r',', r'', row['amount'])  # remove comma
            row['amount'] = float(row['amount'])  # change string to a float
            row['amount'] = round(row['amount'])  # round to nearest dollar
            row['amount'] = int(row['amount'])

        return rows

    def clean_rows(self, rows):
        rows = self.check_for_acronyms(rows)
        rows = self.check_for_mcnames(rows)
        rows = self.check_for_abbreviations(rows)
        rows = self.check_for_adress_abbreviations(rows)
        rows = self.check_for_middle_initials(rows)
        rows = self.check_for_neighborhood_names(rows)

        rows = self.misc_subs(rows)
        rows = self.convert_amounts(rows)

        # print 'rows:', rows

        rows = self.other_stuff_to_clean(rows)

        return rows

    def other_stuff_to_clean(self, rows):
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

            all_addresses_text = ''

            # self.log.debug(address)

            address_list1 = address.split(';')

            for row in address_list1:
                # self.log.debug(row)
                # unit: x, condo: 4, etc.
                address_list2 = row.split(',')

                individiual_address_text = ''

                for l in address_list2:
                    # self.log.debug(l)
                    # condo: x
                    try:
                        # If first addition:
                        if individiual_address_text == '':
                            individiual_address_text = l.strip()
                        else:  # If second addition or later
                            individiual_address_text = (
                                individiual_address_text +
                                ', ' +
                                l.strip())
                    except Exception, e:
                        self.log.exception(e, exc_info=True)
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
                        self.log.exception(e, exc_info=True)
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

            # Write over current row's values with newer, cleaner, smarter,
            # better values
            rows[i]['sellers'] = sellers.strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')

            rows[i]['buyers'] = buyers.strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')

            rows[i]['address'] = all_addresses_text.strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')

            rows[i]['location_info'] = all_locations_text.strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')

            rows[i]['amount'] = amt

            rows[i]['neighborhood'] = neighborhood.replace(
                '  ', ' '
            ).replace(' ,', ',')

        return rows
