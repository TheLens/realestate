# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import urllib
import re
import math
import check_assessor_urls
import json

from flask.ext.cache import Cache
from flask import Flask, render_template, jsonify, request, Response, redirect, url_for
from sqlalchemy import create_engine, desc, insert, update, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Cleaned, Dashboard, Neighborhood
from datetime import datetime, timedelta
from functools import wraps

from app_config import server_connection, server_engine, js, indexjs, searchAreajs, searchjs, mapjs, salejs, dashboardjs, neighborhoodstopo, squarestopo, css, development_username, development_password, app_routing, js_app_routing

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

@cache.memoize(timeout=5000)
@app.errorhandler(404)
def page_not_found(self):
    return render_template('404.html',
                            css = css,
                            js = js,
                            indexjs = indexjs), 404

@app.route("%s/webhook" % (app_routing), methods=['POST'])
def webhook():
    json_data = request.data
    print 'json_data:'
    print json_data

    data = json.loads(json_data)
    #print 'data:', data

    return 'Successful!!'

@cache.memoize(timeout=5000)
@app.route("%s/" % (app_routing), methods=['GET'])
def base():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    #yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    #yesterday_date = MonthCheck(yesterday_date)

    qd = session.query(Cleaned).filter(Cleaned.detail_publish == '1').order_by(desc(Cleaned.document_recorded)).limit(1).all()

    for u in qd:
        yesterday_date = readableDate(u.document_recorded, no_day=True)

    q = session.query(Neighborhood.gnocdc_lab).all()

    neighborhoods = []
    for hood in q:
        neighborhoods.append((hood.gnocdc_lab).title().replace('Mcd', 'McD'))

    neighborhoods.sort()

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119, 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128, 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143, 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153, 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162, 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174, 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183, 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    return render_template(
        'index.html',
        yesterday_date = yesterday_date,
        js = js,
        indexjs = indexjs,
        searchAreajs = searchAreajs,
        js_app_routing = js_app_routing,
        css = css,
        neighborhoods = neighborhoods,
        zip_codes = zip_codes
        )

# @app.route('/realestate/search')
# def searchRedirect():
#     return redirect(url_for('/realestate/search/'))

@cache.memoize(timeout=5000)
@app.route("%s/search/" % (app_routing), methods=['GET', 'POST'])
@app.route("%s/search" % (app_routing), methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
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

        response = query_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

        return response

    if request.method == 'POST':
        # Formerly /realestate/mapsearch
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
            response = geoquery_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, latitude, longitude, mapbuttonstate)
        else:
            response = mapquery_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, page_direction, page, totalpages)

        return response

@cache.memoize(timeout=5000)
@app.route("%s/dashboard/" % (app_routing), methods=['GET', 'POST'])
@requires_auth
def dashboard():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if request.method == 'GET':
        q = session.query(
                Cleaned
            ).filter(
                (Cleaned.detail_publish == '0') | 
                (Cleaned.location_publish == '0')
            ).order_by(Cleaned.document_recorded.desc()).all()

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
            js = js,
            dashboardjs = dashboardjs,
            neighborhoodstopo = neighborhoodstopo,
            squarestopo = squarestopo,
            css = css,
            num_results = num_results,
            js_app_routing = js_app_routing,
            newrows = q,
            jsrows = rows,
            number_of_indexes = len(q)
        )

    if request.method == 'POST':
        # User submitted a change through dashboard
        incomingdata = request.get_json()

        for key in incomingdata:
            incomingdata[key] = incomingdata[key].strip()


        #Set fixed to false
        incomingdata['fixed'] = False

        dumb = incomingdata['document_recorded']
        dumb = dumb.replace('March', 'Mar.')
        dumb = dumb.replace('April', 'Apr.')
        dumb = dumb.replace('May', 'May.')
        dumb = dumb.replace('June', 'Jun.')
        dumb = dumb.replace('July', 'Jul.')
        dumb = datetime.strptime(dumb, '%A, %b. %d, %Y')
        dumb = dumb.strftime('%Y-%m-%d')
        incomingdata['document_recorded'] = dumb

        dumb = incomingdata['document_date']
        dumb = dumb.replace('March', 'Mar.')
        dumb = dumb.replace('April', 'Apr.')
        dumb = dumb.replace('May', 'May.')
        dumb = dumb.replace('June', 'Jun.')
        dumb = dumb.replace('July', 'Jul.')
        dumb = datetime.strptime(dumb, '%A, %b. %d, %Y')
        dumb = dumb.strftime('%Y-%m-%d')
        incomingdata['document_date'] = dumb

        pp.pprint(incomingdata)


        '''
        Insert/update dashboard log table
        '''

        q = session.query(
                Dashboard.instrument_no
            ).filter(
                Dashboard.instrument_no == '%s' % (incomingdata['instrument_no'])
            ).all()

        input_length = len(q)

        if input_length == 0:
            print 'Adding sale in dashboard table'
            #This sale has not been entered into dashboard table yet
            i = insert(Dashboard)
            i = i.values(incomingdata)
            session.execute(i)
            session.commit()
        else:
            print 'Updating sale in dashboard table'
            #This sale has already been entered into dashboard table            
            u = update(Dashboard)
            u = u.values(incomingdata)
            u = u.where(Dashboard.instrument_no == '%s' % incomingdata['instrument_no'])

            session.execute(u)
            session.commit()

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

