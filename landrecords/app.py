# -*- coding: utf-8 -*-

from __future__ import absolute_import

import psycopg2
import psycopg2.extras
import pprint
import urllib
import math
import logging

from flask.ext.cache import Cache
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    Response
)
from sqlalchemy import (
    create_engine,
    desc,
    insert,
    update,
    func
)
from functools import wraps
from fabric.api import local
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import (
    datetime
)
from landrecords import db, clean
from landrecords.settings import dev_config, universal_config

Base = declarative_base()
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

conn = psycopg2.connect("%s" % (dev_config.SERVER_CONNECTION))
c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (dev_config.SERVER_ENGINE))

PAGE_LENGTH = 10

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
fh = logging.FileHandler('logs/app.log', 'w')
# fh.filemode('w')
fh.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('''
    %(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(lineno)d -
     %(message)s''')
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)


def check_auth(username, password):
    return (username == universal_config.DASHBOARD_USERNAME
            and password == universal_config.DASHBOARD_PASSWORD)


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
                           css=dev_config.CSS,
                           js=dev_config.JS,
                           indexjs=dev_config.INDEX_JS), 404


@app.route("%s/webhook" % (dev_config.APP_ROUTING), methods=['POST'])
def webhook():
    logger.info('/webhook')

    data = request.get_json()

    git_pull(data)

    files_list = gather_updated_files(data)

    for f in files_list:
        aws_string = form_aws_string(f)

        if aws_string is None:
            continue

        logger.debug(aws_string)

        local(aws_string)

    logger.info('Done')
    return "None"


def git_pull(data):
    try:
        logger.info('try')
        branch = data['ref']
        logger.debug(branch)
        if branch != 'refs/heads/master':
            logger.info('Not master branch')
            return 'None'
    except:
        logger.info('except')
        return "None"

    local('git pull origin master')


def form_aws_string(f):
    # Ex. f = 'scripts/templates/search.html'
    logger.debug(f)

    file_path = f.split('static/')[-1]  # Ex. 'js/lens.js'

    aws_string = 'aws s3 cp {0}{1} {2}/{3} --acl public-read'.format(
        dev_config.PROJECT_DIR, f, dev_config.S3_DIR, file_path)

    return aws_string


def gather_updated_files(data):
    try:
        logger.info('try')
        branch = data['ref']
        logger.debug(branch)
        if branch != 'refs/heads/master':
            logger.info('Not master branch')
            return 'None'
    except:
        logger.info('except')
        return "None"

    github_branch = data['ref'].split('/')[-1]
    logger.debug(github_branch)

    # Ex: ['scripts/templates/search.html']
    added_files_list = data['commits'][0]['added']
    modified_files_list = data['commits'][0]['modified']

    files_list = []

    for f in added_files_list:
        files_list.append(f)

    for f in modified_files_list:
        files_list.append(f)

    for i, f in enumerate(files_list):
        if f.split('/')[1] != 'static':
            del files_list[i]

    return files_list


@cache.memoize(timeout=5000)
@app.route("%s/" % (dev_config.APP_ROUTING), methods=['GET'])
def base():
    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    qd = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).order_by(
        desc(db.Cleaned.document_recorded)
    ).limit(1).all()

    for u in qd:
        yesterday_date = clean.ymd_to_full_date(
            u.document_recorded, no_day=True)

    q = session.query(db.Neighborhood.gnocdc_lab).all()

    neighborhoods = []
    for hood in q:
        neighborhoods.append((hood.gnocdc_lab).title().replace('Mcd', 'McD'))

    neighborhoods.sort()

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119,
                 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128,
                 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143,
                 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153,
                 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162,
                 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174,
                 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183,
                 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    return render_template(
        'index.html',
        yesterday_date=yesterday_date,
        js=dev_config.JS,
        indexjs=dev_config.INDEX_JS,
        searchAreajs=dev_config.SEARCH_AREA_JS,
        js_app_routing=dev_config.JS_APP_ROUTING,
        css=dev_config.CSS,
        neighborhoods=neighborhoods,
        zip_codes=zip_codes
    )


