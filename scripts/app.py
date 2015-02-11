# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import urllib
import re
import math
import check_assessor_urls

from flask.ext.cache import Cache
from flask import Flask, render_template, jsonify, request, Response
from sqlalchemy import create_engine, desc, insert, update, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Cleaned, Dashboard, Neighborhood
from datetime import datetime, timedelta
from functools import wraps

from app_config import server_connection, server_engine, indexjs, searchjs, salejs, dashboardjs, neighborhoodstopo, squarestopo, css, development_username, development_password

Base = declarative_base()
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

conn = psycopg2.connect("%s" % (server_connection))
c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (server_engine))

pagelength = 10

def check_auth(username, password):
    return username == development_username and password == development_password

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#@cache.memoize(timeout=5000)
@app.route("/realestate/", methods=['GET'])
def base():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)

    q = session.query(Neighborhood).all()

    neighborhoods = []
    for hood in q:
        #print hood.gnocdc_lab
        neighborhoods.append((hood.gnocdc_lab).title())

    neighborhoods.sort()

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119, 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128, 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143, 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153, 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162, 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174, 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183, 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    return render_template(
        'index.html',
        yesterday_date = yesterday_date,
        indexjs = indexjs,
        css = css,
        neighborhoods = neighborhoods,
        zip_codes = zip_codes
        )

#@cache.memoize(timeout=5000)
@app.route("/realestate/search", methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        print 'GET'
        incomingdata = {}

        '''
        Assign query string parameters to incomingdata dictionary.
        '''

        incomingdata['name_address'] = request.args.get('q')
        incomingdata['amountlow'] = request.args.get('a1')
        incomingdata['amounthigh'] = request.args.get('a2')
        incomingdata['begindate'] = request.args.get('d1')
        incomingdata['enddate'] = request.args.get('d2')
        incomingdata['neighborhood'] = request.args.get('nbhd')
        incomingdata['zip_code'] = request.args.get('zip')

        # Change any missing parameters to 0-length string
        for key in incomingdata:
            if incomingdata[key] == None:
                incomingdata[key] = ''

        name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code = assignData(incomingdata)

        amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, amounthigh, begindate, enddate)

        #print amountlow, amounthigh, begindate, enddate

        response = query_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

        return response

    if request.method == 'POST':
        # Formerly /realestate/mapsearch
        print 'POST'
        incomingdata = request.get_json()

        name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code = assignData(incomingdata)

        bounds = incomingdata['bounds']
        mapbuttonstate = incomingdata['mapbuttonstate']
        page = incomingdata['page']
        totalpages = incomingdata['totalpages']
        page_direction = incomingdata['direction']

        amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, amounthigh, begindate, enddate)

        # If a geo query (search near me)
        if 'latitude' in incomingdata and 'longitude' in incomingdata:
            latitude = incomingdata['latitude']
            longitude = incomingdata['longitude']
            response = geoquery_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, latitude, longitude)
        else:
            response = mapquery_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, page_direction, page, totalpages)

        return response

#@cache.memoize(timeout=5000)
@app.route("/realestate/dashboard", methods=['GET', 'POST'])
#@requires_auth#todo: turn back on
def dashboard():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if request.method == 'GET':
        print 'GET'

        q = session.query(
                Cleaned
            ).filter(
                (Cleaned.detail_publish == '0') | 
                (Cleaned.location_publish == '0')
            ).order_by(Cleaned.document_recorded.desc()).limit(20).all()
        #todo: paginate, because loading many maps takes a while

        num_results = len(q)

        for u in q: 
            u.amount = Currency(u.amount)
            u.document_date = readableDate(u.document_date)
            u.document_recorded = readableDate(u.document_recorded)
            u.detail_publish = publishConversion(u.detail_publish)
            u.location_publish = publishConversion(u.location_publish)

        rows = []
        for row in q:
            row_dict = {};
            row_dict['detail_publish'] = row.detail_publish
            row_dict['location_publish'] = row.location_publish
            row_dict['latitude'] = row.latitude
            row_dict['longitude'] = row.longitude
            row_dict['amount'] = row.amount
            row_dict['document_recorded'] = row.document_recorded
            row_dict['document_date'] = row.document_date

            rows.append(row_dict)

        return render_template(
            'dashboard.html',
            dashboardjs = dashboardjs,
            neighborhoodstopo = neighborhoodstopo,
            squarestopo = squarestopo,
            css = css,
            num_results = num_results,
            newrows = q,
            jsrows = rows,
            number_of_indexes = len(q)
        )

    if request.method == 'POST':
        # User submitted a change through dashboard
        print 'POST'

        incomingdata = request.get_json()

        for key in incomingdata:
            incomingdata[key] = incomingdata[key].strip()

        #Set fixed to false
        incomingdata['fixed'] = False

        pp.pprint(incomingdata)

        '''
        Insert/update dashboard log table
        '''

        q = session.query(
                Dashboard
            ).filter(
                Dashboard.instrument_no == '%s' % (incomingdata['instrument_no'])
            ).all()

        input_length = len(q)
        print input_length

        if input_length == 0:
            print 'Adding sale in dashboard table'
            #This sale has not been entered into dashboard table yet
            i = insert(Dashboard)
            i = i.values(incomingdata)
            session.execute(i)
            #session.commit()
        else:
            print 'Updating sale in dashboard table'
            #This sale has already been entered into dashboard table            
            u = update(Dashboard)
            u = u.values(incomingdata)
            u = u.where(Dashboard.instrument_no == '%s' % incomingdata['instrument_no'])

            session.execute(u)
            #session.commit()

        # Update changes in Cleaned table
        updateCleaned()
        
        return 'hi'

