# -*- coding: utf-8 -*-

from subprocess import call
from landrecords import PROJECT_DIR, IMAGE_DIR

name = 'test'

call(['%s/bin/phantomjs' % PROJECT_DIR,
      '%s/bin/screen.js' % PROJECT_DIR,
      'http://vault.thelensnola.org/realestate/sale/2015-13092',
      '%s/tweets/%s.png' % (IMAGE_DIR, name)])
