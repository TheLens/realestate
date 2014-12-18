import psycopg2
import psycopg2.extras
from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Cleaned
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
import pprint
import urllib
from app_config import server_connection, server_engine, js, css
from flask.ext.cache import Cache
import re
import math

Base = declarative_base()
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

conn = psycopg2.connect("%s" % (server_connection))
c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (server_engine))

pagelength = 10

#@cache.memoize(timeout=5000)
@app.route("/", methods=['GET'])
def base():
    with open('output.log', 'a') as f:
        f.write('\n\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\n')
        f.write('New search')
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)
    return render_template(
        'index.html',
        yesterday_date = yesterday_date,
        js = js,
        css = css
        )

@app.route("/dashboard", methods=['GET'])
def dashboard():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(Cleaned).filter(
            Cleaned.detail_publish == '0'
        ).all()
    num_results = len(q)
    return render_template('dashboard.html', num_results = num_results, q = q)

#@cache.memoize(timeout=5000)
@app.route("/search", methods=['POST'])
def search():
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
    incomingdata = request.get_json()
    name_address = incomingdata['name_address']
    decoded_names = urllib.unquote(name_address).decode('utf8')
    names = decoded_names.strip(" $!.,-")
    names = decoded_names.split(" ")
    shorties = []
    #print "name_address: " + name_address
    #print names
    for x in range(0, len(names)):
        names[x] = names[x].strip(" $!.,-")
        if len(names[x]) <= 1:
            shorties.append(x)
    for i in reversed(shorties): #So deleting row won't affect index position
        del names[i]
    #print names
    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']
    amountlow, amounthigh, begindate, enddate = CheckEntry(amountlow, 
        amounthigh, begindate, enddate)
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nSearch')
        f.write('\n')
    response = query_db(names, amountlow, amounthigh, begindate, enddate)
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nReturning')
        f.write('\n')
    return response

#@cache.memoize(timeout=5000)
def query_db(names, amountlow, amounthigh, begindate, enddate):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nQuerying DB')
    conditions = []
    for name in names:
        conditions.append((Cleaned.sellers.ilike('%%%s%%' % name)) | 
            (Cleaned.buyers.ilike('%%%s%%' % name)) | 
            (Cleaned.location.ilike('%%%s%%' % name)) | 
            (Cleaned.instrument_no.ilike('%%%s%%' % name)) |
            #(Cleaned.neighborhood.ilike('%%%s%%' % name)) |
            (Cleaned.zip_code == '%s' % name))
    q = session.query(Cleaned).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).filter(
            and_(*conditions)
        ).all()

    qlength = len(q) # number of records
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nNumber of records returned')
        f.write('\n')
        f.write(str(qlength))
    totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
    page = 1 # start on first page
    recordsoffset = (page - 1) * pagelength # Page 1 offsets 0

    q = session.query(Cleaned).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.document_date >= '%s' % (begindate)
        ).filter(
            Cleaned.document_date <= '%s' % (enddate)
        ).filter(
            Cleaned.amount >= '%s' % (amountlow)
        ).filter(
            Cleaned.amount <= '%s' % (amounthigh)
        ).filter(
            and_(*conditions)
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
    jsdata = {
        "type": "FeatureCollection", 
        "features": features
    }
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nSingle page of many that are returned')
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    yesterday_date = MonthCheck(yesterday_date)
    if qlength == 1:
        plural_or_not = "result"
    else:
        plural_or_not = "results"

    #print qlength
    if qlength == 0:
        page = 0
        #print page
    template1 = render_template(
        'search.html',
        newrows = q,
        qlength = NumberWithCommas(qlength),
        plural_or_not = plural_or_not,
        page = page,
        totalpages = totalpages,
        pagelength = pagelength
    )
    template2 = render_template(
        'foot.html',
        update_date = yesterday_date
    )
    session.close()
    return jsonify(
        template1 = template1, 
        template2 = template2,
        jsdata = jsdata
    )

#@cache.memoize(timeout=5000)
@app.route("/mapsearch", methods=['POST'])
def mapsearch():
    incomingdata = request.get_json()
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nSearching with map and table already present')
    name_address = incomingdata['name_address']
    decoded_names = urllib.unquote(name_address).decode('utf8')
    names = decoded_names.strip(" $!.,-")
    names = decoded_names.split(" ")
    shorties = []
    for x in range(0, len(names)):
        names[x] = names[x].strip(" $!.,-")
        if len(names[x]) <= 1:
            shorties.append(x)
    for i in reversed(shorties): #So deleting row won't affect index position
        del names[i]
    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']
    bounds = incomingdata['bounds']
    mapbuttonstate = incomingdata['mapbuttonstate']
    amountlow, amounthigh, begindate, enddate = CheckEntry(
        amountlow, amounthigh, begindate, enddate)
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nSearching')
    mapresponse = mapquery_db(names, amountlow, amounthigh, begindate, 
        enddate, bounds, mapbuttonstate)
    with open('output.log', 'a') as f:
        f.write('\n')
        f.write(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        f.write('\nReturning')
    return mapresponse

#@cache.memoize(timeout=5000)
def mapquery_db(names, amountlow, amounthigh, 
    begindate, enddate, bounds, mapbuttonstate):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]
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
    if mapbuttonstate == True: #map filtering is on
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).all()

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        page = 1
        recordsoffset = (page - 1) * pagelength 

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).order_by(
                desc(Cleaned.document_date)
            ).offset(
                '%d' % recordsoffset
            ).limit(
                '%d' % pagelength
            ).all()

    if mapbuttonstate == False: # map filtering is off
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
            ).all()

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        page = 1
        recordsoffset = (page - 1) * pagelength

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
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
                "instrument_no": u.instrument_no
            },
            "geometry": {
                "type": "Point",
                "coordinates": [u.longitude, u.latitude]
            }
        }
        features.append(features_dict)
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
        #print page
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

