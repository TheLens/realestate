# -*- coding: utf-8 -*-

'''
Receives sale HTML, hands off to parse.py, which returns structured data.
This then commits the returned structured data.
'''

import os
import glob
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from realestate import db
from realestate.lib import parse
from realestate import log, PROJECT_DIR, DATABASE_NAME


class Build(object):

    '''Take structured data and enter into database.'''

    def __init__(self, initial_date=None, until_date=None):
        '''
        Create self variables for date range and establish connections to
        the database.
        '''

        base = declarative_base()
        engine = create_engine(
            'postgresql://%s:%s@localhost/%s' % (
                os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
                os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
                DATABASE_NAME
            )
        )
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

    def build_all(self):
        '''Runs through all of the building methods.'''

        log.debug('Build all')
        print 'Building...'

        log.debug('Detail')
        print '\nAdding to details table for:'
        self.dict_parse('DetailParser', 'Detail')

        log.debug('Vendor')
        print '\nAdding to vendors table for:'
        self.list_parse('VendorParser', 'Vendor')

        log.debug('Vendee')
        print '\nAdding to vendees table for:'
        self.list_parse('VendeeParser', 'Vendee')

        log.debug('Location')
        print '\nAdding to locations table for:'
        self.list_parse('LocationParser', 'Location')

    def dict_parse(self, parser_name, table):
        '''
        Parses data structured in a dict, which is how `details` returns.
        '''

        initial_datetime = datetime.strptime(
            self.initial_date, '%Y-%m-%d').date()
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d').date()

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')
            log.debug('Current date: %s', current_date)
            print current_date

            glob_string = '%s/data/raw/%s/form-html/*.html' % (
                PROJECT_DIR, current_date)

            # Allows for variable calls to a class.
            # Ex module.Class().method -> parse.parser_name(f).list_output
            for filepath in sorted(glob.glob(glob_string)):
                # log.debug('filepath: %s', filepath)
                dict_output = getattr(parse, parser_name)(filepath).form_dict()

                self.commit_to_database(table, dict_output)

            initial_datetime += timedelta(days=1)

    def commit_to_database(self, table, output):
        '''Commits to database using nested transactions and exceptions.'''

        session = self.sn()

        try:
            with session.begin_nested():
                i = insert(getattr(db, table))
                vals = i.values(output)
                session.execute(vals)
                session.flush()
        except Exception, error:
            log.debug(error, exc_info=True)
            session.rollback()

        session.commit()

        session.close()

    def list_parse(self, parser_name, table):
        '''
        Parses data structured as a list of dicts,
        which is how `locations`, `vendees` and `vendors` returns.
        '''

        initial_datetime = datetime.strptime(
            self.initial_date, '%Y-%m-%d').date()
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d').date()

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            log.debug('Current date: %s', current_date)
            print current_date

            glob_string = '%s/data/raw/%s/form-html/*.html' % (
                PROJECT_DIR, current_date)

            for filepath in sorted(glob.glob(glob_string)):
                list_output = getattr(parse, parser_name)(filepath).form_list()

                # Because output might have multiple rows:
                for output in list_output:
                    self.commit_to_database(table, output)

            initial_datetime += timedelta(days=1)

if __name__ == '__main__':
    pass
