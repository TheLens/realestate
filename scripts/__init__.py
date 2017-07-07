# -*- coding: utf-8 -*-

"""App-wide common variables, such as file names, file paths and dates."""

import os
import logging
import logging.handlers

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Logging
if os.getenv('REALESTATE_ENVIRONMENT') == 'production':
    LOGGING_LEVEL = logging.INFO
else:
    LOGGING_LEVEL = logging.DEBUG

LOG_DIR = '{}/logs'.format(PROJECT_DIR)
LOG_FILE = '{}/scripts.log'.format(LOG_DIR)

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