#@cache.memoize(timeout=5000)
@app.route("/pageforward", methods=['POST'])
def pageforward():
    incomingdata = request.get_json()
    name_address = incomingdata['name_address']
    decoded_names = urllib.unquote(name_address).decode('utf8')
    names = decoded_names.strip(" $!.,-")
    names = decoded_names.split(" ")
    shorties = []
    for x in range(0, len(names)):
        names[x] = names[x].strip(" $!.,-")
        if len(names[x]) <= 1:
            shorties.append(x)
    for i in reversed(shorties): #So deleting row won't affect index position
        del names[i]
    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']
    bounds = incomingdata['bounds']
    mapbuttonstate = incomingdata['mapbuttonstate']
    page = incomingdata['page']
    totalpages = incomingdata['totalpages']
    amountlow, amounthigh, begindate, enddate = CheckEntry(
        amountlow, amounthigh, begindate, enddate)
    return forward_query(names, amountlow, amounthigh, begindate, 
        enddate, bounds, mapbuttonstate, page, totalpages)

#@cache.memoize(timeout=5000)
def forward_query(names, amountlow, amounthigh, 
    begindate, enddate, bounds, mapbuttonstate, page, totalpages):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]

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
    if mapbuttonstate == True: #map filtering is on
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).all()
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        page = int(page) + 1

        if qlength == 0:
            page = 0

        if page == 0:
            recordsoffset = 0
        else:
            recordsoffset = (page - 1) * pagelength

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).order_by(
                desc(Cleaned.document_date)
            ).offset(
                '%d' % recordsoffset
            ).limit(
                '%d' % pagelength
            ).all()

    if mapbuttonstate == False: # map filtering is off
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
            ).all()

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        page = int(page) + 1
        if qlength == 0:
            page = 0

        if page == 0:
            recordsoffset = 0
        else:
            recordsoffset = (page - 1) * pagelength

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
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
                "instrument_no": u.instrument_no
            },
            "geometry": {
                "type": "Point",
                "coordinates": [u.longitude, u.latitude]
            }
        }
        features.append(features_dict)
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

#@cache.memoize(timeout=5000)
@app.route("/pageback", methods=['POST'])
def pageback():
    incomingdata = request.get_json()
    name_address = incomingdata['name_address']
    decoded_names = urllib.unquote(name_address).decode('utf8')
    names = decoded_names.strip(" $!.,-")
    names = decoded_names.split(" ")
    shorties = []
    for x in range(0, len(names)):
        names[x] = names[x].strip(" $!.,-")
        if len(names[x]) <= 1:
            shorties.append(x)
    for i in reversed(shorties): #So deleting row won't affect index position
        del names[i]
    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']
    bounds = incomingdata['bounds']
    mapbuttonstate = incomingdata['mapbuttonstate']
    page = incomingdata['page']
    totalpages = incomingdata['totalpages']
    amountlow, amounthigh, begindate, enddate = CheckEntry(
        amountlow, amounthigh, begindate, enddate)
    return back_query(names, amountlow, amounthigh, begindate, 
        enddate, bounds, mapbuttonstate, page, totalpages)

#@cache.memoize(timeout=5000)
def back_query(names, amountlow, amounthigh, 
    begindate, enddate, bounds, mapbuttonstate, page, totalpages):

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    bounds = [
        bounds['_northEast']['lat'], 
        bounds['_northEast']['lng'], 
        bounds['_southWest']['lat'], 
        bounds['_southWest']['lng']
    ]
    
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
    if mapbuttonstate == True: #map filtering is on
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).all()
        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages

        if qlength == 0:
            page = 0

        if page == 0:
            recordsoffset = 0
        else:
            page = int(page) - 1
            recordsoffset = (page - 1) * pagelength

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
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
            ).filter(
                and_(*conditions)
            ).order_by(
                desc(Cleaned.document_date)
            ).offset(
                '%d' % recordsoffset
            ).limit(
                '%d' % pagelength
            ).all()

    if mapbuttonstate == False: # map filtering is off
        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
            ).all()

        qlength = len(q) # number of records
        totalpages = int(math.ceil(float(qlength)/float(pagelength))) # total number of pages
        if qlength == 0:
            page = 0
        if page == 0:
            recordsoffset = 0
        else:
            page = int(page) - 1
            recordsoffset = (page - 1) * pagelength

        q = session.query(
                Cleaned
            ).filter(
                Cleaned.detail_publish == '1'
            ).filter(
                Cleaned.document_date >= '%s' % (begindate)
            ).filter(
                Cleaned.document_date <= '%s' % (enddate)
            ).filter(
                Cleaned.amount >= '%s' % (amountlow)
            ).filter(
                Cleaned.amount <= '%s' % (amounthigh)
            ).filter(
                and_(*conditions)
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
                "instrument_no": u.instrument_no
            },
            "geometry": {
                "type": "Point",
                "coordinates": [u.longitude, u.latitude]
            }
        }
        features.append(features_dict)
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
    return amountlow, amounthigh, begindate, enddate

if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        use_reloader = True,
        debug = True,
    )
