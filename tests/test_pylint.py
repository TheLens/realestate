# -*- coding: utf-8 -*-

# todo: everything

from unittest import TestCase
import os
import fnmatch
from subprocess import call

# ignore stuff in virtualenvs or version control directories
ignore_patterns = ('bin', 'scripts', 'tests', 'misc')


def ignore(dir):
    """Should the directory be ignored?"""

    for pattern in ignore_patterns:
        if pattern in dir:
            return True
    return False


class TestPylint(TestCase):

    def test_pep8(self):
        "Test that all Python files conform to PEP8 standards."

        # pep8style = pep8.StyleGuide(quiet=False)

        # Find all .py files
        files_list = []
        for root, dirnames, filenames in os.walk(
            '/Users/thomasthoren/projects/land-records/repo'
        ):
            if ignore(root):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):
                files_list.append(os.path.join(root, filename))

        for f in files_list:
            call(['pylint',
                  f])

        # errors = pep8style.check_files(files_list).total_errors

        # self.assertEqual(errors, 0,
        #                  'Found %s PEP8 errors (and warnings).' % errors)
