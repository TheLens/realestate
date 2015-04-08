# -*- coding: utf-8 -*-

import psycopg2

from landrecords import config
from landrecords.lib.log import Log


class Geocoder(object):

    def __init__(self):
        self.log = Log('geocoder').logger

        self.conn = psycopg2.connect(config.SERVER_CONNECTION)
        self.cur = self.conn.cursor()

        self.geocode()

    def geocode(self):
        print "Geocoding..."

        '''
        Geocodes existing records and/or new records — any records that
        have not yet been geocoded.
        Geocoder takes strings: 4029 Ulloa St, New Orleans, LA 70119
        I took a shortcut. Instead of finding a way to concatenate the address
        pieces on the fly, I concatenated them all into a new column, then read
        from that column. Sloppy, but it works for now.
        '''
        self.cur.execute("""UPDATE locations
            SET full_address = street_number::text || ' ' ||
            address::text || ', New Orleans, LA';""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' ST ', ' SAINT ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' FIRST ', ' 1ST ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' SECOND ', ' 2ND ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' THIRD ', ' 3RD ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' FOURTH ', ' 4TH ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' FIFTH ', ' 5TH ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' SIXTH ', ' 6TH ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' SEVENTH ', ' 7TH ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' EIGHTH ', ' 8TH ');""")
        self.cur.execute("""UPDATE locations
            SET full_address = replace(full_address,
             ' NINTH ', ' 9TH ');""")

        '''
        An altered version of the following batch geocoding code:
        http://postgis.net/docs/Geocode.html
        It will only geocode entries without ratings (new records), so this is
        good for either batch processing or only processing new records.
        self.cur.execute("UPDATE locations SET (rating, longitude, latitude) =
        (COALESCE((g.geo).rating,-1), ST_X((g.geo).geomout)::numeric(8,5),
        ST_Y((g.geo).geomout)::numeric(8,5)) FROM (SELECT document_id FROM
        locations WHERE rating IS NULL ORDER BY document_id) As a  LEFT JOIN
        (SELECT document_id, (geocode(full_address,1)) As geo FROM locations
        As ag WHERE ag.rating IS NULL ORDER BY document_id) As g ON a.
        document_id = g.document_id WHERE
        a.document_id = locations.document_id;")

        If restoring database or using a copy of a database creates
        problems with
        TIGER or geocode() function ("HINT:  No function matches the given name
        and argument types. You might need to add explicit type casts."),
        follow the instructions here and run `ALTER DATABASE landrecords SET
        search_path=public, tiger;`: http://lists.osgeo.org/pipermail/postgis-
        users/2011-October/031156.html
        '''
        self.cur.execute("""UPDATE locations
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
        self.conn.commit()
