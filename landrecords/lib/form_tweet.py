# -*- coding: utf-8 -*-

'''Runs logic to find what to tweet and forms language for tweet'''

# todo: run this separate from 3 a.m. scrape/initialize/etc cron job.
# run this on a cron at same time we want to tweet.

import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from subprocess import call

from landrecords import db
from landrecords.config import Config
from landrecords.lib.log import Log
from landrecords.lib.twitter import Twitter


class AutoTweet(object):

    '''Runs logic to find what to tweet and forms language for tweet'''

    def __init__(self):

        base = declarative_base()
        engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

        return_dict = self.figure_out_recorded_date()

        self.document_recorded_early = return_dict['document_recorded_early']
        self.document_recorded_late = return_dict['document_recorded_late']
        self.time_period = return_dict['time_period']

        query_dict = self.get_highest_amount_details()

        self.amount = query_dict['amount']
        self.instrument_no = query_dict['instrument_no']
        self.neighborhood = query_dict['neighborhood']

        self.neighborhood = self.conversational_neighborhoods()

        self.url = self.form_url()

        self.name = self.screenshot_name()

        # self.media_attachment = self.open_image()

        self.message = self.form_message()

        # self.send_tweet(message, image)

    def figure_out_recorded_date(self):
        '''Treat Tuesday-Saturday like any other day. Don\'t do anything on
           Sundays. Mondays tweet about entire previous week.'''

        document_recorded_early = ''
        document_recorded_late = ''
        time_period = ''

        if Config().TODAY_DATETIME.strftime('%A') == 'Sunday':
            sys.exit()
            return
        elif Config().TODAY_DATETIME.strftime('%A') == 'Monday':
            document_recorded_early = (
                Config().TODAY_DATETIME - timedelta(days=7)
            ).strftime(
                '%Y-%m-%d'
            )

            document_recorded_late = (
                Config().TODAY_DATETIME - timedelta(days=3)
            ).strftime(
                '%Y-%m-%d'
            )

            time_period = 'last week'
        else:
            document_recorded_early = (
                Config().TODAY_DATETIME - timedelta(days=1)
            ).strftime(
                '%Y-%m-%d'
            )

            document_recorded_late = (
                Config().TODAY_DATETIME - timedelta(days=1)
            ).strftime(
                '%Y-%m-%d'
            )

            time_period = (
                Config().TODAY_DATETIME - timedelta(days=1)
            ).strftime('%A')

        return_dict = {}
        return_dict['document_recorded_early'] = document_recorded_early
        return_dict['document_recorded_late'] = document_recorded_late
        return_dict['time_period'] = time_period

        return return_dict

    def get_highest_amount_details(self):
        session = self.sn()

        query = session.query(
            db.Cleaned.detail_publish,
            db.Cleaned.document_recorded,
            db.Cleaned.amount,
            db.Cleaned.neighborhood
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.document_recorded >= '%s' % self.document_recorded_early
        ).filter(
            db.Cleaned.document_recorded <= '%s' % self.document_recorded_late
        ).order_by(
            db.Cleaned.amount.desc()
        ).limit(1).all()

        # todo:
        # If no record found, terminate this script so it
        # doesn't tweet out nonsense.
        # Could be because of federal holidays, the city didn't enter
        # records on a given day, or any number of other reasons.
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

    def conversational_neighborhoods(self):
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
            if self.neighborhood == nbhd:
                self.neighborhood == 'the ' + self.neighborhood

    def form_url(self):
        '''Append instrument number to /realestate/sale/'''

        url = 'http://vault.thelensnola.org/realestate/sale/' + \
            + self.instrument_no

        return url

    def screenshot_name(self):
        '''Form filename for map screenshot'''

        name = '%s-%s-high-amount.png' % (
            Config().TODAY_DATE, self.instrument_no)

        return name

    def get_image(self):
        call(['%s/scripts/phantomjs' % Config().PROJECT_DIR,
              '%s/scripts/screen.js' % Config().PROJECT_DIR,
              self.url,
              '%s/tweets/%s' % (Config().PICTURES_DIR, self.name)])

    def open_image(self):
        self.get_image()

        filename = '%s/tweets/%s' % (Config().PICTURES_DIR, self.name)

        return filename

        # with open(filename, 'rb') as image:
        #     return image

    def form_message(self):
        '''Plug variables into mab lib sentences'''

        # options = []

        message = (
            "Priciest property sale recorded %s was in %s: %s.\n%s"
        ).format(
            self.time_period,
            self.neighborhood,
            self.amount,
            self.url
        )

        # option = random.choice(options)

        return message

    def main(self, message, image):
        status = self.form_message()
        media = self.open_image()
        Twitter(status=status).send_with_media(media=media)

if __name__ == '__main__':
    log = Log(__name__).initialize_log()
