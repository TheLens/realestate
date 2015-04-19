# -*- coding: utf-8 -*-

'''Universal logging class'''

import logging
import logging.handlers
import os
# import getpass

from landrecords.config import Config

if os.path.isfile('%s/landrecords.log' % (Config().LOG_DIR)):
    os.remove('%s/landrecords.log' % (Config().LOG_DIR))

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.FileHandler(
    '%s/landrecords.log' % (Config().LOG_DIR))
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)

# return logger
