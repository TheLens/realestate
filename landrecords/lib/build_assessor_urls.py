# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import urllib2
import re
import time
import random

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from databasemaker import Cleaned
from sqlalchemy.orm import sessionmaker
from app_config import server_connection, server_engine

# from landrecords import log

# todo: move this into class

Base = declarative_base()

conn = psycopg2.connect("%s" % (server_connection))
c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
pp = pprint.PrettyPrinter()
engine = create_engine('%s' % (server_engine))


def get_error_page_html(url):
    error_req = urllib2.Request(
        url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/39.0.2171.99 Safari/537.36'})
    error_con = urllib2.urlopen(error_req)
    error_html = error_con.read()
    error_con.close()

    return error_html


def form_assessor_url(location):
    # todo: what if multiple addresses. which to use to form assessor's link?
    # todo: need to account for N/S/E/W designations.
    # Ex: S. Saratoga St. has url_param = 2617-SSARATOGAST. Maybe need to
    # ignore the cardinal direction? Seems like it is always
    # necessary if present though.

    location = location.strip()
    location = location.upper()

    # print location

    address_number = re.match(r"[^ \-]*", location).group(0)
    # print "address_number:", address_number

    if address_number == 'UNIT:':
        return None

    street = re.match(r"\S+\s([^\,]*)", location).group(1)

    street_direction = street.split(' ')[0]

    cond = (street_direction == "N." or
            street_direction == "S." or
            street_direction == "E." or
            street_direction == "W.")

    if cond:
        street_direction = street_direction[0]
    else:
        street_direction = ''

    street_type = street.split(' ')[-1]

    # Taken from:
    # http://en.wikipedia.org/wiki/Street_or_road_name#Street_type_designations
    abbreviations = [
        # Major roads
        ['HIGHWAY', 'HW'],
        ['FREEWAY', ''],
        ['AUTOROUTE', ''],
        ['AUTOBAHN', ''],
        ['EXPRESSWAY', ''],
        ['AUTOSTRASSE', ''],
        ['AUTOSTRADA', ''],
        ['BYWAY', ''],
        ['AUTO-ESTRADA', ''],
        ['MOTORWAY', ''],
        ['PIKE', ''],
        ['AVENUE', 'AV'],
        ['BOULEVARD', 'BL'],
        ['ROAD', 'RD'],
        ['STREET', 'ST'],
        # Small roads
        ['ALLEY', ''],
        ['BAY', ''],
        ['BEND', ''],
        ['DRIVE', 'DR'],
        ['FAIRWAY', ''],
        ['GARDENS', ''],
        ['GATE', ''],
        ['GROVE', ''],
        ['HEIGHTS', ''],
        ['HIGHLANDS', ''],
        ['KNOLL', ''],
        ['LANE', 'LN'],
        ['MANOR', ''],
        ['MEWS', ''],
        ['PATHWAY', ''],
        ['TERRACE', ''],
        ['TRAIL', ''],
        ['VALE', ''],
        ['VIEW', ''],
        ['WALK', ''],
        ['WAY', ''],
        ['WYND', ''],
        # Culs-de-sac
        ['CLOSE', ''],
        ['COURT', 'CT'],
        ['PLACE', 'PL'],
        ['COVE', ''],
        # Shapes
        ['CIRCLE', ''],
        ['CRESCENT', ''],
        ['DIAGONAL', ''],
        ['LOOP', ''],
        ['QUADRANT', ''],
        ['SQUARE', ''],
        # Geographic attributes
        ['HILL', ''],
        ['GRADE', ''],
        ['CAUSEWAY', ''],
        ['CANYON', ''],
        ['RIDGE', ''],
        ['PARKWAY', 'PW'],
        # Functions
        ['ESPLANADE', ''],
        ['APPROACH', ''],
        ['FRONTAGE', ''],
        ['PARADE', ''],
        ['PARK', ''],
        ['PLAZA', ''],
        ['PROMENADE', ''],
        ['QUAY', ''],
        ['BYPASS', ''],
        ['STRAVENUE', '']
    ]
    street_type_abbr = street_type
    for abbreviation in abbreviations:
        abbr0 = abbreviation[0]
        abbr1 = abbreviation[1]
        street_type_abbr = re.sub(abbr0, abbr1, street_type_abbr)

    unit = re.match(r"^.*UNIT\: (.*)\, CONDO", location).group(1)
    # print "unit:", unit

    street = " ".join(street.split()[0:-1])

    # Be careful about regex patterns
    assessor_abbreviations = [
        [r"GRAND ROUTE ST\. JOHN", "GRANDRTESTJO"],  # Grand Route St. John
        [r'GENERAL', 'GEN'],  # General xxx
        [r'ST\.', 'ST'],  # St. xxx
        [r"ROUTE", 'RTE']
    ]

    # print "street (before):", street
    for assessor_abbr in assessor_abbreviations:
        abbr0 = assessor_abbr[0]
        abbr1 = assessor_abbr[1]
        street = re.sub(abbr0, abbr1, street)
    street = "".join(street.split())  # remove spaces
    # print "street (after):", street

    url_param = address_number + unit + '-' + \
        street_direction + street + street_type_abbr
    # print "url_param:", url_param

    return url_param


def array_len(array):
    f = open("assessor_problem_urls.txt", "a")

    num_lines = 0

    print "================="
    f.write("=====================")

    print "Problematic URLs:"
    f.write("Problematic URLs:")

    for line in array:
        print line
        f.write(line)
        num_lines = num_lines + 1

    print "# of problem URLs:", num_lines
    f.write("# of problem URLs: %d" % num_lines)

    f.close()


def test_url(url, error_html):
    req = urllib2.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X ' +
                                    '10_9_5) AppleWebKit/537.36 (KHTML, ' +
                                    'like Gecko) Chrome/39.0.2171.99 ' +
                                    'Safari/537.36'})
    con = urllib2.urlopen(req)
    html = con.read()
    con.close()

    f = open("assessor_problem_urls.txt", "a")

    if html == error_html:
        f.write("%s\n" % url)
        f.close()
        return url
    else:
        f.close()
        return None


