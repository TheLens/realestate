# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import logging
import logging.handlers
from fabric.api import local

from landrecords import config


def initialize_log(name):
    if os.path.isfile('%s/%s.log' % (config.LOG_DIR, name)):
        os.remove('%s/%s.log' % (config.LOG_DIR, name))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler('%s/%s.log' % (config.LOG_DIR, name))
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(funcName)s - '
        '%(levelname)s - %(lineno)d - %(message)s')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)

    return logger


class Models(object):

    def __init__(self):
        self.logger = initialize_log('webhook')

    def main(self, data):
        self.git_pull(data)

        files_list = self.gather_updated_files(data)

        for f in files_list:
            aws_string = self.form_aws_string(f)

            if aws_string is None:
                continue

            self.logger.debug(aws_string)

            local(aws_string)

        self.logger.info('Done')
        return "None"

    def git_pull(self, data):
        try:
            self.logger.info('try')
            branch = data['ref']
            self.logger.debug(branch)
            if branch != 'refs/heads/master':
                self.logger.info('Not master branch')
                return 'None'
        except:
            self.logger.info('except')
            return "None"

        local('git pull origin master')

    def form_aws_string(self, f):
        # Ex. f = 'scripts/templates/search.html'
        self.logger.debug(f)

        file_path = f.split('static/')[-1]  # Ex. 'js/lens.js'

        aws_string = 'aws s3 cp {0}{1} {2}/{3} --acl public-read'.format(
            config.PROJECT_DIR, f, config.S3_DIR, file_path)

        return aws_string

    def gather_updated_files(self, data):
        try:
            self.logger.info('try')
            branch = data['ref']
            self.logger.debug(branch)
            if branch != 'refs/heads/master':
                self.logger.info('Not master branch')
                return 'None'
        except:
            self.logger.info('except')
            return "None"

        github_branch = data['ref'].split('/')[-1]
        self.logger.debug(github_branch)

        # Ex: ['scripts/templates/search.html']
        added_files_list = data['commits'][0]['added']
        modified_files_list = data['commits'][0]['modified']

        files_list = []

        for f in added_files_list:
            files_list.append(f)

        for f in modified_files_list:
            files_list.append(f)

        for i, f in enumerate(files_list):
            if f.split('/')[1] != 'static':
                del files_list[i]

        return files_list
