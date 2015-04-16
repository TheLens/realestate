# -*- coding: utf-8 -*-

'''Universal logging class'''

import logging
import logging.handlers
# import os

from landrecords.config import Config


class Log(object):

    '''Universal logging class'''

    def __init__(self, name):
        self.name = name
        self.logger = self.initialize_log()

    def initialize_log(self):
        '''Set up logger'''

        # if os.path.isfile('%s/%s.log' % (Config().LOG_DIR, name)):
        #     os.remove('%s/%s.log' % (Config().LOG_DIR, name))

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create file handler which logs debug messages or higher
        filehandler = logging.FileHandler(
            '%s/%s.log' % (Config().LOG_DIR, self.name))
        filehandler.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(funcName)s - ' +
            '%(levelname)s - %(lineno)d - %(message)s')
        filehandler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(filehandler)

        return logger
