# -*- coding: utf-8 -*-

'''
Checks the integrity of the data to determine whether to publish each sale,
both for the map and only in the table.
'''

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords import log


class Publish(object):

    '''Runs checks for data integrity.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    @staticmethod
    def check_geocoder_good_rating(session):
        '''Check if PostGIS Geocoder rating scored 3 or lower: good.'''

        session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating <= 3
        ).update({"location_publish": "1"})

        session.flush()

    @staticmethod
    def check_geocoder_bad_rating(session):
        '''Check if PostGIS Geocoder rating scored higher than 3: bad.'''

        session.query(
            db.Location.rating,
            db.Location.location_publish
        ).filter(
            db.Location.rating > 3
        ).update({"location_publish": "0"})
        session.flush()

    @staticmethod
    def check_west_of_new_orleans(session):
        '''Check if geocoded lat/long found is west of New Orleans.'''

        # Long less than -90.140388 is west of New Orleans:
        session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude < -90.140388
        ).update({
            "location_publish": "0"
        })

        session.flush()

    @staticmethod
    def check_east_of_new_orleans(session):
        '''Check if geocoded lat/long found is east of New Orleans.'''

        # Long greater than -89 is east of New Orleans:
        session.query(
            db.Location.longitude,
            db.Location.location_publish
        ).filter(
            db.Location.longitude > -89.0
        ).update({
            "location_publish": "0"
        })

        session.flush()

    @staticmethod
    def check_south_of_new_orleans(session):
        '''Check if geocoded lat/long found is south of New Orleans.'''

        # Lat less than 29.864543 is south of New Orleans:
        session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude < 29.864543
        ).update({
            "location_publish": "0"
        })

        session.flush()

    @staticmethod
    def check_north_of_new_orleans(session):
        '''Check if geocoded lat/long found is north of New Orleans.'''

        # Lat less than 29.864543 is north of New Orleans:
        session.query(
            db.Location.latitude,
            db.Location.location_publish
        ).filter(
            db.Location.latitude > 30.181719
        ).update({
            "location_publish": "0"
        })

        session.flush()

    @staticmethod
    def make_all_details_publishable(session):
        '''
        Assume all sales are publishable. Set detail_publishable = 1.
        Then set to 0 if something questionable is found.
        '''

        # Assume publishable, then check for reasons not to publish.
        session.query(
            db.Detail.detail_publish
        ).update({
            "detail_publish": "1"
        })

        session.flush()

    @staticmethod
    def check_if_no_date(session):
        '''Check if sale has a date.'''

        session.query(
            db.Detail.document_date,
            db.Detail.document_recorded,
            db.Detail.detail_publish
        ).filter(
            (db.Detail.document_date is None) |
            (db.Detail.document_recorded is None)
        ).update(
            {"detail_publish": "0"}
        )

        session.flush()

    def check_relative_date(self, session):
        '''
        Check if the sale date is more than 6 months prior to the date the
        sale was recorded.
        '''

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

            with session.begin_nested():
                # For sales recorded on a given day, check if the document
                # date is unbelievable (too old or in the future)

                session.query(
                    db.Detail.document_recorded,
                    db.Detail.document_date,
                    db.Detail.detail_publish
                ).filter(
                    db.Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    db.Detail.document_date < '%s' % old_date_string
                ).update({"detail_publish": "0"})

                session.flush()

                session.query(
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

                session.flush()

            current_date = current_date + timedelta(days=1)

    @staticmethod
    def check_low_amount(session):
        '''Check if sale amount is unreasonably low (<= $0).'''

        # Not sure about these, so check them all for now to be safe
        session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount <= 0
        ).update({
            "detail_publish": "0"
        })

        session.flush()

    @staticmethod
    def check_high_amount(session):
        '''Check if sale amount is unreasonably high (>= $20,000,000).'''

        # Anything over $20,000,000 wouldn't be impossible, but is rare
        session.query(
            db.Detail.amount,
            db.Detail.detail_publish
        ).filter(
            db.Detail.amount >= 20000000
        ).update({
            "detail_publish": "0"
        })

        session.flush()

    def check_them_all(self):
        '''Runs through each check method.'''

        log.debug('Publish')
        print 'Publishing...'

        session = self.sn()

        self.check_geocoder_good_rating(session)
        self.check_geocoder_bad_rating(session)
        self.check_west_of_new_orleans(session)
        self.check_east_of_new_orleans(session)
        self.check_south_of_new_orleans(session)
        self.check_north_of_new_orleans(session)
        self.make_all_details_publishable(session)
        self.check_if_no_date(session)
        self.check_relative_date(session)
        self.check_low_amount(session)
        self.check_high_amount(session)

        session.commit()
        session.close()

if __name__ == '__main__':
    pass
