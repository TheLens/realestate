#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import re
import urllib2
import psycopg2
import Cleanup
import pprint
import logging
import logging.handlers
import random
import time

from fabric.api import local
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, insert, func, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import gmail, check_assessor_urls
from databasemaker import Detail, Location, Vendor, Vendee, Cleaned, Neighborhood, Square, Dashboard
from pythonEmail.py import main
from app_config import server_engine, server_connection, backup_directory

pp = pprint.PrettyPrinter()

Base = declarative_base()
engine = create_engine('%s' % (server_engine))

conn = psycopg2.connect("%s" % (server_connection))
cur = conn.cursor()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
fh = logging.FileHandler('logs/land-records_%s.log' % (datetime.now().strftime('%Y-%m-%d')))
fh.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(lineno)d - %(message)s')
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today_date = datetime.now
year = (datetime.now() - timedelta(days=1)).strftime('%Y') # "2014"
month = (datetime.now() - timedelta(days=1)).strftime('%m') # "09"
day = (datetime.now() - timedelta(days=1)).strftime('%d') # "09"

# Scrape "Document Detail"
def document_details(form, form_id):
    logger.info('document_details')
    logger.info(form_id)
    soup = BeautifulSoup(open(form))
    rows = soup.find('table', id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList").find_all('tr')
    output = []
    for row in rows:
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            # i = 0, 1, 0, 1, etc. It equals 0 for titles (the first in the tr row)
            # Only want the good stuff (i = 1)
            if i == 1:
                cell = str(cell.string) # Get ".string" for content in between tags, then convert to a string type
                if cell == "None": # In the case that the cell is blank, the loop won't fail
                    cell = ""
                output.append(cell)
                
    output.append(form_id)
    amt = output[10]
    amt = re.sub(r"\$",r"", amt)
    amt = re.sub(r"\,",r"", amt)
    output[10] = int(float(amt))

    dict_output = {}
    dict_output = {
        'document_type': '%s' % (output[0]),
        'instrument_no': '%s' % (output[1]),
        'multi_seq': '%s' % (output[2]),
        'min_': '%s' % (output[3]),
        'cin': '%s' % (output[4]),
        'book_type': '%s' % (output[5]),
        'book': '%s' % (output[6]),
        'page': '%s' % (output[7]),
        'amount': '%d' % (output[10]),
        'status': '%s' % (output[11]),
        'prior_mortage_doc_type': '%s' % (output[12]),
        'prior_conveyance_doc_type': '%s' % (output[13]),
        'cancel_status': '%s' % (output[14]),
        'remarks': '%s' % (output[15]),
        'no_pages_in_image': '%s' % (output[16]),
        'image': '%s' % (output[17]), 
        'document_id': '%s' % (output[18])
       }

    if output[8] == "":
        dict_output['document_date'] = None
    else:
        dict_output['document_date'] = '%s' % (output[8])

    if output[9] == "":
        dict_output['document_recorded'] = None
    else:
        dict_output['document_recorded'] = '%s' % (output[9])

    i = insert(Detail)
    i = i.values(dict_output)
    session.execute(i)

    dict_output = {}
    output = []

# Scrape "Vendor/Mortgagor Names"
def vendors(form, form_id):
    logger.info('vendors')
    logger.info(form_id)
    soup = BeautifulSoup(open(form))
    vendorrows = soup.find('table', id="ctl00_cphNoMargin_f_oprTab_tmpl0_DataList11").find_all('tr')
    output = []
    for row in vendorrows:
        cells = row.find_all('span')
        for i, cell in enumerate(cells):
            if i >= 5 and i % 5 == 0: # means this is the last in a new row, i = 5, 10, 15, etc.
                if isinstance(cell, str) == 0:
                    cell = str(cell.string)
                if cell == "None":
                    cell = ""
                output.append(cell)
                output.append(form_id)
                dict_output = {}
                dict_output = {
                    'vendor_blank': '%s' % (output[0]),
                    'vendor_p_c': '%s' % (output[1]),
                    'vendor_lastname': '%s' % (output[2]),
                    'vendor_firstname': '%s' % (output[3]),
                    'vendor_relator': '%s' % (output[4]),
                    'vendor_cancel_status': '%s' % (output[5]),
                    'document_id': '%s' % (output[6])
                }
                i = insert(Vendor)
                i = i.values(dict_output)
                session.execute(i)
                dict_output = {}
                output = []
            else:
                if isinstance(cell, str) == 0:
                        cell = str(cell.string)
                if cell == "None":
                    cell = ""
                output.append(cell)

# Scrape "Vendee/Mortgagee Names"
def vendees(form, form_id):
    logger.info('vendees')
    logger.info(form_id)
    soup = BeautifulSoup(open(form))
    vendeerows = soup.find('table', id="ctl00_cphNoMargin_f_oprTab_tmpl0_Datalist1").find_all('tr')
    output = []
    for row in vendeerows:
        cells = row.find_all('span')
        for i, cell in enumerate(cells):
            if i >=5 and i%5 == 0: # means this is the last in a new row, i = 5, 10, 15, etc.
                if isinstance(cell, str) == 0:
                    cell = str(cell.string)
                if cell == "None":
                    cell = ""
                output.append(cell)
                output.append(form_id)
                dict_output = {}
                dict_output = {
                    'vendee_blank': '%s' % (output[0]),
                    'vendee_p_c': '%s' % (output[1]),
                    'vendee_lastname': '%s' % (output[2]),
                    'vendee_firstname': '%s' % (output[3]),
                    'vendee_relator': '%s' % (output[4]),
                    'vendee_cancel_status': '%s' % (output[5]),
                    'document_id': '%s' % (output[6])
                }
                i = insert(Vendee)
                i = i.values(dict_output)
                session.execute(i)
                dict_output = {}
                output = []
            else:
                if isinstance(cell, str) == 0:
                        cell = str(cell.string)
                if cell == "None":
                    cell = ""
                output.append(cell)

# Scrape "Legal Description - Combined Legals" tab
def locations(form, form_id):
    logger.info('locations')
    logger.info(form_id)
    soup = BeautifulSoup(open(form))
    combinedlegals = soup.find('table', id="ctl00_cphNoMargin_f_oprTab_tmpl1_ComboLegals").find_all('tr')
    output = []
    for j, row in enumerate(combinedlegals):
        cells = row.find_all('span')
        lot_from_string = ""
        for i, cell in enumerate(cells):
            # check if there are entries for lot_from and lot_to (this adds an extra column, which messes up the database since most records don't have a "Lot to" and a "Lot From" column, but just a "Lot" column:
            # check if j == 3, 13, 23, etc.
            if (j-3)%10 == 0 and len(cells) == 10: #  len(cells) == 8 if just a "lot" field, which is most common
                # If find Lot to and Lot from, concatenate with "to", store as single value, then ....
                if i%2 == 1: # Not sure
                    if isinstance(cell, str) == 0:
                            cell = str(cell.string)
                    if cell == "None":
                        cell = ""
                    if i == 5:
                        lot_from_string = cell
                        continue
                    if i == 7:
                        if lot_from_string == "":
                            cell = cell
                        if cell == "":
                            cell = lot_from_string
                        else:
                            cell = lot_from_string + " to " + cell
                    cell = re.sub(r"'",r"''", cell)
                    output.append(cell)
            else:
                if i%2 == 1: # Not sure
                    if isinstance(cell, str) == 0:
                            cell = str(cell.string)
                    if cell == "None":
                        cell = ""
                    cell = re.sub(r"'",r"''", cell)
                    output.append(cell)
        #if j == 8, 18, 28, etc. Means the end of a table, so need to commit and start over with next table (or stop if the last)
        if (j-8)%10 == 0:
            output.append(form_id)
            dict_output = {}
            dict_output = {
                'subdivision': '%s' % (output[0]),
                'condo': '%s' % (output[1]),
                'district': '%s' % (output[2]),
                'square': '%s' % (output[3]),
                'lot': '%s' % (output[4]),
                'cancel_status': '%s' % (output[5]),
                'street_number': '%s' % (output[6]),
                'address': '%s' % (output[7]),
                'unit': '%s' % (output[8]),
                'weeks': '%s' % (output[9]),
                'cancel_stat': '%s' % (output[10]),
                'freeform_legal': '%s' % (output[11]),
                'document_id': '%s' % (output[12])
            }
            i = insert(Location)
            i = i.values(dict_output)
            session.execute(i)
            dict_output = {}
            output = []

def Geocode():
    print "Geocoding..."
    logger.info('Geocode')
    '''
    Geocodes existing records and/or new records — any records that have not yet been geocoded.
    Geocoder takes strings: 4029 Ulloa St, New Orleans, LA 70119
    I took a shortcut. Instead of finding a way to concatenate the address pieces on the fly, I concatenated them all into a new column, then read from that column. Sloppy, but it works for now.
    '''
    cur.execute("UPDATE locations SET full_address = street_number::text || ' ' || address::text || ', New Orleans, LA';")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' ST ', ' SAINT ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' FIRST ', ' 1ST ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' SECOND ', ' 2ND ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' THIRD ', ' 3RD ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' FOURTH ', ' 4TH ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' FIFTH ', ' 5TH ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' SIXTH ', ' 6TH ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' SEVENTH ', ' 7TH ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' EIGHTH ', ' 8TH ');")
    cur.execute("UPDATE locations SET full_address = replace(full_address, ' NINTH ', ' 9TH ');")

    '''
    An altered version of the following batch geocoding code: http://postgis.net/docs/Geocode.html
    It will only geocode entries without ratings (new records), so this is good for either batch processing or only processing new records.
    cur.execute("UPDATE locations SET (rating, longitude, latitude) = ( COALESCE((g.geo).rating,-1), ST_X((g.geo).geomout)::numeric(8,5), ST_Y((g.geo).geomout)::numeric(8,5)) FROM (SELECT document_id FROM locations WHERE rating IS NULL ORDER BY document_id) As a  LEFT JOIN (SELECT document_id, (geocode(full_address,1)) As geo FROM locations As ag WHERE ag.rating IS NULL ORDER BY document_id) As g ON a.document_id = g.document_id WHERE a.document_id = locations.document_id;")

    If restoring database or using a copy of a database creates problems with TIGER or geocode() function ("HINT:  No function matches the given name and argument types. You might need to add explicit type casts."), follow the instructions here and run `ALTER DATABASE landrecords SET search_path=public, tiger;`: http://lists.osgeo.org/pipermail/postgis-users/2011-October/031156.html
    '''
    logger.info('Begin geocode')
    cur.execute("""
        UPDATE locations
        SET (rating, zip_code, longitude, latitude) = (
            COALESCE((g.geo).rating,-1),
            (g.geo).addy.zip,
            ST_X((g.geo).geomout)::numeric(8,5),
            ST_Y((g.geo).geomout)::numeric(8,5)
        )
        FROM (
            SELECT document_id
            FROM locations
            WHERE rating IS NULL
            ORDER BY document_id
        ) As a
        LEFT JOIN (
            SELECT document_id, (geocode(full_address,1)) As geo
            FROM locations
            WHERE locations.rating IS NULL
            ORDER BY document_id
        ) As g ON a.document_id = g.document_id
        WHERE a.document_id = locations.document_id;
        """)
    logger.info('Finished geocoding')
    conn.commit()

