# -*- coding: utf-8 -*-

import logging
import logging.handlers
import glob
import os
from datetime import datetime
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib import parsers


def initialize_log(name):
    if os.path.isfile('%s/%s.log' % (config.LOG_DIR, name)):
        os.remove('%s/%s.log' % (config.LOG_DIR, name))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler('%s/%s.log' % (config.LOG_DIR, name))
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(funcName)s - '
        '%(levelname)s - %(lineno)d - %(message)s')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)

    return logger


class Build(object):

    def __init__(self, initial_date=None, until_date=None):
        self.initial_date = initial_date
        self.until_date = until_date
        self.logger = initialize_log('build')

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
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            self.logger.debug(folder)
            current_date = folder.split('/')[-1]
            self.logger.debug(current_date)

            # If this date is before the specified self.initial_date,
            # then skip.
            try:
                cur_date = datetime.strptime(current_date, '%Y-%m-%d')
                init_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
                if cur_date < init_date:
                    continue
            except Exception, e:
                self.logger.error(e, exc_info=True)
                continue

            for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
                # print parsers.AllPurposeParser(form).document_id

                dict_output = parsers.DetailParser(form).form_dict()

                try:
                    with self.session.begin_nested():
                        i = insert(db.Detail)
                        i = i.values(dict_output)
                        self.session.execute(i)
                        self.session.flush()
                except Exception, e:
                    self.logger.debug(e, exc_info=True)
                    self.session.rollback()

            # If reached final date, then end.
            if current_date == self.until_date:
                break

        self.session.commit()

    def build_vendors(self):
        print 'Building vendors...'
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            # For all folders (days)
            current_date = folder.split('/')[-1]
            self.logger.debug(current_date)

            # If this date is before the specified self.initial_date,
            # then skip.
            try:
                cur_date = datetime.strptime(current_date, '%Y-%m-%d')
                init_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
                if cur_date < init_date:
                    continue
            except Exception, e:
                self.logger.error(e, exc_info=True)
                continue

            for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
                # print parsers.AllPurposeParser(form).document_id

                list_output = parsers.VendorParser(form).list_output

                try:
                    with self.session.begin_nested():
                        i = insert(db.Vendor)

                        # Because might have multiple rows:
                        for o in list_output:
                            i = i.values(o)
                            self.session.execute(i)
                            self.session.flush()
                except Exception, e:
                    self.logger.debug(e, exc_info=True)
                    self.session.rollback()

            # If reached final date, then end.
            if current_date == self.until_date:
                break

        self.session.commit()

    def build_vendees(self):
        print 'Building vendees...'
        # For all folders (days)
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            current_date = folder.split('/')[-1]
            self.logger.debug(current_date)

            # If this date is before the specified self.initial_date,
            # then skip.
            try:
                cur_date = datetime.strptime(current_date, '%Y-%m-%d')
                init_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
                if cur_date < init_date:
                    continue
            except Exception, e:
                self.logger.error(e, exc_info=True)
                continue

            for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
                # print parsers.AllPurposeParser(form).document_id

                list_output = parsers.VendeeParser(form).list_output

                try:
                    with self.session.begin_nested():
                        i = insert(db.Vendee)

                        # Because might have multiple rows:
                        for o in list_output:
                            i = i.values(o)
                            self.session.execute(i)
                            self.session.flush()
                except Exception, e:
                    self.logger.debug(e, exc_info=True)
                    self.session.rollback()

            # If reached final date, then end.
            if current_date == self.until_date:
                break

        self.session.commit()

    def build_locations(self):
        print 'Building locations...'
        # For all folders (days)
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            current_date = folder.split('/')[-1]
            self.logger.debug(current_date)

            # If this date is before the specified self.initial_date,
            # then skip.
            try:
                cur_date = datetime.strptime(current_date, '%Y-%m-%d')
                init_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
                if cur_date < init_date:
                    continue
            except Exception, e:
                self.logger.error(e, exc_info=True)
                continue

            for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
                # print parsers.AllPurposeParser(form).document_id

                list_output = parsers.LocationParser(form).list_output

                try:
                    with self.session.begin_nested():
                        i = insert(db.Location)

                        # Because might have multiple rows:
                        for o in list_output:
                            i = i.values(o)
                            self.session.execute(i)
                            self.session.flush()
                except Exception, e:
                    self.logger.debug(e, exc_info=True)
                    self.session.rollback()

            # If reached final date, then end.
            if current_date == self.until_date:
                break

        self.session.commit()
