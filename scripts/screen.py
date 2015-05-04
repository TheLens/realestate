# -*- coding: utf-8 -*-

from subprocess import call
from realestate import PROJECT_DIR

name = 'test'

PICTURES_DIR = '%s/realestate/static/pictures' % PROJECT_DIR

call(['%s/bin/phantomjs' % PROJECT_DIR,
      '%s/bin/screen.js' % PROJECT_DIR,
      'http://vault.thelensnola.org/realestate/sale/2015-13092',
      '%s/tweets/%s.png' % (PICTURES_DIR, name)])
