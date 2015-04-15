# -*- coding: utf-8 -*-

import psycopg2

from sqlalchemy import create_engine, func, cast, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords import db
from landrecords.lib.log import Log

log = Log('initialize').logger


class Geocode(object):

    def __init__(self):
        self.conn = psycopg2.connect(Config().SERVER_CONNECTION)
        self.cur = self.conn.cursor()

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    def update_locations_with_neighborhoods(self):
        self.neighborhood_found()
        self.no_neighborhood_found()

    def neighborhood_found(self):
        self.session.query(
            # db.Neighborhood
            db.Location
        ).filter(
            func.ST_Contains(
                db.Neighborhood.geom,
                func.ST_SetSRID(
                    func.ST_Point(
                        cast(db.Location.longitude, Float),
                        cast(db.Location.latitude, Float)
                    ),
                    4326
                )
            )
        ).update(
            {db.Location.neighborhood: db.Neighborhood.gnocdc_lab},
            synchronize_session='fetch'
        )

        self.session.commit()

    def no_neighborhood_found(self):
        self.session.query(
            db.Location
        ).filter(
            db.Location.neighborhood.is_(None)
        ).update(
            {db.Location.neighborhood: "None"},
            synchronize_session='fetch'
        )

        self.session.commit()

    def geocode(self):
        log.debug('Geocoder')

        '''An altered version of the following batch geocoding code:'''
        '''http://postgis.net/docs/Geocode.html'''
        '''It will only geocode entries without ratings (new records), so '''
        '''this is good for batch processing or only processing new records.'''

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
