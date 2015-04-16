# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords.lib.log import Log


class Publish(object):

    def __init__(self, initial_date=None, until_date=None):

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        sn = sessionmaker(bind=engine)

        self.session = sn()

    def check_geocoder_good_rating(self):
        '''Check if PostGIS Geocoder rating scored 3 or lower: good'''

        self.session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating <= 3
        ).update({"location_publish": "1"})

        self.session.flush()

    def check_geocoder_bad_rating(self):
        '''Check if PostGIS Geocoder rating scored higher than 3: bad'''

        self.session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating > 3
        ).update({"location_publish": "0"})
        self.session.flush()

    def check_west_of_new_orleans(self):
        '''Check if geocoded lat/long found is west of New Orleans'''

        # Long less than -90.140388 is west of New Orleans:
        self.session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude < -90.140388
        ).update({
            "location_publish": "0"
        })

        self.session.flush()

    def check_east_of_new_orleans(self):
        '''Check if geocoded lat/long found is east of New Orleans'''

        # Long greater than -89 is east of New Orleans:
        self.session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude > -89.0
        ).update({
            "location_publish": "0"
        })

        self.session.flush()

    def check_south_of_new_orleans(self):
        '''Check if geocoded lat/long found is south of New Orleans'''

        # Lat less than 29.864543 is south of New Orleans:
        self.session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude < 29.864543
        ).update({
            "location_publish": "0"
        })

        self.session.flush()

    def check_north_of_new_orleans(self):
        '''Check if geocoded lat/long found is north of New Orleans'''

        # Lat less than 29.864543 is north of New Orleans:
        self.session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude > 30.181719
        ).update({
            "location_publish": "0"
        })

        self.session.flush()

    def make_all_details_publishable(self):
        '''Assume all sales are publishable. Set detail_publishable = 1.'''
        '''Then set to 0 if something questionable is found.'''

        # Assume publishable, then check for reasons not to publish.
        self.session.query(
            db.Detail.detail_publish
        ).update({
            "detail_publish": "1"
        })

        self.session.flush()

    def check_if_no_date(self):
        '''Check if sale has a date'''

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

        self.session.flush()

    def check_relative_date(self):
        # Convert date strings to datetime format
        new_initial_date = datetime.strptime(self.initial_date, '%Y-%m-%d')
        new_until_date = datetime.strptime(self.until_date, '%Y-%m-%d')
        current_date = new_initial_date

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

                self.session.flush()

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

                self.session.flush()

            current_date = current_date + timedelta(days=1)

    def check_low_amount(self):
        '''Check if sale amount is unreasonably low (<= $0)'''

        # Not sure about these, so check them all for now to be safe
        self.session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount <= 0
        ).update({
            "detail_publish": "0"
        })

        self.session.flush()

    def check_high_amount(self):
        '''Check if sale amount is unreasonably high (>= $20,000,000)'''

        # Anything over $20,000,000 wouldn't be impossible, but is rare
        self.session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount >= 20000000
        ).update({
            "detail_publish": "0"
        })

    def commit_session(self):
        self.session.commit()

    def check_them_all(self):
        self.log.debug('Publish')

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

if __name__ == '__main__':
    log = Log('initialize').initialize_log()
