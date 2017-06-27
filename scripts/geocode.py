# -*- coding: utf-8 -*-

"""
Use the Google Geocoding API to geocode addresses.

Returns ZIP codes, latitude, longitude and an accuracy rating.
A rating of "ROOFTOP" or "RANGE_INTERPOLATED" is good enough for publication.

This also includes a method that uses PostGIS to find the neighborhood in
which each sale occurred, working with a neighborhood shapefile available
from [data.nola.gov](http://data.nola.gov).
"""

import os
import googlemaps

from sqlalchemy import func, cast, Float, update

from www.db import Detail, Location, Neighborhood
from www import log, SESSION


class Geocode(object):
    """Geocode class that needs no input."""

    def __init__(self, initial_date=None, until_date=None):
        """Generate connections to PostgreSQL and SQLAlchemy."""
        self.initial_date = initial_date
        self.until_date = until_date

        self.gmaps = googlemaps.Client(
            key=os.environ.get('GOOGLE_GEOCODING_API_KEY'))

    def update_locations_with_neighborhoods(self):
        """Find neighborhoods and handles if none found."""
        self.neighborhood_found()
        self.no_neighborhood_found()

    def neighborhood_found(self):
        """Use PostGIS to find which neighborhood a long/lat pair is in."""
        log.debug('neighborhood_found')

        SESSION.query(
            Location
        ).filter(
            func.ST_Contains(
                Neighborhood.geom,
                func.ST_SetSRID(
                    func.ST_Point(
                        cast(Location.longitude, Float),
                        cast(Location.latitude, Float)
                    ),
                    4326
                )
            )
        ).update(
            {Location.neighborhood: Neighborhood.gnocdc_lab},
            synchronize_session='fetch'
        )

        SESSION.commit()

    def no_neighborhood_found(self):
        """If no neighborhood is found, update with "None" in nbhd field."""
        log.debug('no_neighborhood_found')

        SESSION.query(
            Location
        ).filter(
            Location.neighborhood.is_(None)
        ).update(
            {Location.neighborhood: "None"},
            synchronize_session='fetch'
        )

        SESSION.commit()

    def get_rows_with_null_rating(self):
        """
        Return query result for locations with rating IS NULL.

        :returns: SQLAlchemy query result.
        """
        query = SESSION.query(
            Location.rating,
            Location.document_id,
            Location.street_number,
            Location.address
        ).join(
            Detail
        ).filter(
            Location.rating.is_(None)
        ).filter(
            Detail.document_recorded >= '{}'.format(self.initial_date)
        ).filter(
            Detail.document_recorded <= '{}'.format(self.until_date)
        ).all()

        log.debug('Rows with rating is NULL: {}'.format(len(query)))

        SESSION.close()

        return query

    def process_google_results(self, result):
        """
        Get values from the geocoding results.

        https://developers.google.com/maps/documentation/geocoding/
            intro#GeocodingResponses

        :param result: Results from Google Geocoding API ("results" list only).
        :type result: list
        :returns: This location's rating, latitude, longitude and ZIP code.
        :rtype: dict
        """
        # TODO: Handle more than one returned location in result.
        #   Could compare accuracies and use that to decide which to store.
        loc = result[0]

        values = {
            'latitude': loc['geometry']['location']['lat'],
            'longitude': loc['geometry']['location']['lng'],
            'rating': loc['geometry']['location_type']}

        try:
            values['zip_code'] = loc['address_components'][7]['short_name']
        except Exception:  # TODO: More specific error.
            log.info("No zip code.")
            values['zip_code'] = "None"  # TODO: Leave blank instead?

        return values

    def geocode(self):
        """Update latitude, longitude, rating and ZIP in Locations table."""
        print('\nGeocoding...')

        null_rating_rows = self.get_rows_with_null_rating()

        for row in null_rating_rows:
            full_address = "{0} {1}, New Orleans, LA".format(
                row.street_number, row.address)

            result = self.gmaps.geocode(full_address)

            if len(result) == 0:
                log.info('No geocoding results for: {}'.format(full_address))

                # TODO: Need to also note failure so future geocoding scripts
                #   don't keep trying and failing on the same addresses.
                #   Possibly update Location's `rating` and/or Cleaned's
                #   `location_publish` fields.
                continue

            details = self.process_google_results(result)

            try:
                with SESSION.begin_nested():
                    u = update(Location)
                    u = u.values(details)
                    u = u.where(Location.document_id == row.document_id)
                    SESSION.execute(u)
                    SESSION.flush()
            except Exception as error:  # TODO: Handle specific errors.
                log.exception(error, exc_info=True)
                SESSION.rollback()

            SESSION.commit()


if __name__ == '__main__':
    pass