@cache.memoize(timeout=5000)
@app.route("%s/search/" % (dev_config.APP_ROUTING), methods=['GET', 'POST'])
@app.route("%s/search" % (dev_config.APP_ROUTING), methods=['GET', 'POST'])
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
            if incomingdata[key] is None:
                incomingdata[key] = ''

        name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code = assign_data(incomingdata)

        amountlow, amounthigh, begindate, enddate = check_entry(
            amountlow, amounthigh, begindate, enddate)

        response = query_db(name_address, amountlow, amounthigh, begindate,
                            enddate, neighborhood, zip_code)

        return response

    if request.method == 'POST':
        # Formerly /realestate/mapsearch
        incomingdata = request.get_json()

        name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code = assign_data(incomingdata)

        bounds = incomingdata['bounds']
        mapbuttonstate = incomingdata['mapbuttonstate']
        page = incomingdata['page']
        totalpages = incomingdata['totalpages']
        page_direction = incomingdata['direction']

        amountlow, amounthigh, begindate, enddate = check_entry(
            amountlow, amounthigh, begindate, enddate)

        # If a geo query (search near me)
        if 'latitude' in incomingdata and 'longitude' in incomingdata:
            latitude = incomingdata['latitude']
            longitude = incomingdata['longitude']
            response = geoquery_db(
                name_address, amountlow, amounthigh, begindate, enddate,
                neighborhood, zip_code, latitude, longitude, mapbuttonstate)
        else:
            response = mapquery_db(
                name_address, amountlow, amounthigh,
                begindate, enddate, neighborhood, zip_code, bounds,
                mapbuttonstate, page_direction, page, totalpages)

        return response


@cache.memoize(timeout=5000)
@app.route("%s/dashboard/" % (dev_config.APP_ROUTING), methods=['GET', 'POST'])
@requires_auth
def dashboard():
    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    if request.method == 'GET':
        q = session.query(
            db.Cleaned
        ).filter(
            (db.Cleaned.detail_publish == '0') |
            (db.Cleaned.location_publish == '0')
        ).order_by(
            db.Cleaned.document_recorded.desc()
        ).all()

        num_results = len(q)

        for u in q:
            u.amount = clean.get_number_with_currency_sign(u.amount)
            u.document_date = clean.ymd_to_full_date(u.document_date)
            u.document_recorded = clean.ymd_to_full_date(u.document_recorded)
            u.detail_publish = clean.binary_to_english(u.detail_publish)
            u.location_publish = clean.binary_to_english(u.location_publish)

        rows = []
        for row in q:
            row_dict = {}
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
            js=dev_config.JS,
            dashboardjs=dev_config.DASHBOARD_JS,
            neighborhoodstopo=dev_config.NEIGHBORHOODS_TOPO,
            squarestopo=dev_config.SQUARES_TOPO,
            css=dev_config.CSS,
            num_results=num_results,
            js_app_routing=dev_config.JS_APP_ROUTING,
            newrows=q,
            jsrows=rows,
            number_of_indexes=len(q)
        )

    if request.method == 'POST':
        # User submitted a change through dashboard
        incomingdata = request.get_json()

        for key in incomingdata:
            incomingdata[key] = incomingdata[key].strip()

        # Set fixed to false
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
            db.Dashboard.instrument_no
        ).filter(
            db.Dashboard.instrument_no == '%s' % (
                incomingdata['instrument_no'])
        ).all()

        input_length = len(q)

        if input_length == 0:
            print 'Adding sale in dashboard table'
            # This sale has not been entered into dashboard table yet
            i = insert(db.Dashboard)
            i = i.values(incomingdata)
            session.execute(i)
            session.commit()
        else:
            print 'Updating sale in dashboard table'
            # This sale has already been entered into dashboard table
            u = update(db.Dashboard)
            u = u.values(incomingdata)
            u = u.where(db.Dashboard.instrument_no == '%s' % (
                incomingdata['instrument_no']))

            session.execute(u)
            session.commit()

        # Update changes in Cleaned table
        update_cleaned()

        return 'hi'


