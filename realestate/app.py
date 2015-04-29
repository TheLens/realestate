# -*- coding: utf-8 -*-

'''The controller that routes requests and returns responses.'''

import os
import urllib
# from flask.ext.cache import Cache
from flask import (
    Flask,
    # render_template,
    request,
    Response
)
from functools import wraps

from realestate import (
    log, APP_ROUTING, DEBUG, RELOADER, PORT
)
from realestate.models import Models
from realestate.views import Views

app = Flask(__name__)

# cache = Cache(app, ={'CACHE_TYPE': 'simple'})


# @cache.memoize(timeout=5000)
@app.route("%s/" % (APP_ROUTING), methods=['GET'])
def home():
    '''
    Receives a GET call for the homepage (/) and returns the view.
    '''

    log.debug('home')
    log.debug(DEBUG)
    log.debug(os.environ)
    log.debug(os.environ.keys())
    log.debug(os.environ.get('REAL_ESTATE_SERVER_ENGINE'))

    data = Models().get_home()

    log.debug(data)

    view = Views().get_home(data)

    log.debug(view)

    return view


# @cache.memoize(timeout=5000)
@app.route("%s/input" % (APP_ROUTING), methods=['POST'])
def searchbar_input():
    '''
    Receives a ___ call from the autocomplete dropdown and returns a dict
    of suggestions.

    :param query: The search bar input.
    :type query: string
    :returns: A dict of matching suggestions.
    '''

    term = request.args.get('q')

    data = Models().searchbar_input(term)

    return data


# @cache.memoize(timeout=5000)
@app.route("%s/search/" % (APP_ROUTING), methods=['GET', 'POST'])
@app.route("%s/search" % (APP_ROUTING), methods=['GET', 'POST'])
def search():
    '''
    Receives a request (GET or POST) for the /search page and returns a view
    of some or all of the /search page, depending on whether GET or POST.

    todo:
    :param request: Incoming data
    :type request: dict?
    :returns: View of search page.
    '''

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
@app.route("%s/sale/<instrument_no>" % (APP_ROUTING), methods=['GET'])
def sale(instrument_no=None):
    """
    Receives a GET request for a particular sale's individual page.

    :param instrument_no: The sale's instrument number, determined via the URL.
    :type instrument_no: string
    :returns: The sale's page or an error page if no sale found.
    """

    log.debug('sale')

    instrument_no = urllib.unquote(instrument_no).decode('utf8')

    data, jsdata, newrows = Models().get_sale(instrument_no)

    if data is None:
        page_not_found(404)
    else:
        return Views().get_sale(data, jsdata, newrows)


def check_auth(username, password):
    """
    Checks if given username and password match correct credentials.

    :param username: The entered username.
    :type username: string
    :param password: The entered password.
    :type password: string
    :returns: bool. True if username and password are correct, False otherwise.
    """

    return (username == os.environ.get('REAL_ESTATE_DASHBOARD_USERNAME') and
            password == os.environ.get('REAL_ESTATE_DASHBOARD_PASSWORD'))


def authenticate():
    """
    Return error message.
    """

    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    """
    Authorization process.
    """

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
@app.route("%s/dashboard/" % (APP_ROUTING), methods=['GET', 'POST'])
@requires_auth
def dashboard():
    """
    The admin dashboard page for making adjustments to the database.
    """

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


@app.route("%s/webhook" % (APP_ROUTING), methods=['POST'])
def webhook():
    '''Run Webhook class to keep server and S3 in sync'''

    log.debug('webhook')

    data = request.get_json()

    webhook.Webhook().main(data)


# @cache.memoize(timeout=5000)
@app.errorhandler(404)
def page_not_found(error):
    """
    Returns an error page.

    :param error: The error message(?).
    :type error: not sure
    :returns: The view.
    """

    log.debug(error)

    view = Views().get_error_page()

    return view


if __name__ == '__main__':
    app.run(
        port=PORT,
        use_reloader=RELOADER,
        debug=DEBUG
    )
