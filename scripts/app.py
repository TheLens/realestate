# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import urllib
import re
import math

from flask import Flask, render_template, jsonify, request, Response
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Cleaned
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
from app_config import server_connection, server_engine, js, salejs, css, development_username, development_password
from flask.ext.cache import Cache
from functools import wraps

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
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)
    return render_template(
        'index.html',
        yesterday_date = yesterday_date,
        js = js,
        css = css,
        incomingdata = 'None'
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

        # Change any missing parameters to 0-length string
        for key in incomingdata:
            if incomingdata[key] == None:
                incomingdata[key] = ''

        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        yesterday_date = MonthCheck(yesterday_date)
        return render_template(
            'index.html',
            yesterday_date = yesterday_date,
            js = js,
            css = css,
            incomingdata = incomingdata
        )

        # '''
        # Has not loaded index.html or lens.js yet, so no HTML to append to
        # and no JS AJAX call to send response to. 
        # '''
        # yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        # yesterday_date = MonthCheck(yesterday_date)
        # return render_template(
        #     'index.html',
        #     yesterday_date = yesterday_date,
        #     js = js,
        #     css = css
        #     )

        # print 'response: '
        # print response
        # return response.template1

    if request.method == 'POST':
        print 'POST'
        incomingdata = request.get_json()

    name_address, amountlow, amounthigh, begindate, enddate = assignData(incomingdata)

    amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, amounthigh, begindate, enddate)

    response = query_db(name_address, amountlow, amounthigh, begindate, enddate)

    return response

#@cache.memoize(timeout=5000)
@app.route("/realestate/mapsearch", methods=['POST'])
def mapsearch():

    incomingdata = request.get_json()

    name_address, amountlow, amounthigh, begindate, enddate = assignData(incomingdata)

    bounds = incomingdata['bounds']
    mapbuttonstate = incomingdata['mapbuttonstate']
    page = incomingdata['page']
    totalpages = incomingdata['totalpages']
    page_direction = incomingdata['direction']

    amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, amounthigh, begindate, enddate)

    mapresponse = mapquery_db(name_address, amountlow, amounthigh, begindate, 
        enddate, bounds, mapbuttonstate, page_direction, page, totalpages)

    return mapresponse

#@cache.memoize(timeout=5000)
@app.route("/realestate/sale/<instrument_no>", methods=['GET', 'POST'])
def sale(instrument_no = None):

    search_term = instrument_no
    instrument_no = urllib.unquote(search_term).decode('utf8')
    # print 'instrument_no'
    # print instrument_no

    if request.method == 'GET':

        incomingdata = {}
        incomingdata['instrument_no'] = instrument_no

        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        yesterday_date = MonthCheck(yesterday_date)

        return render_template(
            'sale.html',
            yesterday_date = yesterday_date,
            salejs = salejs,
            css = css,
            incomingdata = incomingdata
        )

    if request.method == 'POST':

        '''
        Assign query string parameters to incomingdata dictionary.
        '''

        search_term = instrument_no
        instrument_no = urllib.unquote(search_term).decode('utf8')
        # print 'instrument_no'
        # print instrument_no

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                (Cleaned.instrument_no.ilike('%%%s%%' % instrument_no))
            ).all()
        # print 'q:'
        # print q

        location = ''
        
        for u in q: 
            u.amount = Currency(u.amount)
            u.document_date = RewriteDate(u.document_date)
            location = u.location
        # print 'q:'
        # print q

        features = loopThing(q)
        # print 'features:'
        # print features

        jsdata = {
            "type": "FeatureCollection", 
            "features": features
        }
        # print 'jsdata:'
        # print jsdata

        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        yesterday_date = MonthCheck(yesterday_date)

        print 'location:'
        print location

        address_number = re.match("[^ \-]*", location).group(0)

        print 'address_number:'
        print address_number

        street = re.match("\S+\s([^\,]*)", location).group(1)
        print 'street:'
        print street

        #unit = re.match(, location)
        print 'unit:'
        #print unit

        url_param = location
            
        template1 = render_template(
            'sale2.html',
            newrows = q,
            url_param =  url_param
        )

        session.close()

        return jsonify(
            template1 = template1,
            jsdata = jsdata
        )


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

    q_locations = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.location.ilike('%%%s%%' % search_term))
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
    for i, u in enumerate(q_locations):
        response.append(
            {
                "label": u.location,
                "category": "Locations"
            }
        )
        if i == 2:
            break

    for i, u in enumerate(q_buyers):
        response.append(
            {
                "label": u.buyers,
                "category": "Buyers"
            }
        )
        if i == 2:
            break

    for i, u in enumerate(q_sellers):
        response.append(
            {
                "label": u.sellers,
                "category": "Sellers"
            }
        )
        if i == 2:
            break

    return jsonify(
        response = response
        )

    
    '''
    search_term = request.args.get('q')
    print 'search_term:'
    print search_term

    decoded_names = urllib.unquote(search_term).decode('utf8')
    names = decoded_names.strip(" $!.,-")
    names = decoded_names.split(" ")
    shorties = []

    for x in range(0, len(names)):
        names[x] = names[x].strip(" $!.,-")
        if len(names[x]) <= 1:
            shorties.append(x)
    for i in reversed(shorties): #So deleting row won't affect index position
        del names[i]

    #Run names through location, then buyers, then sellers.
    
    location_conditions = []
    buyers_conditions = []
    sellers_conditions = []

    for name in names:
        location_conditions.append(
            (Cleaned.location.ilike('%%%s%%' % name))
        )
        buyers_conditions.append(
            (Cleaned.buyers.ilike('%%%s%%' % name))
        )
        sellers_conditions.append(
            (Cleaned.sellers.ilike('%%%s%%' % name))
        )
        #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    q_locations = session.query(
            Cleaned
        ).filter(
            and_(*location_conditions)
        ).all()

    q_buyers = session.query(
            Cleaned
        ).filter(
            and_(*buyers_conditions)
        ).all()

    q_sellers = session.query(
            Cleaned
        ).filter(
            and_(*sellers_conditions)
        ).all()

    response = []
    for u in q_locations:
        response.append(u.location)

    for u in q_buyers:
        response.append(u.buyers)

    for u in q_sellers:
        response.append(u.sellers)

    return jsonify(
        response = response
        )
    '''

