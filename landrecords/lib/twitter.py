# -*- coding: utf-8 -*-

'''
Methods for working with Twitter.
Takes message and attachment, forms tweet and sends tweet using Twython.
Performs checks on number of characters before sending to prevent an
#embarrassing moment.
'''

import re
import os
from twython import Twython


class Twitter(object):

    '''Methods for working with the Twitter API.'''

    def __init__(self, status=None):
        '''Make connection to Twitter API.'''

        self.status = status
        self.twitter = Twython(os.environ.get('APP_KEY'),
                               os.environ.get('APP_SECRET'),
                               os.environ.get('OAUTH_TOKEN'),
                               os.environ.get('OAUTH_TOKEN_SECRET'))

    @staticmethod
    def get_attachment(media):
        '''Opens a file.'''

        attachment = open(media, 'rb')

        return attachment

    def check_for_urls(self):
        '''Scan for URLs. Replace URL length if any found.'''

        url_length = 0

        # URL is either followed by a whitespace or at the end of the line
        urls = re.findall(r'(http[^\s|$]+)', self.status)

        for url in urls:
            # Subtract length of URL text and replace with length of
            # shortened URL (~22 characters)
            url_length = url_length + len(url) - 22

        return url_length

    def check_length(self, media=False):
        '''Confirm that the status + attachments is <= 140 chars.'''

        length = 140 - len(self.status)

        # Find how many characters to add back:
        # url_length = actual URL length - shortened URL length
        url_length = self.check_for_urls()

        length = length + url_length

        # If there is a media attachment, subtract ~23 characters
        if media:
            length -= 23

        if length < 0:
            return False
        else:
            return True

    def send_as_text(self):
        '''Send plain text tweet.'''

        assert self.check_length()

        self.twitter.update_status(status=self.status)

    def send_with_media(self, media=None):
        '''Send tweet with media attachment.'''

        assert self.check_length(media=True)

        attachment = self.get_attachment(media)

        self.twitter.update_status_with_media(
            status=self.status, media=attachment)

        attachment.close()

if __name__ == '__main__':
    pass
