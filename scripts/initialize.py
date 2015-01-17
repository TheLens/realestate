#!/usr/bin/env python
# coding: utf-8

import glob
import re
import psycopg2
import Cleanup
import gmail
import pprint
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Detail, Location, Vendor, Vendee, Cleaned, Neighborhood, Square
from app_config import server_engine, server_connection

pp = pprint.PrettyPrinter()

Base = declarative_base()
engine = create_engine('%s' % (server_engine))

conn = psycopg2.connect("%s" % (server_connection))
cur = conn.cursor()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today_date = datetime.now
year = (datetime.now() - timedelta(days=1)).strftime('%Y') # "2014"
month = (datetime.now() - timedelta(days=1)).strftime('%m') # "09"
day = (datetime.now() - timedelta(days=1)).strftime('%d') # "09"

# Scrape "Document Detail"
def document_details(form, form_id):
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
    soup = BeautifulSoup(open(form))
    vendorrows = soup.find('table', id="ctl00_cphNoMargin_f_oprTab_tmpl0_DataList11").find_all('tr')
    output = []
    for row in vendorrows:
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
    cur.execute("UPDATE locations SET (rating, longitude, latitude)    = ( COALESCE((g.geo).rating,-1), ST_X((g.geo).geomout)::numeric(8,5), ST_Y((g.geo).geomout)::numeric(8,5)) FROM (SELECT document_id FROM locations WHERE rating IS NULL ORDER BY document_id) As a  LEFT JOIN (SELECT document_id, (geocode(full_address,1)) As geo FROM locations As ag WHERE ag.rating IS NULL ORDER BY document_id) As g ON a.document_id = g.document_id WHERE a.document_id = locations.document_id;")
    '''
    
    cur.execute("UPDATE locations SET (rating, zip_code, longitude, latitude) = ( COALESCE((g.geo).rating,-1), (g.geo).addy.zip, ST_X((g.geo).geomout)::numeric(8,5), ST_Y((g.geo).geomout)::numeric(8,5)) FROM (SELECT document_id FROM locations WHERE rating IS NULL ORDER BY document_id) As a LEFT JOIN (SELECT document_id, (geocode(full_address,1)) As geo  FROM locations As ag WHERE ag.rating IS NULL ORDER BY document_id) As g ON a.document_id = g.document_id WHERE a.document_id = locations.document_id;")
    conn.commit()

def Publish():
    '''
    Checks geocoded ratings, dates, etc. to decide whether to publish or not 
    '''
    old_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d') # Is six months a reasonable window? Some Feb. 2014 records have dates of Nov. 2013, for example, so only a three-month delay period? May need to experiment with this.
    old_date = '2014-01-01'
    session.query(Location).filter(Location.rating <= 3).update({"location_publish": "1"})
    session.commit()

    session.query(Location).filter(Location.rating > 3).update({"location_publish": "0"})
    session.commit()
    session.query(Location).filter(Location.longitude < -90.140388).update({"location_publish": "0"}) # Long less than -90.140388 is west of New Orleans
    session.commit()
    # Long greater than -89 is east of New Orleans, which is practically MS anyway
    session.query(Location).filter(Location.latitude < 29.864543).update({"location_publish": "0"}) # Lat less than 29.864543 is south of New Orleans
    session.commit()
    session.query(Location).filter(Location.latitude > 30.181719).update({"location_publish": "0"}) # Lat less than 29.864543 is north of New Orleans
    session.commit()

    '''
    Decide whether to publish or not based on Detail information, such as dates
    '''
    session.query(Detail).update({"detail_publish": "1"})
    session.commit()
    session.query(Detail).filter(Detail.document_date == None).update({"detail_publish": "0"})
    session.commit()
    session.query(Detail).filter(Detail.document_date <= '%s' % (old_date)).update({"detail_publish": "0"})
    session.commit()
    session.query(Detail).filter(Detail.document_date >= '%s' % (yesterday_date)).update({"detail_publish": "0"}) # If document date is after today's date, there must be an error.
    session.commit()
    session.query(Detail).filter(Detail.amount == 0).update({"detail_publish": "0"}) # Not sure about these, so check them all for now to be safe
    session.commit()
    session.query(Detail).filter(Detail.amount >= 20000000).update({"detail_publish": "0"}) # Anything over $10,000,000 wouldn't be impossible, but is certainly a rare occurrence
    session.commit()

def Clean():
    sql = """ WITH vendee AS (
        SELECT document_id, string_agg(vendee_firstname::text || ' ' || vendee_lastname::text, ', ') AS buyers FROM vendees GROUP BY document_id
    ), vendor AS (
        SELECT document_id, string_agg(vendor_firstname::text || ' ' || vendor_lastname::text, ', ') AS sellers FROM vendors GROUP BY document_id
    ), location AS (
        SELECT document_id, min(location_publish) AS location_publish, string_agg(street_number::text || ' ' || address::text || ', Unit: ' || unit::text || ', Condo: ' || condo::text || ', Weeks: ' || weeks::text || ', Subdivision: ' || subdivision::text || ', District: ' || district::text || ', Square: ' || square::text || ', Lot: ' || lot::text, '; ') AS location, mode(zip_code) AS zip_code, mode(latitude) AS latitude, mode(longitude) AS longitude FROM locations GROUP BY document_id
    )
    SELECT details.amount, details.document_date, details.document_recorded, location.location, vendor.sellers, vendee.buyers, details.instrument_no, location.latitude, location.longitude, location.zip_code, details.detail_publish, location.location_publish FROM details JOIN location ON details.document_id = location.document_id JOIN vendor ON details.document_id = vendor.document_id JOIN vendee ON details.document_id = vendee.document_id;"""
    # WHERE document_recorded = '%s';""" % (yesterday_date)

    #todo: adjust above to clean all records when rebuilding DB

    result = engine.execute(sql)

    rows = []
    for row in result:
        row = dict(row)
        rows.append(row)

    rows = Cleanup.CleanNew(rows) # Clean up things like capitalizations, abbreviations, AP style quirks, etc.

    # Send me an email of new rows
    gmail.main(rows)

    for row in rows:
        i = insert(Cleaned)
        i = i.values(row)
        #session.execute(i)

    session.commit()

def buildFromScratch():
    # To build database from scratch:
    print "details"
    for folder in glob.glob('../data/*'): # For all folders (days)
        print folder
        for form in glob.glob('%s/form-html/*.html' % (folder)): # For all records (within each day)
            # Regex to get Document ID (not Instrument #, but the Document ID only visible in URLs and HTML on the site)
            # This is crucial to identifying records from the same document in other functions, such as combining rows for multiple names on a sale document
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            document_details(form,form_id)
        if folder == '../data/2014-09-11':
            break
    session.commit()

    print "vendors"
    for folder in glob.glob('../data/*'): # For all folders (days)
        for form in glob.glob('%s/form-html/*.html' % (folder)): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            vendors(form,form_id)
        if folder == '../data/2014-09-11':
            break
    session.commit()

    print 'vendees'
    for folder in glob.glob('../data/*'): # For all folders (days)
        for form in glob.glob('%s/form-html/*.html' % (folder)): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            vendees(form,form_id)
        if folder == '../data/2014-09-11':
            break
    session.commit()

    print 'locations'
    for folder in glob.glob('../data/*'): # For all folders (days)
        print folder
        for form in glob.glob('%s/form-html/*.html' % (folder)): # For all records (within each day)
            form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
            form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            form_id = re.search("(?<=/)(.*)\S+", form_id).group()
            print form
            locations(form,form_id)
        if folder == '../data/2014-09-11':
            break
    session.commit()

def buildYesterdayOnly():
    #To enter only the new records from the previous day (downloaded by main.py):
    print "details"
    for form in glob.glob('../data/%s/form-html/*.html' % (yesterday_date)): # For all records (within each day)
	print form
        form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
        print form_id
	form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
        print form_id
	form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        print form_id
	form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        print form_id
        print form
        document_details(form, form_id)
    session.commit()

    print "vendors"
    for form in glob.glob('../data/%s/form-html/*.html' % (yesterday_date)): # For all records (within each day)
        form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
        form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        print form
        print form_id
        vendors(form, form_id)
    session.commit()

    print "vendees"
    for form in glob.glob('../data/%s/form-html/*.html' % (yesterday_date)): # For all records (within each day)        
        form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
        form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        print form
        print form_id
        vendees(form, form_id)
    session.commit()

    print "locations"
    for form in glob.glob('../data/%s/form-html/*.html' % (yesterday_date)): # For all records (within each day)
        form_id = re.search("(?<=/)\S+", form).group() #Leaves string with "OPxxxx.html"
        form_id = re.search("(?<=/)(.*)(?=.html)", form_id).group() # Leaves string with "OPxxxx"
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        form_id = re.search("(?<=/)(.*)\S+", form_id).group()
        print form
        print form_id
        locations(form, form_id)
    session.commit()

def Neighborhoods():
    '''
    It's slow and inelegant, but it works.
    '''
    q = session.query(Cleaned).all()
    for u in q:
        in_no = u.instrument_no
        print in_no
        qq = session.query(Neighborhood).filter(func.ST_Contains(Neighborhood.geom, 'SRID=4326;POINT(%s %s)' % (u.longitude, u.latitude))).all()
        if qq != []:
            for uu in qq:
                hood = uu.gnocdc_lab
        print hood
        session.query(Cleaned).filter(Cleaned.instrument_no == '%s' % (in_no)).update({"neighborhood": "%s" % (hood)})
        session.commit()

    #session.query(Detail).filter(Detail.document_date == None).update({"detail_publish": "0"})
    #session.commit()
    
    #q = session.query(Neighborhood).filter(func.ST_Contains(Neighborhood.geom, 'SRID=4326;POINT(-90.103767 29.970352)')).all()
    #session.query(Detail).filter(Detail.amount == 0).update({"detail_publish": "0"})

def Squares():
    q = session.query(Location).all()
    #q = session.query(Location).filter(Location.rating > 3).all()
    for u in q:
        district = u.district
        district = re.sub(r"ST", r"", district)
        district = re.sub(r"ND", r"", district)
        district = re.sub(r"RD", r"", district)
        district = re.sub(r"TH", r"", district)
        square = u.square
        print district
        print square
        qq = session.query(func.ST_AsText(func.ST_Centroid(Square.geom))).filter(Square.mun_dst == '%s' % (district)).filter(Square.square == '%s' % (square)).all()
        pp.pprint(qq)
        '''
        if qq != []:
            for uu in qq:
                pp.pprint(uu)
        '''

#buildYesterdayOnly()
#buildFromScratch()
print "Geocoding..."
#Geocode() #CAUTION! Geocoding entire archive takes ~45 minutes.
print "Determing whether to publish records..."
#Publish()
print "Adding to cleaned table..."
Clean()
print "Identifying square..."
#Squares()
print "Identifying neighborhoods..."
#Neighborhoods()

#Create new .csv file of table
#cur.execute("COPY cleaned to '/Users/Tom/projects/land-records/temp/table_dump.csv' delimiters',';")
#cur.execute("\copy cleaned to '/home/tom/projects/land-records/repo/scripts/static/lens-property-sales-%s.csv' csv header" % (yesterday_date))
# For limited columns: http://stackoverflow.com/questions/2952366/dump-csv-from-sqlalchemy
#conn.commit()

session.close()
cur.close()
conn.close()
print "Done!"
