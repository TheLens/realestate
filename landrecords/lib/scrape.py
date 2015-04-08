# -*- coding: utf-8 -*-

import time
import os
import re
import glob
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta

from landrecords import config
from landrecords.lib import mail
from landrecords.lib.log import Log


class Scraper(object):

    def __init__(self, from_date, until_date):
        self.log = Log('scrape').logger

        self.from_date = from_date
        self.until_date = until_date
        self.start_date = datetime(2014, 2, 18)
        self.today_date = datetime.now()
        self.yesterday_date = datetime.now() - timedelta(days=1)
        self.driver = webdriver.PhantomJS(
            executable_path='/usr/local/bin/phantomjs',
            port=0)
        # self.driver = webdriver.Firefox(timeout=60)

        self.login()

        try:
            self.cycle_through_dates(from_date, until_date)
        except Exception, e:
            self.log.error(e, exc_info=True)
            mail(
                subject="Error running Land Record's scrape.py script",
                body='Check scrape.log for more details.',
                frm='tthoren@thelensnola.org',
                to=['tthoren@thelensnola.org'])
        finally:
            self.logout()
            self.driver.close()
            self.driver.quit()
            self.log.info('Done!')

    '''
    Login page
    '''

    def load_homepage(self):
        self.log.info('Load homepage')
        self.driver.get("http://onlinerecords.orleanscivilclerk.com/")
        time.sleep(2.2)

    def find_login_link(self):
        self.log.info('Find login link')
        login_link_elem = self.driver.find_element_by_id("Header1_lnkLogin")
        self.log.info('Click login link')
        login_link_elem.click()
        time.sleep(1.2)

    def enter_username(self):
        self.log.info('Find username field')
        unsername_elem = self.driver.find_element_by_id("Header1_txtLogonName")
        self.log.info('Enter username')
        unsername_elem.send_keys(config.LRD_USERNAME)

    def enter_password(self):
        self.log.info('Find password field')
        password_elem = self.driver.find_element_by_id("Header1_txtPassword")
        self.log.info('Enter password')
        password_elem.send_keys(config.LRD_PASSWORD)
        self.log.info('Return')
        password_elem.send_keys('\n')  # To trigger search function
        time.sleep(2.2)

        self.log.debug(self.driver.title)

    def login(self):
        self.load_homepage()
        self.find_login_link()
        self.enter_username()
        self.enter_password()

    '''
    Navigate search page
    '''

    def load_search_page(self, year, month, day):
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")
        time.sleep(2.2)

    def find_permanent_date_range(self):
        date_range_elem = self.driver.find_element_by_id(
            "cphNoMargin_lblSearchSummary")

        date_range = date_range_elem.text
        self.log.debug(date_range)

        first_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                              date_range).group(1)  # 02/18/2014
        first_date = first_date.replace('/', '')
        self.log.debug(first_date)

        second_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)",
                               date_range).group(2)  # 02/25/2015
        second_date = second_date.replace('/', '')
        self.log.debug(second_date)

        date_range_html = self.driver.page_source

        return date_range_html

    def delete_permanent_date_range_when_scraped_file(self):
        self.log.info('Delete old permanent-date-range-when-scraped*.html')
        for fl in glob.glob("%s/raw/%s-%s-%s/permanent-date-range-when" +
                            "-scraped*.html" % (
                                config.DATA_DIR, year, month, day)):
            os.remove(fl)

    def save_permanent_date_range_when_scraped_file(self):
        # Save permanent date range for this individual sale.
        self.log.info('Save new permanent-date-range-when-scraped*.html file')
        individual_html_out = open(
            "%s/raw/%s-%s-%s/permanent-date-range-when-scraped_%s-%s.html" % (
                config.DATA_DIR, year, month, day,
                first_date, second_date
            ), "w")
        individual_html_out.write(date_range_html.encode('utf-8'))
        individual_html_out.close()

    def delete_permanent_date_range_file(self):
        # Delete old file first
        self.log.info('Delete old most-recent-permanent-date-range/*.html file')
        for fl in glob.glob("%s/most-recent-permanent-date-range/*.html"
                            % (config.DATA_DIR)):
                os.remove(fl)

    def save_permanent_date_range_file(self):
        self.log.info('Save new most-recent-permanent-date-range/*.html file')
        overall_html_out = open("""
            %s/most-recent-permanent-date-range/%s-%s.html
            """ % (config.DATA_DIR, first_date, second_date),
            "w")
        overall_html_out.write(date_range_html.encode('utf-8'))
        overall_html_out.close()

        time.sleep(2.2)

    def navigate_search_page(self):
        self.load_search_page()
        self.find_permanent_date_range()
        self.delete_permanent_date_range_when_scraped_file()
        self.save_permanent_date_range_when_scraped_file()
        self.delete_permanent_date_range_file()
        self.save_permanent_date_range_file()

    '''
    Search parameters
    '''

    def click_advanced_tab(self, year, month, day):
        self.log.info('search_parameters')

        search_date = month + day + year
        self.log.debug(search_date)

        # Advanced tab
        self.log.info('Find advanced tab')
        advanced_tab_elem = self.driver.find_element_by_id(
            "x:2130005445.2:mkr:ti1")
        self.log.info('Click on advanced tab')
        advanced_tab_elem.click()
        time.sleep(1.2)

    def enter_date_filed_from(self):
        self.log.info('Find date from input')
        date_file_from_elem = self.driver.find_element_by_id(
            "x:2002578730.0:mkr:3")
        self.log.info('Click in input')
        date_file_from_elem.click()
        self.log.info('Enter begin date')
        date_file_from_elem.send_keys(search_date)

    def enter_date_filed_to(self):
        self.log.info('Find date to input')
        date_file_to_elem = self.driver.find_element_by_id(
            "x:625521537.0:mkr:3")
        self.log.info('Click in input')
        date_file_to_elem.click()
        self.log.info('Enter end date')
        date_file_to_elem.send_keys(search_date)

    def select_document_type(self):
        self.log.info('Find SALE document type')
        document_type_elem = self.driver.find_element_by_id(
            "cphNoMargin_f_dclDocType_291")
        self.log.info('Select SALE document type')
        document_type_elem.click()

    def click_search_button(self):
        self.log.info('Find search button')
        search_button_elem = self.driver.find_element_by_id(
            "cphNoMargin_SearchButtons2_btnSearch__2")
        self.log.info('Click search button')
        search_button_elem.click()
        time.sleep(2.2)

    def search_parameters(self):
        self.click_advanced_tab()
        self.enter_date_filed_from()
        self.enter_date_filed_to()
        self.select_document_type()
        self.click_search_button()

    '''
    Parse results
    '''

    def find_current_page_number(self, year, month, day):
        # Find current page number
        try:
            self.log.info('Find item_list_elem')  # todo: Better description
            item_list_elem = self.driver.find_element_by_id(
                "cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
            self.log.info('Find option')
            options = item_list_elem.find_elements_by_tag_name("option")
        except Exception, e:
            # Save table page
            self.log.error(e, exc_info=True)
            self.log.info('No sales for this day')
            html_out = open("%s/raw/%s-%s-%s/page-html/page1.html"
                            % (config.DATA_DIR, year, month, day), "w")
            html_out.write((self.driver.page_source).encode('utf-8'))
            html_out.close()
            return

        print options  # todo: what is this? todo: log it?

        total_pages = int(options[-1].get_attribute('value'))
        self.log.debug(total_pages)

        for i in range(1, total_pages + 1):
            self.log.debug(i)

            # Save table page
            self.log.info('Write table page HTML')
            html_out = open("%s/raw/%s-%s-%s/page-html/page%d.html"
                            % (config.DATA_DIR, year, month, day, i), "w")
            html_out.write((self.driver.page_source).encode('utf-8'))
            html_out.close()

            self.log.info('Build BeautifulSoup')
            soup = BeautifulSoup(open("%s/raw/%s-%s-%s/page-html/page%d.html"
                                 % (config.DATA_DIR, year, month, day, i)))

            self.log.info('Find all object IDs')
            # List of Object IDs:
            rows = soup.find_all('td', class_="igede12b9e")

            self.log.debug(len(rows))

            for j in range(1, len(rows)):
                self.log.debug((i - 1) * 20 + j)

                document_id = rows[j].string

                self.log.debug(document_id)

                single_sale_url = (
                    "http://onlinerecords.orleanscivilclerk.com/" +
                    "RealEstate/SearchResults.aspx?global_id=%s" +
                    "&type=dtl" % (document_id))

                self.log.debug(single_sale_url)

                try:
                    self.log.info('Load %s', single_sale_url)
                    self.driver.get(single_sale_url)
                    time.sleep(1.2)
                except Exception, e:
                    self.log.error(e, exc_info=True)

                self.log.info('Save this sale HTML')
                html_out = open("""
                    %s/raw/%s-%s-%s/form-html/%s.html
                    """ % (config.DATA_DIR, year, month, day, document_id),
                    "w")
                html_out.write((self.driver.page_source).encode('utf-8'))
                html_out.close()

                time.sleep(1.2)

            self.log.info(
                'Go to http://onlinerecords.orleanscivilclerk.com/' +
                'RealEstate/SearchResults.aspx')
            self.driver.get(
                "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
                "SearchResults.aspx")

            self.log.info('Find next page button')
            next_button_elem = self.driver.find_element_by_id(
                "OptionsBar1_imgNext")
            self.log.info('Click next page button')
            next_button_elem.click()
            time.sleep(2.2)

        # self.driver.get("http://onlinerecords.orleanscivilclerk.com/
        # RealEstate/SearchResults.aspx")

    '''
    Logout
    '''

    def logout(self):
        # No matter which page you're on, you can go back here and logout.
        self.log.info(
            'Load http://onlinerecords.orleanscivilclerk.com/' +
            'RealEstate/SearchEntry.aspx')
        self.driver.get(
            "http://onlinerecords.orleanscivilclerk.com/RealEstate/" +
            "SearchEntry.aspx")

        self.log.info('Find logout button')
        logout_elem = self.driver.find_element_by_id("Header1_lnkLogout")
        self.log.info('Click logout button')
        logout_elem.click()

    def cycle_through_dates(self, from_date, until_date):
        self.log.info('cycle_through_dates')

        self.log.debug(from_date)
        self.log.debug(until_date)

        end_date = until_date + timedelta(days=1)
        self.log.debug(end_date)

        while from_date.strftime('%Y-%m-%d') != end_date.strftime('%Y-%m-%d'):
            self.log.debug(from_date)
            self.log.debug(end_date)

            year = (from_date).strftime('%Y')  # "2014"
            month = (from_date).strftime('%m')  # "09"
            day = (from_date).strftime('%d')  # "09"

            self.log.debug(year + '-' + month + '-' + day)

            # Check if folder for this day exists. if not, then make one
            pagedir = "%s/raw/%s-%s-%s/page-html" % (
                config.DATA_DIR, year, month, day)
            self.log.debug(pagedir)

            formdir = "%s/raw/%s-%s-%s/form-html" % (
                config.DATA_DIR, year, month, day)
            self.log.debug(formdir)

            if not os.path.exists(pagedir):
                self.log.info('Making %s', pagedir)
                os.makedirs(pagedir)
            if not os.path.exists(formdir):
                self.log.info('Making %s', formdir)
                os.makedirs(formdir)

            # The good stuff
            self.navigate_search_page(year, month, day)
            self.search_parameters(year, month, day)
            self.parse_results(year, month, day)

            from_date = from_date + timedelta(days=1)
            self.log.debug(from_date)
