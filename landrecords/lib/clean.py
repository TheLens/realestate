# -*- coding: utf-8 -*-

'''JOIN the four individual tables, clean and commit to cleaned'''

import re

from subprocess import call
from sqlalchemy import create_engine, insert, func, cast, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords.lib.libraries import Library
from landrecords.lib.log import Log


class Join(object):

    '''JOIN the four individual tables'''

    def __init__(self,
                 initial_date=Config().OPENING_DAY,
                 until_date=Config().YESTERDAY_DATE):

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    def get_details(self):
        '''Gathers relevant Detail fields for Cleaned'''

        subq = self.session.query(
            db.Detail
        ).filter(
            db.Detail.document_recorded >= '%s' % self.initial_date
        ).filter(
            db.Detail.document_recorded <= '%s' % self.until_date
        ).subquery()

        log.debug(subq)

        return subq

    def get_vendees(self):
        '''Gathers relevant Vendee fields for Cleaned'''

        subq = self.session.query(
            db.Vendee.document_id,
            func.string_agg(
                cast(db.Vendee.vendee_firstname, Text) + ' ' +
                cast(db.Vendee.vendee_lastname, Text),
                ', '
            ).label('buyers')
        ).group_by(
            db.Vendee.document_id
        ).subquery()

        # log.debug(subq)

        return subq

    def get_vendors(self):
        '''Gathers relevant Vendor fields for Cleaned'''

        subq = self.session.query(
            db.Vendor.document_id,
            func.string_agg(
                cast(db.Vendor.vendor_firstname, Text) + ' ' +
                cast(db.Vendor.vendor_lastname, Text),
                ', '
            ).label('sellers')
        ).group_by(
            db.Vendor.document_id
        ).subquery()

        # log.debug(subq)

        return subq

    def get_locations(self):
        '''Gathers relevant Location fields for Cleaned'''

        subq = self.session.query(
            db.Location.document_id,
            func.min(db.Location.location_publish).label('location_publish'),
            func.string_agg(
                cast(db.Location.street_number, Text) + ' ' +
                cast(db.Location.address, Text),
                '; '
            ).label('address'),
            func.string_agg(
                'Unit: ' + cast(db.Location.unit, Text) + ' ' +
                'Condo: ' + cast(db.Location.condo, Text) + ' ' +
                'Weeks: ' + cast(db.Location.weeks, Text) + ' ' +
                'Subdivision: ' + cast(db.Location.subdivision, Text) + ' ' +
                'District: ' + cast(db.Location.district, Text) + ' ' +
                'Square: ' + cast(db.Location.square, Text) + ' ' +
                'Lot: ' + cast(db.Location.lot, Text),
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
            db.Location.document_id
        ).subquery()

        # log.debug(subq)

        return subq

    def join_subqueries(self):
        '''Runs a JOIN on subqueries'''

        # subq_details = self.get_details()
        subq_vendees = self.get_vendees()
        subq_vendors = self.get_vendors()
        subq_location = self.get_locations()

        q = self.session.query(
            db.Detail.document_id,
            db.Detail.amount,
            db.Detail.document_date,
            db.Detail.document_recorded,
            db.Detail.instrument_no,
            db.Detail.detail_publish,
            db.Detail.permanent_flag,
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
            db.Detail.document_recorded >= '%s' % self.initial_date
        ).filter(
            db.Detail.document_recorded <= '%s' % self.until_date
        ).all()

        log.debug('len(q): %d' % len(q))

        return q

    def get_rows_from_query(self):
        '''Convert query result to row of dicts'''

        q = self.join_subqueries()

        rows = []
        for row in q:
            d = row.__dict__
            del d['_labels']  # todo: necessary?
            rows.append(d)

        log.debug('len(rows): %d' % len(rows))

        return rows

    def temp_hack_to_add_location_fields(self, incoming_rows):
        '''SQLAlchemy doesn't yet support WITHIN GROUP,
           which is necessary for using mode() aggregate function
           in PostgreSQL 9.4 (see get_locations() for normal use).
           So instead, this hack will temporary do that job.'''

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

        result = self.engine.execute(sql)

        rows = []

        # Form dict
        for row in result:
            d = {
                'document_id': row[0],
                'zip_code': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'neighborhood': row[4],
            }
            rows.append(d)

        # Merge fields
        for a in incoming_rows:
            for b in rows:
                if a['document_id'] == b['document_id']:
                    a['zip_code'] = b['zip_code']
                    a['latitude'] = b['latitude']
                    a['longitude'] = b['longitude']
                    a['neighborhood'] = b['neighborhood']

        for row in incoming_rows:
            del row['document_id']  # Not part of Cleaned

        return incoming_rows


class Clean(object):

    '''Clean the joined tables and commit to cleaned'''

    def __init__(self,
                 initial_date=Config().OPENING_DAY,
                 until_date=Config().YESTERDAY_DATE):

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    def update_cleaned_geom(self):
        '''Update the PostGIS geom field in the cleaned table'''

        log.debug('Update Cleaned geometry')

        call(['psql',
              'landrecords',
              '-c',
              'UPDATE cleaned SET geom = ST_SetSRID(' +
              'ST_MakePoint(longitude, latitude), 4326);'])

    def prep_rows(self, rows):
        '''Returns all rows in Titlecase'''

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

    def prep_locations_for_geocoding(self):
        '''Geocodes existing records and/or new records — any
           records that have not yet been geocoded. Geocoder takes
           strings: 4029 Ulloa St, New Orleans, LA 70119
           I took a shortcut. Instead of finding a way to
           concatenate the address pieces on the fly, I
           concatenated them all into a new column, then read
           from that column. Sloppy, but it works for now.'''

        self.engine.execute("""UPDATE locations
            SET full_address = street_number::text || ' ' ||
            address::text || ', New Orleans, LA';""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' ST ', ' SAINT ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' FIRST ', ' 1ST ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' SECOND ', ' 2ND ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' THIRD ', ' 3RD ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' FOURTH ', ' 4TH ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' FIFTH ', ' 5TH ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' SIXTH ', ' 6TH ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' SEVENTH ', ' 7TH ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' EIGHTH ', ' 8TH ');""")
        self.engine.execute("""UPDATE locations
            SET full_address = replace(full_address, ' NINTH ', ' 9TH ');""")

    def check_for_acronyms(self, rows):
        '''Correct acronyms'''

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

    def check_for_mcnames(self, rows):
        '''Correct Mc___ names'''

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

    def check_for_abbreviations(self, rows):
        '''Correct abbreviations'''

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

    def check_for_adress_abbreviations(self, rows):
        '''Correct address abbreviations'''

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

    def check_for_middle_initials(self, rows):
        '''Correct middle initials'''

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

    def check_for_neighborhood_names(self, rows):
        '''Correct neighborhood names'''

        for row in rows:
            for neighborhood_name in Library().neighborhood_names:
                name0 = neighborhood_name[0]
                name1 = neighborhood_name[1]
                row['neighborhood'] = re.sub(
                    name0, name1, row['neighborhood'])

        return rows

    def regex_subs(self, rows):
        '''More than simple find-and-replace tasks'''

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

    def convert_amounts(self, rows):
        '''Convert string, with or without $ and commas, to rounded int'''

        for row in rows:
            row['amount'] = str(row['amount'])
            row['amount'] = re.sub(r'\$', r'', row['amount'])  # remove the $
            row['amount'] = re.sub(r',', r'', row['amount'])  # remove comma
            row['amount'] = float(row['amount'])  # change string to a float
            row['amount'] = round(row['amount'])  # round to nearest dollar
            row['amount'] = int(row['amount'])

        return rows

    def clean_rows(self, rows):
        '''Run rows through all cleaning methods'''

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

    def clean_punctuation(self, rows):
        '''Fix punctuation (leading/trailing spaces or commas)'''

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

    def other_stuff_addresses(self, rows):
        '''Run checks for addresses'''

        # This loop scans for the above problem words and replaces them with
        # their substitutes:

        # log.debug(rows)

        for row in rows:
            all_addresses_text = ''

            address_list1 = row['address'].split(';')

            for i in address_list1:
                address_list2 = i.split(',')

                individual_address_text = ''

                for l in address_list2:
                    try:
                        # If first addition:
                        if individual_address_text == '':
                            individual_address_text = l.strip()
                        else:  # If second addition or later
                            individual_address_text = (
                                individual_address_text +
                                ', ' +
                                l.strip())
                    except Exception, e:
                        log.exception(e, exc_info=True)
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

    def other_stuff_location_info(self, rows):
        '''Run checks for location_info'''

        # This loop scans for the above problem words and replaces them with
        # their substitutes:
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

                for l in list2:
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
                        log.exception(e, exc_info=True)
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
        '''Commits JOIN-ed rows to the Cleaned table'''

        log.debug('%d rows committed' % len(rows))

        for row in rows:
            try:
                with self.session.begin_nested():
                    i = insert(db.Cleaned)
                    i = i.values(row)
                    self.session.execute(i)
                    self.session.flush()
            except Exception, e:
                log.exception(e, exc_info=True)
                self.session.rollback()

        self.session.commit()

    def main(self):
        '''Run Join() and Clean() scripts'''

        log.debug('Clean')

        # log.debug('rows')
        rows = Join(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).get_rows_from_query()

        rows = Join(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).temp_hack_to_add_location_fields(rows)

        log.debug('len(rows): %d', len(rows))

        # log.debug('prepped rows')
        prepped_rows = self.prep_rows(rows)
        # log.debug(len(prepped_rows))

        # log.debug('clean rows')
        clean_rows = self.clean_rows(prepped_rows)
        # log.debug(len(clean_rows))

        # log.debug('commit rows')
        self.commit_rows(clean_rows)

        # log.debug('prep_locations_for_geocoding')
        self.prep_locations_for_geocoding()

if __name__ == '__main__':
    log = Log('initialize').initialize_log()

    Clean().main()
