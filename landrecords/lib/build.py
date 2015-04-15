# -*- coding: utf-8 -*-

import glob
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords.lib import parse
from landrecords.lib.log import Log

log = Log('initialize').logger


class Build(object):

    def __init__(self,
                 initial_date=Config().OPENING_DAY,
                 until_date=Config().YESTERDAY_DATE):

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    def build_all(self):
        log.debug('Build all')

        self.build_details()
        self.build_vendors()
        self.build_vendees()
        self.build_locations()

    def build_details(self):
        log.debug('Build details')

        self.dict_parse('DetailParser', 'Detail')

    def dict_parse(self, parser_name, table):
        session = self.sn()

        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            for f in sorted(glob.glob('%s/' % (Config().DATA_DIR) +
                                      'raw/%s/' % (current_date) +
                                      'form-html/*.html')):

                # log.debug('f: %s', f)
                dict_output = getattr(parse, parser_name)(f).form_dict()

                try:
                    with session.begin_nested():
                        i = insert(getattr(db, table))
                        i = i.values(dict_output)
                        session.execute(i)
                        session.flush()
                except Exception, e:
                    log.debug(e, exc_info=True)
                    session.rollback()

            initial_datetime += timedelta(days=1)

        session.commit()
        session.close()

    def build_vendors(self):
        log.debug('Building vendors')

        self.list_parse('VendorParser', 'Vendor')

    def build_vendees(self):
        log.debug('Building vendees')

        self.list_parse('VendeeParser', 'Vendee')

    def build_locations(self):
        log.debug('Building locations')

        self.list_parse('LocationParser', 'Location')

    def list_parse(self, parser_name, table):
        session = self.sn()

        initial_datetime = datetime.strptime(self.initial_date, '%Y-%m-%d')
        until_datetime = datetime.strptime(self.until_date, '%Y-%m-%d')

        while initial_datetime != (until_datetime + timedelta(days=1)):
            current_date = initial_datetime.strftime('%Y-%m-%d')

            for f in sorted(glob.glob('%s/' % (Config().DATA_DIR) +
                                      'raw/%s/' % (current_date) +
                                      'form-html/*.html')):

                # Allows for variable calls to a class.
                # Ex module.Class().method -> parse.parser_name(f).list_output
                list_output = getattr(parse, parser_name)(f).form_list()

                try:
                    with session.begin_nested():
                        i = insert(getattr(db, table))

                        # Because might have multiple rows:
                        for o in list_output:
                            i = i.values(o)
                            session.execute(i)
                            session.flush()
                except Exception, e:
                    log.debug(e, exc_info=True)
                    session.rollback()

            initial_datetime += timedelta(days=1)

        session.commit()
        session.close()
