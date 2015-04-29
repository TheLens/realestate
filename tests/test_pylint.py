# -*- coding: utf-8 -*-

# todo: everything

'''Tests that all Python files in project pass pylint tests.'''

from unittest import TestCase
import os
import fnmatch
from subprocess import call
from realestate import PROJECT_DIR

# ignore stuff in virtualenvs or version control directories
ignore_patterns = ('scripts', 'tests', 'misc')


def ignore(dir):
    '''Should the directory be ignored?'''

    for pattern in ignore_patterns:
        if pattern in dir:
            return True
    return False


class TestPylint(TestCase):

    '''Test that all Python files pass pylint tests.'''

    def test_pep8(self):
        '''Test that all Python files pass pylint tests.'''

        # pep8style = pep8.StyleGuide(quiet=False)

        # Find all .py files
        files_list = []
        for root, dirnames, filenames in os.walk('%s' % PROJECT_DIR):
            if ignore(root):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):
                files_list.append(os.path.join(root, filename))

        for f in files_list:
            call([
                'pylint',
                '--errors-only',
                # '--ignore=check_assessor_urls.py',  # todo: not working
                # --disable=invalid-name,
                f
            ])