@cache.memoize(timeout=5000)
@app.route("%s/sale/<instrument_no>" % (app_routing), methods=['GET'])
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

        qd = session.query(Cleaned).filter(Cleaned.detail_publish == '1').order_by(desc(Cleaned.document_recorded)).limit(1).all()

        for u in qd:
            yesterday_date = readableDate(u.document_recorded, no_day=True)

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
            u.document_date = readableDate(u.document_date, no_day=True)
            address = u.address
            location_info = u.location_info
            assessor_publish = u.assessor_publish

        features = loopThing(q)

        jsdata = {
            "type": "FeatureCollection", 
            "features": features
        }

        #yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        #yesterday_date = MonthCheck(yesterday_date)

        if assessor_publish == '0' or assessor_publish == None or assessor_publish == '':
            assessor = "Could not find this property on the Orleans Parish Assessor's Office site. <a href='http://www.qpublic.net/la/orleans/search1.html' target='_blank'>Search based on other criteria.</a>"
        else:
            url_param = check_assessor_urls.formAssessorURL(address, location_info)
            assessor_url = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s" % (url_param)
            assessor = "<a href='%s' target='_blank'>Read more about this property on the Assessor's Office's website.</a>" % (assessor_url)
        
        template1 = ''

        if len(q) == 0:
            template1 = page_not_found()
        else:
            template1 =  render_template(
                'sale.html',
                yesterday_date = yesterday_date,
                js = js,
                salejs = salejs,
                css = css,
                newrows = q,
                assessor = assessor,
                jsdata = jsdata
            )

        session.close()

        return template1

@cache.memoize(timeout=5000)
@app.route("%s/input" % (app_routing), methods=['GET', 'POST'])
def input():
    term = request.args.get('q')

    search_term = urllib.unquote(term).decode('utf8')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    q_neighborhoods = session.query(
            Cleaned.neighborhood
        ).filter(
            Cleaned.neighborhood.ilike('%%%s%%' % search_term)
        ).distinct().limit(3).all()

    q_zip = session.query(
            Cleaned.zip_code
        ).filter(
            Cleaned.zip_code.ilike('%%%s%%' % search_term)
        ).distinct().limit(3).all()

    q_locations = session.query(
            Cleaned.detail_publish, Cleaned.address
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.address.ilike('%%%s%%' % search_term)
        ).limit(3).all()

    q_buyers = session.query(
            Cleaned.detail_publish, Cleaned.buyers
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.buyers.ilike('%%%s%%' % search_term)
        ).limit(3).all()

    q_sellers = session.query(
            Cleaned.detail_publish, Cleaned.sellers
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.sellers.ilike('%%%s%%' % search_term)
        ).limit(3).all()

    response = []


    for i, u in enumerate(q_neighborhoods):
        response.append(
            {
                "label": (u.neighborhood).title().replace('Mcd', 'McD'),
                "category": "Neighborhoods"
            }
        )

    for i, u in enumerate(q_zip):
        response.append(
            {
                "label": u.zip_code,
                "category": "ZIP codes"
            }
        )

    for i, u in enumerate(q_locations):
        response.append(
            {
                "label": u.address,
                "category": "Addresses"
            }
        )

    for i, u in enumerate(q_buyers):
        response.append(
            {
                "label": u.buyers,
                "category": "Buyers"
            }
        )

    for i, u in enumerate(q_sellers):
        response.append(
            {
                "label": u.sellers,
                "category": "Sellers"
            }
        )

    return jsonify(
        response = response
        )

