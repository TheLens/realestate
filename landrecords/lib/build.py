# -*- coding: utf-8 -*-

import glob
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib import parsers
from landrecords.lib.log import Log


class Build(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('build').logger

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(engine)
        sn = sessionmaker(bind=engine)

        self.session = sn()

    def build_all(self):
        self.build_details()
        self.build_vendors()
        self.build_vendees()
        self.build_locations()

    def build_details(self):
        print 'Building details...'
        # For all folders (days)

        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            for f in sorted(glob.glob('%s/raw/%s/form-html/*.html' % (config.DATA_DIR, current_date))):

                dict_output = parsers.DetailParser(f).form_dict()

                try:
                    with self.session.begin_nested():
                        i = insert(db.Detail)
                        i = i.values(dict_output)
                        self.session.execute(i)
                        self.session.flush()
                except Exception, e:
                    self.log.debug(e, exc_info=True)
                    self.session.rollback()

            initial_datetime += timedelta(days=1)

        self.session.commit()

    def build_vendors(self):
        print 'Building vendors...'
        self.list_parse('VendorParser', 'Vendor')

    def build_vendees(self):
        print 'Building vendees...'
        self.list_parse('VendeeParser', 'Vendee')

    def build_locations(self):
        print 'Building locations...'
        self.list_parse('LocationParser', 'Location')

    def list_parse(self, parser_name, table):
        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            for f in sorted(glob.glob('%s/raw/%s/form-html/*.html' % (config.DATA_DIR, current_date))):

                list_output = getattr(parsers, parser_name)(f).list_output

                try:
                    with self.session.begin_nested():
                        i = insert(getattr(db, table))

                        # Because might have multiple rows:
                        for o in list_output:
                            i = i.values(o)
                            self.session.execute(i)
                            self.session.flush()
                except Exception, e:
                    self.log.debug(e, exc_info=True)
                    self.session.rollback()

            initial_datetime += timedelta(days=1)

        self.session.commit()
