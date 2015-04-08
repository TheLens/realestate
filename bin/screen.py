# -*- coding: utf-8 -*-

from subprocess import call

from landrecords import config

name = 'test'

call(['%s/bin/phantomjs' % config.PROJECT_DIR,
      '%s/bin/screen.js' % config.PROJECT_DIR,
      'http://vault.thelensnola.org/realestate/sale/2015-13092',
      '%s/tweets/%s.png' % (config.IMAGE_DIR, name)])