#@cache.memoize(timeout=5000)
def query_db(name_address, amountlow, amounthigh, begindate, enddate):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    #conditions = conditionsAppend(names)

    q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate)

    qlength = len(q) # number of records
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

    q = mapQuery3(session, name_address, amountlow, amounthigh, begindate, enddate, recordsoffset)
    
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

    # template0 = render_template(
    #     'index.html',
    #     yesterday_date = yesterday_date,
    #     js = js,
    #     css = css,
    #     newjs = 'hi'
    # )
        
    template1 = render_template(
        'search.html',
        newrows = q,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )

    session.close()

    return jsonify(
        template1 = template1, 
        jsdata = jsdata
    )

#@cache.memoize(timeout=5000)
def mapquery_db(name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate, page_direction, page, totalpages):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]
    #conditions = conditionsAppend(names)
    if mapbuttonstate == True: #map filtering is on        
        q = mapQueryLength(session, name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate)
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == 'none':
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

        q = mapQuery1(session, name_address, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate, recordsoffset)

    if mapbuttonstate == False: # map filtering is off
        q = mapQuery2(session, name_address, amountlow, amounthigh, begindate, enddate)
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if page_direction == 'none':
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

    if qlength == 0:
        page = 0
    tabletemplate = render_template(
        'table.html',
        newrows = q,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )
    resultstemplate = render_template(
        'results.html',
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not
    )
    session.close()
    return jsonify(
        tabletemplate = tabletemplate,
        jsdata = jsdata,
        resultstemplate = resultstemplate
    )

def assignData(incomingdata):
    search_term = incomingdata['name_address']
    name_address = urllib.unquote(search_term).decode('utf8')
    # names = decoded_names.strip(" $!.,-")
    # names = decoded_names.split(" ")
    # shorties = []

    # for x in range(0, len(names)):
    #     names[x] = names[x].strip(" $!.,-")
    #     if len(names[x]) <= 1:
    #         shorties.append(x)
    # for i in reversed(shorties): #So deleting row won't affect index position
    #     del names[i]

    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']

    return (name_address, amountlow, amounthigh, begindate, enddate)

def conditionsAppend(names):
    conditions = []
    for name in names:
        conditions.append(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.location.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name)
        )
    return conditions

def mapQueryLength(session, name, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.location.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name)
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

def mapQuery1(session, name, amountlow, amounthigh, begindate, enddate, bounds, mapbuttonstate, recordsoffset):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.location.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name)
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

def mapQuery2(session, name, amountlow, amounthigh, begindate, enddate):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.location.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name)
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

def mapQuery3(session, name, amountlow, amounthigh, begindate, enddate, recordsoffset):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            (Cleaned.sellers.ilike('%%%s%%' % name)) |
            (Cleaned.buyers.ilike('%%%s%%' % name)) |
            (Cleaned.location.ilike('%%%s%%' % name)) |
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name)
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

    #conditions = conditionsAppend(names)

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
        newrows = q,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )
    resultstemplate = render_template(
        'results.html',
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not
    )
    session.close()
    return jsonify(
        tabletemplate = tabletemplate,
        jsdata = jsdata,
        resultstemplate = resultstemplate
    )

@app.route("/realestate/dashboard", methods=['GET'])
@requires_auth
def dashboard():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(Cleaned).filter(
            Cleaned.detail_publish == '0'
        ).all()
    num_results = len(q)
    return render_template('dashboard.html', num_results = num_results, q = q)

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
            "location": u.location, 
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

def currentsort2model(x):
    x = x[0] # Assuming one column with sorting
    sortfield = x[0]
    if sortfield == 0:
        sortfield = 'document_date'
    if sortfield == 1:
        sortfield = 'amount'
    if sortfield == 2:
        sortfield = 'location'
    if sortfield == 3:
        sortfield = 'sellers'
    if sortfield == 4:
        sortfield = 'buyers'
    if sortfield == 5:
        sortfield = 'instrument_no'
    sortorder = x[1]
    if sortorder == 0:
        sortorder = 'asc()'
    if sortorder == 1:
        sortorder = 'desc()'
    return sortfield, sortorder

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
    return value.strftime("%m-%d-%Y")

def Currency(value):
    return "${:,}".format(value)

def NumberWithCommas(value):
    return "{:,}".format(value)

def CheckEntry(amountlow, amounthigh, begindate, enddate):
    if amountlow == '':
        amountlow = 0
    if amounthigh == '':
        amounthigh = 9999999
    if begindate == '':
        begindate = "1900-01-01"
    if enddate == '':
        enddate = date.today()

    return (amountlow, amounthigh, begindate, enddate)

if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        use_reloader = True,
        debug = True
    )
