# -*- coding: utf-8 -*-

"""
Scrape property sales records from the Land Records Division.

It uses [Selenium](http://github.com/SeleniumHQ/selenium/tree/master/py) and
[PhantomJS](http://phantomjs.org/) to save the HTML.
This also makes a note of when each date was scraped and what the Land Records
Division's permanent date range was at the time of that scrape (see
`check_temp_status.py` for details).

Usage:
    scrape.py
    scrape.py <single_date>
    scrape.py <early_date> <late_date>

Options:
    -h, --help  Show help screen.
    --version   Show version number.

Dates are in the format YYYY-MM-DD. Ex. 2016-12-31
"""

import os
import re
import glob
import time

from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from docopt import docopt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from www import log, YESTERDAY_DAY, PROJECT_DIR, WEBDRIVER_LOG

# Uncomment for local development and testing:
# from selenium.webdriver.common.desired_capabilities import (
#     DesiredCapabilities)


class BadDateRangeError(Exception):
    """Error for when date range is backward."""

    pass


class Scrape(object):
    """
    Navigate and scrape the Land Records Division.

    Scrape the Land Records Division. Give it the date range you want and it
    will download the HTML in /data/raw.
    """

    def __init__(self,
                 initial_date=YESTERDAY_DAY,
                 until_date=YESTERDAY_DAY,
                 rewrite=True):  # TODO: Allow false to avoid previous scrapes
        """Initialize self variables and PhantomJS browser."""
        self.initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
        self.until_date = datetime.strptime(until_date, '%Y-%m-%d')

        # PhantomJS for headless browser in production
        self.driver = webdriver.PhantomJS(
            executable_path='{}/scripts/phantomjs'.format(PROJECT_DIR),
            service_log_path=WEBDRIVER_LOG,
            port=0)

        # Firefox for visible browser during local development.
        #   https://developer.mozilla.org/en-US/docs/Mozilla/QA/
        #   Marionette/WebDriver
        # Download executable and rename as "wires":
        #   https://github.com/mozilla/geckodriver/releases

        # firefox_capabilities = DesiredCapabilities.FIREFOX
        # firefox_capabilities['marionette'] = True
        # self.driver = webdriver.Firefox(
        #     executable_path='{}/scripts/wires'.format(PROJECT_DIR),
        #     capabilities=firefox_capabilities,
        #     timeout=60)

        # Chrome
        # self.driver = webdriver.Chrome(
        #     '{}/scripts/chromedriver'.format(PROJECT_DIR),
        #     service_log_path=LOG_FILE)

    # Login page
    def load_homepage(self):
        """Load homepage."""
        url = 'http://onlinerecords.orleanscivilclerk.com/'
        log.info('Load homepage {}'.format(url))
        self.driver.get(url)

    def find_login_link(self):
        """Find and click on login link."""
        html_id = 'Header1_lnkLogin'

        log.info('Find login link at HTML ID {}'.format(html_id))
        login_link_elem = self.driver.find_element_by_id(html_id)

        log.info('Click login link')
        login_link_elem.click()

    def enter_username(self):
        """Type in username."""
        html_id = 'Header1_txtLogonName'

        log.info('Find username field at HTML ID {}'.format(html_id))
        username_elem = self.driver.find_element_by_id(html_id)

        log.info('Enter username from environment variable')
        username_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_USERNAME'))

    def enter_password(self):
        """Type in password."""
        html_id = 'Header1_txtPassword'

        log.info('Find password field at HTML ID {}'.format(html_id))
        password_elem = self.driver.find_element_by_id(html_id)

        log.info('Enter password from environment variable')
        password_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_PASSWORD'))

        log.info('Press enter to submit credentials and log in')
        # Trigger search function. Don't use RETURN because PhantomJS fails.
        password_elem.send_keys(Keys.ENTER)

    def login(self):
        """Load homepage, find login, enter credentials."""
        self.load_homepage()
        # time.sleep(1.0)

        self.find_login_link()

        log.info('Sleep 1.0 second')
        time.sleep(1.0)

        self.enter_username()

        log.info('Sleep 1.0 second')
        time.sleep(1.0)

        self.enter_password()

        log.info('Sleep 5.0 seconds')
        time.sleep(5.0)

        try:
            self.driver.find_element_by_id("Header1_lnkLogout")
            log.info("Login successful")
        except Exception as error:
            log.info("Login failed")
            log.exception(error)
            raise

    # Navigate search page
    def load_search_page(self):
        """Load search page."""
        # might not have loaded for server scrape:
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")

    def find_permanent_date_range(self):
        """Parse search page for permanent date range."""
        html_id = 'cphNoMargin_lblSearchSummary'

        log.info('Find permanent date range at HTML ID {}'.format(html_id))
        date_range_elem = self.driver.find_element_by_id(html_id)

        match = re.match(r"Permanent Index From ([0-9/]*) to ([0-9/]*)",
                         date_range_elem.text)

        first_date = match.group(1).replace('/', '')  # 02/18/2014
        second_date = match.group(2).replace('/', '')

        return first_date, second_date

    def get_date_range_html(self):
        """Get search page HTML."""
        return self.driver.page_source

    @staticmethod
    def delete_permanent_date_range_when_scraped_file(year, month, day):
        """Delete old permanent-date-range-when-scraped*.html."""
        log.info('Delete old permanent-date-range-when-scraped*.html')

        string = (
            "{0}/data/raw/{1}-{2}-{3}/" +
            "permanent-date-range-when-scraped*.html").format(
            PROJECT_DIR, year, month, day)

        for file_path in glob.glob(string):
            os.remove(file_path)

    @staticmethod
    def save_permanent_date_range_when_scraped_file(year, month, day,
                                                    date_range_html,
                                                    first_date, second_date):
        """Save new permanent-date-range-when-scraped*.html."""
        # Save permanent date range for this individual sale.
        log.info('Save new permanent-date-range-when-scraped*.html file')
        individual_html_out = open(
            (
                "{0}/data/raw/{1}-{2}-{3}/" +
                "permanent-date-range-when-scraped_{4}-{5}.html").format(
                PROJECT_DIR, year, month, day, first_date, second_date
            ),
            "wb")
        individual_html_out.write(date_range_html.encode('utf-8'))
        individual_html_out.close()

    @staticmethod
    def delete_permanent_date_range_file():
        """Delete old most-recent-permanent-date-range/*.html."""
        # Delete old file first
        log.info('Delete old most-recent-permanent-date-range/*.html file')

        file_string = "{}/data/most-recent-permanent-date-range/*.html".format(
            PROJECT_DIR)
        for file_path in glob.glob(file_string):
            os.remove(file_path)

    @staticmethod
    def save_permanent_date_range_file(date_range_html,
                                       first_date,
                                       second_date):
        """Save new most-recent-permanent-date-range/*.html."""
        log.info('Save new most-recent-permanent-date-range/*.html file')

        fn = "{0}/data/most-recent-permanent-date-range/{1}-{2}.html".format(
            PROJECT_DIR, first_date, second_date)

        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))

        overall_html_out = open(fn, "wb")
        overall_html_out.write(date_range_html.encode('utf-8'))
        overall_html_out.close()

    def navigate_search_page(self, year, month, day):
        """
        Navigate search page to find permanent date range.

        Update local date range files.
        """
        self.load_search_page()

        # log.info('Sleep 2.0 seconds')
        # time.sleep(2.0)

        first_date, second_date = self.find_permanent_date_range()

        date_range_html = self.get_date_range_html()

        self.delete_permanent_date_range_when_scraped_file(year, month, day)

        self.save_permanent_date_range_when_scraped_file(
            year, month, day, date_range_html, first_date, second_date)

        self.delete_permanent_date_range_file()

        self.save_permanent_date_range_file(
            date_range_html, first_date, second_date)

        time.sleep(1.0)

    # Search parameters
    def click_advanced_tab(self):
        """Click on the advanced tab."""
        html_id = 'x:2130005445.2:mkr:ti1'

        log.info('Find advanced tab at HTML ID {}'.format(html_id))
        advanced_tab_elem = self.driver.find_element_by_id(html_id)

        log.info('Click on advanced tab')
        advanced_tab_elem.click()

    def enter_date_filed_from(self, search_date):
        """Enter "date from"."""
        html_id = 'x:1221134975.0:mkr:3'

        log.info('Find "date filed from" field at HTML ID {}'.format(html_id))
        date_file_from_elem = self.driver.find_element_by_id(html_id)

        log.info('Click on "date filed from" field')
        date_file_from_elem.click()

        log.info('Enter {} into "date filed from" field'.format(search_date))
        date_file_from_elem.send_keys(search_date)

    def enter_date_filed_to(self, search_date):
        """Enter "date to"."""
        html_id = 'x:96043147.0:mkr:3'

        log.info('Find "date filed to" field at HTML ID {}'.format(html_id))
        date_file_to_elem = self.driver.find_element_by_id(html_id)

        log.info('Click on "date filed to" field')
        date_file_to_elem.click()

        log.info('Enter {} into "date filed to" field'.format(search_date))
        date_file_to_elem.send_keys(search_date)

    def select_document_type(self):
        """Select SALE document type in dropdown."""
        html_id = 'cphNoMargin_f_dclDocType_297'  # SALE

        # TODO: Assert text is SALE
        log.info('Find document type SALE at HTML ID {}'.format(html_id))
        doc_type_elem = self.driver.find_element_by_id(html_id)

        short_type = doc_type_elem.get_attribute('value')

        parent_elem = doc_type_elem.find_element_by_xpath('..')
        long_type = parent_elem.find_element_by_tag_name('label').text

        log.info('Document type is {} ({})'.format(long_type, short_type))
        doc_type_elem.click()

    def click_search_button(self):
        """Click on the search button."""
        html_id = 'cphNoMargin_SearchButtons2_btnSearch__1'

        log.info('Find search button at HTML ID {}'.format(html_id))
        search_button_elem = self.driver.find_element_by_id(html_id)

        log.info('Click search button')
        search_button_elem.click()

    def search_parameters(self, search_date):
        """Enter search parameters."""
        self.click_advanced_tab()
        time.sleep(2.0)

        self.enter_date_filed_from(search_date)
        self.enter_date_filed_to(search_date)

        self.select_document_type()
        time.sleep(1.0)

        self.click_search_button()

        log.info('Sleep 5.0 seconds')
        time.sleep(5.0)

    # Parse results
    def parse_results(self, year, month, day):
        """Parse initial result page for total number of sales."""
        html_id = 'cphNoMargin_cphNoMargin_OptionsBar1_ItemList'

        try:
            log.info('Find results list at HTML ID {}'.format(html_id))
            item_list_elem = self.driver.find_element_by_id(html_id)

            # log.info('Find option')
            options = item_list_elem.find_elements_by_tag_name("option")
        except Exception as error:
            log.info('No sales for this day')
            log.error(error, exc_info=True)

            html_out = '{}/data/raw/{}-{}-{}/page-html/page1.html'.format(
                PROJECT_DIR, year, month, day)

            with open(html_out, 'wb') as f_out:
                f_out.write((self.driver.page_source).encode('utf-8'))

            return

        total_pages = int(options[-1].get_attribute('value'))
        log.info('{0} pages of records for {1}-{2}-{3}'.format(
            total_pages, year, month, day))

        for i in range(1, total_pages + 1):
            self.parse_page(i, year, month, day)

            log.info('Sleep 5.0 seconds')
            time.sleep(5.0)

    def parse_page(self, i, year, month, day):
        """Parse results page for sale document IDs."""
        # Save table page
        log.info('Parse page {0} for {1}-{2}-{3}'.format(i, year, month, day,))

        html_out = '{}/data/raw/{}-{}-{}/page-html/page{}.html'.format(
            PROJECT_DIR, year, month, day, i)

        with open(html_out, 'wb') as f_out:
            f_out.write((self.driver.page_source).encode('utf-8'))

        # TODO: Read from memory instead of new output file
        soup = BeautifulSoup(open(html_out), "html.parser")

        # log.info('Find all object IDs')

        # For this one page
        rows = soup.find_all('td', class_="igede12b9e")  # List of Object IDs

        # First table row is empty
        log.info('{} records to scrape for this page'.format(len(rows) - 1))

        for j in range(1, len(rows)):
            # overall_row = (i - 1) * 20 + j
            self.parse_sale(j, rows, year, month, day)

        url = 'http://onlinerecords.orleanscivilclerk.com/RealEstate/' + \
              'SearchResults.aspx'
        log.info('Load URL {}'.format(url))
        self.driver.get(url)

        html_id = 'OptionsBar1_imgNext'
        log.info('Find next page button at HTML ID {}'.format(html_id))
        next_button_elem = self.driver.find_element_by_id(html_id)

        log.info('Click next page button')
        next_button_elem.click()

    def parse_sale(self, j, rows, year, month, day):
        """Parse single sale page and save HTML."""
        document_id = rows[j].string

        url = ('http://onlinerecords.orleanscivilclerk.com/RealEstate/' +
               'SearchResults.aspx?global_id={}&type=dtl').format(document_id)

        try:
            log.info('Load sale URL {}'.format(url))
            self.driver.get(url)
        except Exception:  # TODO
            log.exception('Error loading sale URL {}'.format(url))

        html = self.driver.page_source
        html_out = "{0}/data/raw/{1}-{2}-{3}/form-html/{4}.html".format(
            PROJECT_DIR, year, month, day, document_id)

        log.info('Save {}'.format(html_out))

        with open(html_out, "wb") as f_out:
            f_out.write(html.encode('utf-8'))

        try:
            assert not self.is_error_page(html_out)  # TODO: Read from memory
        except Exception:  # TODO
            log.exception('Received error page')

            log.info('Deleting error page {}'.format(html_out))
            os.remove(html_out)

    @staticmethod
    def is_error_page(html):
        """Check if the downloaded single sale HTML is an error page.

        TODO: This should read from HTML already in memory not new output file.
        """
        soup = BeautifulSoup(open(html), "html.parser")
        title = soup.find_all('title')[0].string

        return title == 'Error'

    # Logout
    def logout(self):
        """Logout of site."""
        url = 'http://onlinerecords.orleanscivilclerk.com/RealEstate/' + \
              'SearchEntry.aspx'
        # No matter which page you're on, you can go back here and logout.
        log.info('Load {}'.format(url))
        self.driver.get(url)

        html_id = 'Header1_lnkLogout'

        log.info('Find logout button at HTML ID {}'.format(html_id))
        logout_elem = self.driver.find_element_by_id(html_id)

        log.info('Click logout button')
        logout_elem.click()

    def cycle_through_dates(self):
        """For each date in range, search, parse results and save HTML.

        TODO: Make this asynchronous.
        """
        current_date = self.initial_date

        # Must search each date one at a time because there is a limit of
        # 300 results per search. A single day shouldn't reach that ceiling.
        while current_date != (self.until_date + timedelta(days=1)):
            year = current_date.strftime('%Y')  # "2014"
            month = current_date.strftime('%m')  # "09"
            day = current_date.strftime('%d')  # "09"

            log.info('Search records for {}-{}-{}'.format(year, month, day))

            # Check if folder for this day exists. If not, then make one.
            pagedir = "{0}/data/raw/{1}-{2}-{3}/page-html".format(
                PROJECT_DIR, year, month, day)

            formdir = "{0}/data/raw/{1}-{2}-{3}/form-html".format(
                PROJECT_DIR, year, month, day)

            if not os.path.exists(pagedir):
                log.info('Create directory {}'.format(pagedir))
                os.makedirs(pagedir)
            if not os.path.exists(formdir):
                log.info('Create directory {}'.format(formdir))
                os.makedirs(formdir)

            search_date = '{}{}{}'.format(month, day, year)

            # The meat of this loop
            self.navigate_search_page(year, month, day)

            self.search_parameters(search_date)
            self.parse_results(year, month, day)

            current_date += timedelta(days=1)

    def main(self):
        """The main scrape method."""
        try:
            self.login()
        except Exception:
            self.driver.close()
            self.driver.quit()
            raise

        try:
            self.cycle_through_dates()
        except Exception as error:  # TODO
            log.exception(error)  # TODO
        finally:
            self.logout()
            self.driver.close()
            self.driver.quit()


