# -*- coding: utf-8 -*-

import time
import random
import os
import re
import sys
import glob

from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys

from app_config import username, password

driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs', port=0)
#driver = webdriver.Firefox(timeout=60)

start_date = datetime(2014, 2, 18)
today_date = datetime.now()
yesterday_date = datetime.now() - timedelta(days=1)

date_range_html = ''

absolute_link = "/apps/land-records/repo/data"
#absolute_link = "/Users/Tom/projects/land-records/repo/data"

def login():
	print '\nlogin()'

	# Load homepage
	print 'Load homepage'
	driver.get("http://onlinerecords.orleanscivilclerk.com/")
	time.sleep(2.2)

	# Login link
	print 'Click login link'
	login_link_elem = driver.find_element_by_id("Header1_lnkLogin")
	login_link_elem.click()
	time.sleep(1.2)

	# Username input
	print 'Enter username'
	unsername_elem = driver.find_element_by_id("Header1_txtLogonName")
	unsername_elem.send_keys(username)

	# Password input
	print 'Enter password'
	password_elem = driver.find_element_by_id("Header1_txtPassword")
	password_elem.send_keys(password)
	password_elem.send_keys('\n')#To trigger search function
	time.sleep(2.2)

	print 'Page title:', driver.title

	print 'Finished logging in'

def navigateSearchPage(year, month, day):
	print '\nnavigateSearchPage(', year, month, day, ')'

	driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchEntry.aspx")
	time.sleep(2.2)

	date_range_elem = driver.find_element_by_id("cphNoMargin_lblSearchSummary")
	date_range = date_range_elem.text

	print 'date_range:', date_range

	first_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)", date_range).group(1)#02/18/2014
	first_date = first_date.replace('/', '')

	second_date = re.match(r"Permanent\ Index From ([0-9/]*) to ([0-9/]*)", date_range).group(2)#02/25/2015
	second_date = second_date.replace('/', '')

	date_range_html = driver.page_source

	# Delete old file first
	for fl in glob.glob("%s/%s-%s-%s/permanent-date-range-when-scraped*.html" % (absolute_link, year, month, day)):
		os.remove(fl)

	# Save permanent date range for this individual sale.
	individual_html_out = open("%s/%s-%s-%s/permanent-date-range-when-scraped_%s-%s.html" % (absolute_link, year, month, day, first_date, second_date), "w")
	individual_html_out.write(date_range_html.encode('utf-8'))
	individual_html_out.close()

	# Delete old file first
	for fl in glob.glob("%s/most-recent-permanent-date-range*.html" % (absolute_link)):
		os.remove(fl)

	# Save permanent date range for overall sales.
	overall_html_out = open("%s/most-recent-permanent-date-range_%s-%s.html" % (absolute_link, first_date, second_date), "w")
	overall_html_out.write(date_range_html.encode('utf-8'))
	overall_html_out.close()

	time.sleep(2.2)

def searchParameters(year, month, day):
	print '\nsearchParameters(', year, month, day, ')'

	search_date = month + day + year

	# Advanced tab
	advanced_tab_elem = driver.find_element_by_id("x:2130005445.2:mkr:ti1")
	advanced_tab_elem.click()
	time.sleep(1.2)

	# "Date filed from" input
	date_file_from_elem = driver.find_element_by_id("x:2002578730.0:mkr:3")
	date_file_from_elem.click()
	date_file_from_elem.send_keys(search_date)

	# "Date filed to" input
	date_file_to_elem = driver.find_element_by_id("x:625521537.0:mkr:3")
	date_file_to_elem.click()
	date_file_to_elem.send_keys(search_date)

	# Select "SALE" in document type dropdown
	document_type_elem = driver.find_element_by_id("cphNoMargin_f_dclDocType_291")
	document_type_elem.click()

	# Click "Search"
	search_button_elem = driver.find_element_by_id("cphNoMargin_SearchButtons2_btnSearch__2")
	search_button_elem.click()
	time.sleep(2.2)

