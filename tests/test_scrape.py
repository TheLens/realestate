
from landrecords.lib.scrape import Scrape
from landrecords.config import Config

from unittest import TestCase
import os
import fnmatch


class TestScrape(TestCase):

    def test_for_error_html(self):
        '''Tests all scraped single-sale HTML to check if error pages'''

        files_list = []

        for root, dirnames, filenames in os.walk(
            '%s/raw' % Config().DATA_DIR
        ):
            for filename in fnmatch.filter(filenames, 'OPR*.html'):
                # print filename
                files_list.append(os.path.join(root, filename))

        errors = []

        for f in files_list:
            if Scrape.check_if_error(f) is True:
                errors.append(f)

        self.assertEqual(
            len(errors), 0, (
                'Found {0} single-sale pages that were error ' +
                'pages instead of actual sale pages.'
            ).format(len(errors))
        )
