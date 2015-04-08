# -*- coding: utf-8 -*-

import psycopg2
import pprint
from fabric.api import local
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config
from landrecords.lib.log import Log
from landrecords.lib import (
    build,
    # check_assessor_urls,
    check_temp_status,
    clean,
    geocode,
    mail,
    publish,
    stat_analysis
)

pp = pprint.PrettyPrinter()

Base = declarative_base()
engine = create_engine(config.SERVER_ENGINE)

conn = psycopg2.connect(config.SERVER_CONNECTION)
cur = conn.cursor()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today_date = datetime.now
year = (datetime.now() - timedelta(days=1)).strftime('%Y')  # "2014"
month = (datetime.now() - timedelta(days=1)).strftime('%m')  # "09"
day = (datetime.now() - timedelta(days=1)).strftime('%d')  # "09"


def generate_email(initial_date=None, until_date=None):
    stat = stat_analysis.StatAnalysis('cleaned', initial_date, until_date)

    # todo: handle if either or both dates not specified?
    email_string = (
        '<p>http://vault.thelensnola.org/realestate/search?d1={0}&d2={1}' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{2} sales recorded on {3} to {4}.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{5} records not published because of questionable data.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>{6} records not published because location could not be found.' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>http://vault.thelensnola.org/realestate/dashboard' +
        '</p>' +
        '\n' +
        '\n' +
        '<p>High: ${7}</p>' +
        '\n' +
        '\n' +
        '<p>Low: ${8}</p>' +
        '\n' +
        '\n'
    ).format(
        initial_date.strftime('%m/%d/%Y'),
        until_date.strftime('%m/%d/%Y'),
        format(stat.count(), ','),
        initial_date.strftime('%A, %b. %-d, %Y'),
        until_date.strftime('%A, %b. %-d, %Y'),
        format(stat.detail_not_published(), ','),
        format(stat.location_not_published(), ','),
        format(stat.highest_amount(), ','),
        format(stat.lowest_amount(), ',')
    )

    rows = stat.all_records()

    message = ''
    for row in rows:
        if row['document_date'] is None:
            message += '<p><strong>Sale date</strong><br>None<br>\n'
        else:
            message += (
                '<p><strong>Sale date</strong><br>' +
                row['document_date'].strftime('%A, %b. %-d, %Y') +
                '<br>\n')
        message += (
            '<strong>Amount</strong><br>${0}<br>\n' +
            '<strong>Buyers</strong><br>{1}<br>\n' +
            '<strong>Sellers</strong><br>{2}<br>\n' +
            '<strong>Address</strong><br>{3}<br>\n' +
            '<strong>Location info</strong><br>{4}<br>\n' +
            '<strong>Zip</strong><br>{5}<br>\n' +
            '<strong>Neighborhood</strong><br>{6}</p>\n'
        ).format(
            format(row['amount'], ','),
            row['buyers'],
            row['sellers'],
            row['address'],
            row['location_info'],
            row['zip_code'],
            row['neighborhood']
        )

        email_string += message.encode('utf8')
        email_string += '\n'
        message = ''

    return email_string


def send_email(subject='Subject',
               body='Body',
               initial_date=yesterday_date,
               until_date=yesterday_date):
    log.info('sendEmail')
    # if os.path.isfile("logs/email-%s.txt" % datetime.now()
    # .strftime('%Y-%m-%d')):
    #     os.remove("logs/email-%s.txt" % datetime.now().strftime('%Y-%m-%d'))

    send_email.main(subject=subject,
                    body=body,
                    initial_date=initial_date,
                    until_date=until_date)


def update_cleaned_geom():
    log.info('updateCleanedGeom')
    local('''psql landrecords -c
        "UPDATE cleaned
        SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"''')


def do_it_all(initial_date='2014-02-18', until_date=yesterday_date):
    build.Build(initial_date=initial_date, until_date=until_date).build_all()
    geocode.Geocoder()  # Geocoding entire archive can take over an hour.
    publish.PublishChecker(
        initial_date=initial_date, until_date=until_date
    ).check_them_all()
    clean.Clean(initial_date=initial_date, until_date=until_date)

    # # if initial_date != until_date: # Assumes any range of dates also wants
    # # this function.
    # # Don't uncomment: copyDashboardToCleaned()
    # update_cleaned_geom()

    # check_temp_status.CheckTemp().check_permanent_status_of_new_sales()
    # check_temp_status.CheckTemp().check_permanent_status_of_temp_sales()

    # body = generate_email(
    #     initial_date='2015-03-13',
    #     until_date=until_date)
    # mail(
    #     subject="Land records summary for %s to %s" % (
    #         initial_date, until_date),
    #     body=body,
    #     frm='tthoren@thelensnola.org',
    #     to=['tthoren@thelensnola.org'])

    # check_assessor_urls().check(
    #     initial_date=initial_date, until_date=until_date)

if __name__ == '__main__':
    log = Log('initialize').logger

    try:
        do_it_all(initial_date='2014-02-18', until_date='2014-02-18')
        # Default is to build entire archive since 2014/02/18
        # doItAll(initial_date='2014-02-18', until_date=yesterday_date)
    except Exception, e:
        log.error(e, exc_info=True)
        mail.Mail(subject="Error running Land Record's initialize.py script",
                  body='Check initialize.log for more details.',
                  frm='tthoren@thelensnola.org',
                  to=['tthoren@thelensnola.org'])

    session.close()
    cur.close()
    conn.close()
    print "Done!"
    log.info('Done!')
