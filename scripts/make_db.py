# -*- coding: utf-8 -*-

'''Create database and setup tables'''

# from __future__ import absolute_import

import psycopg2
from sqlalchemy import create_engine
from subprocess import call, Popen, PIPE

from landrecords.lib.log import Log
from landrecords.config import Config
from landrecords import db


class MakeDB(object):

    def main(self):
        self.import_neighorhoods()
        self.make_db()
        self.spatial_index_on_cleaned_geom()

    def make_db(self):
        '''Create tables in SQLAlchemy'''

        engine = create_engine(Config().SERVER_ENGINE,
                               implicit_returning=True)
        db.Base.metadata.create_all(engine)

    def import_neighorhoods(self):
        '''Import neighborhood shapefiles'''

        conn = psycopg2.connect("%s" % (Config().SERVER_CONNECTION))
        cur = conn.cursor()

        p1 = Popen(['shp2pgsql',
                    '-I',
                    '{0}/neighborhoods/shapefile'.format(Config().GEO_DIR) +
                    '/Neighborhood_Statistical_Areas', 'neighborhoods'],
                   stdout=PIPE)
        p2 = Popen(['psql',
                    '-d',
                    'landrecords'],
                   stdin=p1.stdout,
                   stdout=PIPE)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.communicate()[0]

        # If need to alter geometry's SRID
        cur.execute("SELECT updategeometrysrid('neighborhoods','geom',3452);")
        cur.execute("""
            ALTER TABLE neighborhoods
            ALTER COLUMN geom TYPE geometry(MultiPolygon,4326)
            USING ST_Transform(geom,4326);""")

        conn.commit()

        cur.close()
        conn.close()

    def spatial_index_on_cleaned_geom(self):
        '''Create spatial index on cleaned table'''

        call(['psql',
              'landrecords',
              '-c',
              'CREATE INDEX index_cleaned_geom ON cleaned USING GIST(geom);'])

    # def delete_duplicate_neighborhoods():
        # cur.execute("DELETE FROM neighborhoods USING neighborhoods n2 WHERE
        # neighborhoods.gnocdc_lab = n2.gnocdc_lab AND neighborhoods.gid
        # < n2.gid;")
        # Note: Using PostGIS to export CBD as JSON
        # produced a file with errors,
        # so I had to manually export that selection in QGIS and change to
        # MultiPolygon in text editor.

    # def neighborhoods_json():
        # local("ogr2ogr -f GeoJSON -s_srs
        # ESRI::../data/neighborhoods/102682.prj
        # -t_srs EPSG:4326 neighborhoods.json
        # ../data/neighborhoods/Neighborhood_Statistical_Areas.shp")
        # local("topojson -o neighborhoods-topo.json
        # --properties name=gnocdc_lab
        # neighborhoods.json")
        # cp neighborhoods-topo.json static/js/neigbhorhoods-topo.js
        # vim neighborhoods-topo.js: var neighborhoods = {...};
        # minify: yuicompressor neighborhoods-topo.js
        # -o neighborhoods-topo.min.js

if __name__ == '__main__':
    log = Log(__name__).initialize_log()
    MakeDB().main()
