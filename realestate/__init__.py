# -*- coding: utf-8 -*-

"""
Package-wide script that is always run.

Includes common variables, such as file names, file paths and dates.
Also includes logging, which can be accessed by any module like so:

`log.debug('Description')`

`log.info('Description')`

`log.error('Description')`

`log.exception(error, exc_info=True)`

You can change the logging level to your choosing. The default is DEBUG.
"""

import logging
import logging.handlers
import os
import getpass

from datetime import date, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

USER = getpass.getuser()
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

if USER == 'ubuntu':  # Server
    BACKUP_DIR = '/backups/realestate'
    GEO_DIR = '/apps/geographic-data/repo'

    PROJECT_URL = 'http://vault.thelensnola.org/realestate'

    # Static assets
    S3_URL = "https://s3-us-west-2.amazonaws.com/lensnola/realestate"

    LENS_JS = "%s/js/lens.js" % S3_URL
    INDEX_JS = "%s/js/index.js" % S3_URL
    SEARCH_AREA_JS = "%s/js/search-area.js" % S3_URL
    SEARCH_JS = "%s/js/search.js" % S3_URL
    MAP_JS = "%s/js/map.js" % S3_URL
    SALE_JS = "%s/js/sale.js" % S3_URL
    DASHBOARD_JS = "%s/js/dashboard.js" % S3_URL
    NEIGHBORHOODS_TOPO = "%s/js/neighborhoods-topo.js" % S3_URL

    LENS_CSS = "%s/css/lens.css" % S3_URL
    REALESTATE_CSS = "%s/css/realestate.css" % S3_URL
    BANNER_CSS = "%s/css/banner.css" % S3_URL
    TABLE_CSS = "%s/css/table.css" % S3_URL

    RELOADER = False
    DEBUG = False
    PORT = 5004
else:  # Local
    BACKUP_DIR = '%s/backups' % PROJECT_DIR
    GEO_DIR = '/Users/%s/projects/geographic-data/repo' % USER

    PROJECT_URL = 'http://localhost:5000/realestate'

    # Static assets
    LENS_JS = '/static/js/lens.js'
    INDEX_JS = "/static/js/index.js"
    SEARCH_AREA_JS = '/static/js/search-area.js'
    SEARCH_JS = "/static/js/search.js"
    MAP_JS = "/static/js/map.js"
    SALE_JS = "/static/js/sale.js"
    DASHBOARD_JS = "/static/js/dashboard.js"
    NEIGHBORHOODS_TOPO = "/static/js/neighborhoods-topo.min.js"

    LENS_CSS = "/static/css/lens.css"
    REALESTATE_CSS = "/static/css/realestate.css"
    BANNER_CSS = "/static/css/banner.css"
    TABLE_CSS = "/static/css/table.css"

    RELOADER = True
    DEBUG = True
    PORT = 5000

APP_ROUTING = '/realestate'
JS_APP_ROUTING = '/realestate'

DATABASE_NAME = 'realestate'

OPENING_DATE = date(2014, 2, 18)
OPENING_DAY = OPENING_DATE.strftime('%Y-%m-%d')

YESTERDAY_DATE = date.today() - timedelta(days=1)
YESTERDAY_DAY = YESTERDAY_DATE.strftime('%Y-%m-%d')

TODAY_DATE = date.today()
TODAY_DAY = TODAY_DATE.strftime('%Y-%m-%d')

S3_PATH = 's3://lensnola/realestate'

# SQLAlchemy session
ENGINE_STRING = 'postgresql://{0}:{1}@localhost/{2}'.format(
    os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
    os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
    DATABASE_NAME)
engine = create_engine(ENGINE_STRING)
sn = sessionmaker(bind=engine)
SESSION = sn()  # Import this to any files that need database

# Logging
LOG_DIR = '%s/logs' % PROJECT_DIR
LOG_FILE = "{}/realestate.log".format(LOG_DIR)

# if os.path.isfile('{0}/{1}'.format(LOG_DIR, LOG)):
#     os.remove('{0}/{1}'.format(LOG_DIR, LOG))

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=(5 * 1024 * 1024),  # 5 MB
    backupCount=5)

filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
