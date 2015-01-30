import mechanize
import time
import random
import logging
import logging.handlers
import os

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from app_config import username, password

'''
Downloads and stores HTML from Land Records Division
'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
fh = logging.FileHandler('logs/land-records_%s.log' % (datetime.now().strftime('%m-%d-%Y')))
fh.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(lineno)d - %(message)s')
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)

# # Application code
# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')

absolute_link = "/apps/land-records/repo/data"

def gimme_login(username, password):
	logger.info('gimme_login')

	base_url = "http://onlinerecords.orleanscivilclerk.com/"
	
	# Navigate browser:
	br = mechanize.Browser()

	#br.set_handle_equiv(True)
	br.set_handle_referer(True)
	br.set_handle_redirect(True)
	#br.set_handle_redirect(mechanize.HTTPRedirectHandler)
	br.set_handle_robots(False)
	#br.set_debug_redirects(True)
	#br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor()) #, max_time=1)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	br.open(base_url)
	br.select_form(nr=0) #there is no name for the form
	for control in br.form.controls:
		control.readonly = False
	br["__EVENTTARGET"] = "ctl00$Header1$btnLogon"
	br["__EVENTARGUMENT"] = ""
	br["Header1_txtLogonName"] = username
	br["Header1_txtPassword"] = password
	br["ctl00$Header1$btnLogon"] = "Logon"
	br["Header1_txtLogonName_clientState"] = "|0|01" + username + "||[[[[]],[],[]],[{},[]],'01'" + username + "']"
	br["Header1_txtPassword_clientState"] = "|0|01||[[[[]],[],[]],[{},[]],'05'" + password + "']"
	br["Header1_WebHDS_clientState"] = ""
	br["Header1_WebDataMenu1_clientState"] = "[[null,[[[null,[],null],[{},[]],null]],null],[{},[{},{}]],null]"
	br["dlgOptionWindow_clientState"] = "[[[[null,3,null,null,'700px','550px',1,1,0,0,null,0]],[[[[[null,'Copy Options',null]],[[[[[]],[],null],[null,null],[null]],[[[[]],[],null],[null,null],[null]],[[[[]],[],null],[null,null],[null]]],[]],[{},[]],null],[[[[null,null,null,null]],[],[]],[{},[]],null]],[]],[{},[]],'3,0,,,700px,550px,0']"
	br["RangeContextMenu_clientState"] = "[[[[null,null,null,null,1]],[[[[[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null]],[],[]],[{},[]],null]],null],[{},[{},{}]],null]"
	br["ctl00$_IG_CSS_LINKS_"] = "~/localization/style.css|~/localization/styleforsearch.css|~/favicon.ico|~/localization/styleFromCounty.css|ig_res/Default/ig_datamenu.css|ig_res/ElectricBlue/ig_dialogwindow.css|ig_res/ElectricBlue/ig_datamenu.css|ig_res/Default/ig_texteditor.css|ig_res/Default/ig_shared.css|ig_res/ElectricBlue/ig_shared.css"
	#br["ctl00$Header1$btnLogon__10"] = ["3"]
	br.submit()
	rand_no = random.randint(1, 10)
	time.sleep(1 + rand_no)
	logger.info('end gimme_login')
	return br

def gimme_results(br, year, month, day):
	logger.info('gimme_results', year, month, day)
	search_url = "http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchEntry.aspx"
	
	beg_year = year # four digits
	beg_month = month #single or double
	beg_day = day #single or double
	end_year = year
	end_month = month
	end_day = day

	br.open(search_url)
	br.select_form(nr=0) #there is no name for the form
	for control in br.form.controls:
		control.readonly = False
	br["__EVENTTARGET"] = "ctl00$cphNoMargin$SearchButtons2$btnSearch"
	br["__EVENTARGUMENT"] = "0"
	br["Header1_txtLogonName_clientState"] = "|0|01||[[[[]],[],[]],[{},[]],'01']"
	br["Header1_txtLogonName"] = ""
	br["Header1_txtPassword_clientState"] = "|0|01||[[[[]],[],[]],[{},[]],'01']"
	br["Header1_txtPassword"] = ""
	br["Header1_WebHDS_clientState"] = ""
	br["Header1_WebDataMenu1_clientState"] = "[[null,[[[null,[],null],[{},[]],null]],null],[{},[{},{}]],null]"
	br["cphNoMargin_f_WebTab1_clientState"] = "[[[[null,'502px',null,null,null,null,null,null,0]],[],[{'0':[[null,null,null,null,null,null,'Basic',1,null,null,null,null]],'1':[[null,null,null,null,null,null,'Advanced',1,null,null,null,null]]}]],[{'0':[3,1]},[{}]],null]"
	br["ctl00$cphNoMargin$f$drbPartyType2"] = [""]
	br["ctl00$cphNoMargin$f$drbPartyType"] = [""]
	# Eventually change the following to allow for variables that are entered more easily (for date range and form type)
	br["cphNoMargin_f_ddcDateFiledFrom_clientState"] = "|0|01%s-%s-%s-0-0-0-0||[[[[]],[],[]],[{},[]],'01%s-%s-%s-0-0-0-0']" % (beg_year, beg_month, beg_day, beg_year, beg_month, beg_day)
	br["cphNoMargin_f_ddcDateFiledTo_clientState"] = "|0|01%s-%s-%s-0-0-0-0||[[[[]],[],[]],[{},[]],'01%s-%s-%s-0-0-0-0']" % (end_year, end_month, end_day, end_year, end_month, end_day)
	br["ctl00$cphNoMargin$f$ddlCancelStatus"] = [""]
	br["ctl00$cphNoMargin$f$dclDocType$291"] = ["S"] 
	# ^^^ the name in the input checkbox on SearchEntry
	#id = cphNoMargin_f_dclDocType_291 (for S)
	br["ctl00$cphNoMargin$f$DataDropDownList1"] = [""]

	response = br.submit()
	data = response.read()
	
	# Save HTML file for page 1
	html_out = open("%s/%s-%s-%s/page-html/page1.html" % (absolute_link, year, month, day), "w")
	html_out.write(data)
	html_out.close()
	# Get an array of links for each form from page 1 and download its HTML
	soup = BeautifulSoup(open("%s/%s-%s-%s/page-html/page1.html"  % (absolute_link, year, month, day)))

	# Get forms HTML from page 1
	rows = soup.find_all('td', class_="igede12b9e")
	print "page1"
	logger.info('page1')
	for x in range(0, len(rows)):
		code = rows[x].string
		print code
		logger.info(code)
		form_url = "http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx?global_id=%s&type=dtl" % (code)
		response = br.open(form_url)
		data = response.read()
		htmlout = open("%s/%s-%s-%s/form-html/%s.html" % (absolute_link, year, month, day, code), "w")
		htmlout.write(data)
		htmlout.close()
		# Take a break
		rand_no = random.randint(1, 10)
		time.sleep(1 + rand_no)

	# Find number of pages
	table = soup.find('select', id="cphNoMargin_cphNoMargin_OptionsBar1_ItemList")
	if (table != None): # Avoids weekends and other days that have no sales
		pages = table.findAll('option')
		no_of_pages = len(pages)

		# Loop through remaining pages, grabbing HTML along the way

		for page in range(2, no_of_pages+1):
			print page
			logger.info(page)
			page_url = "http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx?pg=%d" % (page)
			response = br.open(page_url)
			data = response.read()
			htmlout = open("%s/%s-%s-%s/page-html/page%d.html" % (absolute_link, year, month, day, page), "w")
			htmlout.write(data)
			htmlout.close()
			# Get an array of links for each form from the page and download its HTML
			soup = BeautifulSoup(open("%s/%s-%s-%s/page-html/page%d.html" % (absolute_link, year, month, day, page)))
			rows = soup.find_all('td', class_="igede12b9e")
			for x in range(0, len(rows)):
				code = rows[x].string
				print code
				logger.info(code)
				form_url = "http://onlinerecords.orleanscivilclerk.com/RealEstate/SearchResults.aspx?global_id=%s&type=dtl" % (code)
				response = br.open(form_url)
				data = response.read()
				htmlout = open("%s/%s-%s-%s/form-html/%s.html" % (absolute_link, year, month, day, code), "w")
				htmlout.write(data)
				htmlout.close()
				# Take a break
				rand_no = random.randint(1, 10)
				time.sleep(1 + rand_no)
			# Take a break
			rand_no = random.randint(1, 10)
			time.sleep(1 + rand_no)
	logger.info('end gimme_results')

def gimme_everything():

	#Yesterday's date
	year = (datetime.now() - timedelta(days=1)).strftime('%Y') # "2014"
	month = (datetime.now() - timedelta(days=1)).strftime('%m') # "09"
	day = (datetime.now() - timedelta(days=1)).strftime('%d') # "09"

	# check if folder for this day exists. if not, then make one
	pagedir = "%s/%s-%s-%s/page-html" % (absolute_link, year, month, day)
	formdir = "%s/%s-%s-%s/form-html" % (absolute_link, year, month, day)
	if not os.path.exists(pagedir):
		os.makedirs(pagedir)
	if not os.path.exists(formdir):
		os.makedirs(formdir)

	# convert month and day to integers and back to strings to remove leading zero
	#month = str(int(month)) # "9"
	#day = str(int(day)) # "9"

	login = gimme_login(username, password)
	gimme_results(login, year, month, day)

def gimme_everything_ever():

	original_date = datetime(2014, 2, 18)
	present_date = datetime.now()

	login = gimme_login(username, password)

	while original_date != present_date:
		year = (original_date).strftime('%Y') # "2014"
		month = (original_date).strftime('%m') # "09"
		day = (original_date).strftime('%d') # "09"

		# Check if folder for this day exists. if not, then make one
		pagedir = "%s/%s-%s-%s/page-html" % (absolute_link, year, month, day)
		formdir = "%s/%s-%s-%s/form-html" % (absolute_link, year, month, day)

		if not os.path.exists(pagedir):
			os.makedirs(pagedir)
		if not os.path.exists(formdir):
			os.makedirs(formdir)

		gimme_results(login, year, month, day)

		original_date = original_date + timedelta(days=1)

#gimme_everything()
gimme_everything_ever()

logging.close()