def cli_has_errors(arguments):
    """Check for any CLI parsing errors."""
    single = arguments['<single_date>']
    early = arguments['<early_date>']
    late = arguments['<late_date>']

    all_args = all(arg is not None for arg in (single, early, late))

    if all_args:
        log.error("Date arguments must be a single date or a date range")
        return True

    single_and_other_arg = single is not None and \
        any(arg is not None for arg in (early, late))

    if single_and_other_arg:
        log.error("Cannot use a single date and a date range bound.")
        return True

    only_one_date_bound = any(arg is not None for arg in (early, late)) and \
        any(arg is None for arg in (early, late))

    if only_one_date_bound:
        log.error("Date range must include both dates")
        return True

    return False


def cli(arguments):
    """Parse command-line arguments."""
    if cli_has_errors(arguments):
        return

    if arguments['<single_date>']:
        early_date = arguments['<single_date>']
        late_date = arguments['<single_date>']

        log.info('Scraping single date: {}'.format(early_date))
    elif arguments['<early_date>'] and arguments['<late_date>']:
        early_date = arguments['<early_date>']
        late_date = arguments['<late_date>']

        log.info('Scraping date range: {0} to {1}'.format(
            early_date, late_date))
    else:  # No dates provided. Default is to scrape previous day.
        log.info('Scraping yesterday')

        Scrape().main()
        return

    # Check for errors
    early_datetime = datetime.strptime(early_date, '%Y-%m-%d')
    late_datetime = datetime.strptime(late_date, '%Y-%m-%d')

    if early_datetime > late_datetime:
        raise BadDateRangeError('Bad date range')

    Scrape(initial_date=early_date, until_date=late_date).main()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    cli(arguments)