def Publish(initial_date = None, until_date = None):
    print "Determining whether to publish records..."
    logger.info('Publish')
    '''
    Checks geocoded ratings, dates, etc. to decide whether to publish or not 
    '''

    session.query(
            Location.rating, Location.location_publish
        ).filter(
            Location.rating <= 3
        ).update({"location_publish": "1"})
    session.flush()

    session.query(
            Location.rating, Location.location_publish
        ).filter(
            Location.rating > 3
        ).update({"location_publish": "0"})
    session.flush()

    session.query(Location.longitude, Location.location_publish).filter(Location.longitude < -90.140388).update({"location_publish": "0"}) # Long less than -90.140388 is west of New Orleans
    session.flush()

    # Long greater than -89 is east of New Orleans, which is practically MS anyway
    session.query(Location.latitude, Location.location_publish).filter(Location.latitude < 29.864543).update({"location_publish": "0"}) # Lat less than 29.864543 is south of New Orleans
    session.flush()

    session.query(Location.latitude, Location.location_publish).filter(Location.latitude > 30.181719).update({"location_publish": "0"}) # Lat less than 29.864543 is north of New Orleans
    session.flush()

    '''
    Decide whether to publish or not based on Detail information, such as dates
    '''

    # Assume publishable, then check for reasons not to publish.
    session.query(Detail.detail_publish).update({"detail_publish": "1"})
    session.flush()

    session.query(
            Detail.document_date, Detail.document_recorded, Detail.detail_publish
        ).filter(
            (Detail.document_date == None) | 
            (Detail.document_recorded == None)
        ).update(
            {"detail_publish": "0"}
        )
    session.flush()

    # Convert date strings to datetime format
    new_initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
    new_until_date = datetime.strptime(until_date, '%Y-%m-%d')
    current_date = new_initial_date

    # Evaluate "30 days ago" based on that particular day
    while current_date != new_until_date:
        # Update date range
        old_date = current_date - timedelta(days = 180)
        previous_date = current_date - timedelta(days = 1)

        # Copy datetime objects to date strings
        old_date_string = old_date.strftime('%Y-%m-%d')
        previous_date_string = previous_date.strftime('%Y-%m-%d')
        current_date_string = current_date.strftime('%Y-%m-%d')

        with session.begin_nested():
            # For sales recorded on a given day, check if the document date is unbelievable (too old or in the future)

            session.query(
                    Detail.document_recorded, Detail.document_date, Detail.detail_publish
                ).filter(
                    Detail.document_recorded == '%s' % current_date_string
                ).filter(
                    Detail.document_date < '%s' % old_date_string
                ).update({"detail_publish": "0"})
            session.flush()

            session.query(Detail.document_recorded, Detail.document_date, Detail.detail_publish).filter(Detail.document_recorded == '%s' % current_date_string).filter(Detail.document_date > '%s' % previous_date_string).update({"detail_publish": "0"})
            session.flush()

        current_date = current_date + timedelta(days = 1)

    session.query(Detail.amount, Detail.detail_publish).filter(Detail.amount <= 0).update({"detail_publish": "0"}) # Not sure about these, so check them all for now to be safe
    session.flush()

    session.query(Detail.amount, Detail.detail_publish).filter(Detail.amount >= 20000000).update({"detail_publish": "0"}) # Anything over $20,000,000 wouldn't be impossible, but is a rare occurrence

    session.commit()

