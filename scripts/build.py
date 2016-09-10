# -*- coding: utf-8 -*-

"""
Receive sale HTML, hands off to parse.py, which returns structured data.

This then commits the returned structured data.
"""

# import os
import glob
from datetime import datetime, timedelta
from sqlalchemy import insert

from www import db
from www import log, PROJECT_DIR, SESSION  # ENGINE_STRING
from scripts import parse


class Build(object):
    """Take structured data and enter into database."""

    def __init__(self, initial_date=None, until_date=None):
        """Create class variables for date range and connect to database."""
        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: {}'.format(self.initial_date))
        log.debug('self.until_date: {}'.format(self.until_date))

    def build_all(self):
        """Run through all of the building methods."""
        log.debug('Build all')
        print('Building...')

        log.debug('Detail')
        print('\nAdding to details table for:')
        self.dict_parse('DetailParser', 'Detail')

        log.debug('Vendor')
        print('\nAdding to vendors table for:')
        self.list_parse('VendorParser', 'Vendor')

        log.debug('Vendee')
        print('\nAdding to vendees table for:')
        self.list_parse('VendeeParser', 'Vendee')

        log.debug('Location')
        print('\nAdding to locations table for:')
        self.list_parse('LocationParser', 'Location')

    def dict_parse(self, parser_name, table):
        """Parse data structured in a dict, which is how `details` returns."""
        initial_datetime = datetime.strptime(
            self.initial_date, '%Y-%m-%d').date()
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d').date()

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')
            log.debug('Current date: {}'.format(current_date))
            print(current_date)

            glob_string = '{0}/data/raw/{1}/form-html/*.html'.format(
                PROJECT_DIR, current_date)

            # Allows for variable calls to a class.
            # Ex module.Class().method -> parse.parser_name(f).list_output
            for filepath in sorted(glob.glob(glob_string)):
                # log.debug('filepath: {}'.format(filepath))
                dict_output = getattr(parse, parser_name)(filepath).form_dict()

                self.commit_to_database(table, dict_output)

            initial_datetime += timedelta(days=1)

    def commit_to_database(self, table, output):
        """Commit to database using nested transactions and exceptions."""
        try:
            # TODO: Is this the correct method for this?
            with SESSION.begin_nested():
                i = insert(getattr(db, table))
                vals = i.values(output)
                SESSION.execute(vals)  # TODO: What is this?
                SESSION.flush()
        except Exception as error:
            log.debug(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()  # TODO: Should this be here?

    def list_parse(self, parser_name, table):
        """
        Parse data structured as a list of dicts.

        This is how `locations`, `vendees` and `vendors` returns.
        """
        initial_datetime = datetime.strptime(
            self.initial_date, '%Y-%m-%d').date()
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d').date()

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            log.debug('Current date: {}'.format(current_date))
            print(current_date)

            glob_string = '{0}/data/raw/{1}/form-html/*.html'.format(
                PROJECT_DIR, current_date)

            for filepath in sorted(glob.glob(glob_string)):
                list_output = getattr(parse, parser_name)(filepath).form_list()

                # Because output might have multiple rows:
                for output in list_output:
                    self.commit_to_database(table, output)

            initial_datetime += timedelta(days=1)
