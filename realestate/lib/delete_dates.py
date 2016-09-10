# -*- coding: utf-8 -*-

'''
Accpts command line parameters for quick deletion of all records for a given
date or date range. Meant for quicker testing.

```bash
python delete_dates.py '2014-02-18' # Deletes one day
python delete_dates.py '2014-02-18' '2014-02-19' # Deletes range
```
'''

import os
import sys
import psycopg2

from realestate.db import (
    Cleaned,
    Detail
)
from realestate import log, SESSION, DATABASE_NAME


class DeleteDates(object):

    '''Deletes certain dates from database.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        self.conn = psycopg2.connect(
            'host=localhost dbname=%s user=%s password=%s' % (
                DATABASE_NAME,
                os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
                os.environ.get('REAL_ESTATE_DATABASE_PASSWORD')
            )
        )
        self.cursor = self.conn.cursor()

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

    def main(self):
        '''Run Join() and Clean() scripts.'''

        self.delete_details()
        self.delete_cleaned()
        self.vacuum()

    def vacuum(self):
        '''docstring'''

        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        sql = 'VACUUM;'
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)

    def delete_details(self):
        SESSION.query(
            Detail
        ).filter(
            Detail.document_recorded >= self.initial_date
        ).filter(
            Detail.document_recorded <= self.until_date
        ).delete()

        SESSION.commit()

    def delete_cleaned(self):
        SESSION.query(
            Cleaned
        ).filter(
            Cleaned.document_recorded >= self.initial_date
        ).filter(
            Cleaned.document_recorded <= self.until_date
        ).delete()

        SESSION.commit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
            print (
                "No date(s) specified. Enter a single date to delete that " +
                "one day or enter two days to delete a range of days. " +
                "Use the format 'YYYY-MM-DD'.")
    elif len(sys.argv) == 2:  # One argument
        day = sys.argv[1]

        DeleteDates(
            initial_date=day,
            until_date=day
        ).main()
    elif len(sys.argv) == 3:  # Two arguments
        initial_day = sys.argv[1]
        until_day = sys.argv[2]

        DeleteDates(
            initial_date=initial_day,
            until_date=until_day
        ).main()
    elif len(sys.argv) > 3:
            print (
                "Too many arguments. Enter a single date to delete that one " +
                "day or enter two days to delete a range of days. " +
                "Use the format 'YYYY-MM-DD'.")
