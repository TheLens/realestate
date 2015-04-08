# -*- coding: utf-8 -*-

from __future__ import absolute_import

from fabric.api import local

from landrecords import config
from landrecords.lib.log import Log


class Webhook(object):

    def __init__(self):
        self.log = Log('webhooks').logger

    def main(self, data):
        self.git_pull(data)

        files_list = self.gather_updated_files(data)

        for f in files_list:
            aws_string = self.form_aws_string(f)

            if aws_string is None:
                continue

            self.log.debug(aws_string)

            local(aws_string)

        self.log.info('Done')
        return "None"

    def git_pull(self, data):
        try:
            self.log.info('try')
            branch = data['ref']
            self.log.debug(branch)
            if branch != 'refs/heads/master':
                self.log.info('Not master branch')
                return 'None'
        except:
            self.log.info('except')
            return "None"

        local('git pull origin master')

    def form_aws_string(self, f):
        # Ex. f = 'scripts/templates/search.html'
        self.log.debug(f)

        file_path = f.split('static/')[-1]  # Ex. 'js/lens.js'

        aws_string = 'aws s3 cp {0}{1} {2}/{3} --acl public-read'.format(
            config.PROJECT_DIR, f, config.S3_DIR, file_path)

        return aws_string

    def gather_updated_files(self, data):
        try:
            self.log.info('try')
            branch = data['ref']
            self.log.debug(branch)
            if branch != 'refs/heads/master':
                self.log.info('Not master branch')
                return 'None'
        except:
            self.log.info('except')
            return "None"

        github_branch = data['ref'].split('/')[-1]
        self.log.debug(github_branch)

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
