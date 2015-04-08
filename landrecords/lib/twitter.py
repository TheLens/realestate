# -*- coding: utf-8 -*-

# todo: run this separate from 3 a.m. scrape/initialize/etc cron job.
# run this on a cron at same time we want to tweet.

import random
import sys

from fabric.api import local
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from datetime import datetime, timedelta

from landrecords import config, db
from landrecords.lib.log import Log


class TwitterPreparer(object):

    def __init__(self):
        self.log = Log('twitter_preparer').logger

        base = declarative_base()
        engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(engine)
        self.sn = sessionmaker(bind=engine)

    # twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    def main(self):
        document_recorded = self.figure_out_recorded_date()
        details = self.get_highest_amount_details(document_recorded)

        amount = details['amount']
        instrument_no = details['instrument_no']
        document_date = details['document_date']

        image = self.get_image(instrument_no)

        url = self.form_url(instrument_no)

        message = self.form_message(
            amount, url, document_recorded, document_date)

        self.send_tweet(message, image)

        image.close()

    def figure_out_recorded_date():
        document_recorded = ''

        # Assuming we wanted to tweet a Friday sale on Sunday and
        # Monday, which we don't.
        '''
        if today_date.strftime('%A') == 'Sunday':
            document_recorded = (
                                    today_date - timedelta(days = 2)
                                ).strftime(
                                    '%Y-%m-%d'
                                )

        if today_date.strftime('%A') == 'Monday':
            document_recorded = (
                                    today_date - timedelta(days = 3)
                                ).strftime(
                                    '%Y-%m-%d'
                                )
        '''

        # If today is Sunday or Monday, don't tweet
        # because there is nothing new to tweet.
        # Friday sales would have been tweeted on Saturday.
        # Monday sales won't be recorded and ready
        # for tweeting until Tuesday.
        if (
            (config.TODAY_DATETIME).strftime('%A') == 'Sunday' or
            (config.TODAY_DATETIME).strftime('%A') == 'Monday'
        ):
            sys.exit()

        return document_recorded

    def get_highest_amount_details(self, document_recorded):
        session = self.sn()

        q = session.query(
            db.Cleaned.detail_publish,
            db.Cleaned.document_recorded,
            db.Cleaned.amount
        ).filter(
            db.Cleaned.detail_publish == '1'
        ).filter(
            db.Cleaned.document_recorded == '%s' % document_recorded
        ).order_by(
            db.Cleaned.amount.desc()
        ).limit(1).all()

        # todo:
        # If no record found, terminate this script so it
        # doesn't tweet out nonsense.
        # Could be because of federal holidays, the city didn't enter
        # records on a given day, or any number of other reasons.
        if len(q) == 0:
            sys.exit()

        amount = 0
        instrument_no = ''
        document_recorded = ''
        document_date = ''
        for u in q:
            amount = u.amount

            # .strftime('%A, %b. %-d, %Y')
            document_date = u.document_date.strftime('%A')
            instrument_no = u.instrument_no

        amount = '$' + format(amount, ',')

        session.close()

        return {'amount': amount,
                'instrument_no': instrument_no,
                'document_date': document_date}

    def form_url(self, instrument_no):
        url = 'http://vault.thelensnola.org/realestate/sale/' + instrument_no
        return url

    def form_message(self, amount, url, document_recorded, document_date):
        options = []

        # Normal amounts
        options.append("The most expensive property sale reported %s was for"
                       " %s. %s" % (document_recorded, amount, url))
        options.append("The most expensive property sale reported %s was for"
                       " %s. %s" % (document_recorded, amount, url))

        # High amounts
        if amount >= 1000000:
            # options = []
            options.append("We're moving on up! A property sale on %s went"
                           " for %s. %s" % (document_date, amount, url))
            options.append("Let them have it! This property sold for %s on"
                           " %s. %s" % (amount, document_date, url))

        option = random.choice(options)

        return option

    def get_image(self, instrument_no):
        local('%s/bin/phantomjs ' % (config.PROJECT_DIR) +
              'screen.js ' +
              '%s/sale/%s ' % (config.PROJECT_URL, instrument_no) +
              '%s/%s_date_hi.png' % (config.IMAGE_DIR, instrument_no))
        image = open(
            's/%s_date_hi.png' % (config.IMAGE_DIR, instrument_no),
            'rb')
        return image

    def send_tweet(self, message, image):
        # twitter.update_status_with_media(status = message, media = image)
        print 'Characters left over: ', \
            140 - len(message.split('.')[0] + '. ') - 22 - 23
        print message

if __name__ == '__main__':
    TwitterPreparer().main(0)
