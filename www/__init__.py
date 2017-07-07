# -*- coding: utf-8 -*-

"""App-wide common variables, such as file names, file paths and dates."""

import os
import getpass
import logging
import logging.handlers

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

USER = getpass.getuser()
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

GEO_DIR = '{}/data/geo'.format(PROJECT_DIR)

if os.getenv('REALESTATE_ENVIRONMENT') == 'production':  # TODO
    S3_URL = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate'

    # JavaScript
    LENS_JS = '{}/js/lens.js'.format(S3_URL)
    INDEX_JS = '{}/js/index.js'.format(S3_URL)
    SEARCH_AREA_JS = '{}/js/search-area.js'.format(S3_URL)
    SEARCH_JS = '{}/js/search.js'.format(S3_URL)
    MAP_JS = '{}/js/map.js'.format(S3_URL)
    SALE_JS = '{}/js/sale.js'.format(S3_URL)
    DASHBOARD_JS = '{}/js/dashboard.js'.format(S3_URL)
    NEIGHBORHOODS_TOPO = '{}/js/neighborhoods-topo.js'.format(S3_URL)

    # CSS
    LENS_CSS = '{}/css/lens.css'.format(S3_URL)
    REALESTATE_CSS = '{}/css/realestate.css'.format(S3_URL)
    BANNER_CSS = '{}/css/banner.css'.format(S3_URL)
    TABLE_CSS = '{}/css/table.css'.format(S3_URL)

    RELOADER = False
    DEBUG = False
    PORT = 5004

    LOGGING_LEVEL = logging.INFO
else:  # Local
    # JavaScript
    LENS_JS = '/static/js/lens.js'
    INDEX_JS = '/static/js/index.js'
    SEARCH_AREA_JS = '/static/js/search-area.js'
    SEARCH_JS = '/static/js/search.js'
    MAP_JS = '/static/js/map.js'
    SALE_JS = '/static/js/sale.js'
    DASHBOARD_JS = '/static/js/dashboard.js'
    NEIGHBORHOODS_TOPO = '/static/js/neighborhoods-topo.min.js'

    # CSS
    LENS_CSS = '/static/css/lens.css'
    REALESTATE_CSS = '/static/css/realestate.css'
    BANNER_CSS = '/static/css/banner.css'
    TABLE_CSS = '/static/css/table.css'

    RELOADER = True
    DEBUG = True
    PORT = 5000

    LOGGING_LEVEL = logging.DEBUG

APP_ROUTING = '/realestate'
JS_APP_ROUTING = '/realestate'

DATABASE_NAME = 'realestate'

ENGINE_STRING = 'postgresql://{0}:{1}@localhost/{2}'.format(
    os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
    os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
    DATABASE_NAME)

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
LOG_DIR = '{}/logs'.format(PROJECT_DIR)
LOG_FILE = '{}/www.log'.format(LOG_DIR)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if not os.path.isfile(LOG_FILE):
    open(LOG_FILE, 'a').close()

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)

# Create file handler which logs debug messages or higher
filehandler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=(5 * 1024 * 1024),  # 5 MB
    backupCount=5)

filehandler.setLevel(LOGGING_LEVEL)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
