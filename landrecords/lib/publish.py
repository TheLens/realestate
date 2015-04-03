# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db


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


class PublishChecker(object):

    def __init__(self, initial_date=None, until_date=None):
        self.initial_date = initial_date
        self.until_date = until_date

        self.logger = initialize_log('publish')

        base = declarative_base()
        engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(engine)
        sn = sessionmaker(bind=engine)

        self.session = sn()

    def check_geocoder_good_rating(self):
        self.session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating <= 3
        ).update({"location_publish": "1"})

        self.session.flush()

    def check_geocoder_bad_rating(self):
        self.session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating > 3
        ).update({"location_publish": "0"})
        self.session.flush()

    def check_west_of_new_orleans(self):
        # Long less than -90.140388 is west of New Orleans:
        self.session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude < -90.140388
        ).update({
            "location_publish": "0"
        })

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_east_of_new_orleans(self):
        # Long greater than -89 is east of New Orleans:
        self.session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude > -89.0
        ).update({
            "location_publish": "0"
        })

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_south_of_new_orleans(self):
        # Lat less than 29.864543 is south of New Orleans:
        self.session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude < 29.864543
        ).update({
            "location_publish": "0"
        })

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_north_of_new_orleans(self):
        # Lat less than 29.864543 is north of New Orleans:
        self.session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude > 30.181719
        ).update({
            "location_publish": "0"
        })

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def make_all_details_publishable(self):
        # Assume publishable, then check for reasons not to publish.
        self.session.query(
            db.Detail.detail_publish
        ).update({
            "detail_publish": "1"
        })
        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_if_no_date(self):
        self.session.query(
            db.Detail.document_date,
            db.Detail.document_recorded,
            db.Detail.detail_publish
        ).filter(
            (db.Detail.document_date is None) |
            (db.Detail.document_recorded is None)
        ).update(
            {"detail_publish": "0"}
        )

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_relative_date(self):
        # Convert date strings to datetime format
        new_initial_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
        # logger.debug(new_initial_date)
        new_until_date = datetime.strptime(self.until_date, '%Y-%m-%d')
        # logger.debug(new_until_date)
        current_date = new_initial_date
        # logger.debug(current_date)

        # Evaluate "30 days ago" based on that particular day
        while current_date != new_until_date:
            # Update date range
            old_date = current_date - timedelta(days=180)
            previous_date = current_date - timedelta(days=1)

            # Copy datetime objects to date strings
            old_date_string = old_date.strftime('%Y-%m-%d')
            previous_date_string = previous_date.strftime('%Y-%m-%d')
            current_date_string = current_date.strftime('%Y-%m-%d')

            with self.session.begin_nested():
                # For sales recorded on a given day, check if the document
                # date is unbelievable (too old or in the future)

                self.session.query(
                    db.Detail.document_recorded,
                    db.Detail.document_date,
                    db.Detail.detail_publish
                ).filter(
                    db.Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    db.Detail.document_date < '%s' % old_date_string
                ).update({"detail_publish": "0"})

                # logger.info('query')
                self.session.flush()
                # logger.info('flush')

                self.session.query(
                    db.Detail.document_recorded,
                    db.Detail.document_date,
                    db.Detail.detail_publish
                ).filter(
                    db.Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    db.Detail.document_date > '%s' % previous_date_string
                ).update({
                    "detail_publish": "0"
                })

                # logger.info('query')
                self.session.flush()
                # logger.info('flush')

            current_date = current_date + timedelta(days=1)
            # logger.debug(current_date)

    def check_low_amount(self):
        # Not sure about these, so check them all for now to be safe
        self.session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount <= 0
        ).update({
            "detail_publish": "0"
        })

        # logger.info('query')
        self.session.flush()
        # logger.info('flush')

    def check_high_amount(self):
        # Anything over $20,000,000 wouldn't be impossible, but is rare
        self.session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount >= 20000000
        ).update({
            "detail_publish": "0"
        })

        # logger.info('query')

    def commit_session(self):
        self.session.commit()

    def check_them_all(self):
        print 'Publishing...'
        self.check_geocoder_good_rating()
        self.check_geocoder_bad_rating()
        self.check_west_of_new_orleans()
        self.check_east_of_new_orleans()
        self.check_south_of_new_orleans()
        self.check_north_of_new_orleans()
        self.make_all_details_publishable()
        self.check_if_no_date()
        self.check_relative_date()
        self.check_low_amount()
        self.check_high_amount()
        self.commit_session()