def update_cleaned():
    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    q = session.query(
        db.Dashboard
    ).filter(
        db.Dashboard.fixed is False
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
        print 'Updating Cleaned sale based on Dashboard entry'
        # This sale has already been entered into dashboard table
        u = update(db.Cleaned)
        u = u.values(row)
        u = u.where(db.Cleaned.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        session.commit()

        print 'Changing Dashboard entry fixed field to true'
        # This sale has already been entered into dashboard table
        u = update(db.Dashboard)
        u = u.values({"fixed": True})
        u = u.where(db.Dashboard.instrument_no == '%s' % row['instrument_no'])
        session.execute(u)
        session.commit()


@cache.memoize(timeout=5000)
@app.route("%s/sale/<instrument_no>" % (dev_config.APP_ROUTING),
           methods=['GET'])
def sale(instrument_no=None):
    search_term = instrument_no
    instrument_no = urllib.unquote(search_term).decode('utf8')

    if request.method == 'GET':

        '''
        Assign query string parameters to incomingdata dictionary.
        '''

        Base.metadata.create_all(engine)
        sn = sessionmaker(bind=engine)
        session = sn()

        qd = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).order_by(
            desc(db.Cleaned.document_recorded)
        ).limit(1).all()

        for u in qd:
            yesterday_date = clean.ymd_to_full_date(
                u.document_recorded, no_day=True)

        q = session.query(
            db.Cleaned
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.instrument_no == '%s' % (instrument_no)
        ).all()

        assessor_publish = ''

        for u in q:
            u.amount = clean.get_number_with_currency_sign(u.amount)
            u.document_date = clean.ymd_to_full_date(
                u.document_date, no_day=True)
            address = u.address
            location_info = u.location_info
            assessor_publish = u.assessor_publish

        features = loop_thing(q)

        jsdata = {
            "type": "FeatureCollection",
            "features": features
        }

        # yesterday_date = (
        #     datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
        # yesterday_date = convert_month_to_ap_style(yesterday_date)

        if (assessor_publish == '0' or
            assessor_publish is None or
            assessor_publish == ''):
            assessor = """
                Could not find this property on the Orleans Parish
                Assessor's Office site. <a href='http://www.qpublic
                .net/la/orleans/search1.html' target='_blank'>"
                Search based on other criteria.</a>"""
        else:
            url_param = check_assessor_urls.formAssessorURL(address, location_info)
            assessor_url = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=%s" % (url_param)
            assessor = "<a href='%s' target='_blank'>Read more about this property on the Assessor's Office's website.</a>" % (assessor_url)

        template1 = ''

        if len(q) == 0:
            template1 = page_not_found()
        else:
            template1 = render_template(
                'sale.html',
                yesterday_date=yesterday_date,
                js=dev_config.JS,
                salejs=dev_config.SALE_JS,
                css=dev_config.CSS,
                newrows=q,
                assessor=assessor,
                jsdata=jsdata
            )

        session.close()

        return template1


@cache.memoize(timeout=5000)
@app.route("%s/input" % (dev_config.APP_ROUTING), methods=['GET', 'POST'])
def input():
    term = request.args.get('q')

    search_term = urllib.unquote(term).decode('utf8')

    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    q_neighborhoods = session.query(
        db.Cleaned.neighborhood
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % search_term)
    ).distinct().limit(3).all()

    q_zip = session.query(
        db.Cleaned.zip_code
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % search_term)
    ).distinct().limit(3).all()

    q_locations = session.query(
        db.Cleaned.detail_publish,
        db.Cleaned.address
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        db.Cleaned.address.ilike('%%%s%%' % search_term)
    ).limit(3).all()

    q_buyers = session.query(
        db.Cleaned.detail_publish,
        db.Cleaned.buyers
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        db.Cleaned.buyers.ilike('%%%s%%' % search_term)
    ).limit(3).all()

    q_sellers = session.query(
        db.Cleaned.detail_publish,
        db.Cleaned.sellers
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        db.Cleaned.sellers.ilike('%%%s%%' % search_term)
    ).limit(3).all()

    response = []

    for i, u in enumerate(q_neighborhoods):
        print u.neighborhood
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
        response=response
    )


