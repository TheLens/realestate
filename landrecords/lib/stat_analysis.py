# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from landrecords import config


class StatAnalysis(object):

    def __init__(self, table, begin_date, end_date, amount_low, amount_high):
        self.table = table
        self.begin_date = begin_date
        self.end_date = end_date
        self.amount_low = amount_low
        self.amount_high = amount_high

        self.engine = create_engine(config.SERVER_ENGINE)

    def count(self):
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE document_recorded >= '%s' AND document_recorded <= '%s';
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)
        for r in result:
            count = r.count
            return count

    def detail_not_published(self):
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE detail_publish = '0'
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)
        for r in result:
            count = r.count
            return count

    def detail_published(self):
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE detail_publish = '1'
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)
        for r in result:
            count = r.count
            return count

    def location_not_published(self):
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE location_publish = '0'
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)
        for r in result:
            count = r.count
            return count

    def location_published(self):
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE location_publish = '1'
            AND document_recorded >= '%s'
            AND document_recorded <= '%s';
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)
        for r in result:
            count = r.count
            return count

    def highest_amount(self):
        sql = """
            SELECT amount
            FROM %s
            WHERE document_recorded >= '%s'
            AND document_recorded <= '%s'
            ORDER BY amount DESC
            LIMIT 1;
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)

        for r in result:
            high_amount = r.amount
            return high_amount

    def lowest_amount(self):
        sql = """
            SELECT amount
            FROM %s
            WHERE document_recorded >= '%s'
            AND document_recorded <= '%s'
            ORDER BY amount ASC
            LIMIT 1;
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)

        for r in result:
            low_amount = r.amount
            return low_amount

    def all_records(self):
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
            """ % (self.table, self.begin_date, self.end_date)

        result = self.engine.execute(sql)

        rows = []
        for r in result:
            row = dict(r)
            rows.append(row)

        return rows
