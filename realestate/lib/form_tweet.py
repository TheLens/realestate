# -*- coding: utf-8 -*-

'''
Does analysis and uses results to craft language of the tweet. Also takes
screenshot of that particular sale's map using `screen.js` (PhantomJS).
'''

# todo: run this separate from 3 a.m. scrape/initialize/etc cron job.
# run this on a cron at same time we want to tweet.

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from subprocess import call

from realestate.db import Cleaned
from realestate import log, TODAY_DATE, PROJECT_DIR, DATABASE_NAME
from realestate.lib.twitter import Twitter


class AutoTweet(object):

    '''Runs logic to find what to tweet and forms language for tweet.'''

    def __init__(self):
        '''Initialize self variables and establish connection to database.'''

        base = declarative_base()
        engine = create_engine(
            'postgresql://%s:%s@localhost/%s' % (
                os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
                os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
                DATABASE_NAME
            )
        )
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    @staticmethod
    def figure_out_recorded_date():
        '''
        Treat Tuesday-Saturday like any other day. Don\'t do anything on
        Sundays. Mondays tweet about entire previous week.
        '''

        document_recorded_early = ''
        document_recorded_late = ''
        time_period = ''

        if TODAY_DATE.strftime('%A') == 'Sunday':
            sys.exit()
            return
        elif TODAY_DATE.strftime('%A') == 'Monday':
            document_recorded_early = (
                TODAY_DATE - timedelta(days=7)
            ).strftime(
                '%Y-%m-%d'
            )

            document_recorded_late = (
                TODAY_DATE - timedelta(days=3)
            ).strftime(
                '%Y-%m-%d'
            )

            time_period = 'last week'
        else:
            document_recorded_early = (
                TODAY_DATE - timedelta(days=1)
            ).strftime(
                '%Y-%m-%d'
            )

            document_recorded_late = (
                TODAY_DATE - timedelta(days=1)
            ).strftime(
                '%Y-%m-%d'
            )

            time_period = (
                TODAY_DATE - timedelta(days=1)
            ).strftime('%A')

        return_dict = {}
        return_dict['document_recorded_early'] = document_recorded_early
        return_dict['document_recorded_late'] = document_recorded_late
        return_dict['time_period'] = time_period

        return return_dict

    def get_highest_amount_details(self,
                                   document_recorded_early,
                                   document_recorded_late):
        '''Get the relevant fields about the sale with the highest amount.'''

        session = self.sn()

        query = session.query(
            Cleaned.detail_publish,
            Cleaned.document_recorded,
            Cleaned.amount,
            Cleaned.neighborhood,
            Cleaned.instrument_no
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.document_recorded >= '%s' % document_recorded_early
        ).filter(
            Cleaned.document_recorded <= '%s' % document_recorded_late
        ).order_by(
            Cleaned.amount.desc()
        ).limit(1).all()

        log.debug(query)

        # If no record found, terminate this script so it
        # doesn't tweet out nonsense.
        # Could be because of holidays, no records or old-fashioned bug.
        if len(query) == 0:
            sys.exit()

        query_dict = {}

        for row in query:
            query_dict['amount'] = '$' + format(row.amount, ',')
            query_dict['instrument_no'] = row.instrument_no
            query_dict['neighborhood'] = row.neighborhood
            # todo: neighborhood cleaning in clean.py? "Dev" => "Development"

        session.close()

        return query_dict

    @staticmethod
    def conversational_neighborhoods(neighborhood):
        '''
        Converts neighborhoods to the way you would refer to them in
        conversation. Ex. "French Quarter" => "the French Quarter."
        '''

        # todo: needs work

        nbhd_list = [
            'BLACK PEARL'
            'BYWATER'
            'CENTRAL BUSINESS DISTRICT'
            'DESIRE AREA'
            'FAIRGROUNDS'
            'FISCHER DEV'
            'FLORIDA AREA'
            'FLORIDA DEV'
            'FRENCH QUARTER'
            'GARDEN DISTRICT'
            'IRISH CHANNEL'
            'LOWER GARDEN DISTRICT'
            'LOWER NINTH WARD'
            'MARIGNY'
            'SEVENTH WARD'
            'ST. BERNARD AREA'
            'ST. THOMAS DEV'
            'U.S. NAVAL BASE'
        ]

        for nbhd in nbhd_list:
            if neighborhood == nbhd:
                neighborhood = 'the ' + neighborhood

    @staticmethod
    def form_url(instrument_no):
        '''Append instrument number to /realestate/sale/'''

        url = 'http://vault.thelensnola.org/realestate/sale/' + \
            instrument_no

        return url

    @staticmethod
    def screenshot_name(instrument_no):
        '''Form filename for map screenshot.'''

        name = '%s-%s-high-amount.png' % (
            TODAY_DATE, instrument_no)

        return name

    @staticmethod
    def get_image(url, name):
        '''Take screenshot of map with PhantomJS.'''

        log.debug('get_image')
        log.debug('url: %s', url)

        call([
            '%s/scripts/phantomjs' % PROJECT_DIR,
            '%s/scripts/screen.js' % PROJECT_DIR,
            url,
            '%s/realestate/static/pictures/tweets/%s' % (
                PROJECT_DIR, name)
        ])

    def open_image(self, url, name):
        '''Get file path to screenshot.'''

        self.get_image(url, name)

        filename = '%s/realestate/' % PROJECT_DIR + \
            'static/pictures/tweets/%s' % name

        return filename

        # with open(filename, 'rb') as image:
        #     return image

    @staticmethod
    def form_message(time_period, neighborhood, amount, url):
        '''Plug variables into mab lib sentences.'''

        log.debug('form_message')

        # options = []

        message = (
            "Priciest property sale recorded {0} was in {1}: {2}.\n{3}"
        ).format(
            time_period,
            neighborhood,
            amount,
            url
        )

        # option = random.choice(options)

        return message

    def main(self):
        '''Runs through all methods.'''

        return_dict = self.figure_out_recorded_date()

        document_recorded_early = return_dict['document_recorded_early']
        log.debug(
            'document_recorded_early: %s',
            document_recorded_early)

        document_recorded_late = return_dict['document_recorded_late']
        log.debug(
            'document_recorded_late: %s',
            document_recorded_late)

        time_period = return_dict['time_period']
        log.debug('time_period: %s', time_period)

        try:
            query_dict = self.get_highest_amount_details(
                document_recorded_early, document_recorded_late)
        except Exception, error:
            log.exception(error, exc_info=True)

        amount = query_dict['amount']
        log.debug('amount: %s', amount)

        instrument_no = query_dict['instrument_no']
        log.debug('instrument_no: %s', instrument_no)

        neighborhood = query_dict['neighborhood']
        log.debug('neighborhood: %s', neighborhood)

        # todo:
        # neighborhood = self.conversational_neighborhoods()

        url = self.form_url(instrument_no)
        log.debug('url: %s', url)

        name = self.screenshot_name(instrument_no)
        log.debug('name: %s', name)

        status = self.form_message(time_period, neighborhood, amount, url)
        log.debug('status: %s', status)

        media = self.open_image(url, name)
        log.debug('media: %s', media)

        print 'status:', status
        print 'media:', media
        # Twitter(status=status).send_with_media(media=media)

if __name__ == '__main__':
    AutoTweet().main()