@cache.memoize(timeout=5000)
def query_db(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    qd = session.query(Cleaned).filter(Cleaned.detail_publish == '1').order_by(desc(Cleaned.document_recorded)).limit(1).all()

    for u in qd:
        yesterday_date = readableDate(u.document_recorded, no_day=True)

    q = session.query(Neighborhood.gnocdc_lab).all()

    neighborhoods = []
    for hood in q:
        neighborhoods.append((hood.gnocdc_lab).title().replace('Mcd', 'McD'))

    neighborhoods.sort()

    q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

    qlength = len(q) # number of records
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

    q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset, pagelength)
    
    for u in q:
        u.amount = Currency(u.amount)
        u.document_date = readableDate(u.document_date, no_day=True)

    features = loopThing(q)
    newrows = q

    jsdata = {
        "type": "FeatureCollection", 
        "features": features
    }

    # yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    # yesterday_date = MonthCheck(yesterday_date)

    show_results = 'none'
    if qlength == 0:
        page = 0
        show_results = 'block'

    amountlow, amounthigh, begindate, enddate = revertEntries(amountlow, amounthigh, begindate, enddate)

    parameters = {}
    parameters['name_address'] = name_address
    parameters['amountlow'] = amountlow
    parameters['amounthigh'] = amounthigh
    parameters['begindate'] = begindate
    parameters['enddate'] = enddate
    parameters['neighborhood'] = neighborhood
    parameters['zip_code'] = zip_code

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119, 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128, 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143, 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153, 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162, 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174, 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183, 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    map_button = False
    results_language = constructResultsLanguage(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, qlength, map_button)

    print '564page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', pagelength

    template1 = render_template(
        'search.html',
        yesterday_date = yesterday_date,
        js = js,
        searchjs = searchjs,
        searchAreajs = searchAreajs,
        mapjs = mapjs,
        css = css,
        js_app_routing = js_app_routing,
        newrows = newrows,
        jsdata = jsdata,
        show_results = show_results,
        #qlength = NumberWithCommas(qlength),
        #plural_or_not = plural_or_not,
        results_language = results_language,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength,
        parameters = parameters,
        neighborhoods = neighborhoods,
        zip_codes = zip_codes
    )

    session.close()

    return template1

def constructResultsLanguage(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, qlength, map_button):
    '''
    In goes filter values, out of this messy function comes a coherent sentence such as, "10 results found in the Mid-City neighborhood."
    '''

    if qlength == 1:
        plural_or_not = "sale"
    else:
        plural_or_not = "sales"

    final_sentence = str(NumberWithCommas(qlength)) + ' ' + str(plural_or_not) + ' found'#10 records found
    if name_address == '' and amountlow == '' and amounthigh == '' and begindate == '' and enddate == '' and neighborhood == '' and zip_code == '':
        if map_button == True:
            final_sentence = final_sentence + ' in the current map view.'#10 records found.
        else:
            final_sentence = final_sentence + '.'#10 records found.
    else:
        if name_address != '':
            if len(name_address.split()) > 1:
                final_sentence = final_sentence + ' for key phrase "' + name_address + '"'#10 records found for 'keyword'
            else:
                final_sentence = final_sentence + ' for keyword "' + name_address + '"'#10 records found for 'keyword'

        if neighborhood != '':
            if zip_code != '':
                final_sentence = final_sentence + " in the " + neighborhood + " neighborhood and " + zip_code#10 records found for 'keyword' in Mid-City and 70119
            else:
                final_sentence = final_sentence + " in the " + neighborhood + " neighborhood"#10 records found for 'keyword' in Mid-City
        elif zip_code != '':
            final_sentence = final_sentence + " in ZIP code " + zip_code#10 records found for 'keyword' in 70119

        if amountlow != '':
            if amounthigh != '':
                final_sentence = final_sentence + " where the price was between " + Currency(amountlow) + " and " + Currency(amounthigh)#10 records found for 'keyword' in Mid-City, where the amount is between $10 and $20
            else:
                final_sentence = final_sentence + " where the price was greater than " + Currency(amountlow)#10 records found for 'keyword' in Mid-City, where the amount is greater than $10
        elif amounthigh != '':
            final_sentence = final_sentence + " where the price was less than " + Currency(amounthigh)#10 records found for 'keyword' in Mid-City, where the amount is less than $20

        if begindate != '':
            if enddate != '':
                final_sentence = final_sentence + " between " + readableDate(begindate) + ", and " + readableDate(enddate)#10 records found for 'keyword' in Mid-City, where the amount is between $10 and $20, between Feb. 10, 2014, and Feb. 12, 2014
            else:
                final_sentence = final_sentence + " after " + readableDate(begindate)#10 records found for 'keyword' in Mid-City, where the amount is greater than $10, after Feb. 10, 2014.
        elif enddate != '':
            final_sentence = final_sentence + " before " + readableDate(enddate)#10 records found for 'keyword' in Mid-City, where the amount is less than $20, before Feb. 20, 2014.

        if map_button == True:
            final_sentence = final_sentence + " in the current map view"

        if final_sentence[-1] == "'" or final_sentence[-1] == '"':
            last_character = final_sentence[-1]
            l = list(final_sentence)
            l[-1] = '.'
            l.append(last_character)
            final_sentence = ''.join(l)
        else:
            final_sentence = final_sentence + '.'

    return final_sentence

