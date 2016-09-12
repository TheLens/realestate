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
        Return a dict of the returned geocoding results.

        :param result: The returned results from Google.
        :type result: JSON
        :returns: A dict with rating, latitude, longitude and ZIP code.
        :rtype: dict
        """
        log.debug('process_google_results')

        dict_output = {}

        geometry = result[0]['geometry']
        address_components = result[0]['address_components']

        # TODO: result[1] or more?
        dict_output['latitude'] = geometry['location']['lat']
        dict_output['longitude'] = geometry['location']['lng']
        dict_output['rating'] = geometry['location_type']

        try:
            dict_output['zip_code'] = address_components[7]['short_name']
        except Exception:
            log.info("No zip code.")
            dict_output['zip_code'] = "None"

        return dict_output

    def geocode(self):
        """Update latitude, longitude, rating & zip in the locations table."""
        log.debug('Geocode')
        print('\nGeocoding...')

        null_query = self.get_rows_with_null_rating()

        for row in null_query:
            full_address = "{0} {1}, New Orleans, LA".format(
                row.street_number, row.address)

            # Let it fail on any errors so API doesn't continue to get hit.
            geocode_result = self.gmaps.geocode(full_address)
            dict_output = self.process_google_results(geocode_result)

            try:
                with SESSION.begin_nested():
                    u = update(Location)
                    u = u.values(dict_output)
                    u = u.where(Location.document_id == row.document_id)
                    SESSION.execute(u)
                    SESSION.flush()
            except Exception as error:
                log.exception(error, exc_info=True)
                SESSION.rollback()

            SESSION.commit()

        log.debug('Done geocoding')

if __name__ == '__main__':
    pass
