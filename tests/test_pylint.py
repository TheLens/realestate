# -*- coding: utf-8 -*-

"""Test that all Python files in project pass pylint tests."""

import os
import fnmatch

from subprocess import call

from www import PROJECT_DIR

# Ignore stuff in virtualenvs or version control directories
ignore_patterns = [
    '.egg-info', '.git', '.tox',
    'backups', 'confs', 'data', 'docs', 'logs', 'misc']


def ignore(directory):
    """Check if the directory should be ignored."""
    for pattern in ignore_patterns:
        if pattern in directory:
            return True

    return False


class RunPylint(object):
    """Run pylint on all Python files."""

    def test_pylint(self):
        """Run pylint on all Python files."""
        files_list = []

        for root, dirnames, filenames in os.walk(PROJECT_DIR):
            if ignore(root):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):
                files_list.append(os.path.join(root, filename))

        for file in files_list:
            # (pylint_stdout, pylint_stderr) = epylint.py_run(
            #     command_options="{} --errors-only".format(file),
            #     return_std=True)

            # print(pylint_stdout.getvalue())
            # print(pylint_stderr.getvalue())

            call([
                'pylint',
                '--errors-only',
                file])

if __name__ == '__main__':
    RunPylint().test_pylint()
