# -*- coding: utf-8 -*-

"""
Create database and make tables.
Creates the database if not yet created, creates tables, imports geographic
data and creates spatial indexes. It makes use of `db.py`.
"""

import os
import psycopg2
from sqlalchemy import create_engine
from subprocess import call, Popen, PIPE

from realestate import log, DATABASE_NAME, GEO_DIR
from realestate import db


class MakeDB(object):

    '''Create database and make tables.'''

    def main(self):
        '''Run all methods.'''

        self.create_db()
        self.create_tables()
        self.import_neighorhoods()
        self.spatial_index_on_cleaned_geom()

    @staticmethod
    def create_db():
        """
        Create database if it doesn\'t already exist.
        """

        log.debug('create_db')

        try:
            conn = psycopg2.connect(
                "%s" % (os.environ.get('REAL_ESTATE_SERVER_CONNECTION')))
            cur = conn.cursor()
            sql = "SELECT 1;"
            cur.execute(sql)
        except Exception, error:
            log.exception(error, exc_info=True)
            call([
                'createdb',
                '%s' % DATABASE_NAME
            ])

            conn = psycopg2.connect(
                "%s" % (os.environ.get('REAL_ESTATE_SERVER_CONNECTION')))
            cur = conn.cursor()
            cur.execute("CREATE EXTENSION POSTGIS;")

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def create_tables():
        '''Create tables in SQLAlchemy.'''

        log.debug('create_tables')

        engine = create_engine(
            os.environ.get('REAL_ESTATE_SERVER_ENGINE')
        )
        db.Base.metadata.create_all(engine)

    @staticmethod
    def import_neighorhoods():
        '''Import neighborhood shapefiles.'''

        log.debug('import_neighorhoods')

        conn = psycopg2.connect(
            "%s" % (os.environ.get('REAL_ESTATE_SERVER_CONNECTION')))
        cur = conn.cursor()

        p1 = Popen(
            [
                'shp2pgsql',
                '-I',
                '-a',  # appends data to existing table. don't create.
                '{0}/neighborhoods/shapefile'.format(GEO_DIR) +
                '/Neighborhood_Statistical_Areas',
                'neighborhoods'
            ],
            stdout=PIPE
        )

        p2 = Popen(
            [
                'psql',
                '-d',
                '%s' % DATABASE_NAME
            ],
            stdin=p1.stdout,
            stdout=PIPE
        )

        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.communicate()[0]

        # If need to alter geometry's SRID
        cur.execute("""
            SELECT updategeometrysrid('neighborhoods', 'geom', 3452);""")
        cur.execute("""
            ALTER TABLE neighborhoods
            ALTER COLUMN geom TYPE geometry(MultiPolygon, 4326)
            USING ST_Transform(geom, 4326);""")

        conn.commit()

        cur.close()
        conn.close()

    @staticmethod
    def spatial_index_on_cleaned_geom():
        '''Create spatial index on cleaned table.'''

        log.debug('spatial_index_on_cleaned_geom')

        conn = psycopg2.connect(
            "%s" % (os.environ.get('REAL_ESTATE_SERVER_CONNECTION')))
        cur = conn.cursor()

        sql = """
            CREATE INDEX index_cleaned_geom ON cleaned USING GIST(geom);"""

        cur.execute(sql)

        conn.commit()

        cur.close()
        conn.close()

if __name__ == '__main__':
    MakeDB().main()
    # MakeDB().create_db()
