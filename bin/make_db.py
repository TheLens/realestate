# -*- coding: utf-8 -*-

from __future__ import absolute_import

import psycopg2
from sqlalchemy import create_engine
from fabric.api import local

from landrecords import db
from landrecords.settings import dev_config


def make_db():
    engine = create_engine('%s' % (dev_config.SERVER_ENGINE),
                           implicit_returning=True)
    db.Base.metadata.create_all(engine)

# def neighborhoods_json():
    # local("ogr2ogr -f GeoJSON -s_srs ESRI::../data/neighborhoods/102682.prj
    # -t_srs EPSG:4326 neighborhoods.json
    # ../data/neighborhoods/Neighborhood_Statistical_Areas.shp")
    # local("topojson -o neighborhoods-topo.json --properties name=gnocdc_lab
    # neighborhoods.json")
    # cp neighborhoods-topo.json static/js/neigbhorhoods-topo.js
    # vim neighborhoods-topo.js: var neighborhoods = {...};
    # minify: yuicompressor neighborhoods-topo.js -o neighborhoods-topo.min.js

# def squares_json():
    # local("ogr2ogr -f GeoJSON -s_srs ESRI::../data/squares/102682.prj -t_srs
    # EPSG:4326 squares.json ../data/squares/NOLA_Squares_20140221.shp")
    # local("topojson -o squares-topo.json --properties square=SQUARE
    # --properties dist=MUN_DST squares.json")
    # cp squares-topo.json static/js/squares-topo.js
    # vim squares-topo.js: var squares = {...};
    # too big to be minified


def import_neighorhoods():
    local("""
        shp2pgsql -I %s/neighborhoods/Neighborhood_Statistical_Areas \
        neighborhoods | psql -d landrecords""" % (dev_config.GEO_DIR))
    # If need to alter geometry's SRID
    cur.execute("SELECT updategeometrysrid('neighborhoods','geom',3452);")
    cur.execute("""
        ALTER TABLE neighborhoods
        ALTER COLUMN geom TYPE geometry(MultiPolygon,4326)
        USING ST_Transform(geom,4326);""")

    # Delete duplicate neighborhoods
    # cur.execute("DELETE FROM neighborhoods USING neighborhoods n2 WHERE
    # neighborhoods.gnocdc_lab = n2.gnocdc_lab AND neighborhoods.gid
    # < n2.gid;")
    # Note: Using PostGIS to export CBD as JSON produced a file with errors,
    # so I had to manually export that selection in QGIS and change to
    # MultiPolygon in text editor.

    conn.commit()


# def import_squares():
#     local("""
#         shp2pgsql -I %s/squares/NOLA_Squares_20140221 squares \
#         | psql -d landrecords""" % (dev_config.GEO_DIR))
#     cur.execute("SELECT updategeometrysrid('squares','geom',3452);")
#     cur.execute("""
#         ALTER TABLE squares
#         ALTER COLUMN geom TYPE geometry(MultiPolygon,4326)
#         USING ST_Transform(geom,4326);""")
#     conn.commit()


def spatial_index_on_cleaned_geom():
    local('''
        psql landrecords -c "CREATE INDEX index_cleaned_geom ON cleaned \
        USING GIST(geom);"''')

if __name__ == '__main__':
    conn = psycopg2.connect("%s" % (dev_config.SERVER_CONNECTION))
    cur = conn.cursor()

    import_neighorhoods()
    # import_squares()

    make_db()

    spatial_index_on_cleaned_geom()

    cur.close()
    conn.close()