def Clean(initial_date = None, until_date = None):
    print "Adding to cleaned table..."
    logger.info('Clean')

    email_file = "logs/email-%s.txt" % datetime.now().strftime('%Y-%m-%d')
    open(email_file, 'w').close()# Blank slate
    f = open(email_file, 'a')

    '''
    All sales (just yesterday or every day, depending)
    '''

    sql_with_neighborhood = """
        WITH vendee AS (
          SELECT document_id, string_agg(vendee_firstname::text || ' ' || vendee_lastname::text, ', ') AS buyers
          FROM vendees
          GROUP BY document_id
        ), vendor AS (
          SELECT document_id, string_agg(vendor_firstname::text || ' ' || vendor_lastname::text, ', ') AS sellers
          FROM vendors
          GROUP BY document_id
        ), location AS (
          SELECT document_id, min(location_publish) AS location_publish, string_agg(street_number::text || ' ' || address::text, '; ') AS address, string_agg('Unit: ' || unit::text || ', Condo: ' || condo::text || ', Weeks: ' || weeks::text || ', Subdivision: ' || subdivision::text || ', District: ' || district::text || ', Square: ' || square::text || ', Lot: ' || lot::text, '; ') AS location_info, mode(zip_code) AS zip_code, mode(latitude) AS latitude, mode(longitude) AS longitude
          FROM locations
          GROUP BY document_id
        ), hood AS (
          SELECT document_id, longitude, latitude
          FROM locations
        ), neighborhood AS (
          SELECT document_id, mode(gnocdc_lab) AS neighborhood
          FROM neighborhoods, hood
          WHERE ST_Contains(neighborhoods.geom, ST_SetSRID(ST_Point(hood.longitude::float, hood.latitude::float),4326))
          GROUP BY document_id
        )
        SELECT details.amount, details.document_date, details.document_recorded, location.address, location.location_info, vendor.sellers, vendee.buyers, details.instrument_no, location.latitude, location.longitude, location.zip_code, details.detail_publish, details.permanent_flag, location.location_publish, neighborhood.neighborhood
        FROM details
        JOIN location ON details.document_id = location.document_id
        JOIN vendor ON details.document_id = vendor.document_id
        JOIN vendee ON details.document_id = vendee.document_id
        JOIN neighborhood ON details.document_id = neighborhood.document_id
        WHERE document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)
    
    result = engine.execute(sql_with_neighborhood)

    # rows is used again at end of function
    rows = []
    for row in result:
        row = dict(row)
        rows.append(row)
        
    rows = Cleanup.CleanNew(rows) # Clean up things like capitalizations, abbreviations, AP style quirks, etc.

    for row in rows:
        logger.info('Inserting', row)
        try:
            with session.begin_nested():
                i = insert(Cleaned)
                i = i.values(row)
                session.execute(i)
                session.flush()
        except:
            # e = sys.exc_info()[1]
            #print 'Error!'
            logger.info('ERROR! Probably an integrity error (a sale with this instrument number has already been entered into the cleaned table.');

    session.commit()

    '''
    No neighborhood found.
    '''

    sql_without_neighborhood = """
        WITH vendee AS (
          SELECT document_id, string_agg(vendee_firstname::text || ' ' || vendee_lastname::text, ', ') AS buyers
          FROM vendees
          GROUP BY document_id
        ), vendor AS (
          SELECT document_id, string_agg(vendor_firstname::text || ' ' || vendor_lastname::text, ', ') AS sellers
          FROM vendors
          GROUP BY document_id
        ), location AS (
          SELECT document_id, min(location_publish) AS location_publish, string_agg(street_number::text || ' ' || address::text, '; ') AS address, string_agg('Unit: ' || unit::text || ', Condo: ' || condo::text || ', Weeks: ' || weeks::text || ', Subdivision: ' || subdivision::text || ', District: ' || district::text || ', Square: ' || square::text || ', Lot: ' || lot::text, '; ') AS location_info, mode(zip_code) AS zip_code, mode(latitude) AS latitude, mode(longitude) AS longitude
          FROM locations
          GROUP BY document_id
        ), hood AS (
          SELECT document_id, longitude, latitude
          FROM locations
        ), neighborhood AS (
          SELECT document_id
          FROM hood, (SELECT ST_Union(geom) as geom from neighborhoods) as nbhd
          WHERE NOT ST_Contains(nbhd.geom, ST_SetSRID(ST_Point(hood.longitude::float, hood.latitude::float),4326))
          GROUP BY document_id
        )
        SELECT details.amount, details.document_date, details.document_recorded, location.address, location.location_info, vendor.sellers, vendee.buyers, details.instrument_no, location.latitude, location.longitude, location.zip_code, details.detail_publish, details.permanent_flag, location.location_publish
        FROM details
        JOIN location ON details.document_id = location.document_id
        JOIN vendor ON details.document_id = vendor.document_id
        JOIN vendee ON details.document_id = vendee.document_id
        JOIN neighborhood ON details.document_id = neighborhood.document_id
        WHERE document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    
    no_neighborhood_result = engine.execute(sql_without_neighborhood)

    no_neighborhood_rows = []
    for row in no_neighborhood_result:
        row = dict(row)
        row['neighborhood'] = "None"
        no_neighborhood_rows.append(row)

    #pp.pprint(no_neighborhood_rows)
        
    no_neighborhood_rows = Cleanup.CleanNew(no_neighborhood_rows) # Clean up things like capitalizations, abbreviations, AP style quirks, etc.

    for row in no_neighborhood_rows:
        logger.info('Inserting', row)
        try:
            with session.begin_nested():
                i = insert(Cleaned)
                i = i.values(row)
                session.execute(i)
                session.flush()
        except:
            # e = sys.exc_info()[1]
            #print 'Error!'
            logger.info('ERROR! Probably an integrity error (a sale with this instrument number has already been entered into the cleaned table.');

    session.commit()
    


    '''
    Cleaned table has new records now. Can use straightforward SQL queries on Cleaned.
    '''

    f.write('<p>http://vault.thelensnola.org/realestate/search?d1={0}&d2={0}</p>\n\n'.format((datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')))

    '''
    Number of new records
    '''

    count_sql = """
        SELECT COUNT(*)
        FROM cleaned
        WHERE document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    count_result = engine.execute(count_sql)
    count = 1 # placeholder
    for r in count_result:
        count = r.count
    
    f.write('<p>%s sales recorded on %s.</p>\n\n' % (format(count, ','), (datetime.now() - timedelta(days=1)).strftime('%A, %b. %-d, %Y')))

    '''
    detail_publish = 0
    '''

    detail_no_pub_sql = """
        SELECT COUNT(*)
        FROM cleaned
        WHERE detail_publish = '0' AND document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    count_result = engine.execute(detail_no_pub_sql)
    count = 1
    for r in count_result:
        count = r.count
    
    f.write('<p>%s records not published because of questionable data.</p>\n\n' % (format(count, ',')))

    '''
    location_publish = 0
    '''

    location_no_pub_sql = """
        SELECT COUNT(*)
        FROM cleaned
        WHERE location_publish = '0' AND document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    count_result = engine.execute(location_no_pub_sql)
    count = 1
    for r in count_result:
        count = r.count
    
    f.write('<p>%s records not published because location could not be found.</p>\n\n' % (format(count, ',')))

    f.write('<p>http://vault.thelensnola.org/realestate/dashboard</p>\n\n')

    '''
    Highest amount
    '''

    high_amount_sql = """
        SELECT amount
        FROM cleaned
        WHERE document_recorded >= '%s' AND document_recorded <= '%s' ORDER BY amount DESC LIMIT 1;
    """ % (initial_date, until_date)

    high_result = engine.execute(high_amount_sql)

    for u in high_result:
        high_count = u.amount
        f.write('<p>High: %s</p>\n\n' % ('$' + format(high_count, ',')))

    '''
    Lowest amount
    '''

    low_amount_sql = """
        SELECT amount
        FROM cleaned
        WHERE document_recorded >= '%s' AND document_recorded <= '%s'
        ORDER BY amount ASC
        LIMIT 1;
    """ % (initial_date, until_date)

    low_result = engine.execute(low_amount_sql)

    for u in low_result:
        low_count = u.amount
        f.write('<p>Low: %s</p>\n\n' % ('$' + format(low_count, ',')))

    '''
    Writing all new records here because want it at end of email message.
    'rows' is from Cleaned commit output
    '''

    message = ''
    for row in rows:
        if row['document_date'] == None:
            message += '<p><strong>Sale date</strong><br>None<br>\n'
        else:
            message += '<p><strong>Sale date</strong><br>' + row['document_date'].strftime('%A, %b. %-d, %Y') + '<br>\n'
        message += '<strong>Amount</strong><br>$' + format(row['amount'], ',') + '<br>\n'
        message += '<strong>Buyers</strong><br>' + row['buyers'] + '<br>\n'
        message += '<strong>Sellers</strong><br>' + row['sellers'] + '<br>\n'
        message += '<strong>Address</strong><br>' + row['address'] + '<br>\n'
        message += '<strong>Location info</strong><br>' + row['location_info'] + '<br>\n'
        message += '<strong>Zip</strong><br>' + row['zip_code'] + '<br>\n'
        message += '<strong>Neighborhood</strong><br>' + row['neighborhood'] + '</p>\n'
        #message = message + row['document_date'] + '\n'
        f.write(message.encode('utf8'))
        f.write('\n')
        message = ''

    f.close()

def copyDashboardToCleaned():
    '''
    Correct Cleaned entries based on overrides made in dashboard.
    Only for building database from scratch: Normal flow is add yesterday to Cleaned and publish accordingly. Dashboard interaction then comes after and directly updates Cleaned while simultaneously adding to/updating same entry in Dashboard table.
    '''

    print "Restoring dashboard table..."
    logger.info('Dashboard')

    try:
        local("pg_restore --data-only -d landrecords -t dashboard " + backup_directory + "/dashboard_table_$(date +%Y-%m-%d).sql")
    except:
        logger.info('Could not restore dashboard table')
        print 'could not restore dashboard table'

    # Correct dashboard table's id field
    fix_id_sql = "SELECT setval('dashboard_id_seq', MAX(id)) FROM dashboard;"
    engine.execute(fix_id_sql)

    q = session.query(
            Dashboard
        ).order_by(
            Dashboard.id.asc()#update Cleaned in order Dashboard changes were made
        ).all()

    rows = []
    for row in q:
        row_dict = {};
        row_dict['instrument_no'] = row.instrument_no
        row_dict['detail_publish'] = row.detail_publish
        row_dict['location_publish'] = row.location_publish
        row_dict['document_date'] = row.document_date
        row_dict['amount'] = row.amount
        row_dict['address'] = row.address
        row_dict['location_info'] = row.location_info
        row_dict['sellers'] = row.sellers
        row_dict['buyers'] = row.buyers
        row_dict['document_recorded'] = row.document_recorded
        row_dict['latitude'] = row.latitude
        row_dict['longitude'] = row.longitude
        row_dict['zip_code'] = row.zip_code
        row_dict['neighborhood'] = row.neighborhood

        rows.append(row_dict)

    for row in rows:
        print 'row:'
        print row['instrument_no']

        print 'Updating Cleaned sale based on Dashboard entry'
        #This sale has already been entered into dashboard table            
        u = update(Cleaned)
        u = u.values(row)
        u = u.where(Cleaned.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        session.commit()

        print 'Changing Dashboard entry fixed field to true'
        #This sale has already been entered into dashboard table            
        u = update(Dashboard)
        u = u.values({"fixed": True})
        u = u.where(Dashboard.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        session.commit()

def Build(initial_date = None, until_date = None):
    print "Building tables..."
    logger.info('buildFromScratch')

    print "details"
    logger.info('details')
    for folder in sorted(glob.glob('../data/*')): # For all folders (days)

        current_date = folder.split('/')[-1]

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except:
            continue

        print folder
        logger.info(folder)
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))): # For all records (within each day)
            # Regex to get Document ID (not Instrument #, but the Document ID only visible in URLs and HTML on the site)
            # This is crucial to identifying records from the same document in other functions, such as combining rows for multiple names on a sale document
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            logger.info(form)
            document_details(form,form_id)
        # If reached final date, then end.
        if current_date == until_date:
            break
    session.commit()

    print "vendors"
    logger.info('vendors')
    for folder in sorted(glob.glob('../data/*')): # For all folders (days)
        
        current_date = folder.split('/')[-1]

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except:
            continue

        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            logger.info(form)
            vendors(form,form_id)
        if current_date == until_date:
            break
    session.commit()

    print 'vendees'
    logger.info('vendees')
    for folder in sorted(glob.glob('../data/*')): # For all folders (days)
        
        current_date = folder.split('/')[-1]

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except:
            continue

        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            logger.info(form)
            vendees(form,form_id)
        if current_date == until_date:
            break
    session.commit()

    print 'locations'
    logger.info('locations')
    for folder in sorted(glob.glob('../data/*')): # For all folders (days)
        
        current_date = folder.split('/')[-1]

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except:
            continue

        print folder
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            logger.info(form)
            locations(form,form_id)
        if current_date == until_date:
            break
    session.commit()

def sendEmail(initial_date = yesterday_date, until_date = yesterday_date):
    # Send me an email of new rows
    print "Sending email summary..."
    logger.info('gmail function:')
    gmail.main(initial_date = initial_date, until_date = until_date)

def updateCleanedGeom():
    local('psql landrecords -c "UPDATE cleaned SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"')

def getErrorPageHtml(url):
    error_req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'})
    error_con = urllib2.urlopen(error_req)
    error_html = error_con.read()
    error_con.close()

    return error_html

def testUrl(url, error_html):
    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'})
    con = urllib2.urlopen(req)
    html = con.read()
    con.close()

    if html == error_html:
        return url
    else:
        return None

def checkAssessorLinks(initial_date = None, until_date = None):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.document_recorded >= '%s' % (initial_date)
        ).filter(
            Cleaned.document_recorded <= '%s' % (until_date)
        ).filter(
            Cleaned.assessor_publish == '0'
        ).all()
    
    error_html = getErrorPageHtml("http://qpublic9.qpublic.net/la_orleans_display.php?KEY=7724-BURTHESTt")

    num_records = len(q)
    print '%d records to check.' % num_records

    for u in q:
        print '%d records left.' % num_records
        num_records = num_records - 1
        address = u.address
        location_info = u.location_info
        instrument_no = u.instrument_no
        url_param = check_assessor_urls.formAssessorURL(address, location_info)


        if url_param == None:
            '''
            session.query(Cleaned.instrument_no, Cleaned.assessor_publish).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })
            session.commit()
            '''
            continue
        
        assessor_url = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s" % (url_param)

        response = testUrl(assessor_url, error_html)

        if response == None:#No error page
            session.query(Cleaned.instrument_no, Cleaned.assessor_publish).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "1"
            })
            session.commit()
        '''
        else:#Error page
            session.query(Cleaned.instrument_no, Cleaned.assessor_publish).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })
            session.commit()
        '''

        time.sleep(random.randint(1,2) + random.uniform(1.0, 2.0))

def checkPermanentStatusOfNewSales():
    '''
    Examine first-time sales and assign True or False for permanent_flag.
    '''

    # Find the date range of sales to look at. This is only to reduce the number of iterations needed by the for-loop below.

    earliest_none_date = ''
    latest_none_date = ''

    q = session.query(
            func.min(Detail.document_recorded).label('early_date')
        ).filter(
            Detail.permanent_flag == None
        )

    for u in q:
        earliest_none_date = u.early_date

    print 'earliest_none_date:', earliest_none_date

    q = session.query(
            func.max(Detail.document_recorded).label('late_date')
        ).filter(
            Detail.permanent_flag == None
        )

    for u in q:
        latest_none_date = u.late_date

    print 'latest_none_date:', latest_none_date

    for folder in sorted(glob.glob('../data/*')): # For all folders (dates)
        current_iteration_date = folder.split('/')[-1]

        try:
            current_iteration_datetime = datetime.strptime(current_iteration_date, '%Y-%m-%d')
        except:
            continue

        try:
            earliest_none_datetime = datetime.combine(earliest_none_date, datetime.min.time())
        except:
            continue

        if current_iteration_datetime < earliest_none_datetime:
            continue

        # For this date that is currently considered temporary (whether by default or because it was previously confirmed to be temporary), check on the permanent date range at the time of the scrape.
        for pathname in sorted(glob.glob('%s/permanent-date-range-when-scraped_*.html' % (folder))): # For all records (within each day)
            #print 'pathname:', pathname

            permanent_range_first_date_when_scraped = re.match(r"../data/" + current_iteration_date + r"/permanent-date-range-when-scraped_(\d+)-(\d+).html", pathname).group(1)
            print 'permanent_range_first_date_when_scraped:', permanent_range_first_date_when_scraped
            permanent_range_first_date_when_scraped = datetime.strptime(permanent_range_first_date_when_scraped, '%m%d%Y')#).strftime('%Y-%m-%d')

            permanent_range_last_date_when_scraped = re.match(r"../data/" + current_iteration_date + r"/permanent-date-range-when-scraped_(\d+)-(\d+).html", pathname).group(2)
            print 'permanent_range_last_date_when_scraped:', permanent_range_last_date_when_scraped
            permanent_range_last_date_when_scraped = datetime.strptime(permanent_range_last_date_when_scraped, '%m%d%Y')#).strftime('%Y-%m-%d')

            if (permanent_range_first_date_when_scraped <= current_iteration_datetime and current_iteration_datetime <= permanent_range_last_date_when_scraped):
                session.query(Detail).filter(Detail.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": True})
                session.query(Cleaned).filter(Cleaned.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": True})
                session.commit()
            else:
                session.query(Detail).filter(Detail.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": False})
                session.query(Cleaned).filter(Cleaned.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": False})
                session.commit()
        print '\n'

        # If reached final date, then end.
        if current_iteration_date == latest_none_date:
            break

def checkPermanentStatusOfTempSales():
    '''
    Compare most recently downloaded permanent date range against sales that were previously determined to have permanent_flag = False to see if any sales should be re-scraped.
    '''

    # Find the date range of temporary sales to look at. This is only to reduce the number of iterations needed by the for-loop below.

    earliest_temp_date = ''
    latest_temp_date = ''

    q = session.query(
            func.min(Detail.document_recorded).label('early_date')
        ).filter(
            Detail.permanent_flag == False
        )
    for u in q:
        print u
        earliest_temp_date = u.early_date
    print 'earliest_temp_date:', earliest_temp_date


    q = session.query(
            func.max(Detail.document_recorded).label('late_date')
        ).filter(
            Detail.permanent_flag == False
        )
    for u in q:
        print u
        earliest_temp_date = u.late_date
    print 'latest_temp_date:', latest_temp_date

    dates_to_redo = []

    permanent_range_first_date = ''
    permanent_range_last_date = ''

    # Find most recently updated permanent date range.
    for pathname in glob.glob('../data/most-recent-permanent-date-range_*.html'):
        print 'pathname:', pathname

        permanent_range_first_date = re.match(r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html", pathname).group(1)
        permanent_range_first_date = datetime.strptime(permanent_range_first_date, '%m%d%Y')#).strftime('%Y-%m-%d')

        permanent_range_last_date = re.match(r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html", pathname).group(2)
        permanent_range_last_date = datetime.strptime(permanent_range_last_date, '%m%d%Y')#).strftime('%Y-%m-%d')

    for folder in sorted(glob.glob('../data/*')): # For all folders (dates)
        current_iteration_date = folder.split('/')[-1]
        #print 'current_iteration_date:', current_iteration_date

        try:
            current_iteration_datetime = datetime.strptime(current_iteration_date, '%Y-%m-%d')
        except:
            continue

        try:
            earliest_temp_datetime = datetime.combine(earliest_temp_date, datetime.min.time())
        except:
            continue

        if current_iteration_datetime < earliest_temp_datetime:
            continue

        if (permanent_range_first_date <= current_iteration_datetime and current_iteration_datetime <= permanent_range_last_date):
            dates_to_redo.append(current_iteration_datetime)
        
        #else:
            #Do nothing. Keep records and don't change permanent_flag

        # If reached final date, then end.
        if current_iteration_date == latest_temp_date:
            break

    try:
        early_date = min(dates_to_redo)
        late_date = max(dates_to_redo)
    except:
        #Nothing left to do because no records are "temporary"
        return

    #Delete existing records for this date
    location_sql = """
        DELETE FROM locations USING details
        WHERE details.document_id = locations.document_id
        AND details.document_recorded >= '%s'
        AND details.document_recorded <= '%s'
    """ % (early_date, late_date)
    engine.execute(location_sql)

    vendor_sql = """
        DELETE FROM vendors USING details
        WHERE details.document_id = vendors.document_id
        AND details.document_recorded >= '%s'
        AND details.document_recorded <= '%s'
    """ % (early_date, late_date)
    engine.execute(vendor_sql)

    vendee_sql = """
        DELETE FROM vendees USING details
        WHERE details.document_id = vendees.document_id
        AND details.document_recorded >= '%s'
        AND details.document_recorded <= '%s'
    """ % (early_date, late_date)
    engine.execute(vendee_sql)

    detail_sql = """
        DELETE FROM details
        WHERE document_recorded >= '%s'
        AND document_recorded <= '%s'
    """ % (early_date, late_date)
    engine.execute(detail_sql)

    cleaned_sql = """
        DELETE FROM cleaned
        WHERE document_recorded >= '%s'
        AND document_recorded <= '%s'
    """ % (early_date, late_date)
    engine.execute(cleaned_sql)

    # Scrape those days over again
    selen.main(from_date = earliest_date_need_to_rescrape_datetime, until_date = latest_date_need_to_rescrape_datetime)

    # Build those newly scraped records. This will set perm_flag = True in checkPermanentStatusOfNewSales().
    doItAll(earliest_date_need_to_rescrape, latest_date_need_to_rescrape)


def doItAll(initial_date = '2014-02-18', until_date = yesterday_date):
    Build(initial_date = initial_date, until_date = until_date)
    Geocode() #CAUTION! Geocoding entire archive takes ~45 minutes.
    Publish(initial_date = initial_date, until_date = until_date)
    Clean(initial_date = initial_date, until_date = until_date)  
    if initial_date != until_date: # Assumes any range of dates also wants this function.
        copyDashboardToCleaned()
    updateCleanedGeom()

    checkPermanentStatusOfNewSales()
    checkPermanentStatusOfTempSales()

    sendEmail(initial_date = initial_date, until_date = until_date)
    #checkAssessorLinks(initial_date = initial_date, until_date = until_date)

if __name__ == '__main__':
    try:
        doItAll(initial_date = yesterday_date, until_date = yesterday_date)
        #doItAll()#Default is to build entire archive
    except:
        pythonEmail.main(email_subject = "Error running Land Record's initialize.py script", email_body = 'Sorry.')

    session.close()
    cur.close()
    conn.close()
    logging.shutdown()
    print "Done!"
