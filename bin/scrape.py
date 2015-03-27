# -*- coding: utf-8 -*-

import time
import os
import re
import glob
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta

import pythonEmail
from landrecords.settings import dev_config

driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs',
                             port=0)
# driver = webdriver.Firefox(timeout=60)

start_date = datetime(2014, 2, 18)
today_date = datetime.now()
yesterday_date = datetime.now() - timedelta(days=1)

date_range_html = ''

logger = logging.getLogger(__name__)


def initialize_log():
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler('logs/scrape.log')
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s'
                                  ' - %(levelname)s - %(lineno)d - '
                                  '%(message)s')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)


def login():
    logger.info('login')

    # Load homepage
    logger.info('Load homepage')
    driver.get("http://onlinerecords.orleanscivilclerk.com/")
    time.sleep(2.2)

    # Login link
    logger.info('Find login link')
    login_link_elem = driver.find_element_by_id("Header1_lnkLogin")
    logger.info('Click login link')
    login_link_elem.click()
    time.sleep(1.2)

    # Username input
    logger.info('Find username field')
    unsername_elem = driver.find_element_by_id("Header1_txtLogonName")
    logger.info('Enter username')
    unsername_elem.send_keys(dev_config.LRD_USERNAME)

    # Password input
    logger.info('Find password field')
    password_elem = driver.find_element_by_id("Header1_txtPassword")
    logger.info('Enter password')
    password_elem.send_keys(dev_config.LRD_PASSWORD)
    logger.info('Return')
    password_elem.send_keys('\n')  # To trigger search function
    time.sleep(2.2)

    logger.debug(driver.title)


def navigate_search_page(year, month, day):
    logger.info('navigate_search_page')

    logger.debug("Load http://onlinerecords.orleanscivilclerk.com/"
                 "RealEstate/SearchEntry.aspx")
    driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/"
               "SearchEntry.aspx")
    time.sleep(2.2)

    logger.info('Find permanent date range')
    date_range_elem = driver.find_element_by_id("cphNoMargin_lblSearchSummary")

    date_range = date_range_elem.text
    logger.debug(date_range)

    first_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                          date_range).group(1)  # 02/18/2014
    first_date = first_date.replace('/', '')
    logger.debug(first_date)

    second_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                           date_range).group(2)  # 02/25/2015
    second_date = second_date.replace('/', '')
    logger.debug(second_date)

    date_range_html = driver.page_source

    # Delete old file first
    logger.info('Delete old permanent-date-range-when-scraped*.html file')
    for fl in glob.glob("""
        %s/raw/%s-%s-%s/permanent-date-range-when-scraped*.html
        """ % (
            dev_config.DATA_DIR, year, month, day)):
        os.remove(fl)

    # Save permanent date range for this individual sale.
    logger.info('Save new permanent-date-range-when-scraped*.html file')
    individual_html_out = open("""
        %s/raw/%s-%s-%s/permanent-date-range-when-scraped_%s-%s.html
        """ % (dev_config.DATA_DIR, year, month, day, first_date, second_date),
        "w")
    individual_html_out.write(date_range_html.encode('utf-8'))
    individual_html_out.close()

    # Delete old file first
    logger.info('Delete old most-recent-permanent-date-range/*.html file')
    for fl in glob.glob("%s/most-recent-permanent-date-range/*.html"
                        % (dev_config.DATA_DIR)):
            os.remove(fl)

    # Save permanent date range for overall sales.
    logger.info('Save new most-recent-permanent-date-range/*.html file')
    overall_html_out = open("""
        %s/most-recent-permanent-date-range/%s-%s.html
        """ % (dev_config.DATA_DIR, first_date, second_date),
        "w")
    overall_html_out.write(date_range_html.encode('utf-8'))
    overall_html_out.close()

    time.sleep(2.2)


def search_parameters(year, month, day):
    logger.info('search_parameters')

    search_date = month + day + year
    logger.debug(search_date)

    # Advanced tab
    logger.info('Find advanced tab')
    advanced_tab_elem = driver.find_element_by_id("x:2130005445.2:mkr:ti1")
    logger.info('Click on advanced tab')
    advanced_tab_elem.click()
    time.sleep(1.2)

    # "Date filed from" input
    logger.info('Find date from input')
    date_file_from_elem = driver.find_element_by_id("x:2002578730.0:mkr:3")
    logger.info('Click in input')
    date_file_from_elem.click()
    logger.info('Enter begin date')
    date_file_from_elem.send_keys(search_date)

    # "Date filed to" input
    logger.info('Find date to input')
    date_file_to_elem = driver.find_element_by_id("x:625521537.0:mkr:3")
    logger.info('Click in input')
    date_file_to_elem.click()
    logger.info('Enter end date')
    date_file_to_elem.send_keys(search_date)

    # Select "SALE" in document type dropdown
    logger.info('Find SALE document type')
    document_type_elem = driver.find_element_by_id(
        "cphNoMargin_f_dclDocType_291")
    logger.info('Select SALE document type')
    document_type_elem.click()

    # Click "Search"
    logger.info('Find search button')
    search_button_elem = driver.find_element_by_id(
        "cphNoMargin_SearchButtons2_btnSearch__2")
    logger.info('Click search button')
    search_button_elem.click()
    time.sleep(2.2)


