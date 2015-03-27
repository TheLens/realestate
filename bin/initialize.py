# -*- coding: utf-8 -*-

import glob
import re
import urllib2
import psycopg2
import pprint
import logging
import logging.handlers
import random
import time
import os

from fabric.api import local
from datetime import datetime, timedelta
from sqlalchemy import create_engine, insert, func, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# import gmail
# import check_assessor_urls
# import pythonEmail
# import scrape

from landrecords import clean, db, parsers, publish, stat_analysis
from landrecords.settings import dev_config

pp = pprint.PrettyPrinter()

Base = declarative_base()
engine = create_engine(dev_config.SERVER_ENGINE)

conn = psycopg2.connect(dev_config.SERVER_CONNECTION)
cur = conn.cursor()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today_date = datetime.now
year = (datetime.now() - timedelta(days=1)).strftime('%Y')  # "2014"
month = (datetime.now() - timedelta(days=1)).strftime('%m')  # "09"
day = (datetime.now() - timedelta(days=1)).strftime('%d')  # "09"

logger = logging.getLogger(__name__)


def initialize_log(name):
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler(
        '%s/logs/%s.log' % (dev_config.PROJECT_DIR, name))
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(funcName)s '
        '- %(levelname)s - %(lineno)d - '
        '%(message)s')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)