def get_instrument_numbers():
    Base.metadata.create_all(engine)
    sn = sessionmaker(bind=engine)
    session = sn()

    open('assessor_problem_urls.txt', 'w').close()  # Blank slate
    f = open("assessor_problem_urls.txt", "a")

    q = session.query(  # todo: limit to instrument numbers and locations
        Cleaned
    ).all()  # .filter(Cleaned.detail_publish == '1')

    locations = []
    url_params = []
    assessor_urls = []

    print "# of records:", len(q)
    f.write("# of records: %d" % len(q))

    for u in q:
        locations.append(u.location)

    session.close()

    for location in locations:
        url_params.append(form_assessor_url(location))

    for url_param in url_params:
        if url_param is None:
            continue
        else:
            assessor_urls.append(
                "http://qpublic9.qpublic.net/" +
                "la_orleans_display.php?KEY=%s" % (url_param))

    print "# of assessor URLs to check:", len(assessor_urls)
    f.write("# of assessor URLs to check: %d" % len(assessor_urls))

    error_html = get_error_page_html(
        "http://qpublic9.qpublic.net/la_orleans_display" +
        ".php?KEY=7724-BURTHESTt")

    problem_urls = []

    for i, assessor_url in enumerate(assessor_urls):
        if assessor_url == '':
            print 'this should never print'
            f.write("This should never appear.")

            continue
        else:
            response = test_url(assessor_url, error_html)
            if response is not None:
                problem_urls.append(response)

        # if i == 5:
        #     break

        time.sleep(random.randint(3, 5) + random.uniform(1.0, 2.0))

    # Find number of problem URLs
    array_len(problem_urls)

    f.close()

if __name__ == '__main__':
    get_instrument_numbers()
    # form_assessor_url("7471 Restgate Road, Unit: , Condo: , Weeks: ,
    # Subdivision: Lake Forest No 8 Warwick East, District: 3rd,
    # Square: 7, Lot: 2")
