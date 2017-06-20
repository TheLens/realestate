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

# from scripts.mail import Mail
from www import log, YESTERDAY_DAY, PROJECT_DIR, LOG_FILE

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
            service_log_path=LOG_FILE,
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

    # Login page
    def load_homepage(self):
        """Load homepage."""
        log.info('Load homepage')
        self.load_url("http://onlinerecords.orleanscivilclerk.com/")

    def find_login_link(self):
        """Find and click on login link."""
        log.info('Find login link')
        login_link_elem = self.driver.find_element_by_id("Header1_lnkLogin")

        log.info('Click login link')
        login_link_elem.click()

    def enter_username(self):
        """Type in username."""
        log.info('Find username field')
        username_elem = self.driver.find_element_by_id("Header1_txtLogonName")
        log.info('Enter username')

        username_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_USERNAME'))

    def enter_password(self):
        """Type in password."""
        log.info('Find password field')
        password_elem = self.driver.find_element_by_id("Header1_txtPassword")
        log.info('Enter password')

        password_elem.send_keys(os.environ.get('REAL_ESTATE_LRD_PASSWORD'))

        log.info('Return')

        # Trigger search function. Don't use RETURN because PhantomJS fails.
        password_elem.send_keys(Keys.ENTER)

        log.debug(self.driver.title)

    def login(self):
        """Load homepage, find login, enter credentials."""
        self.load_homepage()
        time.sleep(1.0)

        self.find_login_link()
        time.sleep(4.0)

        self.enter_username()
        time.sleep(2.0)

        self.enter_password()
        time.sleep(15.0)

    def is_logged_in(self):
        """Confirm that login was successful."""
        try:
            self.driver.find_element_by_id("Header1_lnkLogout")
            log.debug("Login successful.")
            return True
        except Exception as error:
            log.debug("Login failed.")
            log.error(error, exc_info=True)
            return False

    # Navigate search page
    def load_search_page(self):
        """Load search page."""
        # might not have loaded for server scrape:
        self.load_url(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")

    def find_permanent_date_range(self):
        """Parse search page for permanent date range."""
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
        log.info(
            'Delete old most-recent-permanent-date-range/*.html file')

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
        overall_html_out = open(
            "{0}/data/most-recent-permanent-date-range/{1}-{2}.html".format(
                PROJECT_DIR, first_date, second_date),
            "wb")
        overall_html_out.write(date_range_html.encode('utf-8'))
        overall_html_out.close()

    def navigate_search_page(self, year, month, day):
        """
        Navigate search page to find permanent date range.

        Update local date range files.
        """
        self.load_search_page()
        time.sleep(5.0)

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
        log.info('click_advanced_tab')

        # Advanced tab
        log.info('Find advanced tab')
        advanced_tab_elem = self.driver.find_element_by_id(
            "x:2130005445.2:mkr:ti1")
        log.info('Click on advanced tab')
        advanced_tab_elem.click()

    def enter_date_filed_from(self, search_date):
        """Enter "date from"."""
        date_file_from_elem = self.driver.find_element_by_id(
            "x:1221134975.0:mkr:3")
        date_file_from_elem.click()
        date_file_from_elem.send_keys(search_date)

    def enter_date_filed_to(self, search_date):
        """Enter "date to"."""
        date_file_to_elem = self.driver.find_element_by_id(
            "x:96043147.0:mkr:3")
        date_file_to_elem.click()
        date_file_to_elem.send_keys(search_date)

    def select_document_type(self):
        """Select SALE document type in dropdown."""
        document_type_elem = self.driver.find_element_by_id(
            "cphNoMargin_f_dclDocType_292")
        log.info('Select SALE document type')
        document_type_elem.click()

    def click_search_button(self):
        """Click on the search button."""
        log.info('Find search button')
        search_button_elem = self.driver.find_element_by_id(
            "cphNoMargin_SearchButtons2_btnSearch__1")  # Was __2

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
        time.sleep(15.0)

    # Parse results
    def parse_results(self, year, month, day):
        """Parse initial result page for total number of sales."""
        # Find current page number
        try:
            log.info('Find item_list_elem')
            item_list_elem = self.driver.find_element_by_id(
                "cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
            log.info('Find option')
            options = item_list_elem.find_elements_by_tag_name("option")
        except Exception as error:
            # Save table page
            log.error(error, exc_info=True)
            log.info('No sales for this day')
            html_out = open(
                "{0}/data/raw/{1}-{2}-{3}/page-html/page1.html".format(
                    PROJECT_DIR, year, month, day
                ), "wb")
            html_out.write((self.driver.page_source).encode('utf-8'))
            html_out.close()
            return

        total_pages = int(options[-1].get_attribute('value'))
        log.debug('{0} pages to parse for {1}-{2}-{3}'.format(
                  total_pages, year, month, day))

        for i in range(1, total_pages + 1):
            log.debug('Page: {}'.format(i))

            self.parse_page(i, year, month, day)
            time.sleep(15.0)

    def parse_page(self, i, year, month, day):
        """Parse results page for sale document IDs."""
        # Save table page
        log.info('Parse results page table HTML')
        html_out = open((
            "{0}/data/raw/{1}-{2}-{3}/page-html/page{4}.html").format(
                PROJECT_DIR, year, month, day, i),
            "wb")
        html_out.write((self.driver.page_source).encode('utf-8'))
        html_out.close()

        bs_file = "{0}/data/raw/{1}-{2}-{3}/page-html/page{4}.html".format(
            PROJECT_DIR, year, month, day, i)
        soup = BeautifulSoup(open(bs_file), "html.parser")

        log.info('Find all object IDs')

        # For this one page
        rows = soup.find_all('td', class_="igede12b9e")  # List of Object IDs

        log.debug('There are {} rows for this page'.format(len(rows)))

        for j in range(1, len(rows)):
            overall_row = (i - 1) * 20 + j
            log.debug(
                'Analyzing overall row {0} for {1}-{2}-{3}'.format(
                    overall_row, year, month, day))

            self.parse_sale(j, rows, year, month, day)
            time.sleep(5.0)

        log.info(
            'Go to http://onlinerecords.orleanscivilclerk.com/' +
            'RealEstate/SearchResults.aspx')
        self.load_url(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchResults.aspx")

        log.info('Find next page button')
        next_button_elem = self.driver.find_element_by_id(
            "OptionsBar1_imgNext")

        log.info('Click next page button')
        next_button_elem.click()

    def load_url(self, url):
        """Load a new URL and give enough time to load."""
        self.driver.get(url)
        time.sleep(10.0)

    def parse_sale(self, j, rows, year, month, day):
        """Parse single sale page and save HTML."""
        document_id = rows[j].string

        log.debug(
            'Saving HTML for {0} on {1}-{2}-{3}'.format(
                document_id, year, month, day))

        single_sale_url = (
            "http://onlinerecords.orleanscivilclerk.com/" +
            "RealEstate/SearchResults.aspx?" +
            "global_id={}" +
            "&type=dtl").format(document_id)
        log.debug('Sale URL: {}'.format(single_sale_url))

        try:
            log.info('Loading {}'.format(single_sale_url))
            self.load_url(single_sale_url)
        except Exception as error:
            log.error(error, exc_info=True)

        html = self.driver.page_source

        log.info('Save this sale HTML')

        html_file = "{0}/data/raw/{1}-{2}-{3}/form-html/{4}.html".format(
            PROJECT_DIR, year, month, day, document_id)

        html_out = open(html_file, "wb")
        html_out.write(html.encode('utf-8'))
        html_out.close()

        try:
            assert not self.is_error_page(html_file)
        except Exception as error:
            log.debug('Deleting error page: {}'.format(html_file))
            log.error(error, exc_info=True)

            os.remove(html_file)

            return

    @staticmethod
    def is_error_page(html):
        """Check if the downloaded single sale HTML is an error page."""
        soup = BeautifulSoup(open(html), "html.parser")
        title = soup.find_all('title')[0].string

        # log.debug('Error page was downloaded.')
        return title == 'Error'

    # Logout
    def logout(self):
        """Logout of site."""
        # No matter which page you're on, you can go back here and logout.
        log.info(
            'Load http://onlinerecords.orleanscivilclerk.com/' +
            'RealEstate/SearchEntry.aspx')
        self.load_url(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")

        log.info('Find logout button')
        logout_elem = self.driver.find_element_by_id("Header1_lnkLogout")
        log.info('Click logout button')
        logout_elem.click()

    def cycle_through_dates(self):
        """For each date in range, search, parse results and save HTML."""
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
            pagedir = "{0}/data/raw/{1}-{2}-{3}/page-html".format(
                PROJECT_DIR, year, month, day)
            log.debug(pagedir)

            formdir = "{0}/data/raw/{1}-{2}-{3}/form-html".format(
                PROJECT_DIR, year, month, day)
            log.debug(formdir)

            if not os.path.exists(pagedir):
                log.info('Making {}'.format(pagedir))
                os.makedirs(pagedir)
            if not os.path.exists(formdir):
                log.info('Making {}'.format(formdir))
                os.makedirs(formdir)

            search_date = month + day + year

            # The meat of this loop
            self.navigate_search_page(year, month, day)

            self.search_parameters(search_date)
            self.parse_results(year, month, day)

            current_date += timedelta(days=1)
            log.debug(current_date)

    def main(self):
        """The main scrape method."""
        self.login()  # Has built-in delay after

        assert self.is_logged_in()

        try:
            self.cycle_through_dates()
        except Exception as error:
            log.error(error, exc_info=True)

            # TODO: Switch to Slack
            # m = Mail(
            #     subject="Error running Land Record's scrape.py script",
            #     body='Check the log for more details.',
            #     frm='lens.real.estate.scraper@gmail.com',
            #     to=['tthoren@thelensnola.org'])
            # m.send_with_attachment(files=[LOG_FILE])
        finally:
            self.logout()
            self.driver.close()
            self.driver.quit()

            log.info('Done!')


def cli_has_errors(arguments):
    """Check for any CLI parsing errors."""
    all_arguments = (
        arguments['<single_date>'] is not None and
        arguments['<early_date>'] is not None and
        arguments['<late_date>'] is not None)

    if all_arguments:
        # print("Must use single date or date range, but not both.")
        return True

    single_and_other_arguments = (
        (
            arguments['<single_date>'] is not None and
            arguments['<early_date>'] is not None
        ) or
        (
            arguments['<single_date>'] is not None and
            arguments['<late_date>'] is not None
        ))

    if single_and_other_arguments:
        # print("Cannot use a single date and a date range bound.")
        return True

    one_date_bound_only = (
        (
            arguments['<early_date>'] is not None and
            arguments['<late_date>'] is None
        ) or
        (
            arguments['<early_date>'] is None and
            arguments['<late_date>'] is not None
        ))

    if one_date_bound_only:
        # print("Must pick both ends of a date range bound.")
        return True

    return False


def cli(arguments):
    """Parse command-line arguments."""
    # Catch any missed errors
    if cli_has_errors(arguments):
        return

    if arguments['<single_date>']:  # Single date
        early_date = arguments['<single_date>']
        late_date = arguments['<single_date>']

        log.info('Scraping single date: {}.'.format(early_date))
    elif arguments['<early_date>'] and arguments['<late_date>']:  # Date range
        early_date = arguments['<early_date>']
        late_date = arguments['<late_date>']

        log.info('Scraping date range: {0} to {1}.'.format(
            early_date, late_date))
    else:  # No dates provided
        log.info('Scraping yesterday.')

        Scrape().main()  # Default: scrape yesterday.
        return

    # Check for errors
    early_datetime = datetime.strptime(early_date, "%Y-%m-%d")
    late_datetime = datetime.strptime(late_date, "%Y-%m-%d")

    if early_datetime > late_datetime:
        raise BadDateRangeError("The date range does not make sense.")

    Scrape(initial_date=early_date, until_date=late_date).main()

if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.0.1")
    cli(arguments)