@cache.memoize(timeout=5000)
def query_db(name_address, amountlow, amounthigh, begindate, enddate,
             neighborhood, zip_code):

    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    qd = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).order_by(
        desc(db.Cleaned.document_recorded)
    ).limit(1).all()

    for u in qd:
        yesterday_date = clean.ymd_to_full_date(
            u.document_recorded, no_day=True)

    q = session.query(db.Neighborhood.gnocdc_lab).all()

    neighborhoods = []
    for hood in q:
        neighborhoods.append((hood.gnocdc_lab).title().replace('Mcd', 'McD'))

    neighborhoods.sort()

    q = map_query2(
        session, name_address, amountlow, amounthigh, begindate, enddate,
        neighborhood, zip_code)

    qlength = len(q)  # number of records
    # total number of pages:
    totalpages = int(math.ceil(float(qlength) / float(PAGE_LENGTH)))
    page = 1  # start on first page
    recordsoffset = (page - 1) * PAGE_LENGTH  # Page 1 offsets 0

    q = map_query3(session, name_address, amountlow, amounthigh, begindate,
                   enddate, neighborhood, zip_code, recordsoffset, PAGE_LENGTH)

    for u in q:
        u.amount = clean.get_number_with_currency_sign(u.amount)
        u.document_date = clean.ymd_to_full_date(u.document_date, no_day=True)

    features = loop_thing(q)
    newrows = q

    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }

    # yesterday_date = (
    #     datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    # yesterday_date = convert_month_to_ap_style(yesterday_date)

    show_results = 'none'
    if qlength == 0:
        page = 0
        show_results = 'block'

    amountlow, amounthigh, begindate, enddate = revert_entries(
        amountlow, amounthigh, begindate, enddate)

    parameters = {}
    parameters['name_address'] = name_address
    parameters['amountlow'] = amountlow
    parameters['amounthigh'] = amounthigh
    parameters['begindate'] = begindate
    parameters['enddate'] = enddate
    parameters['neighborhood'] = neighborhood
    parameters['zip_code'] = zip_code

    zip_codes = [70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119,
                 70121, 70122, 70123, 70124, 70125, 70126, 70127, 70128,
                 70129, 70130, 70131, 70139, 70140, 70141, 70142, 70143,
                 70145, 70146, 70148, 70149, 70150, 70151, 70152, 70153,
                 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162,
                 70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174,
                 70175, 70176, 70177, 70178, 70179, 70181, 70182, 70183,
                 70184, 70185, 70186, 70187, 70189, 70190, 70195]

    map_button = False
    results_language = construct_results_language(
        name_address, amountlow, amounthigh, begindate, enddate, neighborhood,
        zip_code, qlength, map_button)

    print '564page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', PAGE_LENGTH

    template1 = render_template(
        'search.html',
        yesterday_date=yesterday_date,
        js=dev_config.JS,
        searchjs=dev_config.SEARCH_JS,
        searchAreajs=dev_config.SEARCH_AREA_JS,
        mapjs=dev_config.MAP_JS,
        css=dev_config.CSS,
        js_app_routing=dev_config.JS_APP_ROUTING,
        newrows=newrows,
        jsdata=jsdata,
        show_results=show_results,
        # qlength = get_number_with_commas(qlength),
        # plural_or_not = plural_or_not,
        results_language=results_language,
        page=page,
        totalpages=totalpages,
        pagelength=PAGE_LENGTH,
        parameters=parameters,
        neighborhoods=neighborhoods,
        zip_codes=zip_codes
    )

    session.close()

    return template1


