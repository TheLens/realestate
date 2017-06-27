# -*- coding: utf-8 -*-

"""
Run checks on `cleaned` table to make sure data is ready for publication.

Checks for things such as lat/long coordinates outside of
New Orleans, sale amounts that are questionably high or low and whether the
sale has a date or not.

Sales can fail for detail data (`detail_publish` field) or location data (
`location_publish`). If a sale fails meet all criteria for each field, it
will be set as False. Sales will only appear in the table if `detail_publish`
is True but `location_publish` is False. If both are False, then sale won't
appear at all.
"""

from datetime import datetime, timedelta

from www.db import Detail, Location
from www import log, SESSION


class Publish(object):
    """Run checks for data integrity."""

    def __init__(self, initial_date=None, until_date=None):
        """Initialize self variables and establish connection to database."""
        self.initial_date = initial_date
        self.until_date = until_date

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

    def make_all_locations_publishable(self):
        """
        Assume all sales are publishable.

        Set location_publish = 1. Then set to 0 if questionable data is found.
        """
        # Assume publishable, then check for reasons not to publish.
        SESSION.query(
            Location.location_publish
        ).update({
            "location_publish": True
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_geocoder_good_rating(self):
        """Check if PostGIS Geocoder rating scored 3 or lower: good."""
        SESSION.query(
            Location.rating,
            Location.location_publish
        ).filter(
            (Location.rating == 'RANGE_INTERPOLATED') |
            (Location.rating == 'ROOFTOP')
        ).update({"location_publish": True})

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_geocoder_bad_rating(self):
        """Check if PostGIS Geocoder rating scored higher than 3: bad."""
        SESSION.query(
            Location.rating,
            Location.location_publish
        ).filter(
            (Location.rating == 'GEOMETRIC_CENTER') |
            (Location.rating == 'APPROXIMATE') |
            (Location.rating.is_(None))
        ).update({"location_publish": False})

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_west_of_new_orleans(self):
        """Check if geocoded coords are within west border of New Orleans."""
        # Long less than -90.140388 is west of New Orleans:
        SESSION.query(
            Location.longitude,
            Location.location_publish
        ).filter(
            Location.longitude < -90.140388
        ).update({
            "location_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_east_of_new_orleans(self):
        """Check if geocoded coords are within east border of New Orleans."""
        # Long greater than -89 is east of New Orleans:
        SESSION.query(
            Location.longitude,
            Location.location_publish
        ).filter(
            Location.longitude > -89.0
        ).update({
            "location_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_south_of_new_orleans(self):
        """Check if geocoded coords are within south border of New Orleans."""
        # Lat less than 29.864543 is south of New Orleans:
        SESSION.query(
            Location.latitude,
            Location.location_publish
        ).filter(
            Location.latitude < 29.864543
        ).update({
            "location_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_north_of_new_orleans(self):
        """Check if geocoded coords are within north border of New Orleans."""
        # Lat less than 29.864543 is north of New Orleans:
        SESSION.query(
            Location.latitude,
            Location.location_publish
        ).filter(
            Location.latitude > 30.181719
        ).update({
            "location_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def make_all_details_publishable(self):
        """
        Assume all sales are publishable.

        Set detail_publishable = 1. Then set to 0 if questionable data found.
        """
        # Assume publishable, then check for reasons not to publish.
        SESSION.query(
            Detail.detail_publish
        ).update({
            "detail_publish": True
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_if_no_date(self):
        """Check if sale has a date."""
        SESSION.query(
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
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_relative_date(self):
        """Check if sale date is >6 months prior to the recorded date."""
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

            # For sales recorded on a given day, check if the document
            # date is unbelievable (too old or in the future)

            try:
                with SESSION.begin_nested():
                    SESSION.query(
                        Detail.document_recorded,
                        Detail.document_date,
                        Detail.detail_publish
                    ).filter(
                        Detail.document_recorded == current_date_string
                    ).filter(
                        Detail.document_date < old_date_string
                    ).update({"detail_publish": False})

                    SESSION.flush()
            except Exception as error:
                log.exception(error, exc_info=True)
                SESSION.rollback()

            try:
                with SESSION.begin_nested():
                    SESSION.query(
                        Detail.document_recorded,
                        Detail.document_date,
                        Detail.detail_publish
                    ).filter(
                        Detail.document_recorded == current_date_string
                    ).filter(
                        Detail.document_date > previous_date_string
                    ).update({
                        "detail_publish": False
                    })

                    SESSION.flush()
            except Exception as error:
                log.exception(error, exc_info=True)
                SESSION.rollback()

            SESSION.commit()

            current_date = current_date + timedelta(days=1)

    def check_low_amount(self):
        """Check if sale amount is unreasonably low (<= $0)."""
        # Not sure about these, so check them all for now to be safe
        SESSION.query(
            Detail.amount,
            Detail.detail_publish
        ).filter(
            Detail.amount <= 0
        ).update({
            "detail_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def check_high_amount(self):
        """Check if sale amount is unreasonably high (>= $20,000,000)."""
        # Anything over $20,000,000 wouldn't be impossible, but is rare
        SESSION.query(
            Detail.amount,
            Detail.detail_publish
        ).filter(
            Detail.amount >= 20000000
        ).update({
            "detail_publish": False
        })

        try:
            with SESSION.begin_nested():
                SESSION.flush()
        except Exception as error:
            log.exception(error, exc_info=True)
            SESSION.rollback()

        SESSION.commit()

    def main(self):
        """Run through each check method."""
        log.debug('Publish')
        print('Publishing...')

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
