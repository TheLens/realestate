# -*- coding: utf-8 -*-

'''
Geocoding and spatial queries.
Geocode street addresses and find which neighborhood they are in.
'''

import psycopg2

from sqlalchemy import create_engine, func, cast, Float
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

        self.conn = psycopg2.connect(Config().SERVER_CONNECTION)
        self.cur = self.conn.cursor()

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

    def geocode(self):
        '''
        This will geocode entries without ratings (new records), so
        this is good for batch processing an untouched archive and
        only processing new records.
        An altered version of the following batch geocoding code:
        http://postgis.net/docs/Geocode.html
        '''

        log.debug('Geocode')
        print 'Geocoding...'

        self.engine.execute("""UPDATE locations
            SET (rating, zip_code, longitude, latitude) = (
                COALESCE((g.geo).rating, -1),
                (g.geo).addy.zip,
                ST_X((g.geo).geomout)::numeric(8, 5),
                ST_Y((g.geo).geomout)::numeric(8, 5)
            )
            FROM (
                SELECT document_id
                FROM locations
                WHERE rating IS NULL
                ORDER BY document_id
            ) As a
            LEFT JOIN (
                SELECT document_id, (geocode(full_address, 1)) As geo
                FROM locations
                WHERE locations.rating IS NULL
                ORDER BY document_id
            ) As g ON a.document_id = g.document_id
            WHERE a.document_id = locations.document_id;""")

if __name__ == '__main__':
    pass
