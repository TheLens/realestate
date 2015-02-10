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
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert, func, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import gmail, check_assessor_urls
from databasemaker import Detail, Location, Vendor, Vendee, Cleaned, Neighborhood, Square, Dashboard
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
            FROM locations As ag
            WHERE ag.rating IS NULL
            ORDER BY document_id
        ) As g ON a.document_id = g.document_id
        WHERE a.document_id = locations.document_id;
        """)
    logger.info('Finished geocoding')
    conn.commit()

def Publish(initial_date = None, until_date = None):
    logger.info('Publish')
    '''
    Checks geocoded ratings, dates, etc. to decide whether to publish or not 
    '''

    session.query(Location).filter(Location.rating <= 3).update({"location_publish": "1"})
    session.flush()

    session.query(Location).filter(Location.rating > 3).update({"location_publish": "0"})
    session.flush()

    session.query(Location).filter(Location.longitude < -90.140388).update({"location_publish": "0"}) # Long less than -90.140388 is west of New Orleans
    session.flush()

    # Long greater than -89 is east of New Orleans, which is practically MS anyway
    session.query(Location).filter(Location.latitude < 29.864543).update({"location_publish": "0"}) # Lat less than 29.864543 is south of New Orleans
    session.flush()

    session.query(Location).filter(Location.latitude > 30.181719).update({"location_publish": "0"}) # Lat less than 29.864543 is north of New Orleans
    session.flush()

    '''
    Decide whether to publish or not based on Detail information, such as dates
    '''

    # Assume publishable, then check for reasons not to publish.
    session.query(Detail).update({"detail_publish": "1"})
    session.flush()

    session.query(
            Detail
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
        old_date = current_date - timedelta(days = 30)
        previous_date = current_date - timedelta(days = 1)

        # Copy datetime objects to date strings
        old_date_string = old_date.strftime('%Y-%m-%d')
        previous_date_string = previous_date.strftime('%Y-%m-%d')
        current_date_string = current_date.strftime('%Y-%m-%d')

        with session.begin_nested():
            # For sales recorded on a given day, check if the document date is unbelievable (too old or in the future)

            session.query(Detail).filter(Detail.document_recorded == '%s' % current_date_string).filter(Detail.document_date < '%s' % old_date_string).update({"detail_publish": "0"})
            session.flush()

            session.query(Detail).filter(Detail.document_recorded == '%s' % current_date_string).filter(Detail.document_date > '%s' % previous_date_string).update({"detail_publish": "0"})
            session.flush()

        current_date = current_date + timedelta(days = 1)

    session.query(Detail).filter(Detail.amount <= 0).update({"detail_publish": "0"}) # Not sure about these, so check them all for now to be safe
    session.flush()

    session.query(Detail).filter(Detail.amount >= 20000000).update({"detail_publish": "0"}) # Anything over $20,000,000 wouldn't be impossible, but is certainly a rare occurrence
    session.commit()

def Clean(initial_date = None, until_date = None):
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
          SELECT document_id, min(location_publish) AS location_publish, string_agg(street_number::text || ' ' || address::text || ', Unit: ' || unit::text || ', Condo: ' || condo::text || ', Weeks: ' || weeks::text || ', Subdivision: ' || subdivision::text || ', District: ' || district::text || ', Square: ' || square::text || ', Lot: ' || lot::text, '; ') AS location, mode(zip_code) AS zip_code, mode(latitude) AS latitude, mode(longitude) AS longitude
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
        SELECT details.amount, details.document_date, details.document_recorded, location.location, vendor.sellers, vendee.buyers, details.instrument_no, location.latitude, location.longitude, location.zip_code, details.detail_publish, location.location_publish, neighborhood.neighborhood
        FROM details
        JOIN location ON details.document_id = location.document_id
        JOIN vendor ON details.document_id = vendor.document_id
        JOIN vendee ON details.document_id = vendee.document_id
        JOIN neighborhood ON details.document_id = neighborhood.document_id
        WHERE document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    
    result = engine.execute(sql_with_neighborhood)

    rows = []
    for row in result:
        row = dict(row)
        rows.append(row)

    rows = Cleanup.CleanNew(rows) # Clean up things like capitalizations, abbreviations, AP style quirks, etc.

    #pp.pprint(rows)

    for row in rows:
        logger.info('Inserting', row)
        #print row, '\n'
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

    # f.write('=============\n')
    # f.write('NEW RECORDS\n')
    # f.write('=============\n\n')

    #f.write('View:\n')
    f.write('<p>http://vault.thelensnola.org/realestate/search?d1={0}&d2={0}</p>\n\n'.format(datetime.now().strftime('%m/%d/%Y')))

    '''
    STATS
    '''

    # f.write('======\n')
    # f.write('STATS\n')
    # f.write('======\n\n')

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

    #f.write('Dashboard:\n')
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

    high_count = 1 # placeholder

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

    low_count = 1 # placeholder
    for u in low_result:
        low_count = u.amount
    
    f.write('<p>Low: %s</p>\n\n' % ('$' + format(low_count, ',')))

    '''
    Writing all new records here because want it at end of email message.
    'rows' is from Cleaned commit output
    '''

    # f.write('============\n')
    # f.write('ALL RECORDS\n')
    # f.write('============\n\n')

    message = ''
    #pp.pprint(rows)
    for row in rows:
        #print row
        # for (key, val) in row.iteritems():
        #u'\u2022'
        #     message = message + "%s: %s" % (key, val) + '\n'
        if row['document_date'] == None:
            message = message + '<p>Sale date: None<br>\n'
        else:
            message = message + '<p>Sale date: ' + row['document_date'].strftime('%A, %b. %-d, %Y') + '<br>\n'
        message = message + 'Amount: $' + format(row['amount'], ',') + '<br>\n'
        message = message + 'Buyers: ' + row['buyers'] + '<br>\n'
        message = message + 'Sellers: ' + row['sellers'] + '<br>\n'
        message = message + 'Location: ' + row['location'] + '<br>\n'
        message = message + 'Zip: ' + row['zip_code'] + '<br>\n'
        message = message + 'Neighborhood: ' + row['neighborhood'] + '</p>\n'
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
        row_dict['location'] = row.location
        row_dict['sellers'] = row.sellers
        row_dict['buyers'] = row.buyers
        row_dict['document_recorded'] = row.document_recorded
        row_dict['latitude'] = row.latitude
        row_dict['longitude'] = row.longitude
        row_dict['zip_code'] = row.zip_code
        row_dict['neighborhood'] = row.neighborhood

        rows.append(row_dict)

    # print 'rows:'
    # pp.pprint(rows)

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

def Squares(initial_date = None, until_date = None):
    '''
    Problems with matching square and district values to shapefile.
    There are integrity issues with the squares file to begin with, so don't use this function until improvements are made.
    '''
    logger.info('Squares')
    q = session.query(Location).filter(Location.rating > 3).all()
    for u in q:
        doc_id = u.document_id
        #print "Document ID:", doc_id

        # original_latitude = u.latitude
        # original_longitude = u.longitude

        untouched_district = u.district
        district = re.sub(r"ST", r"", untouched_district)
        district = re.sub(r"ND", r"", district)
        district = re.sub(r"RD", r"", district)
        district = re.sub(r"TH", r"", district)

        untouched_square = u.square
        square = re.sub(r"-", r"", untouched_square)

        '''
        print "Untouched district:", untouched_district
        print "Untouched square:", untouched_square

        print "District:", district
        print "Square:", square
        '''

        if district == '' or square == '' or square == '-1':
            # print "No information about district and/or square."
            # print "\n"
            continue

        qq = session.query(
                # func.ST_AsText(
                #     func.ST_Centroid(Square.geom)
                # )
                func.ST_X(
                    func.ST_Centroid(Square.geom)
                ).label('ST_X'),
                func.ST_Y(
                    func.ST_Centroid(Square.geom)
                ).label('ST_Y')
            ).filter(
                Square.mun_dst == '%s' % (district)
            ).filter(
                Square.square == Square.square == '%s' % (square)
            ).all()

        #qq should only find one point (a given district's square). todo: make sure.

        for uu in qq:
            #print uu.keys()
            latitude = uu.ST_Y
            longitude = uu.ST_X

        #should only be one set of lat/long..., as noted above

        '''
        print 'Latitude:', latitude
        print "Longitude:", longitude
        '''

        qqq = session.query(
                Detail
            ).filter(
                Detail.document_id == '%s' % doc_id
            ).all()

        #print "This should say 1:", len(qqq)

        for uuu in qqq:
            #print 'Instrument #:', uuu.instrument_no
            in_no = uuu.instrument_no

        # Don't update location_publish to '1' because not sure yet that this is trustworthy. This gives a new lat/long, but is not displayed on the map until confirmation from dashboard.
        session.query(
                Cleaned
            ).filter(
                Cleaned.instrument_no == '%s' % (in_no)
            ).filter(
                Cleaned.document_recorded >= '%s' % (initial_date)
            ).filter(
                Cleaned.document_recorded <= '%s' % (until_date)
            ).update({
                "latitude": "%s" % (latitude),
                "longitude": "%s" % (longitude)
            })
        session.commit()

        '''
        print "Original latitude:", original_latitude
        print "Original longitude:", original_longitude

        print "New latitude:", latitude
        print "New longitude:", longitude
        print "\n"
        '''

def Neighborhoods(initial_date = None, until_date = None):
    '''
    This is incredibly slow. Needs overhaul.

    avoid updates. aim to only use inserts. run postgis queries before inserting row to cleaned in the first place.

    '''
    logger.info('Neighborhoods')

    insert_directly_into_cleaned_sql = """
    WITH vendee AS (
      SELECT document_id, string_agg(vendee_firstname::text || ' ' || vendee_lastname::text, ', ') AS buyers
      FROM vendees
      GROUP BY document_id
    ), vendor AS (
      SELECT document_id, string_agg(vendor_firstname::text || ' ' || vendor_lastname::text, ', ') AS sellers
      FROM vendors
      GROUP BY document_id
    ), location AS (
      SELECT document_id, min(location_publish) AS location_publish, string_agg(street_number::text || ' ' || address::text || ', Unit: ' || unit::text || ', Con
    do: ' || condo::text || ', Weeks: ' || weeks::text || ', Subdivision: ' || subdivision::text || ', District: ' || district::text || ', Square: ' || square::t
    ext || ', Lot: ' || lot::text, '; ') AS location, mode(zip_code) AS zip_code, mode(latitude) AS latitude, mode(longitude) AS longitude
      FROM locations
      GROUP BY document_id
    ), hood AS (
      SELECT document_id, longitude, latitude
      FROM locations
    ), neighborhood AS (
      SELECT document_id, gnocdc_lab AS neighborhood
      FROM neighborhoods, hood
      WHERE ST_Contains(neighborhoods.geom, ST_SetSRID(ST_Point(hood.longitude::float, hood.latitude::float),4326))
    )
    INSERT INTO cleaned (
        amount, document_date, document_recorded, location, sellers, buyers, instrument_no, latitude, longitude, zip_code, detail_publish, location_publish, neighborhood
    )
    (
        SELECT details.amount, details.document_date, details.document_recorded, location.location, vendor.sellers, vendee.buyers, details.instrument_no, location.la
        titude, location.longitude, location.zip_code, details.detail_publish, location.location_publish, neighborhood.neighborhood
        FROM details
        JOIN location ON details.document_id = location.document_id
        JOIN vendor ON details.document_id = vendor.document_id
        JOIN vendee ON details.document_id = vendee.document_id
        JOIN neighborhood ON details.document_id = neighborhood.document_id
        WHERE document_recorded >= '2014-02-18' AND document_recorded <= '2014-09-11'
    );
    """

    if 1 == 0:
        print insert_directly_into_cleaned_sql

    q = session.query(
            Cleaned
        ).filter(
            Cleaned.document_recorded >= '%s' % (initial_date)
        ).filter(
            Cleaned.document_recorded <= '%s' % (until_date)
        ).all()

    for u in q:
        in_no = u.instrument_no
        '''
        print "Instrument #:", in_no
        print "Longitude: ", u.longitude
        print "Latitude:", u.latitude
        '''

        # Find neighborhood containing this sale's lat/lng
        qq = session.query(
                Neighborhood
            ).filter(
                func.ST_Contains(
                    Neighborhood.geom,
                    'SRID=4326;POINT(%s %s)' % (u.longitude, u.latitude)
                )
            ).all()

        # If a neighborhood is found, apply GNOCDC name to neighborhood value
        if qq != []:
            for uu in qq:
                hood = uu.gnocdc_lab
        #print "Neighborhood:", hood

        # Update cleaned table with this new neighborhood value
        session.query(
                Cleaned
            ).filter(
                Cleaned.instrument_no == '%s' % (in_no)
            ).update({
                "neighborhood": "%s" % (hood.title())
            })
        session.commit()

def Build(initial_date = None, until_date = None):

    logger.info('buildFromScratch')

    print "details"
    logger.info('details')
    for folder in sorted(glob.glob('../data/*')): # For all folders (days)

        current_date = folder.split('/')[-1]

        # If this date is before the specified initial_date, then skip.
        if current_date < initial_date:
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
        if current_date < initial_date:
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
        if current_date < initial_date:
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
        if current_date < initial_date:
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

def sendEmail():
    # Send me an email of new rows
    logger.info('gmail function:')
    gmail.main()

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
        ).all()
    
    error_html = getErrorPageHtml("http://qpublic9.qpublic.net/la_orleans_display.php?KEY=7724-BURTHESTt")

    num_records = len(q)
    print '%d records to check.' % num_records

    for i, u in enumerate(q):
        print '%d records left.' % num_records
        num_records = num_records - 1
        location = u.location
        instrument_no = u.instrument_no
        url_param = check_assessor_urls.formAssessorURL(location)

        if url_param == None:
            session.query(Cleaned).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })
            session.commit()
            continue
        
        assessor_url = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s" % (url_param)

        response = testUrl(assessor_url, error_html)

        if response == None:#No error page
            session.query(Cleaned).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "1"
            })
            session.commit()
        else:#Error page
            session.query(Cleaned).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })
            session.commit()

        # if i == 5:
        #     break

        time.sleep(random.randint(3,5) + random.uniform(1.0, 2.0))

def doItAll(initial_date = '2014-02-18', until_date = None):
    print "Building tables..."
    Build(initial_date = initial_date, until_date = until_date)

    print "Geocoding..."
    Geocode() #CAUTION! Geocoding entire archive takes ~45 minutes.

    print "Determining whether to publish records..."
    Publish(initial_date = initial_date, until_date = until_date)

    print "Adding to cleaned table..."
    Clean(initial_date = initial_date, until_date = until_date)

    '''
    print "Identifying square..."
    # Don't run Squares() until data integrity issues are solved.
    #Squares(initial_date = initial_date, until_date = until_date)
    '''

    if initial_date != until_date: # Assumes any range of dates also wants this function.
        print "Restoring dashboard table..."
        copyDashboardToCleaned()

    updateCleanedGeom()

    print "Sending email summary..."
    #sendEmail()#todo: need dates?

    checkAssessorLinks(initial_date = initial_date, until_date = until_date)

if __name__ == '__main__':
    # From scratch:
    doItAll(initial_date = '2014-02-18', until_date = '2014-03-18')#Default is to run through entire archive, from 2014-02-18 through most recent

    # Just yesterday:
    #doItAll(initial_date = yesterday_date, until_date = yesterday_date)

    #Create new .csv file of table
    #cur.execute("COPY cleaned to '/Users/Tom/projects/land-records/temp/table_dump.csv' delimiters',';")
    #cur.execute("\copy cleaned to '/home/tom/projects/land-records/repo/scripts/static/lens-property-sales-%s.csv' csv header" % (yesterday_date))
    # For limited columns: http://stackoverflow.com/questions/2952366/dump-csv-from-sqlalchemy
    #conn.commit()

    session.close()
    cur.close()
    conn.close()
    logging.shutdown()
    print "Done!"
