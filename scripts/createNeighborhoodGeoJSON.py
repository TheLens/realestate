# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import urllib

from sqlalchemy import create_engine, desc, insert, update, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app_config import server_connection, server_engine

Base = declarative_base()

conn = psycopg2.connect("%s" % (server_connection))
c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (server_engine))

def doStuff():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    sql = """
    SELECT ST_AsGeoJSON(geom), gnocdc_lab FROM neighborhoods;
    """

    result = engine.execute(sql)

    for row in result:

        file_name = str(row['gnocdc_lab'])

        # file_name = urllib.quote(file_name, '')
        # file_name = file_name.replace('.', '%2E')

        f = open('static/neighborhood-geojson/' + file_name + '.json', 'w')
        row = str(row['st_asgeojson'])
        f.write(row)
        #f.write('var neighborhood_geojson = ' + row + ';')
        f.close

if __name__ == '__main__':
    doStuff()