@cache.memoize(timeout=5000)
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

    qd = session.query(Cleaned).filter(Cleaned.detail_publish == '1').order_by(desc(Cleaned.document_recorded)).limit(1).all()

    for u in qd:
        yesterday_date = readableDate(u.document_recorded, no_day=True)

    if mapbuttonstate == True: #map filtering is on        
        q = mapQueryLength(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate)
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == None:
            page = 1
            recordsoffset = (page - 1) * pagelength
        elif page_direction == 'back' or page_direction == 'forward':
            if page_direction == 'forward':
                print '682LOOK'
                print '682page:', page
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
                print '707LOOK'
                print '709page:', page
                page = int(page) + 1
            
            if qlength == 0:
                page = 0

            if page == 0:
                recordsoffset = 0
            else:
                if page_direction == 'back':
                    page = int(page) - 1
                recordsoffset = (page - 1) * pagelength

        q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset, pagelength)

    for u in q: 
        u.amount = Currency(u.amount)
        u.document_date = readableDate(u.document_date, no_day=True)

    features = loopThing(q)

    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }

    # yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    # yesterday_date = MonthCheck(yesterday_date)

    show_results = 'none'
    if qlength == 0:
        page = 0
        show_results = 'block'

    tabletemplate = render_template(
        'table.html',
        newrows = q
    )

    session.close()

    amountlow, amounthigh, begindate, enddate = revertEntries(amountlow, amounthigh, begindate, enddate)

    results_language = constructResultsLanguage(name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, qlength, mapbuttonstate)

    print '754page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', pagelength

    return jsonify(
        tabletemplate = tabletemplate,
        yesterday_date = yesterday_date,
        jsdata = jsdata,
        #qlength = NumberWithCommas(qlength),
        results_language = results_language,
        show_results = show_results,
        #plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )

@cache.memoize(timeout=5000)
def geoquery_db(name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, latitude, longitude, mapbuttonstate):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    qd = session.query(Cleaned).filter(Cleaned.detail_publish == '1').order_by(desc(Cleaned.document_recorded)).limit(1).all()

    for u in qd:
        yesterday_date = readableDate(u.document_recorded, no_day=True)

    q = mapQuery2(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)

    qlength = len(q) # number of records
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

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
        u.document_date = readableDate(u.document_date, no_day=True)

    features = loopThing(q)

    jsdata = {
        "type": "FeatureCollection", 
        "features": features
    }

    #yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    #yesterday_date = MonthCheck(yesterday_date)

    if qlength == 0:
        page = 0
    tabletemplate = render_template(
        'table.html',
        newrows = q
    )

    amountlow, amounthigh, begindate, enddate = revertEntries(amountlow, amounthigh, begindate, enddate)

    session.close()

    results_language = constructResultsLanguage(name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, qlength, mapbuttonstate)

    print '848page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', pagelength

    return jsonify(
        tabletemplate = tabletemplate,
        yesterday_date = yesterday_date,
        jsdata = jsdata,
        results_language = results_language,
        #qlength = NumberWithCommas(qlength),
        #plural_or_not = plural_or_not,
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

def mapQuery3(session, name, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, recordsoffset, pagelength):
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

def loopThing(q):
    features = []
    features_dict = {}
    for u in q:
        if u.location_publish == "0":
            u.document_date = u.document_date + "*"
            continue
        if u.permanent_flag == False:
            u.document_date = u.document_date + u"\u2020"
            # continue
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

def readableDate(value, no_day=None):
    # Receive yyyy-mm-dd. Return Day, Month Date, Year
    if (value != None):
        if (type(value) == unicode):
            #value = urllib.unquote(value).decode('utf8')
            value = str(value)
            value = datetime.strptime(value, '%m/%d/%Y')
            value = value.strftime('%b. %-d, %Y')

            return value
        else:
            #value = str(value)
            if no_day == None:
                readable_date = value.strftime('%A, %b. %-d, %Y')
            else:
                readable_date = value.strftime('%b. %-d, %Y')

            readable_date = readable_date.replace('Mar.', 'March')
            readable_date = readable_date.replace('Apr.', 'April')
            readable_date = readable_date.replace('May.', 'May')
            readable_date = readable_date.replace('Jun.', 'June')
            readable_date = readable_date.replace('Jul.', 'July')

            return readable_date#value.strftime('%A, %b. %-d, %Y')

    else:
        return "None"

def Currency(value):
    value = int(value)
    return "${:,}".format(value)

def publishConversion(bit):
    bit = int(bit)
    conversion_dict = {
        0: "No",
        1: "Yes"
    }
    english = conversion_dict[bit]
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
        # host = "0.0.0.0",
        #use_reloader = True,
        # debug = True
    )
