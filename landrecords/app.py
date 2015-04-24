# -*- coding: utf-8 -*-

'''docstring'''

# from __future__ import absolute_import

import urllib
# from flask.ext.cache import Cache
from flask import (
    Flask,
    # render_template,
    request,
    Response
)
from functools import wraps

from landrecords.config import Config
from landrecords import log
from landrecords.models import Models
from landrecords.views import Views

app = Flask(__name__)

# cache = Cache(app, Config().={'CACHE_TYPE': 'simple'})


# @cache.memoize(timeout=5000)
@app.route("%s/" % (Config().APP_ROUTING), methods=['GET'])
def home():
    '''docstring'''

    log.debug('home')

    data = Models().get_home()

    view = Views().get_home(data)

    return view


# @cache.memoize(timeout=5000)
@app.route("%s/input" % (Config().APP_ROUTING), methods=['GET', 'POST'])
def searchbar_input():
    '''docstring'''

    term = request.args.get('q')

    data = Models().searchbar_input(term)

    return data


# @cache.memoize(timeout=5000)
@app.route("%s/search/" % (Config().APP_ROUTING), methods=['GET', 'POST'])
@app.route("%s/search" % (Config().APP_ROUTING), methods=['GET', 'POST'])
def search():
    '''docstring'''

    if request.method == 'GET':
        log.debug('search GET')

        data, newrows, jsdata = Models().get_search(request)

        view = Views().get_search(data, newrows, jsdata)

    if request.method == 'POST':
        log.debug('search POST')

        data = request.get_json()

        data, newrows, jsdata = Models().post_search(data)

        view = Views().post_search(data, newrows, jsdata)

    return view


# @cache.memoize(timeout=5000)
@app.route("%s/sale/<instrument_no>" % (Config().APP_ROUTING), methods=['GET'])
def sale(instrument_no=None):
    '''docstring'''

    log.debug('sale')

    instrument_no = urllib.unquote(instrument_no).decode('utf8')

    data, jsdata, newrows = Models().get_sale(instrument_no)

    if data is None:
        page_not_found()
    else:
        return Views().get_sale(data, jsdata, newrows)


def check_auth(username, password):
    '''Checks if given username and password match correct credentials'''

    return (username == Config().DASHBOARD_USERNAME and
            password == Config().DASHBOARD_PASSWORD)


def authenticate():
    '''Return error message'''

    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    '''Authorization process'''

    @wraps(f)
    def decorated(*args, **kwargs):
        '''docstring'''

        auth = request.authorization

        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        return f(*args, **kwargs)

    return decorated


# todo
# @cache.memoize(timeout=5000)
@app.route("%s/dashboard/" % (Config().APP_ROUTING), methods=['GET', 'POST'])
@requires_auth
def dashboard():
    '''Dashboard'''

    if request.method == 'GET':
        log.debug('GET dashboard')

        # data = Models().get_dashboard()

        # view = Views().get_dashboard(data)

        # return view

    if request.method == 'POST':
        log.debug('POST dashboard')

        # data = request.get_json()

        # data = Models().post_dashboard(data)

        # view = Views().post_dashboard(data)

        # return view


@app.route("%s/webhook" % (Config().APP_ROUTING), methods=['POST'])
def webhook():
    '''Run Webhook class to keep server and S3 in sync'''

    log.debug('webhook')

    data = request.get_json()

    webhook.Webhook().main(data)


# @cache.memoize(timeout=5000)
@app.errorhandler(404)
def page_not_found(error):
    '''Return error page'''

    log.debug(error)

    view = Views().get_error_page()

    return view


if __name__ == '__main__':
    app.run(
        # host = "0.0.0.0",
        use_reloader=Config().RELOADER,
        debug=Config().DEBUG
    )