def construct_results_language(name_address, amountlow, amounthigh, begindate,
                               enddate, neighborhood, zip_code, qlength,
                               map_button):
    '''
    In goes filter values, out of this messy function comes a coherent
    sentence such as, "10 results found in the Mid-City neighborhood."
    '''

    if qlength == 1:
        plural_or_not = "sale"
    else:
        plural_or_not = "sales"

    final_sentence = str(clean.get_number_with_commas(qlength)) + ' ' + str(plural_or_not) + ' found'  # 10 records found
    if name_address == '' and amountlow == '' and amounthigh == '' and begindate == '' and enddate == '' and neighborhood == '' and zip_code == '':
        if map_button is True:
            # 10 records found.
            final_sentence = final_sentence + ' in the current map view.'
        else:
            final_sentence = final_sentence + '.'#10 records found.
    else:
        if name_address != '':
            if len(name_address.split()) > 1:
                # 10 records found for 'keyword'
                final_sentence = final_sentence + ' for key phrase "' + name_address + '"'
            else:
                # 10 records found for 'keyword'
                final_sentence = final_sentence + ' for keyword "' + name_address + '"'

        if neighborhood != '':
            if zip_code != '':
                # 10 records found for 'keyword' in Mid-City and 70119
                final_sentence = final_sentence + " in the " + neighborhood + " neighborhood and " + zip_code
            else:
                # 10 records found for 'keyword' in Mid-City
                final_sentence = final_sentence + " in the " + neighborhood + " neighborhood"
        elif zip_code != '':
            # 10 records found for 'keyword' in 70119
            final_sentence = final_sentence + " in ZIP code " + zip_code

        if amountlow != '':
            if amounthigh != '':
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is between $10 and $20
                final_sentence = final_sentence + " where the price was between " + get_number_with_currency_sign(amountlow) + " and " + get_number_with_currency_sign(amounthigh)
            else:
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is greater than $10
                final_sentence = final_sentence + " where the price was greater than " + get_number_with_currency_sign(amountlow)
        elif amounthigh != '':
            # 10 records found for 'keyword' in Mid-City, where the amount is
            # less than $20
            final_sentence = final_sentence + " where the price was less than " + get_number_with_currency_sign(amounthigh)

        if begindate != '':
            if enddate != '':
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is between $10 and $20, between Feb. 10, 2014, and Feb. 12,
                # 2014
                final_sentence = final_sentence + " between " + ymd_to_full_date(begindate) + ", and " + ymd_to_full_date(enddate)
            else:
                # 10 records found for 'keyword' in Mid-City, where the amount
                # is greater than $10, after Feb. 10, 2014.
                final_sentence = final_sentence + " after " + ymd_to_full_date(begindate)
        elif enddate != '':
            # 10 records found for 'keyword' in Mid-City, where the amount is
            # less than $20, before Feb. 20, 2014.
            final_sentence = final_sentence + " before " + ymd_to_full_date(enddate)

        if map_button is True:
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
def mapquery_db(name_address, amountlow, amounthigh, begindate, enddate,
                neighborhood, zip_code, bounds, mapbuttonstate,
                page_direction, page, totalpages):

    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()
    bounds = [
        bounds['_northEast']['lat'],
        bounds['_northEast']['lng'],
        bounds['_southWest']['lat'],
        bounds['_southWest']['lng']
    ]

    qd = session.query(db.Cleaned).filter(db.Cleaned.detail_publish == '1').order_by(desc(db.Cleaned.document_recorded)).limit(1).all()

    for u in qd:
        yesterday_date = ymd_to_full_date(u.document_recorded, no_day=True)

    if mapbuttonstate is True:  # map filtering is on
        q = map_query_length(session, name_address, amountlow, amounthigh,
            begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate)
        qlength = len(q)  # number of records
        # total number of pages:
        totalpages = int(math.ceil(float(qlength) / float(PAGE_LENGTH)))

        if page_direction is None:
            page = 1
            recordsoffset = (page - 1) * PAGE_LENGTH
        elif page_direction == 'back' or page_direction == 'forward':
            if page_direction == 'forward':
                print '\n782LOOK'
                print '783page:', page
                page = int(page) + 1

            if qlength == 0:
                page = 0

            if page == 0:
                recordsoffset = 0
            else:
                if page_direction == 'back':
                    page = int(page) - 1
                recordsoffset = (page - 1) * PAGE_LENGTH

        q = map_query1(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code, bounds, mapbuttonstate, recordsoffset)

    if mapbuttonstate is False:  # map filtering is off
        q = map_query2(session, name_address, amountlow, amounthigh, begindate, enddate, neighborhood, zip_code)
        qlength = len(q)  # number of records
        # total number of pages:
        totalpages = int(math.ceil(float(qlength) / float(PAGE_LENGTH)))

        if page_direction is None:
            page = 1
            recordsoffset = (page - 1) * PAGE_LENGTH
        elif page_direction == 'back' or page_direction == 'forward':
            if page_direction == 'forward':
                print '\n808LOOK'
                print '809page:', page
                page = int(page) + 1

            if qlength == 0:
                page = 0

            if page == 0:
                recordsoffset = 0
            else:
                if page_direction == 'back':
                    page = int(page) - 1
                recordsoffset = (page - 1) * PAGE_LENGTH

        q = map_query3(
            session, name_address, amountlow, amounthigh, begindate,
            enddate, neighborhood, zip_code, recordsoffset, PAGE_LENGTH)

    for u in q:
        u.amount = clean.get_number_with_currency_sign(u.amount)
        u.document_date = ymd_to_full_date(u.document_date, no_day=True)

    features = loop_thing(q)

    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }

    # yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    # yesterday_date = convert_month_to_ap_style(yesterday_date)

    show_results = 'none'
    if qlength == 0:
        page = 0
        show_results = 'block'

    tabletemplate = render_template(
        'table.html',
        newrows=q
    )

    session.close()

    amountlow, amounthigh, begindate, enddate = revert_entries(
        amountlow, amounthigh, begindate, enddate)

    results_language = construct_results_language(
        name_address, amountlow, amounthigh, begindate, enddate,
        neighborhood, zip_code, qlength, mapbuttonstate)

    print '754page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', PAGE_LENGTH

    return jsonify(
        tabletemplate=tabletemplate,
        yesterday_date=yesterday_date,
        jsdata=jsdata,
        # qlength = get_number_with_commas(qlength),
        results_language=results_language,
        show_results=show_results,
        # plural_or_not = plural_or_not,
        page=page,
        totalpages=totalpages,
        pagelength=PAGE_LENGTH
    )


