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
from landrecords.db import (
    Detail,
    Location
)
from landrecords import log


class Publish(object):

    '''Runs checks for data integrity.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables and establish connection to database.'''

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

    def make_all_locations_publishable(self):
        '''
        Assume all sales are publishable. Set location_publish = 1.
        Then set to 0 if something questionable is found.
        '''

        session = self.sn()

        # Assume publishable, then check for reasons not to publish.
        session.query(
            Location.location_publish
        ).update({
            "location_publish": True
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_geocoder_good_rating(self):
        '''Check if PostGIS Geocoder rating scored 3 or lower: good.'''

        session = self.sn()

        session.query(
            Location.rating,
            Location.location_publish
        ).filter(
            (Location.rating == 'RANGE_INTERPOLATED') |
            (Location.rating == 'ROOFTOP')
        ).update({"location_publish": True})

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_geocoder_bad_rating(self):
        '''Check if PostGIS Geocoder rating scored higher than 3: bad.'''

        session = self.sn()

        session.query(
            Location.rating,
            Location.location_publish
        ).filter(
            (Location.rating == 'GEOMETRIC_CENTER') |
            (Location.rating == 'APPROXIMATE') |
            (Location.rating.is_(None))
        ).update({"location_publish": False})

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_west_of_new_orleans(self):
        '''
        Check if geocoded lat/long found is within west border of New Orleans.
        '''

        session = self.sn()

        # Long less than -90.140388 is west of New Orleans:
        session.query(
            Location.longitude,
            Location.location_publish
        ).filter(
            Location.longitude < -90.140388
        ).update({
            "location_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_east_of_new_orleans(self):
        '''
        Check if geocoded lat/long found is within east border of New Orleans.
        '''

        session = self.sn()

        # Long greater than -89 is east of New Orleans:
        session.query(
            Location.longitude,
            Location.location_publish
        ).filter(
            Location.longitude > -89.0
        ).update({
            "location_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_south_of_new_orleans(self):
        '''
        Check if geocoded lat/long found is within south border of New Orleans.
        '''

        session = self.sn()

        # Lat less than 29.864543 is south of New Orleans:
        session.query(
            Location.latitude,
            Location.location_publish
        ).filter(
            Location.latitude < 29.864543
        ).update({
            "location_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_north_of_new_orleans(self):
        '''
        Check if geocoded lat/long found is within north border of New Orleans.
        '''

        session = self.sn()

        # Lat less than 29.864543 is north of New Orleans:
        session.query(
            Location.latitude,
            Location.location_publish
        ).filter(
            Location.latitude > 30.181719
        ).update({
            "location_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def make_all_details_publishable(self):
        '''
        Assume all sales are publishable. Set detail_publishable = 1.
        Then set to 0 if something questionable is found.
        '''

        session = self.sn()

        # Assume publishable, then check for reasons not to publish.
        session.query(
            Detail.detail_publish
        ).update({
            "detail_publish": True
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_if_no_date(self):
        '''Check if sale has a date.'''

        session = self.sn()

        session.query(
            Detail.document_date,
            Detail.document_recorded,
            Detail.detail_publish
        ).filter(
            (Detail.document_date is None) |
            (Detail.document_recorded is None)
        ).update(
            {"detail_publish": False}
        )

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_relative_date(self):
        '''
        Check if the sale date is more than 6 months prior to the date the
        sale was recorded.
        '''

        session = self.sn()

        # Convert date strings to date format
        new_initial_date = datetime.strptime(
            self.initial_date, '%Y-%m-%d').date()
        new_until_date = datetime.strptime(
            self.until_date, '%Y-%m-%d').date()
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
                    Detail.document_recorded,
                    Detail.document_date,
                    Detail.detail_publish
                ).filter(
                    Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    Detail.document_date < '%s' % old_date_string
                ).update({"detail_publish": False})

                try:
                    session.commit()
                    # with session.begin_nested():
                    #     session.flush()
                except Exception, error:
                    log.exception(error, exc_info=True)
                    session.rollback()

                session.query(
                    Detail.document_recorded,
                    Detail.document_date,
                    Detail.detail_publish
                ).filter(
                    Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    Detail.document_date > '%s' % previous_date_string
                ).update({
                    "detail_publish": False
                })

                try:
                    session.commit()
                    # with session.begin_nested():
                    #     session.flush()
                except Exception, error:
                    log.exception(error, exc_info=True)
                    session.rollback()

            current_date = current_date + timedelta(days=1)

        session.close()

    def check_low_amount(self):
        '''Check if sale amount is unreasonably low (<= $0).'''

        session = self.sn()

        # Not sure about these, so check them all for now to be safe
        session.query(
            Detail.amount,
            Detail.detail_publish
        ).filter(
            Detail.amount <= 0
        ).update({
            "detail_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def check_high_amount(self):
        '''Check if sale amount is unreasonably high (>= $20,000,000).'''

        session = self.sn()

        # Anything over $20,000,000 wouldn't be impossible, but is rare
        session.query(
            Detail.amount,
            Detail.detail_publish
        ).filter(
            Detail.amount >= 20000000
        ).update({
            "detail_publish": False
        })

        try:
            with session.begin_nested():
                session.flush()
        except Exception, error:
            log.exception(error, exc_info=True)
            session.rollback()

        session.commit()
        session.close()

    def main(self):
        '''Runs through each check method.'''

        log.debug('Publish')
        print 'Publishing...'

        self.make_all_locations_publishable()
        self.check_geocoder_bad_rating()
        self.check_geocoder_good_rating()
        self.check_west_of_new_orleans()
        self.check_east_of_new_orleans()
        self.check_north_of_new_orleans()
        self.check_south_of_new_orleans()
        self.make_all_details_publishable()
        self.check_if_no_date()
        self.check_relative_date()
        self.check_low_amount()
        self.check_high_amount()

if __name__ == '__main__':
    pass
