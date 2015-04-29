# -*- coding: utf-8 -*-

'''Commmon statistical analyses, like high amounts, sales per day, etc.'''

import os
from sqlalchemy import create_engine


class StatAnalysis(object):

    '''Commmon statistical analyses.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        self.table = 'cleaned'
        self.initial_date = initial_date
        self.until_date = until_date

        self.engine = create_engine(
            os.environ.get('REAL_ESTATE_SERVER_ENGINE'))

    def count(self):
        '''Get number of records.'''

        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE document_recorded >= '%s' AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        for row in result:
            count = row.count
            return count

    def detail_not_published(self):
        '''Get rows that have unpublishable detail data.'''

        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE detail_publish = False
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)
        for row in result:
            count = row.count
            return count

    def detail_published(self):
        '''Get rows that have publishable detail data.'''

        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE detail_publish IS True
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)
        for row in result:
            count = row.count
            return count

    def location_not_published(self):
        '''Get rows that have unpublishable location data.'''

        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE location_publish IS False
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)
        for row in result:
            count = row.count
            return count

    def location_published(self):
        '''Get rows that have publishable location data.'''

        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE location_publish IS True
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)
        for row in result:
            count = row.count
            return count

    def highest_amount(self):
        '''Find the highest sale amount for a given date range.'''

        sql = """
            SELECT amount
            FROM %s
            WHERE document_recorded >= '%s'
            AND document_recorded <= '%s'
            ORDER BY amount DESC
            LIMIT 1;
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        for row in result:
            high_amount = row.amount
            return high_amount

    def lowest_amount(self):
        '''Find the lowest sale amount for a given date range.'''

        sql = """
            SELECT amount
            FROM %s
            WHERE document_recorded >= '%s'
            AND document_recorded <= '%s'
            ORDER BY amount ASC
            LIMIT 1;
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        for row in result:
            low_amount = row.amount
            return low_amount

    def all_records(self):
        '''Get all rows for the given date range.'''

        sql = """
            SELECT amount,
                   document_date,
                   document_recorded,
                   address,
                   location_info,
                   sellers,
                   buyers,
                   instrument_no,
                   latitude,
                   longitude,
                   zip_code,
                   detail_publish,
                   permanent_flag,
                   location_publish,
                   neighborhood
            FROM %s
            WHERE document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.initial_date, self.until_date)

        result = self.engine.execute(sql)

        rows = []
        for row in result:
            row = dict(row)
            rows.append(row)

        return rows

if __name__ == '__main__':
    pass
