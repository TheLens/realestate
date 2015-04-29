# -*- coding: utf-8 -*-

"""
Uses the Google Geocoding API (we used to use the PostGIS Geocoder) to
geocode addresses, resulting in ZIP codes, latitude, longitude and an
accuracy rating. A rating of "ROOFTOP" or "RANGE_INTERPOLATED" is good enough
for publication.

This also includes a method that uses PostGIS to find the neighborhood in
which each sale occurred, working with a neighborhood shapefile available
from [data.nola.gov](http://data.nola.gov).
"""

import os
import psycopg2
import googlemaps
from sqlalchemy import create_engine, func, cast, Float, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.db import (
    Detail,
    Location,
    Neighborhood
)
from landrecords import log


class Geocode(object):

    '''Geocode class that needs no input.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Generates connections to PostgreSQL and SQLAlchemy.'''

        self.initial_date = initial_date
        self.until_date = until_date

        self.gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_API_KEY'))

        self.conn = psycopg2.connect(os.environ.get('SERVER_CONNECTION'))
        self.cursor = self.conn.cursor()

        base = declarative_base()
        self.engine = create_engine(os.environ.get('SERVER_ENGINE'))
        base.metadata.create_all(self.engine)
        self.sn = sessionmaker(bind=self.engine)

    def update_locations_with_neighborhoods(self):
        '''Finds neighborhoods and handles if none found.'''

        self.neighborhood_found()
        self.no_neighborhood_found()

    def neighborhood_found(self):
        '''Use PostGIS to find which neighborhood a long/lat pair is in.'''

        log.debug('neighborhood_found')

        session = self.sn()

        session.query(
            # Neighborhood,
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

        session.commit()
        session.close()

    def no_neighborhood_found(self):
        '''If no neighborhood is found, update with "None" in nbhd field.'''

        log.debug('no_neighborhood_found')

        session = self.sn()

        session.query(
            Location
        ).filter(
            Location.neighborhood.is_(None)
        ).update(
            {Location.neighborhood: "None"},
            synchronize_session='fetch'
        )

        session.commit()
        session.close()

    def get_rows_with_null_rating(self):
        '''Gets locations with rating IS NULL.'''

        session = self.sn()

        query = session.query(
            Location.rating,
            Location.document_id,
            Location.street_number,
            Location.address
        ).join(
            Detail
        ).filter(
            Location.rating.is_(None)
        ).filter(
            Detail.document_recorded >= '%s' % self.initial_date
        ).filter(
            Detail.document_recorded <= '%s' % self.until_date
        ).all()

        log.debug('Rows with rating is NULL: %d', len(query))

        session.close()

        return query

    def process_google_results(self, result):
        '''
        Returns a dict of the returned geocoding results.

        :param result: The returned results from Google.
        :type result: JSON
        :returns: A dict with rating, latitude, longitude and ZIP code.
        :rtype: dict
        '''

        log.debug('process_google_results')

        dict_output = {}

        geometry = result[0]['geometry']
        address_components = result[0]['address_components']

        # todo: result[1] or more?
        dict_output['latitude'] = geometry['location']['lat']
        dict_output['longitude'] = geometry['location']['lng']
        dict_output['rating'] = geometry['location_type']

        try:
            dict_output['zip_code'] = address_components[7]['short_name']
        except Exception, error:
            log.exception(error, exc_info=True)
            dict_output['zip_code'] = "None"

        # log.debug(dict_output)

        return dict_output

    def geocode(self):
        '''
        Updates latitude, longitude, rating and zip_code fields in the
        locations table using the Google Geocoding API.
        '''

        session = self.sn()

        log.debug('Geocode')
        print '\nGeocoding...'

        null_query = self.get_rows_with_null_rating()

        for row in null_query:
            full_address = row.street_number + ' ' + row.address + \
                ', New Orleans, LA'

            # Let it fail on any errors so API doesn't continue to get hit.
            geocode_result = self.gmaps.geocode(full_address)
            dict_output = self.process_google_results(geocode_result)

            try:
                with session.begin_nested():
                    u = update(Location)
                    u = u.values(dict_output)
                    u = u.where(Location.document_id == row.document_id)
                    session.execute(u)
                    session.flush()
            except Exception, error:
                log.exception(error, exc_info=True)
                session.rollback()

            session.commit()

            # break

        session.close()

        log.debug('Done geocoding')

if __name__ == '__main__':
    try:
        Geocode(
            initial_date='2014-02-18',
            until_date='2014-05-08'
        ).get_rows_with_null_rating()
    except Exception, error:
        log.exception(error, exc_info=True)

    pass
