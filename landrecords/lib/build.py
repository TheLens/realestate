# -*- coding: utf-8 -*-

'''
Accesses scrapd HTML and hands off to parse.py.
This receives parsed, structured data and inputs to database.
'''

import glob
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords.lib import parse
from landrecords import log


class Build(object):

    '''Take structured data and enter into database.'''

    def __init__(self,
                 initial_date=Config().OPENING_DAY,
                 until_date=Config().YESTERDAY_DATE):
        '''
        Create self variables for date range and establish connections to
        the database.
        '''

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    def build_all(self):
        '''Runs through all of the building methods.'''

        log.debug('Build all')
        print 'Building...'

        log.debug('Detail')
        print '\nDetail...'
        self.dict_parse('DetailParser', 'Detail')

        log.debug('Vendor')
        print '\nVendor...'
        self.list_parse('VendorParser', 'Vendor')

        log.debug('Vendee')
        print '\nVendee...'
        self.list_parse('VendeeParser', 'Vendee')

        log.debug('Location')
        print '\nLocation...'
        self.list_parse('LocationParser', 'Location')

    def dict_parse(self, parser_name, table):
        '''Parses data structured in a dict, which is how `details` returns.'''

        session = self.sn()

        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            log.debug(initial_datetime)
            log.debug(until_datetime)
            log.debug('Current date: %s', current_date)
            print current_date

            glob_string = '%s/raw/%s/form-html/*.html' % (
                Config().DATA_DIR, current_date)

            # Allows for variable calls to a class.
            # Ex module.Class().method -> parse.parser_name(f).list_output
            for filepath in sorted(glob.glob(glob_string)):
                # log.debug('filepath: %s', filepath)
                dict_output = getattr(parse, parser_name)(filepath).form_dict()

                try:
                    with session.begin_nested():
                        i = insert(getattr(db, table))
                        i = i.values(dict_output)
                        session.execute(i)
                        session.flush()
                except Exception, error:
                    log.debug(error, exc_info=True)
                    session.rollback()

                session.commit()

            initial_datetime += timedelta(days=1)

        session.close()

    def list_parse(self, parser_name, table):
        '''
        Parses data structured as a list of dicts,
        which is how `locations`, `vendees` and `vendors` returns.
        '''

        session = self.sn()

        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            log.debug('Current date: %s', current_date)
            print current_date

            glob_string = '%s/raw/%s/form-html/*.html' % (
                Config().DATA_DIR, current_date)

            for filepath in sorted(glob.glob(glob_string)):
                list_output = getattr(parse, parser_name)(filepath).form_list()

                try:
                    with session.begin_nested():
                        i = insert(getattr(db, table))

                        # Because might have multiple rows:
                        for output in list_output:
                            vals = i.values(output)
                            session.execute(vals)
                            session.flush()
                except Exception, error:
                    log.debug(error, exc_info=True)
                    session.rollback()

                session.commit()

            initial_datetime += timedelta(days=1)

        session.close()

if __name__ == '__main__':
    pass
