# -*- coding: utf-8 -*-

'''
Package-wide script that is always run.
Includes common variables, such as file names, file paths and dates.

Also includes logging, which can be accessed by any module like so:

`log.debug('Description')`

`log.info('Description')`

`log.error('Description')`

`log.exception(error, exc_info=True)`

You can change the logging level to your choosing. The default is DEBUG.
'''

import logging
import logging.handlers
import os
from datetime import date, timedelta
import getpass

USER = getpass.getuser()
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

if USER == 'thomasthoren':  # Local
    PROJECT_DIR = '%s' % PROJECT_DIR
    BACKUP_DIR = '%s/backups' % PROJECT_DIR
    DATA_DIR = '%s/data' % PROJECT_DIR
    LOG_DIR = '%s/logs' % PROJECT_DIR
    LIB_DIR = '%s/realestate/lib' % PROJECT_DIR
    GEO_DIR = '/Users/thomasthoren/projects/geographic-data/repo'
    PICTURES_DIR = '%s' % PROJECT_DIR + \
        '/realestate/static/pictures'
    SCRIPTS_DIR = '%s' % PROJECT_DIR + \
        '/scripts'

    PROJECT_URL = 'http://localhost:5000/realestate'

    APP_ROUTING = '/realestate'
    JS_APP_ROUTING = '/realestate'

    # Static assets
    JS = '/static/js/lens.js'
    SEARCH_AREA_JS = '/static/js/search-area.js'
    INDEX_JS = "/static/js/index.js"
    SEARCH_JS = "/static/js/search.js"
    MAP_JS = "/static/js/map.js"
    SALE_JS = "/static/js/sale.js"
    DASHBOARD_JS = "/static/js/dashboard.js"
    NEIGHBORHOODS_TOPO = "/static/js/neighborhoods-topo.min.js"
    SQUARES_TOPO = "/static/js/squares-topo.js"

    LENS_CSS = "/static/css/lens.css"
    REALESTATE_CSS = "/static/css/realestate.css"
    BANNER_CSS = "/static/css/banner.css"
    TABLE_CSS = "/static/css/table.css"

    RELOADER = True
    DEBUG = True
    PORT = 5000

else:  # Server
    PROJECT_DIR = '%s' % PROJECT_DIR
    BACKUP_DIR = '/backups/realestate'
    DATA_DIR = '%s/data' % PROJECT_DIR
    LOG_DIR = '%s/logs' % PROJECT_DIR
    LIB_DIR = '%s/realestate/lib' % PROJECT_DIR
    GEO_DIR = '/apps/geographic-data/repo'
    PICTURES_DIR = '%s' % PROJECT_DIR + \
        '/realestate/static/pictures'
    SCRIPTS_DIR = '%s/scripts' % PROJECT_DIR

    PROJECT_URL = 'http://vault.thelensnola.org/realestate'

    PROJECT_URL = 'http://vault.thelensnola.org/realestate'

    APP_ROUTING = '/realestate'
    JS_APP_ROUTING = '/realestate'

    # Static assets
    JS = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/js/lens.js"
    SEARCH_AREA_JS = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/js/search-area.js"
    INDEX_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/js/index.js"
    SEARCH_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/js/search.js"
    MAP_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/js/map.js"
    SALE_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/js/sale.js"
    DASHBOARD_JS = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/js/dashboard.js"
    NEIGHBORHOODS_TOPO = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/js/neighborhoods-topo.min.js"
    SQUARES_TOPO = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/js/squares-topo.js"

    LENS_CSS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/css/lens.css"
    REALESTATE_CSS = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/css/realestate.css"
    BANNER_CSS = "https://s3-us-west-2.amazonaws.com/" + \
        "lensnola/realestate/css/banner.css"
    TABLE_CSS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
        "realestate/css/table.css"

    RELOADER = False
    DEBUG = False
    PORT = 5004

# Stuff that is permanent, such as for fabfile deployment
SERVER_NAME = 'vault.thelensnola.org'
DATABASE_NAME = 'realestate'

LOCAL_PROJECT_DIR = '%s' % PROJECT_DIR
LOCAL_APP_DIR = '%s/realestate' % PROJECT_DIR
LOCAL_DATA_DIR = '%s/data' % PROJECT_DIR
LOCAL_SCRIPTS_DIR = '%s/scripts' % PROJECT_DIR
LOCAL_TESTS_DIR = '%s/tests' % PROJECT_DIR
LOCAL_TEMPLATE_DIR = '%s/realestate' % PROJECT_DIR + \
    '/templates'
LOCAL_LIB_DIR = '%s/realestate/lib' % PROJECT_DIR
LOCAL_CSS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/css'
LOCAL_JS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/js'
LOCAL_FONTS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/fonts'
LOCAL_IMAGES_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/css/images'

SERVER_PROJECT_DIR = '%s' % PROJECT_DIR
SERVER_APP_DIR = '%s/realestate' % PROJECT_DIR
SERVER_DATA_DIR = '%s/data' % PROJECT_DIR
SERVER_SCRIPTS_DIR = '%s/scripts' % PROJECT_DIR
SERVER_TESTS_DIR = '%s/tests' % PROJECT_DIR
SERVER_TEMPLATE_DIR = '%s' % PROJECT_DIR + \
    '/realestate/templates'
SERVER_LIB_DIR = '%s' % PROJECT_DIR + \
    '/realestate/lib'
SERVER_CSS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/css'
SERVER_JS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/js'
SERVER_FONTS_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/fonts'
SERVER_IMAGES_DIR = '%s' % PROJECT_DIR + \
    '/realestate/static/css/images'

OPENING_DAY = date(2014, 2, 18).strftime('%Y-%m-%d')

OPENING_DATE = date(2014, 2, 18)

YESTERDAY_DAY = (
    date.today() - timedelta(days=1)
).strftime('%Y-%m-%d')

YESTERDAY_DATE = date.today() - timedelta(days=1)

TODAY_DAY = (date.today()).strftime('%Y-%m-%d')
TODAY_DATE = date.today()

S3_PATH = 's3://lensnola/realestate'

# Logging
if os.path.isfile('%s/realestate.log' % (LOG_DIR)):
    os.remove('%s/realestate.log' % (LOG_DIR))

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.FileHandler(
    '%s/realestate.log' % (LOG_DIR))
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