def updateCleaned():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    q = session.query(
            Dashboard
        ).filter(
            Dashboard.fixed == False
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

#@cache.memoize(timeout=5000)
@app.route("/realestate/sale/<instrument_no>", methods=['GET'])
def sale(instrument_no = None):

    search_term = instrument_no
    instrument_no = urllib.unquote(search_term).decode('utf8')

    if request.method == 'GET':

        '''
        Assign query string parameters to incomingdata dictionary.
        '''

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.instrument_no == '%s' % (instrument_no)
            ).all()

        assessor_publish = ''
        
        for u in q: 
            u.amount = Currency(u.amount)
            u.document_date = readableDate(u.document_date)
            address = u.address
            location_info = u.location_info
            assessor_publish = u.assessor_publish

        features = loopThing(q)

        jsdata = {
            "type": "FeatureCollection", 
            "features": features
        }

        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        yesterday_date = MonthCheck(yesterday_date)

        if assessor_publish == '0' or assessor_publish == None or assessor_publish == '':
            assessor = "Could not find this location in the assessor's database. <a href='http://www.qpublic.net/la/orleans/search1.html' target='_blank'>Search based on other criteria.</a>"
        else:
            url_param = check_assessor_urls.formAssessorURL(address, location_info)
            assessor_url = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s" % (url_param)
            assessor = "<a href='%s' target='_blank'>Read more about this property on the Assessor's Office's website.</a>" % (assessor_url)
        template1 =  render_template(
            'sale.html',
            yesterday_date = yesterday_date,
            salejs = salejs,
            css = css,
            newrows = q,
            assessor = assessor,
            jsdata = jsdata
        )

        session.close()

        return template1

#@cache.memoize(timeout=5000)
@app.route("/realestate/input", methods=['GET', 'POST'])
def input():
    print 'request:'
    print request

    term = request.args.get('q')
    print 'term:'
    print term

    search_term = urllib.unquote(term).decode('utf8')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    q_neighborhoods = session.query(
            Neighborhood
        ).filter(
            (Neighborhood.gnocdc_lab.ilike('%%%s%%' % search_term))
        ).all()

    q_locations = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.address.ilike('%%%s%%' % search_term))
        ).all()

    q_buyers = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.buyers.ilike('%%%s%%' % search_term))
        ).all()

    q_sellers = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % search_term))
        ).all()

    response = []

    print len(q_neighborhoods)

    for i, u in enumerate(q_neighborhoods):
        response.append(
            {
                "label": (u.gnocdc_lab).title(),
                "category": "Neighborhoods"
            }
        )
        # Limit of three options
        if i == 2:
            break

    for i, u in enumerate(q_locations):
        response.append(
            {
                "label": u.address,
                "category": "Addresses"
            }
        )
        # Limit of three options
        if i == 2:
            break

    for i, u in enumerate(q_buyers):
        response.append(
            {
                "label": u.buyers,
                "category": "Buyers"
            }
        )
        # Limit of three options
        if i == 2:
            break

    for i, u in enumerate(q_sellers):
        response.append(
            {
                "label": u.sellers,
                "category": "Sellers"
            }
        )
        # Limit of three options
        if i == 2:
            break

    pp.pprint(response)

    return jsonify(
        response = response
        )

