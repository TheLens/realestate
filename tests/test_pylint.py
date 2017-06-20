# -*- coding: utf-8 -*-

"""Test that all Python files in project pass pylint tests."""

import os
import fnmatch

from subprocess import call

from www import PROJECT_DIR

python_dirs = ['realestate/scripts/', 'realestate/tests/', 'realestate/www/']


def should_check_directory(directory):
    """Check if this directory should be checked."""
    for python_dir in python_dirs:
        if python_dir in directory:
            return True

    return False


class RunPylint(object):
    """Run pylint on all Python files."""

    def test_pylint(self):
        """Run pylint on all Python files."""
        files_list = []

        for root, dirnames, filenames in os.walk(PROJECT_DIR):
            if not should_check_directory(root):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):
                files_list.append(os.path.join(root, filename))

        for file in files_list:
            call(['pylint', '--errors-only', file])

if __name__ == '__main__':
    RunPylint().test_pylint()
