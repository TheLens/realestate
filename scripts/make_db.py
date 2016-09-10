# -*- coding: utf-8 -*-

"""
Create database and make tables.

Creates the database if not yet created, creates tables, imports geographic
data and creates spatial indexes. It makes use of `db.py`.
"""

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from subprocess import call, Popen, PIPE

from www.db import Base
from www import log, DATABASE_NAME, ENGINE_STRING, GEO_DIR


class MakeDB(object):
    """Create database and make tables."""

    def __init__(self):
        """Create database."""
        try:
            self._database_connection()
        except OperationalError as error:
            print(error)
            log.exception(error, exc_info=True)

            db_error = (
                '(psycopg2.OperationalError) FATAL:  database "{}" ' +
                'does not exist').format(DATABASE_NAME)

            if str(error).strip() == db_error:
                self.create_db()

        self._create_tables()
        self._import_neighorhoods()
        self._spatial_index_on_cleaned_geom()

        self.conn.close()

    def create_db(self):
        """Create database."""
        log.debug('create_db')

        call(['createdb', DATABASE_NAME])  # Create database
        self._database_connection()  # Connect to database
        self._add_db_extensions()  # Add Postgres extensions

    def _add_db_extensions(self):
        """Add Postgres extensions."""
        self.engine.execute("CREATE EXTENSION POSTGIS;")

    def _database_connection(self):
        """Create connection to the database."""
        self.engine = create_engine(ENGINE_STRING)
        self.conn = self.engine.connect()

    def _create_tables(self):
        """Create tables in SQLAlchemy."""
        log.debug('create_tables')

        Base.metadata.create_all(self.engine)

    def _import_neighorhoods(self):
        """Import neighborhood shapefiles."""
        # TODO: This causes errors on second run.

        log.debug('import_neighorhoods')

        p1 = Popen(
            [
                'shp2pgsql',
                '-I',
                '-a',  # Append data to existing table. Don't create.
                (
                    '{}/neighborhoods/shapefile/Neighborhood_Statistical_Areas'
                ).format(GEO_DIR),
                'neighborhoods'
            ],
            stdout=PIPE)

        p2 = Popen(
            [
                'psql',
                '-d',
                DATABASE_NAME
            ],
            stdin=p1.stdout,
            stdout=PIPE)

        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.communicate()[0]

        # If need to alter geometry's SRID
        self.conn.execute("""
            SELECT updategeometrysrid('neighborhoods', 'geom', 3452);""")
        self.conn.execute("""
            ALTER TABLE neighborhoods
            ALTER COLUMN geom TYPE geometry(MultiPolygon, 4326)
            USING ST_Transform(geom, 4326);""")

    def _spatial_index_on_cleaned_geom(self):
        """Create spatial index on cleaned table."""
        log.debug('spatial_index_on_cleaned_geom')

        sql = """
            CREATE INDEX index_cleaned_geom
            ON cleaned
            USING GIST(geom);"""

        self.conn.execute(sql)

if __name__ == '__main__':
    MakeDB()