@cache.memoize(timeout=5000)
def geoquery_db(name, amountlow, amounthigh, begindate, enddate, neighborhood,
                zip_code, latitude, longitude, mapbuttonstate):
    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    qd = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).order_by(
        desc(db.Cleaned.document_recorded)
    ).limit(1).all()

    for u in qd:
        yesterday_date = clean.ymd_to_full_date(u.document_recorded, no_day=True)

    q = map_query2(
        session, name, amountlow, amounthigh, begindate,
        enddate, neighborhood, zip_code)

    qlength = len(q)  # number of records
    # total number of pages:
    totalpages = int(math.ceil(float(qlength) / float(PAGE_LENGTH)))
    page = 1  # start on first page
    recordsoffset = (page - 1) * PAGE_LENGTH  # Page 1 offsets 0

    # Near me query
    q = session.query(
        db.Cleaned
    ).filter(
        func.ST_Distance_Sphere(
            db.Cleaned.geom, func.ST_MakePoint(
                '%f' % longitude, '%f' % latitude)
        ) <= 1 * 1609.34
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        (db.Cleaned.sellers.ilike('%%%s%%' % name)) |
        (db.Cleaned.buyers.ilike('%%%s%%' % name)) |
        (db.Cleaned.address.ilike('%%%s%%' % name)) |
        (db.Cleaned.instrument_no.ilike('%%%s%%' % name))
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % zip_code)
    ).filter(
        db.Cleaned.document_date >= '%s' % (begindate)
    ).filter(
        db.Cleaned.document_date <= '%s' % (enddate)
    ).filter(
        db.Cleaned.amount >= '%s' % (amountlow)
    ).filter(
        db.Cleaned.amount <= '%s' % (amounthigh)
    ).order_by(
        desc(db.Cleaned.document_date)
    ).offset(
        '%d' % recordsoffset
    ).limit(
        '%d' % PAGE_LENGTH
    ).all()

    for u in q:
        u.amount = clean.get_number_with_currency_sign(u.amount)
        u.document_date = clean.ymd_to_full_date(u.document_date, no_day=True)

    features = loop_thing(q)

    jsdata = {
        "type": "FeatureCollection",
        "features": features
    }

    # yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%b %-d, %Y')
    # yesterday_date = convert_month_to_ap_style(yesterday_date)

    if qlength == 0:
        page = 0
    tabletemplate = render_template(
        'table.html',
        newrows=q
    )

    amountlow, amounthigh, begindate, enddate = revert_entries(
        amountlow, amounthigh, begindate, enddate)

    session.close()

    results_language = construct_results_language(
        name, amountlow, amounthigh, begindate, enddate, neighborhood,
        zip_code, qlength, mapbuttonstate)

    print '848page:', page
    print 'totalpages:', totalpages
    print 'pagelength:', PAGE_LENGTH

    return jsonify(
        tabletemplate=tabletemplate,
        yesterday_date=yesterday_date,
        jsdata=jsdata,
        results_language=results_language,
        # qlength = get_number_with_commas(qlength),
        # plural_or_not = plural_or_not,
        page=page,
        totalpages=totalpages,
        pagelength=PAGE_LENGTH
    )