def geocode():
    print "Geocoding..."
    '''
    Geocodes existing records and/or new records — any records that have not
    yet been geocoded.
    Geocoder takes strings: 4029 Ulloa St, New Orleans, LA 70119
    I took a shortcut. Instead of finding a way to concatenate the address
    pieces on the fly, I concatenated them all into a new column, then read
    from that column. Sloppy, but it works for now.
    '''
    cur.execute("""UPDATE locations SET full_address = street_number::text
         || ' ' || address::text || ', New Orleans, LA';""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' ST ', ' SAINT ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' FIRST ', ' 1ST ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' SECOND ', ' 2ND ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' THIRD ', ' 3RD ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' FOURTH ', ' 4TH ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' FIFTH ', ' 5TH ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' SIXTH ', ' 6TH ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' SEVENTH ', ' 7TH ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' EIGHTH ', ' 8TH ');""")
    cur.execute("""UPDATE locations SET full_address = replace(full_address,
         ' NINTH ', ' 9TH ');""")

    '''
    An altered version of the following batch geocoding code:
    http://postgis.net/docs/Geocode.html
    It will only geocode entries without ratings (new records), so this is
    good for either batch processing or only processing new records.
    cur.execute("UPDATE locations SET (rating, longitude, latitude) = (
    COALESCE((g.geo).rating,-1), ST_X((g.geo).geomout)::numeric(8,5),
    ST_Y((g.geo).geomout)::numeric(8,5)) FROM (SELECT document_id FROM
    locations WHERE rating IS NULL ORDER BY document_id) As a  LEFT JOIN
    (SELECT document_id, (geocode(full_address,1)) As geo FROM locations
    As ag WHERE ag.rating IS NULL ORDER BY document_id) As g ON a.
    document_id = g.document_id WHERE a.document_id = locations.document_id;")

    If restoring database or using a copy of a database creates problems with
    TIGER or geocode() function ("HINT:  No function matches the given name
    and argument types. You might need to add explicit type casts."),
    follow the instructions here and run `ALTER DATABASE landrecords SET
    search_path=public, tiger;`: http://lists.osgeo.org/pipermail/postgis-
    users/2011-October/031156.html
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
        WHERE a.document_id = locations.document_id;""")
    logger.info('Finished geocoding')
    conn.commit()


def cleanup(initial_date=None, until_date=None):
    print "Adding to cleaned table..."
    logger.info('Clean')

    '''
    All sales (just yesterday or every day, depending)
    '''

    sql_with_neighborhood = """
        WITH vendee AS (
          SELECT document_id, string_agg(vendee_firstname::text || ' ' ||
           vendee_lastname::text, ', ') AS buyers
          FROM vendees
          GROUP BY document_id
        ), vendor AS (
          SELECT document_id, string_agg(vendor_firstname::text || ' ' ||
             vendor_lastname::text, ', ') AS sellers
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
          WHERE ST_Contains(neighborhoods.geom, ST_SetSRID(ST_Point(
            hood.longitude::float, hood.latitude::float),4326))
          GROUP BY document_id
        )
        SELECT details.amount, details.document_date,
        details.document_recorded, location.address, location.location_info,
        vendor.sellers, vendee.buyers, details.instrument_no,
        location.latitude, location.longitude, location.zip_code,
        details.detail_publish, details.permanent_flag,
        location.location_publish, neighborhood.neighborhood
        FROM details
        JOIN location ON details.document_id = location.document_id
        JOIN vendor ON details.document_id = vendor.document_id
        JOIN vendee ON details.document_id = vendee.document_id
        JOIN neighborhood ON details.document_id = neighborhood.document_id
        WHERE document_recorded >= '%s' AND document_recorded <= '%s';
    """ % (initial_date, until_date)

    logger.info('SQL w/ neighborhoods')

    result = engine.execute(sql_with_neighborhood)

    logger.info('Executed SQL w/ neighborhoods')

    # rows is used again at end of function
    rows = []
    for row in result:
        logger.debug(row)
        row = dict(row)
        rows.append(row)

    logger.info('Pre clean')

    # Clean up things like capitalizations, abbreviations, AP style quirks
    rows = clean.CleanNew(rows)

    logger.info('Ran clean')

    for row in rows:
        logger.debug(row)
        try:
            with session.begin_nested():
                i = insert(db.Cleaned)
                i = i.values(row)
                session.execute(i)
                logger.info('post execute')
                session.flush()
                logger.info('post flush')
        except Exception, e:
            # e = sys.exc_info()[1]
            # print 'Error!'
            logger.error(e, exc_info=True)

    session.commit()
    logger.info('post commit')

    '''
    No neighborhood found.
    '''

    sql_without_neighborhood = """
        WITH vendee AS (
          SELECT document_id, string_agg(vendee_firstname::text || ' ' ||
           vendee_lastname::text, ', ') AS buyers
          FROM vendees
          GROUP BY document_id
        ), vendor AS (
          SELECT document_id, string_agg(vendor_firstname::text || ' ' ||
           vendor_lastname::text, ', ') AS sellers
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
          WHERE NOT ST_Contains(nbhd.geom,
            ST_SetSRID(ST_Point(hood.longitude::float, hood.latitude::float),
                4326))
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

    logger.info('SQL w/ out neighborhoods')

    no_neighborhood_result = engine.execute(sql_without_neighborhood)

    logger.info('Executed SQL w/ out neighborhoods')

    no_neighborhood_rows = []
    for row in no_neighborhood_result:
        logger.debug(row)
        row = dict(row)
        row['neighborhood'] = "None"
        no_neighborhood_rows.append(row)

    # Clean up things like capitalizations, abbreviations, AP style quirks
    no_neighborhood_rows = clean.CleanNew(no_neighborhood_rows)

    for row in no_neighborhood_rows:
        logger.debug(row)
        try:
            with session.begin_nested():
                i = insert(Cleaned)
                i = i.values(row)
                session.execute(i)
                logger.info('post execute')
                session.flush()
                logger.info('post flush')
        except Exception, e:
            # e = sys.exc_info()[1]
            logger.error(e, exc_info=True)

    session.commit()
    logger.info('post commit')


def generate_email(initial_date=None, until_date=None):
    stat = stat_analysis.StatAnalysis('cleaned', initial_date, until_date)

    # todo: handle if either or both dates not specified?
    email_string = (
        '<p>http://vault.thelensnola.org/realestate/search?d1={0}&d2={1}' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{2} sales recorded on {3} to {4}.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{5} records not published because of questionable data.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{6} records not published because location could not be found.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>http://vault.thelensnola.org/realestate/dashboard' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>High: ${7}</p>' +
        '\n' +
        '\n' +
        '<p>Low: ${8}</p>' +
        '\n' +
        '\n'
    ).format(
        initial_date.strftime('%m/%d/%Y'),
        until_date.strftime('%m/%d/%Y'),
        format(stat.count(), ','),
        initial_date.strftime('%A, %b. %-d, %Y'),
        until_date.strftime('%A, %b. %-d, %Y'),
        format(stat.detail_not_published(), ','),
        format(stat.location_not_published(), ','),
        format(stat.highest_amount(), ','),
        format(stat.lowest_amount(), ',')
    )

    rows = stat.all_records()

    message = ''
    for row in rows:
        if row['document_date'] is None:
            message += '<p><strong>Sale date</strong><br>None<br>\n'
        else:
            message += (
                '<p><strong>Sale date</strong><br>' +
                row['document_date'].strftime('%A, %b. %-d, %Y') +
                '<br>\n')
        message += (
            '<strong>Amount</strong><br>${0}<br>\n' +
            '<strong>Buyers</strong><br>{1}<br>\n' +
            '<strong>Sellers</strong><br>{2}<br>\n' +
            '<strong>Address</strong><br>{3}<br>\n' +
            '<strong>Location info</strong><br>{4}<br>\n' +
            '<strong>Zip</strong><br>{5}<br>\n' +
            '<strong>Neighborhood</strong><br>{6}</p>\n'
        ).format(
            format(row['amount'], ','),
            row['buyers'],
            row['sellers'],
            row['address'],
            row['location_info'],
            row['zip_code'],
            row['neighborhood']
        )

        email_string += message.encode('utf8')
        email_string += '\n'
        message = ''

    return email_string


def copy_dashboard_to_cleaned():
    '''
    Correct Cleaned entries based on overrides made in dashboard.
    Only for building database from scratch: Normal flow is add yesterday to
    Cleaned and publish accordingly. Dashboard interaction then comes after
    and directly updates Cleaned while simultaneously adding to/updating same
    entry in Dashboard table.
    '''

    print "Restoring dashboard table..."
    logger.info('copyDashboardToCleaned')

    try:
        local("pg_restore --data-only -d landrecords -t dashboard " +
              dev_config.BACKUP_DIR + "/dashboard_table_$(date +%Y-%m-%d).sql")
        logger.info('successfully restored Dashboard DB')
    except Exception, e:
        logger.info('Could not restore dashboard table')
        logger.error(e, exc_info=True)

    # Correct dashboard table's id field
    fix_id_sql = "SELECT setval('dashboard_id_seq', MAX(id)) FROM dashboard;"
    engine.execute(fix_id_sql)

    q = session.query(
        db.Dashboard
    ).order_by(
        # update Cleaned in order Dashboard changes were made
        db.Dashboard.id.asc()
    ).all()

    rows = []
    for row in q:
        row_dict = {}
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
        logger.info('Updating Cleaned sale based on Dashboard entry')
        # This sale has already been entered into dashboard table
        u = update(db.Cleaned)
        u = u.values(row)
        u = u.where(db.Cleaned.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        logger.info('execute')
        session.commit()
        logger.info('commit')

        print 'Changing Dashboard entry fixed field to true'
        logger.info('Changing Dashboard entry fixed field to true')
        # This sale has already been entered into dashboard table
        u = update(db.Dashboard)
        u = u.values({"fixed": True})
        u = u.where(db.Dashboard.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        logger.info('execute')
        session.commit()
        logger.info('commit')


def build(initial_date=None, until_date=None):
    print "Building tables..."
    logger.info('Build')

    print "details"
    logger.info('details')
    # For all folders (days)
    for folder in sorted(glob.glob('%s/raw/*' % (dev_config.DATA_DIR))):
        logger.debug(folder)
        current_date = folder.split('/')[-1]
        logger.debug(current_date)

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        # print folder
        # logger.debug(folder)
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
            print parsers.AllPurposeParser(form).document_id

            dict_output = parsers.DetailParser(form).form_dict()

            i = insert(db.Detail)
            i = i.values(dict_output)
            session.execute(i)

        # If reached final date, then end.
        if current_date == until_date:
            break

    # logger.info('commit details')
    session.commit()

    print "vendors"
    logger.info('vendors')
    for folder in sorted(glob.glob('%s/data/raw/*' % (dev_config.PROJECT_DIR))):
        # For all folders (days)
        current_date = folder.split('/')[-1]
        logger.debug(current_date)

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        print folder
        # logger.debug(folder)
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
            print parsers.AllPurposeParser(form).document_id

            parsers.VendorParser(form)
        # If reached final date, then end.
        if current_date == until_date:
            break

    # logger.info('commit vendors')
    session.commit()

    print 'vendees'
    # logger.info('vendees')
    # For all folders (days)
    for folder in sorted(glob.glob('%s/raw/*' % (dev_config.DATA_DIR))):
        current_date = folder.split('/')[-1]
        logger.debug(current_date)

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        print folder
        # logger.debug(folder)
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
            print parsers.AllPurposeParser(form).document_id

            parsers.VendeeParser(form)
        # If reached final date, then end.
        if current_date == until_date:
            break

    # logger.info('commit vendors')
    session.commit()

    print 'locations'
    # logger.info('locations')
    # For all folders (days)
    for folder in sorted(glob.glob('%s/raw/*' % (dev_config.DATA_DIR))):
        current_date = folder.split('/')[-1]
        logger.debug(current_date)

        # If this date is before the specified initial_date, then skip.
        try:
            if datetime.strptime(current_date, '%Y-%m-%d') < datetime.strptime(initial_date, '%Y-%m-%d'):
                continue
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        print folder
        # logger.debug(folder)
        for form in sorted(glob.glob('%s/form-html/*.html' % (folder))):
            print parsers.AllPurposeParser(form).document_id

            parsers.LocationParser(form)
        # If reached final date, then end.
        if current_date == until_date:
            break

    # logger.info('commit vendors')
    session.commit()


def send_email(subject='Subject',
               body='Body',
               initial_date=yesterday_date,
               until_date=yesterday_date):
    logger.info('sendEmail')
    # if os.path.isfile("logs/email-%s.txt" % datetime.now()
    # .strftime('%Y-%m-%d')):
    #     os.remove("logs/email-%s.txt" % datetime.now().strftime('%Y-%m-%d'))

    send_email.main(subject=subject,
                    body=body,
                    initial_date=initial_date,
                    until_date=until_date)


def update_cleaned_geom():
    logger.info('updateCleanedGeom')
    local('''psql landrecords -c
        "UPDATE cleaned
        SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"''')


