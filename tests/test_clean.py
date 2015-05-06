# -*- coding: utf-8 -*-

import os
# import mock
from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from realestate.db import (
    Detail
    # Cleaned
)
from realestate.lib.clean import (
    Clean,
    Join
)
from realestate import DATABASE_NAME
# from datetime import date

# global application scope.  create Session class, engine
Session = sessionmaker()

engine = create_engine(
    'postgresql://%s:%s@localhost/%s' % (
        os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
        os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
        DATABASE_NAME
    )
)


class TestJoin(TestCase):
    "Test the Join class in `clean.py`."

    def setup(self):
        '''
        Connect to the database, begin a non-ORM transaction and bind an
        individual Session to the connection.
        '''

        # connect to the database
        self.connection = engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection
        self.session = Session(bind=self.connection)

    def teardown(self):
        '''
        rollback - everything that happened with the Session above (including
        calls to commit()) is rolled back.
        '''

        self.trans.rollback()
        self.session.close()

        # return connection to the Engine
        self.connection.close()

    def test_join_subqueries_length(self):
        '''
        Test that JOIN with each subquery results in same number of rows as
        just the details table for the same date range.
        '''

        self.setup()

        d1 = '2014-02-18'
        d2 = '2014-11-20'

        details_query = self.session.query(
            Detail
        ).filter(
            Detail.document_recorded >= d1
        ).filter(
            Detail.document_recorded <= d2
        ).all()

        subquery = Join(initial_date=d1, until_date=d2).join_subqueries()

        self.assertEqual(len(details_query), len(subquery))

        self.teardown()


class TestClean(TestCase):

    '''Test the Clean class in `clean.py`.'''

    def setup(self):
        '''
        Connect to the database, begin a non-ORM transaction and bind an
        individual Session to the connection.
        '''

        # connect to the database
        self.connection = engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection
        self.session = Session(bind=self.connection)

    def teardown(self):
        '''
        rollback - everything that happened with the Session above (including
        calls to commit()) is rolled back.
        '''

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        self.trans.rollback()
        self.session.close()

        # return connection to the Engine
        self.connection.close()

    # def test_commit_rows(self):
    #     '''
    #     Test that committing cleaned rows handles any problems.
    #     '''

    #     self.setup()

    #     initial_query = self.session.query(Cleaned).all()

    #     initial_length = len(initial_query)

    #     # Input with two new unique instrument numbers,
    #     # but also one duplicate.
    #     rows = [
    #         {
    #             'location_publish': '0',
    #             'buyers': 'Jean Tran, Trang Thi Phuong Tran',
    #             'document_recorded': date(2015, 4, 16),
    #             'neighborhood': 'None',
    #             'detail_publish': '1',
    #             'longitude': -90.17215,
    #             'sellers': 'Thap Van Nguyen',
    #             'location_info': '',
    #             'amount': 250000,
    #             'instrument_no': '1234-56789',  # New instrument number
    #             'address': '',
    #             'latitude': 29.96238,
    #             'zip_code': '70121',
    #             'document_date': None
    #         },
    #         {
    #             'location_publish': '0',
    #             'buyers': 'Jean Tran, Trang Thi Phuong Tran',
    #             'document_recorded': date(2015, 4, 16),
    #             'neighborhood': 'None',
    #             'detail_publish': '1',
    #             'longitude': -90.17215,
    #             'sellers': 'Thap Van Nguyen',
    #             'location_info': '',
    #             'amount': 250000,
    #             'instrument_no': '1234-56789',  # Duplicate instrument number
    #             'address': '',
    #             'latitude': 29.96238,
    #             'zip_code': '70121',
    #             'document_date': None
    #         },
    #         {
    #             'location_publish': '0',
    #             'buyers': 'Jean Tran, Trang Thi Phuong Tran',
    #             'document_recorded': date(2015, 4, 16),
    #             'neighborhood': 'None',
    #             'detail_publish': '1',
    #             'longitude': -90.17215,
    #             'sellers': 'Thap Van Nguyen',
    #             'location_info': '',
    #             'amount': 250000,
    #             'instrument_no': '1234-56790',  # New instrument number
    #             'address': '',
    #             'latitude': 29.96238,
    #             'zip_code': '70121',
    #             'document_date': None
    #         }
    #     ]

    #     Clean().commit_rows(rows)

    #     final_query = self.session.query(Cleaned).all()

    #     final_length = len(final_query)

    #     self.assertEqual(initial_length + 2, final_length)

    #     self.teardown()

    def test_prep_rows(self):
        '''
        Test that JOIN with each subquery results in same number of rows as
        just the details table for the same date range.
        '''

        self.setup()

        rows = [
            {
                'sellers': 'john doe',
                'buyers': 'JANE DOE',
                'address': '123 main street',
                'location_info': 'Unit: 4, Lot: 3',
                'neighborhood': 'BLACK PEARL'
            },
            {
                'sellers': 'john doe',
                'buyers': 'JANE DOE',
                'address': '',
                'location_info': 'Unit: 1, Lot: 2',
                'neighborhood': 'None'
            }
        ]

        outputrows = [
            {
                'sellers': 'John Doe',
                'buyers': 'Jane Doe',
                'address': '123 Main Street',
                'location_info': 'Unit: 4, Lot: 3',
                'neighborhood': 'Black Pearl'
            },
            {
                'sellers': 'John Doe',
                'buyers': 'Jane Doe',
                'address': '',
                'location_info': 'Unit: 1, Lot: 2',
                'neighborhood': 'None'
            }
        ]

        rows = Clean().prep_rows(rows)

        self.assertEqual(outputrows, rows)

        self.teardown()