def parse_results(year, month, day):
    logger.info('parse_results')

    # Find current page number
    try:
        logger.info('Find item_list_elem')  # todo: Better description
        item_list_elem = driver.find_element_by_id(
            "cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
        logger.info('Find option')
        options = item_list_elem.find_elements_by_tag_name("option")
    except Exception, e:
        # Save table page
        logger.error(e, exc_info=True)
        logger.info('No sales for this day')
        html_out = open("%s/raw/%s-%s-%s/page-html/page1.html"
                        % (dev_config.DATA_DIR, year, month, day), "w")
        html_out.write((driver.page_source).encode('utf-8'))
        html_out.close()
        return

    print options  # todo: what is this? todo: log it?

    total_pages = int(options[-1].get_attribute('value'))
    logger.debug(total_pages)

    for i in range(1, total_pages + 1):
        logger.debug(i)

        # Save table page
        logger.info('Write table page HTML')
        html_out = open("%s/raw/%s-%s-%s/page-html/page%d.html"
                        % (dev_config.DATA_DIR, year, month, day, i), "w")
        html_out.write((driver.page_source).encode('utf-8'))
        html_out.close()

        logger.info('Build BeautifulSoup')
        soup = BeautifulSoup(open("%s/raw/%s-%s-%s/page-html/page%d.html"
                             % (dev_config.DATA_DIR, year, month, day, i)))

        logger.info('Find all object IDs')
        rows = soup.find_all('td', class_="igede12b9e")  # List of Object IDs

        logger.debug(len(rows))

        for j in range(1, len(rows)):
            logger.debug((i - 1) * 20 + j)

            document_id = rows[j].string

            logger.debug(document_id)

            single_sale_url = "http://onlinerecords.orleanscivilclerk.com/" \
                              "RealEstate/SearchResults.aspx?global_id=%s" \
                              "&type=dtl" % (document_id)

            logger.debug(single_sale_url)

            try:
                logger.info('Load %s', single_sale_url)
                driver.get(single_sale_url)
                time.sleep(1.2)
            except Exception, e:
                logger.error(e, exc_info=True)

            logger.info('Save this sale HTML')
            html_out = open("""
                %s/raw/%s-%s-%s/form-html/%s.html
                """ % (dev_config.DATA_DIR, year, month, day, document_id),
                "w")
            html_out.write((driver.page_source).encode('utf-8'))
            html_out.close()

            time.sleep(1.2)

        logger.info('Go to http://onlinerecords.orleanscivilclerk.com/'
                    'RealEstate/SearchResults.aspx')
        driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/"
                   "SearchResults.aspx")

        logger.info('Find next page button')
        next_button_elem = driver.find_element_by_id("OptionsBar1_imgNext")
        logger.info('Click next page button')
        next_button_elem.click()
        time.sleep(2.2)

    # driver.get("http://onlinerecords.orleanscivilclerk.com/
    # RealEstate/SearchResults.aspx")


def logout():
    logger.info('logout')

    # No matter which page you're on, you can go back here and logout.
    logger.info('Load http://onlinerecords.orleanscivilclerk.com/'
                'RealEstate/SearchEntry.aspx')
    driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/"
               "SearchEntry.aspx")

    logger.info('Find logout button')
    logout_elem = driver.find_element_by_id("Header1_lnkLogout")
    logger.info('Click logout button')
    logout_elem.click()


def cycle_through_dates(from_date, until_date):
    logger.info('cycle_through_dates')

    logger.debug(from_date)
    logger.debug(until_date)

    end_date = until_date + timedelta(days=1)
    logger.debug(end_date)

    while from_date.strftime('%Y-%m-%d') != end_date.strftime('%Y-%m-%d'):
        logger.debug(from_date)
        logger.debug(end_date)

        year = (from_date).strftime('%Y')  # "2014"
        month = (from_date).strftime('%m')  # "09"
        day = (from_date).strftime('%d')  # "09"

        logger.debug(year + '-' + month + '-' + day)

        # Check if folder for this day exists. if not, then make one
        pagedir = "%s/raw/%s-%s-%s/page-html" % (
            dev_config.DATA_DIR, year, month, day)
        logger.debug(pagedir)

        formdir = "%s/raw/%s-%s-%s/form-html" % (
            dev_config.DATA_DIR, year, month, day)
        logger.debug(formdir)

        if not os.path.exists(pagedir):
            logger.info('Making %s', pagedir)
            os.makedirs(pagedir)
        if not os.path.exists(formdir):
            logger.info('Making %s', formdir)
            os.makedirs(formdir)

        # The good stuff
        navigate_search_page(year, month, day)

        search_parameters(year, month, day)

        parse_results(year, month, day)

        from_date = from_date + timedelta(days=1)
        logger.debug(from_date)


def main(from_date=start_date, until_date=yesterday_date):
    initialize_log()
    logger.info('main')

    login()

    try:
        cycle_through_dates(from_date, until_date)
    except Exception, e:
        logger.error(e, exc_info=True)
        pythonEmail.main(
            email_subject="Error running Land Record's scrape.py script",
            email_body='Check scrape.log for more details.')
    finally:
        logout()
        driver.close()
        driver.quit()
        logger.info('Done!')

if __name__ == '__main__':
    # main(from_date = datetime(2015, 3, 9),
    # until_date = datetime(2015, 3, 11))
    # Default is entire archive from Feb. 18, 2014, to yesterday.
    main(from_date=yesterday_date, until_date=yesterday_date)