def assign_data(incomingdata):
    search_term = incomingdata['name_address']
    name_address = urllib.unquote(search_term).decode('utf8')

    amountlow = incomingdata['amountlow']
    amounthigh = incomingdata['amounthigh']
    begindate = incomingdata['begindate']
    enddate = incomingdata['enddate']

    neighborhood = incomingdata['neighborhood']
    neighborhood = urllib.unquote(neighborhood).decode('utf8')

    zip_code = incomingdata['zip_code']

    return (
        name_address, amountlow, amounthigh, begindate, enddate,
        neighborhood, zip_code)


def map_query_length(session, name, amountlow, amounthigh, begindate, enddate,
                     neighborhood, zip_code, bounds, mapbuttonstate):
    q = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        (db.Cleaned.sellers.ilike('%%%s%%' % name)) |
        (db.Cleaned.buyers.ilike('%%%s%%' % name)) |
        (db.Cleaned.address.ilike('%%%s%%' % name)) |
        (db.Cleaned.instrument_no.ilike('%%%s%%' % name))
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % zip_code)
    ).filter(
        db.Cleaned.document_date >= '%s' % (begindate)
    ).filter(
        db.Cleaned.document_date <= '%s' % (enddate)
    ).filter(
        db.Cleaned.amount >= '%s' % (amountlow)
    ).filter(
        db.Cleaned.amount <= '%s' % (amounthigh)
    ).filter(
        (db.Cleaned.latitude <= bounds[0]) &
        (db.Cleaned.latitude >= bounds[2]) &
        (db.Cleaned.longitude <= bounds[1]) &
        (db.Cleaned.longitude >= bounds[3])
    ).all()
    return q