def get_error_page_html(url):
    logger.info('getErrorPageHtml')
    error_req = urllib2.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 ('
        'Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like'
        'Gecko) Chrome/39.0.2171.99 Safari/537.36'})
    error_con = urllib2.urlopen(error_req)
    error_html = error_con.read()
    error_con.close()

    return error_html


def test_url(url, error_html):
    logger.info('testUrl')
    req = urllib2.Request(url, headers={
        'User-Agent': 'Mozilla/5.0'
        '(Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like'
        'Gecko) Chrome/39.0.2171.99 Safari/537.36'})
    con = urllib2.urlopen(req)
    html = con.read()
    con.close()

    if html == error_html:
        return url
    else:
        return None


def check_assessor_links(initial_date=None, until_date=None):
    logger.info('checkAssessorLinks')
    q = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.document_recorded >= '%s' % (initial_date)
    ).filter(
        db.Cleaned.document_recorded <= '%s' % (until_date)
    ).filter(
        db.Cleaned.assessor_publish == '0'
    ).all()

    error_html = get_error_page_html(
        "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=7724-"
        "BURTHESTt")

    num_records = len(q)
    print '%d records to check.' % num_records

    for u in q:
        print '%d records left.' % num_records
        num_records = num_records - 1
        address = u.address
        location_info = u.location_info
        instrument_no = u.instrument_no
        url_param = check_assessor_urls.formAssessorURL(address, location_info)

        if url_param is None:
            '''
            session.query(
                db.Cleaned.instrument_no,
                db.Cleaned.assessor_publish
            ).filter(
                db.Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })

            session.commit()
            '''
            continue

        assessor_url = """
            http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s
            """ % (url_param)

        response = test_url(assessor_url, error_html)

        if response is None:  # No error page
            session.query(
                db.Cleaned.instrument_no,
                db.Cleaned.assessor_publish
            ).filter(
                db.Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "1"
            })

            session.commit()
        '''
        else:#Error page
            session.query(
                db.Cleaned.instrument_no,
                db.Cleaned.assessor_publish
            ).filter(
                db.Cleaned.instrument_no == '%s' % (instrument_no)
            ).update({
                "assessor_publish": "0"
            })

            session.commit()
        '''

        time.sleep(random.randint(1, 2) + random.uniform(1.0, 2.0))