#@cache.memoize(timeout=5000)
def query_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    print 'query_db'

    q = session.query(Neighborhood).all()

    neighborhoods = []
    for hood in q:
        #print hood.gnocdc_lab
        neighborhoods.append((hood.gnocdc_lab).title())

    neighborhoods.sort()

    q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

    qlength = len(q) # number of records
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

    q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset)
    
    for u in q: 
        u.amount = Currency(u.amount)
        u.document_date = RewriteDate(u.document_date)

    features = loopThing(q)
    newrows = q

    jsdata = {
        "type": "FeatureCollection", 
        "features": features
    }

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)

    if qlength == 1:
        plural_or_not = "result"
    else:
        plural_or_not = "results"

    if qlength == 0:
        page = 0

    amountlow, amounthigh, begindate, enddate = revertEntries(amountlow, amounthigh, begindate, enddate)

    parameters = {}
    parameters['name_address'] = name_address
    parameters['amountlow'] = amountlow
    parameters['amounthigh'] = amounthigh
    parameters['begindate'] = begindate
    parameters['enddate'] = enddate

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119, 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128, 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143, 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153, 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162, 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174, 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183, 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    template1 = render_template(
        'search.html',
        yesterday_date = yesterday_date,
        searchjs = searchjs,
        css = css,
        newrows = newrows,
        jsdata = jsdata,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength,
        parameters = parameters,
        neighborhoods = neighborhoods,
        zip_codes = zip_codes
    )

    session.close()

    return template1

#@cache.memoize(timeout=5000)
def mapquery_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, page_direction, page, totalpages):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]

    print 'mapbuttonstate:', mapbuttonstate
    print 'page direction:', page_direction
    print 'page:', page
    #print 'totalpages:', totalpages

    if mapbuttonstate == True: #map filtering is on        
        q = mapQueryLength(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate)
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        print 'totalpages:', totalpages

        if page_direction == None:
            page = 1
            recordsoffset = (page - 1) * pagelength
        elif page_direction == 'back' or page_direction == 'forward':
            if page_direction == 'forward':
                page = int(page) + 1

            if qlength == 0:
                page = 0

            if page == 0:
                recordsoffset = 0
            else:
                if page_direction == 'back':
                    page = int(page) - 1
                recordsoffset = (page - 1) * pagelength

        q = mapQuery1(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, recordsoffset)

    if mapbuttonstate == False: # map filtering is off
        q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == None:
            page = 1
            recordsoffset = (page - 1) * pagelength
        elif page_direction == 'back' or page_direction == 'forward':
            if page_direction == 'forward':
                page = int(page) + 1
            
            if qlength == 0:
                page = 0

            if page == 0:
                recordsoffset = 0
            else:
                if page_direction == 'back':
                    page = int(page) - 1
                recordsoffset = (page - 1) * pagelength

        q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset)

    for u in q: 
        u.amount = Currency(u.amount)
        u.document_date = RewriteDate(u.document_date)

    features = loopThing(q)

    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)

    if qlength == 1:
        plural_or_not = "result"
    else:
        plural_or_not = "results"

    if qlength == 0:
        page = 0
    tabletemplate = render_template(
        'table.html',
        newrows = q
    )

    session.close()

    return jsonify(
        tabletemplate = tabletemplate,
        yesterday_date = yesterday_date,
        jsdata = jsdata,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )

