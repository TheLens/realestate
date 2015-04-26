# -*- coding: utf-8 -*-

'''Deletes certain dates from database.'''

import sys
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords.db import (
    Cleaned,
    Detail
)
from landrecords import log


class DeleteDates(object):

    '''Deletes certain dates from database.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        self.sn = sessionmaker(bind=self.engine)

        self.conn = psycopg2.connect(Config().SERVER_CONNECTION)
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
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        sql = 'VACUUM;'
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)

    def delete_details(self):
        session = self.sn()

        session.query(
            Detail
        ).filter(
            Detail.document_recorded >= self.initial_date
        ).filter(
            Detail.document_recorded <= self.until_date
        ).delete()

        session.commit()
        session.close()

    def delete_cleaned(self):
        session = self.sn()

        session.query(
            Cleaned
        ).filter(
            Cleaned.document_recorded >= self.initial_date
        ).filter(
            Cleaned.document_recorded <= self.until_date
        ).delete()

        session.commit()
        session.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        date = sys.argv[1]

        DeleteDates(
            initial_date=date,
            until_date=date
        ).main()
    else:
        initial_date = sys.argv[1]
        until_date = sys.argv[2]

        DeleteDates(
            initial_date=initial_date,
            until_date=until_date
        ).main()