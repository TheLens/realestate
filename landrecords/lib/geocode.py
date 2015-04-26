# -*- coding: utf-8 -*-

'''
Geocoding and spatial queries.
Geocode street addresses and find which neighborhood they are in.
'''

import psycopg2
import googlemaps
from sqlalchemy import create_engine, func, cast, Float, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords.db import (
    Location,
    Neighborhood
)
from landrecords import log


class Geocode(object):

    '''Geocode class that needs no input.'''

    def __init__(self):
        '''Generates connections to PostgreSQL and SQLAlchemy.'''

        self.gmaps = googlemaps.Client(key=Config().GOOGLE_API_KEY)

        self.conn = psycopg2.connect(Config().SERVER_CONNECTION)
        self.cursor = self.conn.cursor()

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
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
        ).filter(
            Location.rating.is_(None)
        ).all()

        log.debug('Rows with rating is NULL: %d', len(query))

        session.close()

        return query

    def process_google_results(self, result):
        '''Process the returned geocoding results.'''

        # log.debug(result)

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
        Uses Google Geocoding API for locations with rating/lat/lng of NULL.
        '''

        session = self.sn()

        log.debug('Geocode')
        print '\nGeocoding...'

        null_query = self.get_rows_with_null_rating()

        for row in null_query:
            full_address = row.street_number + ' ' + row.address + \
                ', New Orleans, LA'

            try:
                geocode_result = self.gmaps.geocode(full_address)
                dict_output = self.process_google_results(geocode_result)
            except Exception, error:
                log.exception(error, exc_info=True)

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
    pass