# For when map filtering is turned on
def map_query1(session, name, amountlow, amounthigh, begindate, enddate,
               neighborhood, zip_code, bounds, mapbuttonstate, recordsoffset):
    q = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        (db.Cleaned.sellers.ilike('%%%s%%' % name)) |
        (db.Cleaned.buyers.ilike('%%%s%%' % name)) |
        (db.Cleaned.address.ilike('%%%s%%' % name)) |
        (db.Cleaned.instrument_no.ilike('%%%s%%' % name))
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % zip_code)
    ).filter(
        db.Cleaned.document_date >= '%s' % (begindate)
    ).filter(
        db.Cleaned.document_date <= '%s' % (enddate)
    ).filter(
        db.Cleaned.amount >= '%s' % (amountlow)
    ).filter(
        db.Cleaned.amount <= '%s' % (amounthigh)
    ).filter(
        (db.Cleaned.latitude <= bounds[0]) &
        (db.Cleaned.latitude >= bounds[2]) &
        (db.Cleaned.longitude <= bounds[1]) &
        (db.Cleaned.longitude >= bounds[3])
    ).order_by(
        desc(db.Cleaned.document_date)
    ).offset(
        '%d' % recordsoffset
    ).limit(
        '%d' % PAGE_LENGTH
    ).all()

    return q


def map_query2(session, name, amountlow, amounthigh, begindate, enddate,
               neighborhood, zip_code):
    q = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        (db.Cleaned.sellers.ilike('%%%s%%' % name)) |
        (db.Cleaned.buyers.ilike('%%%s%%' % name)) |
        (db.Cleaned.address.ilike('%%%s%%' % name)) |
        (db.Cleaned.instrument_no.ilike('%%%s%%' % name))
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % zip_code)
    ).filter(
        db.Cleaned.document_date >= '%s' % (begindate)
    ).filter(
        db.Cleaned.document_date <= '%s' % (enddate)
    ).filter(
        db.Cleaned.amount >= '%s' % (amountlow)
    ).filter(
        db.Cleaned.amount <= '%s' % (amounthigh)
    ).all()

    return q


def map_query3(session, name, amountlow, amounthigh, begindate, enddate,
               neighborhood, zip_code, recordsoffset, pagelength):
    q = session.query(
        db.Cleaned
    ).filter(
        db.Cleaned.detail_publish == '1'
    ).filter(
        (db.Cleaned.sellers.ilike('%%%s%%' % name)) |
        (db.Cleaned.buyers.ilike('%%%s%%' % name)) |
        (db.Cleaned.address.ilike('%%%s%%' % name)) |
        (db.Cleaned.instrument_no.ilike('%%%s%%' % name))
    ).filter(
        db.Cleaned.neighborhood.ilike('%%%s%%' % neighborhood)
    ).filter(
        db.Cleaned.zip_code.ilike('%%%s%%' % zip_code)
    ).filter(
        db.Cleaned.document_date >= '%s' % (begindate)
    ).filter(
        db.Cleaned.document_date <= '%s' % (enddate)
    ).filter(
        db.Cleaned.amount >= '%s' % (amountlow)
    ).filter(
        db.Cleaned.amount <= '%s' % (amounthigh)
    ).order_by(
        desc(db.Cleaned.document_date)
    ).offset(
        '%d' % recordsoffset
    ).limit(
        '%d' % pagelength
    ).all()

    return q


def loop_thing(q):
    features = []
    features_dict = {}
    for u in q:
        if u.location_publish == "0":
            u.document_date = u.document_date + "*"
            continue
        if u.permanent_flag is False:
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
                "instrument_no": u.instrument_no
            },
            "geometry": {
                "type": "Point",
                "coordinates": [u.longitude, u.latitude]
            }
        }
        features.append(features_dict)

    return features


def check_entry(amountlow, amounthigh, begindate, enddate):
    if amountlow == '':
        amountlow = 0
    if amounthigh == '':
        amounthigh = 9999999999999
    if begindate == '':
        begindate = "1900-01-01"
    if enddate == '':
        enddate = (datetime.today()).strftime('%Y-%m-%d')

    return (amountlow, amounthigh, begindate, enddate)


def revert_entries(amountlow, amounthigh, begindate, enddate):
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
        use_reloader=dev_config.RELOADER,
        debug=dev_config.DEBUG
    )
