# -*- coding: utf-8 -*-

"""
Command line tool for deleting all records for a given date or date range.

Meant for quicker testing.

Usage:
    delete_dates.py <single_date>
    delete_dates.py <early_date> <late_date>

Options:
    -h, --help  Show help screen.
    --version   Show version number.

Dates are in the format YYYY-MM-DD. Ex. 2016-12-31
"""

import os
import psycopg2

from datetime import datetime
from docopt import docopt

from www.db import Cleaned, Detail
from www import log, SESSION, DATABASE_NAME


class BadDateRangeError(Exception):
    """Error for when date range is backward."""

    pass


class DeleteDates(object):
    """Delete certain dates from database."""

    def __init__(self, initial_date=None, until_date=None):
        """Initialize self variables and establish connection to database."""
        engine_string = (
            'host=localhost dbname={0} user={1} password={2}').format(
                DATABASE_NAME,
                os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
                os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'))
        self.conn = psycopg2.connect(engine_string)
        self.cursor = self.conn.cursor()

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: {}'.format(self.initial_date))
        log.debug('self.until_date: {}'.format(self.until_date))

    def main(self):
        """Run Join() and Clean() scripts."""
        self.delete_details()
        self.delete_cleaned()
        self.vacuum()

    def vacuum(self):
        """Update database."""
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        sql = 'VACUUM;'
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)

    def delete_details(self):
        """TODO."""
        SESSION.query(
            Detail
        ).filter(
            Detail.document_recorded >= '{}'.format(self.initial_date)
        ).filter(
            Detail.document_recorded <= '{}'.format(self.until_date)
        ).delete()

        SESSION.commit()

    def delete_cleaned(self):
        """TODO."""
        SESSION.query(
            Cleaned
        ).filter(
            Cleaned.document_recorded >= '{}'.format(self.initial_date)
        ).filter(
            Cleaned.document_recorded <= '{}'.format(self.until_date)
        ).delete()

        SESSION.commit()


def cli_has_errors(arguments):
    """Check for any CLI parsing errors."""
    all_arguments = (
        arguments['<single_date>'] is not None and
        arguments['<early_date>'] is not None and
        arguments['<late_date>'] is not None)

    if all_arguments:
        # print("Must use single date or date range, but not both.")
        return True

    no_arguments = (
        arguments['<single_date>'] is not None and
        arguments['<early_date>'] is not None and
        arguments['<late_date>'] is not None)

    if no_arguments:
        # print("You must supply at least one date.")
        return True

    single_and_other_arguments = (
        (
            arguments['<single_date>'] is not None and
            arguments['<early_date>'] is not None
        ) or
        (
            arguments['<single_date>'] is not None and
            arguments['<late_date>'] is not None
        ))

    if single_and_other_arguments:
        # print("Cannot use a single date and a date range bound.")
        return True

    one_date_bound_only = (
        (
            arguments['<early_date>'] is not None and
            arguments['<late_date>'] is None
        ) or
        (
            arguments['<early_date>'] is None and
            arguments['<late_date>'] is not None
        ))

    if one_date_bound_only:
        # print("Must pick both ends of a date range bound.")
        return True

    # All good
    return False


def cli(arguments):
    """Parse command-line arguments."""
    # Catch any missed errors.
    if cli_has_errors(arguments):
        return

    if arguments['<single_date>']:  # Single date
        early_date = arguments['<single_date>']
        late_date = arguments['<single_date>']

        log.info('Initializing single date: {}.'.format(early_date))
    elif arguments['<early_date>'] and arguments['<late_date>']:  # Date range
        early_date = arguments['<early_date>']
        late_date = arguments['<late_date>']

        log.info('Initializing date range: {0} to {1}.'.format(
            early_date, late_date))

    # Check for errors
    early_datetime = datetime.strptime(early_date, "%Y-%m-%d")
    late_datetime = datetime.strptime(late_date, "%Y-%m-%d")

    if early_datetime > late_datetime:
        raise BadDateRangeError("The date range does not make sense.")

    DeleteDates(initial_date=early_date, until_date=late_date).main()

if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.0.1")
    cli(arguments)