#@cache.memoize(timeout=5000)
def geoquery_db(name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, latitude, longitude):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    print 'geoquery_db'

    q = mapQuery2(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

    qlength = len(q) # number of records
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

    '''
    todo: make these changes to cleaned in databasemaker

    ALTER TABLE cleaned ADD COLUMN geom geometry(POINT,4326);
    UPDATE cleaned SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    CREATE INDEX index_cleaned_geom ON cleaned USING GIST(geom);

    example query:
    SELECT count(*) FROM cleaned WHERE ST_Distance_Sphere(geom, ST_MakePoint(-90.1016, 29.9684)) <= 1 * 1609.34;
    '''

    '''
    qq = session.query(
                func.ST_Y(
                    func.ST_Centroid(Square.geom)
                ).label('ST_Y')
            ).all()
    '''

    print 'Latitude:', latitude
    print type(latitude)
    print 'Longitude:', longitude
    print type(longitude)

    # Near me query
    q = session.query(
            Cleaned
        ).filter(
            func.ST_Distance_Sphere(
                Cleaned.geom, func.ST_MakePoint('%f' % longitude, '%f' % latitude)
                ) <= 1 * 1609.34
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.address.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % zip_code)
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).order_by(
            desc(Cleaned.document_date)
        ).offset(
            '%d' % recordsoffset
        ).limit(
            '%d' % pagelength
        ).all()

    for u in q: 
        u.amount = Currency(u.amount)
        u.document_date = RewriteDate(u.document_date)

    features = loopThing(q)

    jsdata = {
        "type": "FeatureCollection", 
        "features": features
    }

    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)

    if qlength == 1:
        plural_or_not = "result"
    else:
        plural_or_not = "results"

    if qlength == 0:
        page = 0
    tabletemplate = render_template(
        'table.html',
        newrows = q
    )

    amountlow, amounthigh, begindate, enddate = revertEntries(amountlow, amounthigh, begindate, enddate)

    session.close()

    return jsonify(
        tabletemplate = tabletemplate,
        yesterday_date = yesterday_date,
        jsdata = jsdata,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )

def assignData(incomingdata):
    search_term = incomingdata['name_address']
    name_address = urllib.unquote(search_term).decode('utf8')

    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']

    neighborhood = incomingdata['neighborhood']
    neighborhood = urllib.unquote(neighborhood).decode('utf8')

    zip_code = incomingdata['zip_code']

    return (name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

def mapQueryLength(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.address.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % zip_code)
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).filter(
            (Cleaned.latitude <= bounds[0]) & 
            (Cleaned.latitude >= bounds[2]) & 
            (Cleaned.longitude <= bounds[1]) & 
            (Cleaned.longitude >= bounds[3])
        ).all()
    return q

# For when map filtering is turned on
def mapQuery1(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, recordsoffset):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.address.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % zip_code)
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).filter(
            (Cleaned.latitude <= bounds[0]) & 
            (Cleaned.latitude >= bounds[2]) & 
            (Cleaned.longitude <= bounds[1]) & 
            (Cleaned.longitude >= bounds[3])
        ).order_by(
            desc(Cleaned.document_date)
        ).offset(
            '%d' % recordsoffset
        ).limit(
            '%d' % pagelength
        ).all()
    return q

def mapQuery2(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.address.ilike('%%%s%%' % name))|
            (Cleaned.instrument_no.ilike('%%%s%%' % name))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % zip_code)
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).all()
    return q

def mapQuery3(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.address.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name))
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % zip_code)
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).order_by(
            desc(Cleaned.document_date)
        ).offset(
            '%d' % recordsoffset
        ).limit(
            '%d' % pagelength
        ).all()
    return q

'''
#@cache.memoize(timeout=5000)
@app.route("/realestate/pageflip", methods=['POST'])
def pageflip():
    incomingdata = request.get_json()

    name_address, amountlow, amounthigh, begindate, enddate = assignData(incomingdata)
    
    bounds = incomingdata['bounds']
    mapbuttonstate = incomingdata['mapbuttonstate']
    page = incomingdata['page']
    totalpages = incomingdata['totalpages']
    page_direction = incomingdata['direction']
    
    amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, amounthigh, begindate, enddate)

    return page_query(name_address, amountlow, amounthigh, begindate, 
        enddate, bounds, mapbuttonstate, page_direction, page, totalpages)
'''
'''
#@cache.memoize(timeout=5000)
def page_query(name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate, page_direction, page, totalpages):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]

    if mapbuttonstate == True: #map filtering is on
        q = mapQueryLength(session, name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate)

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == 'forward':
            page = int(page) + 1

        if qlength == 0:
            page = 0

        if page == 0:
            recordsoffset = 0
        else:
            if page_direction == 'back':
                page = int(page) - 1
            recordsoffset = (page - 1) * pagelength

        q = mapQuery1(session, name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate, recordsoffset)

    if mapbuttonstate == False: # map filtering is off
        q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate)

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == 'forward':
            page = int(page) + 1
        
        if qlength == 0:
            page = 0

        if page == 0:
            recordsoffset = 0
        else:
            if page_direction == 'back':
                page = int(page) - 1
            recordsoffset = (page - 1) * pagelength

        q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, recordsoffset)

    for u in q: 
        u.amount = Currency(u.amount)
        u.document_date = RewriteDate(u.document_date)
    
    features = loopThing(q)
    
    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }
    if qlength == 1:
        plural_or_not = "result"
    else:
        plural_or_not = "results"
    tabletemplate = render_template(
        'table.html',
        newrows = q
    )
    session.close()

    return jsonify(
        tabletemplate = tabletemplate,
        jsdata = jsdata,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )
'''