def parseResults(year, month, day):
	print '\nparseResults(', year, month, day, ')'

	# Find current page number
	try:
		item_list_elem = driver.find_element_by_id("cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
		options = item_list_elem.find_elements_by_tag_name("option")
	except:
		# Save table page
		print 'No results for this day. Saving HTML and returning'
		html_out = open("%s/%s-%s-%s/page-html/page1.html" % (absolute_link, year, month, day), "w")
		html_out.write((driver.page_source).encode('utf-8'))
		html_out.close()
		return

	print options

	total_pages = int(options[-1].get_attribute('value'))
	print 'Total pages:', total_pages

	for i in range(1, total_pages + 1):
		print 'Results page #:', i

		# Save table page
		print 'Write HTML'
		html_out = open("%s/%s-%s-%s/page-html/page%d.html" % (absolute_link, year, month, day, i), "w")
		html_out.write((driver.page_source).encode('utf-8'))
		html_out.close()

		print 'Build BeautifulSoup'
		soup = BeautifulSoup(open("%s/%s-%s-%s/page-html/page%d.html" % (absolute_link, year, month, day, i)))

		print 'Find all <td class="">'
		rows = soup.find_all('td', class_="igede12b9e")# List of Object IDs

		print '%s rows' % len(rows)
		print 'rows:\n', rows

		for j in range(1, len(rows)):
			print 'Single sale #', (i - 1) * 20 + j

			document_id = rows[j].string

			print 'Document ID:', document_id

			single_sale_url = "http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx?global_id=%s&type=dtl" % (document_id)

			print single_sale_url

			try:
				driver.get(single_sale_url)
				time.sleep(1.2)
			except:
				print 'Exception: could not open single sale url'

			html_out = open("%s/%s-%s-%s/form-html/%s.html" % (absolute_link, year, month, day, document_id), "w")
			html_out.write((driver.page_source).encode('utf-8'))
			html_out.close()

			time.sleep(1.2)		

		print 'Go to /SearchResults.aspx'
		driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx")

		print 'Go to next page in results'

		next_button_elem = driver.find_element_by_id("OptionsBar1_imgNext")
		next_button_elem.click()
		time.sleep(2.2)

	#driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx")

def logout():
	print '\nlogout()'

	# No matter which page you're on, you can go back here and logout.
	driver.get("http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchEntry.aspx")

	logout_elem = driver.find_element_by_id("Header1_lnkLogout")
	logout_elem.click()

def cycleThroughDates(from_date, until_date):
	print 'cycleThroughDates'

	print 'intial from_date:', from_date
	print 'initial until_date:', until_date

	end_date = until_date + timedelta(days=1)

	print 'while loop:\n'
	while from_date.strftime('%Y-%m-%d') != end_date.strftime('%Y-%m-%d'):
		print 'from_date:', from_date
		print 'end_date:', end_date

		print 'Building year, month, day'
		year = (from_date).strftime('%Y') # "2014"
		month = (from_date).strftime('%m') # "09"
		day = (from_date).strftime('%d') # "09"

		# Check if folder for this day exists. if not, then make one
		print 'Checking on folders'
		pagedir = "%s/%s-%s-%s/page-html" % (absolute_link, year, month, day)
		print 'pagedir:', pagedir

		formdir = "%s/%s-%s-%s/form-html" % (absolute_link, year, month, day)
		print 'formdir:', formdir

		print 'Building folders'
		if not os.path.exists(pagedir):
			os.makedirs(pagedir)
		if not os.path.exists(formdir):
			os.makedirs(formdir)

		# The good stuff
		print 'About to navigateSearchPage'
		navigateSearchPage(year, month, day)

		print 'About to searchParameters'
		searchParameters(year, month, day)

		print 'About to parseResults'
		parseResults(year, month, day)

		print 'Increasing from_date by 1'
		from_date = from_date + timedelta(days=1)

def main(from_date = start_date, until_date = yesterday_date):
	print '\nmain()'

	login()

	try:
		cycleThroughDates(from_date, until_date)
	except Exception, e:
		'Exception in main() function'
		print e
	finally:
		logout()
		driver.close()
		driver.quit()

if __name__ == '__main__':
	#main(from_date = datetime(2015, 2, 24))# Default is entire archive from Feb. 18, 2014, to yesterday.
	main(from_date = yesterday_date, until_date = yesterday_date)
