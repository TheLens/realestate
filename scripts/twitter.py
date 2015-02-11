# -*- coding: utf-8 -*-

#todo: run this separate from 3 a.m. scrape/initialize/etc cron job.
# run this on a cron at same time we want to tweet.

import psycopg2
import psycopg2.extras
import pprint
import random
import sys

from fabric.api import local
from twython import Twython
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databasemaker import Cleaned
from datetime import datetime, timedelta
from app_config import server_connection, server_engine, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

pp = pprint.PrettyPrinter()

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

conn = psycopg2.connect("%s" % (server_connection))
c = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (server_engine))

Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()

def figureOutRecordedDate():
    today_date = datetime.now()

    document_recorded = ''

    # Assuming we wanted to tweet a Friday sale on Sunday and Monday, which we don't.
    '''
    if today_date.strftime('%A') == 'Sunday':
        document_recorded = (today_date - timedelta(days = 2)).strftime('%Y-%m-%d')

    if today_date.strftime('%A') == 'Monday':
        document_recorded = (today_date - timedelta(days = 3)).strftime('%Y-%m-%d')
    '''

    # If today is Sunday or Monday, don't tweet because there is nothing new to tweet. Friday sales would have been tweeted on Saturday. Monday sales won't be recorded and ready for tweetin' until Tuesday.
    if today_date.strftime('%A') == 'Sunday' or today_date.strftime('%A') == 'Monday':
        sys.exit()

    return document_recorded

def getHighestAmountDetails(document_recorded):
    q = session.query(
            Cleaned
        ).filter(
            Cleaned.detail_publish == '1'
        ).filter(
            Cleaned.document_recorded == '%s' % '2014-02-18'#todo: switch to document_recorded for server
        ).order_by(
            Cleaned.amount.desc()
        ).limit(1).all()

    # If no record found, terminate this script so it doesn't tweet out nonsense. Could be because of federal holidays, the city didn't enter records on a given day, or any number of other reasons.
    if len(q) == 0:
        sys.exit()

    amount = 0
    instrument_no = ''
    document_recorded = ''
    document_date = ''
    for u in q:
        amount = u.amount
        document_recorded = (u.document_recorded).strftime('%A')#.strftime('%A, %b. %-d, %Y')
        document_date = u.document_date.strftime('%A')
        instrument_no = u.instrument_no

    print instrument_no
    print amount

    amount = '$' + format(amount, ',')
    
    return (amount, instrument_no, document_recorded, document_date)

def formURL(instrument_no):
    url = 'http://vault.thelensnola.org/realestate/sale/' + instrument_no
    return url

def formMessage(amount, url, document_recorded, document_date):
    options = []

    # Normal amounts
    options.append("The most expensive property sale reported %s was for %s. %s" % (document_recorded, amount, url))
    options.append("The most expensive property sale reported %s was for %s. %s" % (document_recorded, amount, url))

    # High amounts
    if amount >= 1000000:
        #options = []
        options.append("We're moving on up! A property sale on %s went for %s. %s" % (document_date, amount, url))
        options.append("Let them have it! This property sold for %s on %s. %s" % (amount, document_date, url))

    option = random.choice(options)

    return option

def getImage(instrument_no):
    local('/Users/Tom/projects/land-records/repo/scripts/phantomjs screen.js http://localhost:5000/realestate/sale/{0} images/{0}.png'.format(instrument_no))
    image = open('images/%s.png' % (instrument_no), 'rb')
    return image

def sendTweet(message, image):
    #twitter.update_status_with_media(status = message, media = image)
    print 'Characters left over: ', 140 - len(message.split('.')[0] + '. ') - 22 - 23
    print message

if __name__ == '__main__':
    document_recorded = figureOutRecordedDate()
    amount, instrument_no, document_recorded, document_date = getHighestAmountDetails(document_recorded)
    print 'instrument_no: ', instrument_no
    image = getImage(instrument_no)
    url = formURL(instrument_no)
    message = formMessage(amount, url, document_recorded, document_date)
    sendTweet(message, image)

    image.close()
    session.close()
