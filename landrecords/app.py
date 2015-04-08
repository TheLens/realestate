# -*- coding: utf-8 -*-

from __future__ import absolute_import

import urllib
# from flask.ext.cache import Cache
from flask import (
    Flask,
    render_template,
    request,
    Response
)
from functools import wraps

from landrecords import config
from landrecords.lib.log import Log
from landrecords.models import Models
from landrecords.views import Views

app = Flask(__name__)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

log = Log('app').logger


# @cache.memoize(timeout=5000)
@app.route("%s/" % (config.APP_ROUTING), methods=['GET'])
def home():
    log.debug('home')

    data = Models().get_home()

    view = Views().get_home(data)

    return view


# @cache.memoize(timeout=5000)
@app.route("%s/input" % (config.APP_ROUTING), methods=['GET', 'POST'])
def searchbar_input():
    term = request.args.get('q')

    data = Models().searchbar_input(term)

    return data


# @cache.memoize(timeout=5000)
@app.route("%s/search/" % (config.APP_ROUTING), methods=['GET', 'POST'])
@app.route("%s/search" % (config.APP_ROUTING), methods=['GET', 'POST'])
def search():
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
@app.route("%s/sale/<instrument_no>" % (config.APP_ROUTING), methods=['GET'])
def sale(instrument_no=None):
    log.debug('sale')

    instrument_no = urllib.unquote(instrument_no).decode('utf8')

    data, jsdata, newrows = Models().get_sale(instrument_no)

    if data is None:
        page_not_found()
    else:
        return Views().get_sale(data, jsdata, newrows)


'''
Dashboard
'''


def check_auth(username, password):
    return (username == config.DASHBOARD_USERNAME and
            password == config.DASHBOARD_PASSWORD)


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
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


# @cache.memoize(timeout=5000)
@app.route("%s/dashboard/" % (config.APP_ROUTING), methods=['GET', 'POST'])
@requires_auth
def dashboard():
    if request.method == 'GET':
        log.debug('dashboard GET')

        return Views().get_dashboard()

    if request.method == 'POST':
        log.debug('dashboard POST')

        data = request.get_json()

        return Views().post_dashboard(data)


'''
Misc.
'''


@app.route("%s/webhook" % (config.APP_ROUTING), methods=['POST'])
def webhook():
    log.debug('webhook')

    data = request.get_json()

    webhook.Webhook().main(data)


# @cache.memoize(timeout=5000)
@app.errorhandler(404)
def page_not_found():
    log.debug('404 error')

    return render_template('404.html',
                           css=config.CSS,
                           js=config.JS,
                           indexjs=config.INDEX_JS), 404


if __name__ == '__main__':
    app.run(
        # host = "0.0.0.0",
        use_reloader=config.RELOADER,
        debug=config.DEBUG
    )
