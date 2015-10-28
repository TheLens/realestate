# -*- coding: utf-8 -*-

'''
The daily scraper that checks for the previous day's sales and saves the HTML
for those records. It uses [Selenium](
https://github.com/SeleniumHQ/selenium/tree/master/py) and [PhantomJS](
http://phantomjs.org/). This also makes a note of when each date was scraped
and what the Land Records Division's permanent date range was at the time of
that scrape (see `check_temp_status.py` for details).
'''

import os
import re
import sys
import time
import glob
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import timedelta, datetime
from realestate.lib.mail import Mail
from realestate import (
    log, YESTERDAY_DAY, PROJECT_DIR, LOG_DIR
)


class Scrape(object):

    '''
    Navigate and scrape the Land Records Division.
    Scrape the Land Records Division. Give it the date range you want and it
    will download the HTML in /data/raw.
    '''

    # todo: write function with rewrite = False that ignores any
    # sales previously scraped.
    def __init__(self,
                 initial_date=YESTERDAY_DAY,
                 until_date=YESTERDAY_DAY,
                 rewrite=True):
        '''Initialize self variables and PhantomJS browser.'''

        self.initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
        self.until_date = datetime.strptime(until_date, '%Y-%m-%d')

        self.driver = webdriver.PhantomJS(
            executable_path='%s/scripts/phantomjs' % PROJECT_DIR,
            service_log_path='%s/realestate.log' % LOG_DIR,
            port=0)
        # self.driver = webdriver.Firefox(timeout=60)

    # Login page
    def load_homepage(self):
        '''Load homepage.'''

        log.info('Load homepage')
        self.driver.get("http://onlinerecords.orleanscivilclerk.com/")
        time.sleep(1.2)

    def find_login_link(self):
        '''Find and click on login link.'''

        log.info('Find login link')
        login_link_elem = self.driver.find_element_by_id("Header1_lnkLogin")
        log.info('Click login link')
        login_link_elem.click()
        time.sleep(4.2)

    def enter_username(self):
        '''Type in username.'''

        log.info('Find username field')
        unsername_elem = self.driver.find_element_by_id("Header1_txtLogonName")
        log.info('Enter username')
        unsername_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_USERNAME'))
        time.sleep(4.2)

    def enter_password(self):
        '''Type in password.'''

        log.info('Find password field')
        password_elem = self.driver.find_element_by_id("Header1_txtPassword")
        log.info('Enter password')
        password_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_PASSWORD'))
        log.info('Return')
        password_elem.send_keys('\n')  # To trigger search function
        time.sleep(4.2)

        log.debug(self.driver.title)

    def login(self):
        '''Load homepage, find login, enter credentials.'''

        self.load_homepage()
        self.find_login_link()
        self.enter_username()
        self.enter_password()

    # Navigate search page
    def load_search_page(self):
        '''Load search page.'''

        # might not have loaded for server scrape:
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")
        time.sleep(4.2)

    def find_permanent_date_range(self):
        '''Parse search page for permanent date range.'''

        # wasn't found in server scraper error:
        date_range_elem = self.driver.find_element_by_id(
            "cphNoMargin_lblSearchSummary")

        date_range = date_range_elem.text
        log.debug(date_range)

        first_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                              date_range).group(1)  # 02/18/2014
        first_date = first_date.replace('/', '')
        log.debug(first_date)

        second_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                               date_range).group(2)  # 02/25/2015
        second_date = second_date.replace('/', '')
        log.debug(second_date)

        return first_date, second_date

    def get_date_range_html(self):
        '''Get search page HTML.'''

        date_range_html = self.driver.page_source

        return date_range_html

    @staticmethod
    def delete_permanent_date_range_when_scraped_file(year, month, day):
        '''Delete old permanent-date-range-when-scraped*.html.'''

        log.info('Delete old permanent-date-range-when-scraped*.html')

        for file_path in glob.glob("%s/data/raw/" % (PROJECT_DIR) +
                                   "%s-%s-%s/" % (year, month, day) +
                                   "permanent-date-range-when-scraped*.html"):
            os.remove(file_path)

    @staticmethod
    def save_permanent_date_range_when_scraped_file(year, month, day,
                                                    date_range_html,
                                                    first_date, second_date):
        """Save new permanent-date-range-when-scraped*.html."""

        # Save permanent date range for this individual sale.
        log.info('Save new permanent-date-range-when-scraped*.html file')
        individual_html_out = open(
            "%s/data/raw/" % PROJECT_DIR +
            "%s-%s-%s/permanent-date-range-when-scraped" % (year, month, day) +
            "_%s-%s.html" % (first_date, second_date),
            "w")
        individual_html_out.write(date_range_html.encode('utf-8'))
        individual_html_out.close()

    @staticmethod
    def delete_permanent_date_range_file():
        '''Delete old most-recent-permanent-date-range/*.html.'''

        # Delete old file first
        log.info(
            'Delete old most-recent-permanent-date-range/*.html file')

        file_string = "%s/data/most-recent-permanent-date-range/*.html" % (
            PROJECT_DIR)
        for file_path in glob.glob(file_string):
            os.remove(file_path)

    @staticmethod
    def save_permanent_date_range_file(date_range_html,
                                       first_date,
                                       second_date):
        '''Save new most-recent-permanent-date-range/*.html.'''

        log.info('Save new most-recent-permanent-date-range/*.html file')
        overall_html_out = open("%s/data/" % (PROJECT_DIR) +
                                "most-recent-permanent-date-range/" +
                                "%s-%s.html" % (first_date, second_date),
                                "w")
        overall_html_out.write(date_range_html.encode('utf-8'))
        overall_html_out.close()

        time.sleep(1.2)

    def navigate_search_page(self, year, month, day):
        '''Navigate search page to find permanent date range
           and update local date range files..'''

        self.load_search_page()
        first_date, second_date = self.find_permanent_date_range()
        date_range_html = self.get_date_range_html()
        self.delete_permanent_date_range_when_scraped_file(year, month, day)
        self.save_permanent_date_range_when_scraped_file(
            year, month, day, date_range_html, first_date, second_date)
        self.delete_permanent_date_range_file()
        self.save_permanent_date_range_file(
            date_range_html, first_date, second_date)

    # Search parameters
    def click_advanced_tab(self):
        '''Click on the advanced tab.'''

        log.info('search_parameters')

        # Advanced tab
        log.info('Find advanced tab')
        advanced_tab_elem = self.driver.find_element_by_id(
            "x:2130005445.2:mkr:ti1")
        log.info('Click on advanced tab')
        advanced_tab_elem.click()
        time.sleep(1.2)

    def enter_date_filed_from(self, search_date):
        '''Enter "date from".'''

        date_file_from_elem = self.driver.find_element_by_id(
            "x:1221134975.0:mkr:3")
        date_file_from_elem.click()
        date_file_from_elem.send_keys(search_date)

    def enter_date_filed_to(self, search_date):
        '''Enter "date to".'''

        date_file_to_elem = self.driver.find_element_by_id(
            "x:96043147.0:mkr:3")
        date_file_to_elem.click()
        date_file_to_elem.send_keys(search_date)

    def select_document_type(self):
        '''Select SALE document type in dropdown.'''

        document_type_elem = self.driver.find_element_by_id(
            "cphNoMargin_f_dclDocType_292")
        log.info('Select SALE document type')
        document_type_elem.click()

    def click_search_button(self):
        '''Click on the search button.'''

        log.info('Find search button')
        search_button_elem = self.driver.find_element_by_id(
            "cphNoMargin_SearchButtons2_btnSearch__2")
        log.info('Click search button')
        search_button_elem.click()
        time.sleep(1.2)

    def search_parameters(self, search_date):
        '''Enter search parameters.'''

        self.click_advanced_tab()
        self.enter_date_filed_from(search_date)
        self.enter_date_filed_to(search_date)
        self.select_document_type()
        time.sleep(1.2)
        self.click_search_button()

    # Parse results
    def parse_results(self, year, month, day):
        '''Parse initial result page for total number of sales.'''

        # Find current page number
        try:
            log.info('Find item_list_elem')
            item_list_elem = self.driver.find_element_by_id(
                "cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
            log.info('Find option')
            options = item_list_elem.find_elements_by_tag_name("option")
        except Exception, error:
            # Save table page
            log.error(error, exc_info=True)
            log.info('No sales for this day')
            html_out = open("%s/data/raw/%s-%s-%s/page-html/page1.html"
                            % (PROJECT_DIR, year, month, day), "w")
            html_out.write((self.driver.page_source).encode('utf-8'))
            html_out.close()
            return

        total_pages = int(options[-1].get_attribute('value'))
        log.debug('%d pages to parse for %s-%s-%s',
                  total_pages, year, month, day)

        for i in range(1, total_pages + 1):
            log.debug('Page: %d', i)

            self.parse_page(i, year, month, day)

    def parse_page(self, i, year, month, day):
        '''Parse results page for sale document IDs.'''

        # Save table page
        log.info('Parse results page table HTML')
        html_out = open("%s/data/raw/%s-%s-%s/page-html/page%d.html"
                        % (PROJECT_DIR, year, month, day, i), "w")
        html_out.write((self.driver.page_source).encode('utf-8'))
        html_out.close()

        bs_file = "%s/data/raw/%s-%s-%s/page-html/page%d.html" % (
            PROJECT_DIR, year, month, day, i)
        soup = BeautifulSoup(open(bs_file))

        log.info('Find all object IDs')

        rows = soup.find_all('td', class_="igede12b9e")  # List of Object IDs

        log.debug('There are %d rows for this page', len(rows))

        for j in range(1, len(rows)):
            log.debug(
                'Analyzing overall row %d for %s-%s-%s',
                (i - 1) * 20 + j, year, month, day)

            self.parse_sale(j, rows, year, month, day)

        log.info(
            'Go to http://onlinerecords.orleanscivilclerk.com/' +
            'RealEstate/SearchResults.aspx')
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchResults.aspx")

        log.info('Find next page button')
        next_button_elem = self.driver.find_element_by_id(
            "OptionsBar1_imgNext")
        log.info('Click next page button')
        next_button_elem.click()
        time.sleep(1.2)

    def parse_sale(self, j, rows, year, month, day):
        '''Parse single sale page and save HTML.'''

        document_id = rows[j].string

        log.debug(
            'Saving HTML for %s on %s-%s-%s', document_id, year, month, day)

        single_sale_url = (
            "http://onlinerecords.orleanscivilclerk.com/" +
            "RealEstate/SearchResults.aspx?" +
            "global_id=%s" % (document_id) +
            "&type=dtl")

        log.debug('Sale URL: %s', single_sale_url)

        try:
            log.info('Loading %s', single_sale_url)
            self.driver.get(single_sale_url)
            time.sleep(1.2)
        except Exception, error:
            log.error(error, exc_info=True)

        html = self.driver.page_source

        log.info('Save this sale HTML')

        html_file = "%s/data/raw/" % (PROJECT_DIR) + \
                    "%s-%s-%s/" % (year, month, day) + \
                    "form-html/%s.html" % (document_id)

        html_out = open(html_file, "w")
        html_out.write(html.encode('utf-8'))
        html_out.close()

        try:
            assert not self.check_if_error(html_file)
        except Exception, error:
            # todo: better way to track:
            log.debug('Deleting error page: %s', html_file)
            os.remove(html_file)
            log.error(error, exc_info=True)
            return

        time.sleep(1.2)

    @staticmethod
    def check_if_error(html):
        'Checks if the download single sale HTML is an error page'

        soup = BeautifulSoup(open(html))

        title = soup.find_all('title')[0].string

        if title == 'Error':
            log.debug('Error page was downloaded')
            return True
        else:
            return False

    # Logout
    def logout(self):
        '''Logout of site.'''

        # No matter which page you're on, you can go back here and logout.
        log.info(
            'Load http://onlinerecords.orleanscivilclerk.com/' +
            'RealEstate/SearchEntry.aspx')
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")

        log.info('Find logout button')
        logout_elem = self.driver.find_element_by_id("Header1_lnkLogout")
        log.info('Click logout button')
        logout_elem.click()

    def cycle_through_dates(self):
        '''For each date in range specified, fill out search,
           parse results and save the HTML.'''

        current_date = self.initial_date

        # Must search each date one at a time because there is a limit of
        # 300 results per search.
        while current_date != (self.until_date + timedelta(days=1)):
            log.debug(current_date)
            log.debug(self.until_date)

            year = current_date.strftime('%Y')  # "2014"
            month = current_date.strftime('%m')  # "09"
            day = current_date.strftime('%d')  # "09"

            log.debug(year + '-' + month + '-' + day)

            # Check if folder for this day exists. If not, then make one.
            pagedir = "%s/data/raw/%s-%s-%s/page-html" % (
                PROJECT_DIR, year, month, day)
            log.debug(pagedir)

            formdir = "%s/data/raw/%s-%s-%s/form-html" % (
                PROJECT_DIR, year, month, day)
            log.debug(formdir)

            if not os.path.exists(pagedir):
                log.info('Making %s', pagedir)
                os.makedirs(pagedir)
            if not os.path.exists(formdir):
                log.info('Making %s', formdir)
                os.makedirs(formdir)

            search_date = month + day + year

            # The meat of this loop
            self.navigate_search_page(year, month, day)
            self.search_parameters(search_date)
            self.parse_results(year, month, day)

            current_date += timedelta(days=1)
            log.debug(current_date)

    def main(self):
        '''The main scrape method.'''

        self.login()

        try:
            self.cycle_through_dates()
        except Exception, error:
            print error
            log.error(error, exc_info=True)
            Mail(
                subject="Error running Land Record's scrape.py script",
                body='Check scrape.log for more details.',
                frm='tthoren@thelensnola.org',
                to=['tthoren@thelensnola.org']).send_as_text()
        finally:
            self.logout()
            self.driver.close()
            self.driver.quit()
            log.info('Done!')

if __name__ == '__main__':
    if len(sys.argv) < 2:  # No arguments, default to yesterday date.
        Scrape().main()
    elif len(sys.argv) == 2:  # One argument
        day = sys.argv[1]

        Scrape(
            initial_date=day,
            until_date=day
        ).main()
    elif len(sys.argv) == 3:  # Two arguments
        initial_day = sys.argv[1]
        until_day = sys.argv[2]

        Scrape(
            initial_date=initial_day,
            until_date=until_day
        ).main()
    elif len(sys.argv) > 3:
        print (
            "Too many arguments. Enter a single date to scrape that one " +
            "day, enter two days to scrape a range of days, or do not " +
            "enter any days at all to scrape yesterday. " +
            "Use the format 'YYYY-MM-DD'.")