def loopThing(q):
    features = []
    features_dict = {}
    for u in q:
        if u.location_publish == "0":
            u.document_date = u.document_date + "*"
            continue
        features_dict = { 
            "type": "Feature", 
            "properties": { 
            "document_date": u.document_date,
            "address": u.address,
            "location_info": u.location_info, 
            "amount": u.amount, 
            "buyers": u.buyers, 
            "sellers": u.sellers, 
            "instrument_no": u.instrument_no}, 
            "geometry": { 
                "type": "Point", 
                "coordinates": [u.longitude, u.latitude]
            }
        }
        features.append(features_dict)

    return features

def MonthCheck(yesterday_date):
    yesterday_date = re.sub(r"Jan",r"Jan.", yesterday_date)
    yesterday_date = re.sub(r"Feb",r"Feb.", yesterday_date)
    yesterday_date = re.sub(r"Mar",r"March", yesterday_date)
    yesterday_date = re.sub(r"Apr",r"April", yesterday_date)
    yesterday_date = re.sub(r"Jun",r"June", yesterday_date)
    yesterday_date = re.sub(r"Jul",r"July", yesterday_date)
    yesterday_date = re.sub(r"Aug",r"Aug.", yesterday_date)
    yesterday_date = re.sub(r"Sep",r"Sept.", yesterday_date)
    yesterday_date = re.sub(r"Oct",r"Oct.", yesterday_date)
    yesterday_date = re.sub(r"Nov",r"Nov.", yesterday_date)
    yesterday_date = re.sub(r"Dec",r"Dec.", yesterday_date)
    return yesterday_date
    
def RewriteDate(value):
    # Receive yyyy-mm-dd. Return mm-dd-yyyy
    if (value != None):
        return value.strftime("%m-%d-%Y")
    else:
        return "None"

def readableDate(value):
    # Receive yyyy-mm-dd. Return Day, Month Date, Year
    if (value != None):
        readable_date = value.strftime('%A, %b. %-d, %Y')

        readable_date = readable_date.replace('Mar.', 'March')
        readable_date = readable_date.replace('Apr.', 'April')
        readable_date = readable_date.replace('May.', 'May')
        readable_date = readable_date.replace('Jun.', 'June')
        readable_date = readable_date.replace('Jul.', 'July')

        return value.strftime('%A, %b. %-d, %Y')

    else:
        return "None"

def Currency(value):
    return "${:,}".format(value)

def publishConversion(bit):
    bit = int(bit)
    conversion_dict = {
        0: "No",
        1: "Yes"
    }
    english = conversion_dict[bit]
    #print english
    return english

def publishReversion(english):
    english = english[0].title()#Accepts Yes, Y, yeah, yes sir, etc.
    conversion_dict = {
        "N": 0,
        "Y": 1
    }
    bit = conversion_dict[english]
    return bit

def NumberWithCommas(value):
    return "{:,}".format(value)

def CheckEntry(amountlow, amounthigh, begindate, enddate):
    if amountlow == '':
        amountlow = 0
    if amounthigh == '':
        amounthigh = 9999999999999
    if begindate == '':
        begindate = "1900-01-01"
    if enddate == '':
        enddate = (datetime.today()).strftime('%Y-%m-%d')

    return (amountlow, amounthigh, begindate, enddate)

def revertEntries(amountlow, amounthigh, begindate, enddate):
    if amountlow == 0:
        amountlow = ''
    if amounthigh == 9999999999999:
        amounthigh = ''
    if begindate == '1900-01-01':
        begindate = ''
    if enddate == (datetime.today()).strftime('%Y-%m-%d'):
        enddate = ''

    return (amountlow, amounthigh, begindate, enddate)

if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        use_reloader = True,
        debug = True
    )