def check_permanent_status_of_new_sales():
    '''
    Examine first-time sales and assign True or False for permanent_flag.
    '''

    logger.info('checkPermanentStatusOfNewSales')

    # Find the date range of sales to look at. This is only to reduce the
    # number of iterations needed by the for-loop below.

    earliest_none_date = ''
    latest_none_date = ''

    q = session.query(
        func.min(db.Detail.document_recorded).label('early_date')
    ).filter(
        db.Detail.permanent_flag is None
    )

    for u in q:
        earliest_none_date = u.early_date

    print 'earliest_none_date:', earliest_none_date
    logger.debug(earliest_none_date)

    q = session.query(
        func.max(db.Detail.document_recorded).label('late_date')
    ).filter(
        db.Detail.permanent_flag is None
    )

    for u in q:
        latest_none_date = u.late_date

    print 'latest_none_date:', latest_none_date
    logger.debug(latest_none_date)

    for folder in sorted(glob.glob('../data/*')):  # For all folders (dates)
        # logger.debug(folder)

        current_iteration_date = folder.split('/')[-1]
        # logger.debug(current_iteration_date)

        try:
            current_iteration_datetime = datetime.strptime(current_iteration_date, '%m-%d-%Y')
            # logger.debug(current_iteration_datetime)
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        try:
            earliest_none_datetime = datetime.combine(earliest_none_date, datetime.min.time())
            # logger.debug(earliest_none_datetime)
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        if current_iteration_datetime < earliest_none_datetime:
            continue

        # For this date that is currently considered temporary (whether by
        # default or because it was previously confirmed to be temporary),
        # check on the permanent date range at the time of the scrape.
        for pathname in sorted(glob.glob('%s/permanent-date-range-when-scraped_*.html' % (folder))):
            # For all records (within each day)
            # print 'pathname:', pathname
            logger.debug(pathname)

            permanent_range_first_date_when_scraped = re.match(r"../data/" + current_iteration_date + r"/permanent-date-range-when-scraped_(\d+)-(\d+).html", pathname).group(1)
            print 'permanent_range_first_date_when_scraped:', permanent_range_first_date_when_scraped
            logger.debug(permanent_range_first_date_when_scraped)
            permanent_range_first_date_when_scraped = datetime.strptime(permanent_range_first_date_when_scraped, '%m%d%Y')  # ).strftime('%Y-%m-%d')
            logger.debug(permanent_range_first_date_when_scraped)

            permanent_range_last_date_when_scraped = re.match(r"../data/" + current_iteration_date + r"/permanent-date-range-when-scraped_(\d+)-(\d+).html", pathname).group(2)
            print 'permanent_range_last_date_when_scraped:', permanent_range_last_date_when_scraped
            logger.debug(permanent_range_last_date_when_scraped)
            permanent_range_last_date_when_scraped = datetime.strptime(permanent_range_last_date_when_scraped, '%m%d%Y')  # ).strftime('%Y-%m-%d')
            logger.debug(permanent_range_last_date_when_scraped)

            if (permanent_range_first_date_when_scraped <= current_iteration_datetime and current_iteration_datetime <= permanent_range_last_date_when_scraped):
                logger.info('query')
                session.query(Detail).filter(Detail.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": True})
                logger.info('query')
                session.query(Cleaned).filter(Cleaned.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": True})
                logger.info('commit')
                session.commit()
            else:
                logger.info('query')
                session.query(Detail).filter(Detail.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": False})
                logger.info('query')
                session.query(Cleaned).filter(Cleaned.document_recorded == '%s' % current_iteration_date).update({"permanent_flag": False})
                logger.info('commit')
                session.commit()
        print '\n'

        # If reached final date, then end.
        if current_iteration_date == latest_none_date:
            break


def check_permanent_status_of_temp_sales():
    '''
    Compare most recently downloaded permanent date range against sales that
    were previously determined to have permanent_flag = False to see if any
    sales should be re-scraped.
    '''

    logger.info('checkPermanentStatusOfTempSales')

    # Find the date range of temporary sales to look at. This is only to
    # reduce the number of iterations needed by the for-loop below.

    earliest_temp_date = ''
    latest_temp_date = ''

    q = session.query(
        db.Detail
    ).filter(
        db.Detail.permanent_flag is False
    ).order_by(
        # update Cleaned in order Dashboard changes were made
        db.Detail.document_recorded
    ).limit(1).all()

    logger.debug(q)

    for u in q:
        logger.debug(u)
        earliest_temp_date = u.document_recorded
        logger.debug(earliest_temp_date)

    q = session.query(
        db.Detail
    ).filter(
        db.Detail.permanent_flag is False
    ).order_by(
        # update Cleaned in order Dashboard changes were made
        db.Detail.document_recorded.desc()
    ).limit(1).all()

    for u in q:
        latest_temp_date = u.document_recorded
        logger.debug(latest_temp_date)

    dates_to_redo = []

    permanent_range_first_date = ''
    permanent_range_last_date = ''

    # Find most recently updated permanent date range.
    for pathname in glob.glob('../data/most-recent-permanent-date-range_*.html'):
        logger.debug(pathname)

        permanent_range_first_date = re.match(r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html", pathname).group(1)
        permanent_range_first_date = datetime.strptime(permanent_range_first_date, '%m%d%Y')#).strftime('%Y-%m-%d')
        logger.debug(permanent_range_first_date)

        permanent_range_last_date = re.match(r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html", pathname).group(2)
        permanent_range_last_date = datetime.strptime(permanent_range_last_date, '%m%d%Y')#).strftime('%Y-%m-%d')
        logger.debug(permanent_range_last_date)

    for folder in sorted(glob.glob('../data/*')): # For all folders (dates)
        current_iteration_date = folder.split('/')[-1]

        try:
            current_iteration_datetime = datetime.strptime(
                current_iteration_date, '%m-%d-%Y')
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        try:
            earliest_temp_datetime = datetime.combine(
                earliest_temp_date, datetime.min.time())
        except Exception, e:
            logger.error(e, exc_info=True)
            continue

        if current_iteration_datetime < earliest_temp_datetime:
            continue

        logger.debug(current_iteration_date)
        logger.debug(current_iteration_datetime)
        logger.debug(earliest_temp_datetime)

        if (permanent_range_first_date <= current_iteration_datetime and current_iteration_datetime <= permanent_range_last_date):
            logger.info('date_to_redo.append')
            dates_to_redo.append(current_iteration_datetime)

        # else:
            # Do nothing. Keep records and don't change permanent_flag

        # If reached final date, then end.
        if current_iteration_date == latest_temp_date:
            logger.info('break')
            break

    # print 'date_to_redo:'
    # print dates_to_redo

    try:
        early_date = min(dates_to_redo)
        logger.debug(early_date)

        late_date = max(dates_to_redo)
        logger.debug(late_date)
    except Exception, e:
        # Nothing left to do because no records are "temporary"
        logger.error(e, exc_info=True)
        return

    early_datetime = datetime.strptime(early_date, '%Y-%m-%d')
    logger.debug(early_datetime)
    late_datetime = datetime.strptime(late_date, '%Y-%m-%d')
    logger.debug(early_datetime)

    # Scrape those days over again
    logger.info('scrape')
    try:
        scrape.main(from_date=early_datetime, until_date=late_datetime)
    except Exception, e:
        logger.error(e, exc_info=True)

    # Delete existing records for this date
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

    # Build those newly scraped records. This will set perm_flag = True in
    # checkPermanentStatusOfNewSales().
    logger.info('doitall')
    do_it_all(early_date, late_date)


def do_it_all(initial_date='2014-02-18', until_date=yesterday_date):

    build(initial_date=initial_date, until_date=until_date)
    geocode()  # CAUTION! Geocoding entire archive takes ~45 minutes.
    publish.PublishChecker(
        initial_date=initial_date, until_date=until_date
    ).check_them_all()
    # clean(initial_date=initial_date, until_date=until_date)
    # if initial_date != until_date: # Assumes any range of dates also wants
    # this function.
    # Don't uncomment: copyDashboardToCleaned()
    # updateCleanedGeom()
    # checkPermanentStatusOfNewSales()

    # checkPermanentStatusOfTempSales()

    # body = runQueriesForEmail(initial_date='2015-03-13',
    # until_date=until_date)
    # sendEmail(
    # subject='Land records summary for %s to %s'
    # % (initial_date, until_date),
    # body=body)

    # checkAssessorLinks(initial_date=initial_date, until_date=until_date)

if __name__ == '__main__':
    if os.path.isfile('%s/logs/initialize.log' % (dev_config.PROJECT_DIR)):
            os.remove('%s/logs/initialize.log' % (dev_config.PROJECT_DIR))

    initialize_log('initialize')

    try:
        do_it_all(initial_date='2014-02-18', until_date='2014-02-18')
        # Default is to build entire archive since 2014/02/18
        # doItAll(initial_date='2014-02-18', until_date=yesterday_date)
    except Exception, e:
        logger.error(e, exc_info=True)
        # pythonEmail.main(
        #     email_subject="Error running Land Record's initialize.py script",
        #     email_body='Check initialize.log for more details.')

    session.close()
    cur.close()
    conn.close()
    logging.shutdown()
    print "Done!"
    logger.info('Done!')
