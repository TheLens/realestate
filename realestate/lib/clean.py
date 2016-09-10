# -*- coding: utf-8 -*-

"""
Has two classes: `Join` and `Clean`.
`Join` joins each of the four sale tables (details, vendors, vendees and
locations) on their document ID and commits each sale to the `cleaned` table.

`Clean` has methods to check for errors, mistakes and style issues. It
utilizes `libraries.py`, a collection of items to check for.
"""

import os
import re
from sqlalchemy import insert, func, cast, Text

from realestate.db import (
    Cleaned,
    Detail,
    Location,
    Vendee,
    Vendor
)
from realestate.lib.libraries import Library
from realestate import log, USER, DATABASE_NAME


class Join(object):

    '''JOIN the four individual tables.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        self.initial_date = initial_date
        self.until_date = until_date

    def get_details(self):
        '''Returns SQL query of details table for given date range.'''

        subquery = SESSION.query(
            Detail
        ).filter(
            Detail.document_recorded >= '%s' % self.initial_date
        ).filter(
            Detail.document_recorded <= '%s' % self.until_date
        ).subquery()

        log.debug(subquery)

        SESSION.close()

        return subquery

    def get_vendees(self):
        '''Returns SQL query of vendees table for given date range.'''

        log.debug('get_vendees')

        subquery = SESSION.query(
            Vendee.document_id,
            func.string_agg(
                cast(Vendee.vendee_firstname, Text) + ' ' +
                cast(Vendee.vendee_lastname, Text),
                ', '
            ).label('buyers')
        ).group_by(
            Vendee.document_id
        ).subquery()

        # log.debug(subquery)

        SESSION.close()

        return subquery

    def get_vendors(self):
        '''Returns SQL query of vendors table for given date range.'''

        log.debug('get_vendors')

        subquery = SESSION.query(
            Vendor.document_id,
            func.string_agg(
                cast(Vendor.vendor_firstname, Text) + ' ' +
                cast(Vendor.vendor_lastname, Text),
                ', '
            ).label('sellers')
        ).group_by(
            Vendor.document_id
        ).subquery()

        # log.debug(subquery)

        SESSION.close()

        return subquery

    def get_locations(self):
        '''Returns SQL query of locations table for given date range.'''

        log.debug('get_locations')

        subquery = SESSION.query(
            Location.document_id,
            func.bool_and(Location.location_publish).label('location_publish'),
            func.string_agg(
                cast(Location.street_number, Text) + ' ' +
                cast(Location.address, Text),
                '; '
            ).label('address'),
            func.string_agg(
                'Unit: ' + cast(Location.unit, Text) + ', ' +
                'Condo: ' + cast(Location.condo, Text) + ', ' +
                'Weeks: ' + cast(Location.weeks, Text) + ', ' +
                'Subdivision: ' + cast(Location.subdivision, Text) + ', ' +
                'District: ' + cast(Location.district, Text) + ', ' +
                'Square: ' + cast(Location.square, Text) + ', ' +
                'Lot: ' + cast(Location.lot, Text),
                '; '
            ).label('location_info')
            # todo: Once SQLAlchemy supports this, add these fields this way.
            # 'mode() WITHIN GROUP (ORDER BY locations.zip_code) AS zip_code',
            # 'mode() WITHIN GROUP (ORDER BY locations.latitude) AS latitude',
            # 'mode() WITHIN GROUP (ORDER BY locations.longitude) ' +
            # ' AS longitude',
            # 'mode() WITHIN GROUP (ORDER BY locations.neighborhood) ' +
            # 'AS neighborhood'
        ).group_by(
            Location.document_id
        ).subquery()

        # log.debug(subquery)

        SESSION.close()

        return subquery

    def join_subqueries(self):
        '''Runs a JOIN on subqueries.'''

        log.debug('join_subqueries')

        subq_vendees = self.get_vendees()
        subq_vendors = self.get_vendors()
        subq_location = self.get_locations()

        log.debug('query...')

        query = SESSION.query(
            Detail.document_id,
            Detail.amount,
            Detail.document_date,
            Detail.document_recorded,
            Detail.instrument_no,
            Detail.detail_publish,
            Detail.permanent_flag,
            subq_vendees.c.buyers,
            subq_vendors.c.sellers,
            subq_location.c.location_publish,
            subq_location.c.address,
            subq_location.c.location_info
            # todo: Once SQLAlchemy supports WITHIN GROUP, uncomment these.
            # subq_location.c.zip_code,
            # subq_location.c.latitude,
            # subq_location.c.longitude,
            # subq_location.c.neighborhood
        ).join(
            subq_vendees
        ).join(
            subq_vendors
        ).join(
            subq_location
        ).filter(
            Detail.document_recorded >= '%s' % self.initial_date
        ).filter(
            Detail.document_recorded <= '%s' % self.until_date
        ).all()

        log.debug('len(query): %d', len(query))

        SESSION.close()

        return query

    def get_rows_from_query(self):
        '''Convert query result to row of dicts.'''

        log.debug('get_rows_from_query')

        query = self.join_subqueries()

        rows = []
        for row in query:
            dict_val = row.__dict__
            del dict_val['_labels']  # todo: necessary?
            # del dict_val['document_id']  # leave for now bc of ___ todo
            rows.append(dict_val)

        log.debug('len(rows): %d', len(rows))

        return rows

    def add_location_fields_temp_hack(self, incoming_rows):
        '''
        SQLAlchemy doesn't yet support WITHIN GROUP, which is necessary for
        using mode() aggregate function in PostgreSQL 9.4 (see get_locations()
        for normal use). So instead, this hack will temporary do that job.
        '''

        if USER == 'thomasthoren':
            sql = """SELECT
                document_id,
                -- mode(zip_code) AS zip_code,
                -- mode(latitude) AS latitude,
                -- mode(longitude) AS longitude,
                -- mode(neighborhood) AS neighborhood
                mode() WITHIN GROUP (ORDER BY zip_code) AS zip_code,
                mode() WITHIN GROUP (ORDER BY latitude) AS latitude,
                mode() WITHIN GROUP (ORDER BY longitude) AS longitude,
                mode() WITHIN GROUP (ORDER BY neighborhood) AS neighborhood
            FROM locations
            GROUP BY document_id"""
        else:
            sql = """SELECT
                document_id,
                mode(zip_code) AS zip_code,
                mode(latitude) AS latitude,
                mode(longitude) AS longitude,
                mode(neighborhood) AS neighborhood
                -- mode() WITHIN GROUP (ORDER BY zip_code) AS zip_code,
                -- mode() WITHIN GROUP (ORDER BY latitude) AS latitude,
                -- mode() WITHIN GROUP (ORDER BY longitude) AS longitude,
                -- mode() WITHIN GROUP (ORDER BY neighborhood) AS neighborhood
            FROM locations
            GROUP BY document_id"""

        result = self.engine.execute(sql)

        rows = []

        # Form dict
        for row in result:
            location_dict = {
                'document_id': row[0],
                'zip_code': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'neighborhood': row[4],
            }
            rows.append(location_dict)

        # Merge fields
        for incoming_row in incoming_rows:
            for row in rows:
                if incoming_row['document_id'] == row['document_id']:
                    incoming_row['zip_code'] = row['zip_code']
                    incoming_row['latitude'] = row['latitude']
                    incoming_row['longitude'] = row['longitude']
                    incoming_row['neighborhood'] = row['neighborhood']

        for row in incoming_rows:
            del row['document_id']  # Not part of Cleaned

        return incoming_rows


class Clean(object):

    '''Clean the joined tables and commit to cleaned.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

    def update_cleaned_geom(self):
        '''Update the PostGIS geom field in the cleaned table.'''

        log.debug('Update Cleaned geometry')

        sql = """UPDATE cleaned
            SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"""

        self.engine.execute(sql)

    @staticmethod
    def prep_rows(rows):
        '''Returns all rows in Titlecase.'''

        # This loop returns text that is not all-caps, but is still flawed:
        # to standardize upper and lowercases
        for row in rows:
            # Capitalizes the first letter in each word.
            # Results in words like Llc, Xiv, etc

            row['sellers'] = row['sellers'].title()
            row['buyers'] = row['buyers'].title()
            row['address'] = row['address'].title()
            row['location_info'] = row['location_info'].title()
            row['neighborhood'] = row['neighborhood'].title()

        return rows

    @staticmethod
    def check_for_acronyms(rows):
        '''Corrects acronyms.'''

        # This loop scans for the above problem words and replaces them with
        # their substitutes:
        for row in rows:
            # Check for occurences of problematic acronyms
            for acronym in Library().acronyms:
                acronym0 = acronym[0]  # Problem acronym
                acronym1 = acronym[1]  # Solution acronym
                # If find problem acronym (acronym0) in a string,
                # replace with solution acronym (acronym1)

                # log.debug(row['sellers'])
                # log.debug(type(row['sellers']))

                row['sellers'] = re.sub(acronym0, acronym1, row['sellers'])

                # log.debug(row['sellers'])
                # log.debug(type(row['sellers']))

                row['buyers'] = re.sub(acronym0, acronym1, row['buyers'])
                row['address'] = re.sub(acronym0, acronym1, row['address'])
                row['location_info'] = re.sub(
                    acronym0, acronym1, row['location_info'])

        return rows

    @staticmethod
    def check_for_mcnames(rows):
        '''Corrects Mc___ names.'''

        for row in rows:
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

    @staticmethod
    def check_for_abbreviations(rows):
        '''Corrects abbreviations.'''

        for row in rows:
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

    @staticmethod
    def check_for_adress_abbreviations(rows):
        '''Corrects address abbreviations.'''

        for row in rows:
            # Fix address abbreviations (for AP style purposes)
            for address_abbreviation in Library().streets:
                address0 = address_abbreviation[0]
                address1 = address_abbreviation[1]
                row['address'] = re.sub(
                    address0, address1, row['address'])
                row['location_info'] = re.sub(
                    address0, address1, row['location_info'])
                # Good for "E" to "E." too:
                row['address'] = re.sub(
                    address0, address1, row['address'])

        return rows

    @staticmethod
    def check_for_middle_initials(rows):
        '''Corrects middle initials.'''

        for row in rows:
            for middle_initial in Library().middle_initials:
                middle_initial0 = middle_initial[0]
                middle_initial1 = middle_initial[1]

                # log.debug(row['sellers'])
                # log.debug(type(row['sellers']))

                row['sellers'] = re.sub(
                    middle_initial0, middle_initial1, row['sellers'])

                # log.debug(row['sellers'])
                # log.debug(type(row['sellers']))

                row['buyers'] = re.sub(
                    middle_initial0, middle_initial1, row['buyers'])

        return rows

    @staticmethod
    def check_for_neighborhood_names(rows):
        '''Corrects neighborhood names.'''

        for row in rows:
            for neighborhood_name in Library().neighborhood_names:
                name0 = neighborhood_name[0]
                name1 = neighborhood_name[1]
                row['neighborhood'] = re.sub(
                    name0, name1, row['neighborhood'])

        return rows

    @staticmethod
    def regex_subs(rows):
        '''More than simple find-and-replace tasks.'''

        for row in rows:
            # Must do regex for "St" and others. Imagine "123 Star St".
            # Scanning for " St" in the above loop would catch the start of
            # the street name here. "St " wouldn't work either.
            # Check for "St" followed by end-of-line character:
            row['address'] = re.sub(r"St$", r"St.", row['address'])
            row['address'] = re.sub(r"Ave$", r"Ave.", row['address'])
            row['address'] = re.sub(r"Dr$", r"Dr.", row['address'])
            row['sellers'] = re.sub(r"Inc$", r"Inc.", row['sellers'])
            row['buyers'] = re.sub(r"Inc$", r"Inc.", row['buyers'])

        return rows

    @staticmethod
    def convert_amounts(rows):
        '''Convert string, with or without $ and commas, to rounded int.'''

        for row in rows:
            row['amount'] = str(row['amount'])
            row['amount'] = re.sub(r'\$', r'', row['amount'])  # remove the $
            row['amount'] = re.sub(r',', r'', row['amount'])  # remove comma
            row['amount'] = float(row['amount'])  # change string to a float
            row['amount'] = round(row['amount'])  # round to nearest dollar
            row['amount'] = int(row['amount'])

        return rows

    def clean_rows(self, rows):
        '''Run rows through all cleaning methods.'''

        rows = self.check_for_acronyms(rows)
        rows = self.check_for_mcnames(rows)
        rows = self.check_for_abbreviations(rows)
        rows = self.check_for_adress_abbreviations(rows)
        rows = self.check_for_middle_initials(rows)
        rows = self.check_for_neighborhood_names(rows)

        rows = self.regex_subs(rows)
        # log.debug(len(rows))

        rows = self.convert_amounts(rows)
        # log.debug(len(rows))

        rows = self.other_stuff_addresses(rows)
        # log.debug(len(rows))

        rows = self.other_stuff_location_info(rows)
        # log.debug(len(rows))

        rows = self.clean_punctuation(rows)
        # log.debug(len(rows))

        return rows

    @staticmethod
    def clean_punctuation(rows):
        '''Fix punctuation (leading/trailing spaces or commas).'''

        for row in rows:
            row['sellers'] = row['sellers'].strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')

            row['buyers'] = row['buyers'].strip(
                ' ,'
            ).replace('  ', ' ').replace(' ,', ',')

            row['address'] = row['address'].strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')

            row['location_info'] = row['location_info'].strip(
                " ,"
            ).replace('  ', ' ').replace(' ,', ',')

            row['neighborhood'] = row['neighborhood'].replace(
                '  ', ' '
            ).replace(' ,', ',')

        return rows

    @staticmethod
    def other_stuff_addresses(rows):
        '''Runs checks for addresses.'''

        # log.debug(rows)

        for row in rows:
            all_addresses_text = ''

            address_list1 = row['address'].split(';')

            for i in address_list1:
                address_list2 = i.split(',')

                individual_address_text = ''

                for j in address_list2:
                    try:
                        # If first addition:
                        if individual_address_text == '':
                            individual_address_text = j.strip()
                        else:  # If second addition or later
                            individual_address_text = (
                                individual_address_text +
                                ', ' +
                                j.strip())
                    except Exception, error:
                        log.exception(error, exc_info=True)
                        continue

                if all_addresses_text == '' and individual_address_text != '':
                    all_addresses_text = individual_address_text.strip()
                elif individual_address_text != '':
                    all_addresses_text = (
                        all_addresses_text +
                        '; ' +
                        individual_address_text.strip())

            # location_info = location_info.replace(';', ',')
            # So can split on commas for both semi-colons and commas

            row['address'] = all_addresses_text

        return rows

    @staticmethod
    def other_stuff_location_info(rows):
        '''Runs checks for location_info.'''

        for row in rows:
            # To remove district ordinal
            row['location_info'] = row['location_info'].replace('1st', '1')
            row['location_info'] = row['location_info'].replace('2nd', '2')
            row['location_info'] = row['location_info'].replace('3rd', '3')
            row['location_info'] = row['location_info'].replace('4th', '4')
            row['location_info'] = row['location_info'].replace('5th', '5')
            row['location_info'] = row['location_info'].replace('6th', '6')
            row['location_info'] = row['location_info'].replace('7th', '7')

            all_locations_text = ''

            list1 = row['location_info'].split(';')

            for i in list1:
                list2 = i.split(',')

                individiual_location_text = ''

                for j in list2:
                    try:
                        if j.strip()[-1] != ':':
                            # If first addition:
                            if individiual_location_text == '':
                                individiual_location_text = j.strip()
                            else:  # If second addition or later
                                individiual_location_text = (
                                    individiual_location_text +
                                    ', ' +
                                    j.strip())
                    except Exception, error:
                        log.exception(error, exc_info=True)
                        continue

                if all_locations_text == '':
                    if individiual_location_text != '':
                        all_locations_text = individiual_location_text.strip()
                else:
                    if individiual_location_text != '':
                        all_locations_text = (
                            all_locations_text +
                            '; ' +
                            individiual_location_text.strip())

            row['location_info'] = all_locations_text

        return rows

    def commit_rows(self, rows):
        '''Commits JOIN-ed rows to the cleaned table.'''

        log.debug('Committing %d rows', len(rows))

        for count, row in enumerate(rows):
            log.debug("Row %d", count)
            try:
                with SESSION.begin_nested():
                    i = insert(Cleaned)
                    i = i.values(row)
                    SESSION.execute(i)
                    SESSION.flush()
            except Exception, error:
                log.debug('count: %s', count)
                log.exception(error, exc_info=True)
                SESSION.rollback()

            SESSION.commit()

        log.debug('%d rows committed', len(rows))

        # session.close()

    def main(self):
        '''Run Join() and Clean() scripts.'''

        log.info('Clean')
        print 'Cleaning...'

        log.debug('get_rows_from_query')
        rows = Join(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).get_rows_from_query()

        log.debug('add_location_fields_temp_hack')
        rows = Join(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).add_location_fields_temp_hack(rows)

        log.debug('len(rows): %d', len(rows))

        prepped_rows = self.prep_rows(rows)

        clean_rows = self.clean_rows(prepped_rows)

        self.commit_rows(clean_rows)

if __name__ == '__main__':
    Clean().main()
