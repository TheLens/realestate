import re
import pprint

pp = pprint.PrettyPrinter()

def CleanNew(rows):
	'''
	This function takes in ALL CAPS and returns clean text.
	'''
	# This loop returns text that is not all-caps, but is still flawed:
	for i, row in enumerate(rows): # to standardize upper and lowercases
		# Read this row's values
		sellers = row['sellers']
		buyers = row['buyers']
		address = row['address']
		location_info = row['location_info']
		neighborhood = row['neighborhood']

		sellers = sellers.title() # Capitalizes the first letter in each word. Great, except for words like "LLC" (Llc)
		buyers = buyers.title()
		address = address.title()
		location_info = location_info.title()
		neighborhood = neighborhood.title()

		# Write over this rows values with newer, cleaner values
		rows[i]['sellers'] = sellers
		rows[i]['buyers'] = buyers
		rows[i]['address'] = address
		rows[i]['location_info'] = location_info
		rows[i]['neighborhood'] = neighborhood

	# Accumulate all problematic words and give substitutions
	acronyms = [
		[' Iii ', ' III '],
		[' Ii ', ' II '],
		[' Iv ', ' IV '],
		[' Xiv ', ' XIV '], 
		['Llc', 'LLC'], 
		['L L C', 'LLC'], 
		['Fbo', 'FBO'], 
		['Pcw85', 'PCW85'], 
		['Nola', 'NOLA'], 
		['Fka', 'FKA'], 
		['Bwe ', 'BWE '],
		['Mjh', 'MJH'],
		['Jmh ', 'JMH '],
		['Gmj', 'GMJ'],
		['Ctn', 'CTN'],
		['Ll ', 'LL '],
		['Co ', 'Co. '],
		['Jlra', 'JLRA'],
		['Jsw', 'JSW'],
		['Jcl', 'JCL'],
		[' And ', ' and '],
		[' Of ', ' of '],
		[' The ', ' the '],
		['Cdc', 'CDC'],
		['Bssb', 'BSSB'],
		['Uv', 'UV']
	]
	abbreviations = [
		['Jr', 'Jr.'], 
		['Sr', 'Sr.'], 
		['St ', 'St. '],
		['Dr ', 'Dr. ']
	]
	mcnames = [
		['Mca', 'McA'], 
		['Mcb', 'McB'], 
		['Mcc', 'McC'], 
		['Mcd', 'McD'], 
		['Mce', 'McE'], 
		['Mcf', 'McF'], 
		['Mcg', 'McG'], 
		['Mch', 'McH'], 
		['Mci', 'McI'], 
		['Mcj', 'McJ'], 
		['Mck', 'McK'], 
		['Mcl', 'McL'], 
		['Mcm', 'McM'], 
		['Mcn', 'McN'], 
		['Mco', 'McO'], 
		['Mcp', 'McP'], 
		['Mcq', 'McQ'], 
		['Mcr', 'McR'], 
		['Mcs', 'McS'], 
		['Mct', 'McT'], 
		['Mcu', 'McU'], 
		['Mcv', 'McV'], 
		['Mcw', 'McW'], 
		['Mcx', 'McX'], 
		['Mcy', 'McY'], 
		['Mcz', 'McZ']
	]
	address_abbreviations = [
		['Blvd', 'Blvd.'], 
		['Hwy', 'Highway'], 
		[' Rd', ' Road'],
		['Ct', 'Court'], 
		['Ave,', 'Ave.,'], 
		['Blvd,', 'Blvd.,'], 
		[' To ', ' to '],
		
		['1St', '1st'], 
		['2Nd', '2nd'], 
		['3Rd', '3rd'], 
		['4Th', '4th'], 
		['5Th', '5th'], 
		['6Th', '6th'], 
		['7Th', '7th'], 
		['8Th', '8th'], 
		['9Th', '9th'], 
		['0Th', '0th']
	] # Not sure what to do for "St.". This --> [' St', ' St.'] would also pick up something such as 123 Straight Road. The same could conceivably happen with "Ave". "Dr" needs to become "Drive", but have the same problem
	middle_initials = [
		[' A ', ' A. '], 
		[' B ', ' B. '], 
		[' C ', ' C. '], 
		[' D ', ' D. '], 
		[' E ', ' E. '], 
		[' F ', ' F. '], 
		[' G ', ' G. '], 
		[' H ', ' H. '], 
		[' I ', ' I. '], 
		[' J ', ' J. '], 
		[' K ', ' K. '], 
		[' L ', ' L. '], 
		[' M ', ' M. '], 
		[' N ', ' N. '], 
		[' O ', ' O. '], 
		[' P ', ' P. '], 
		[' Q ', ' Q. '], 
		[' R ', ' R. '], 
		[' S ', ' S. '], 
		[' T ', ' T. '], 
		[' U ', ' U. '], 
		[' V ', ' V. '], 
		[' W ', ' W. '], 
		[' X ', ' X. '], 
		[' Y ', ' Y. '], 
		[' Z ', ' Z. ']
	]
	neighborhood_names = [
		['B. W.', 'B.W.'],
		['St.  A', 'St. A']
	]
	# This loop scans for the above problem words and replaces them with their substitutes:
	for i, row in enumerate(rows):
		# Read the current rows values
		sellers = row['sellers']
		buyers = row['buyers']
		address = row['address']
		location_info = row['location_info']
		amt = row['amount']
		neighborhood = row['neighborhood']
		# Check for occurences of problematic acronyms
		for acronym in acronyms:
			acronym0 = acronym[0] # Problem acronym
			acronym1 = acronym[1] # Solution acronym
			# If find problem acronym (acronym0) in a string, replace with solution acronym (acronym1) 
			sellers = re.sub(acronym0,acronym1, sellers)
			buyers = re.sub(acronym0,acronym1, buyers)
			address = re.sub(acronym0,acronym1, address)
			location_info = re.sub(acronym0, acronym1, location_info)
		# Check for occurences of problematic "Mc" names. Corrections assume that the letter after should be capitalized:
		for mcname in mcnames:
			mcname0 = mcname[0]
			mcname1 = mcname[1]
			sellers = re.sub(mcname0,mcname1, sellers)
			buyers = re.sub(mcname0,mcname1, buyers)
			address = re.sub(mcname0, mcname1, address)
			location_info = re.sub(mcname0,mcname1, location_info)
		# Check for problematic abbreviations:
		for abbreviation in abbreviations:
			abbreviation0 = abbreviation[0]
			abbreviation1 = abbreviation[1]
			sellers = re.sub(abbreviation0, abbreviation1, sellers)
			buyers = re.sub(abbreviation0, abbreviation1, buyers)
			address = re.sub(abbreviation0, abbreviation1, address)
			location_info = re.sub(abbreviation0, abbreviation1, location_info)
		# Fix address abbreviations (for AP style purposes)
		for address_abbreviation in address_abbreviations:
			address0 = address_abbreviation[0]
			address1 = address_abbreviation[1]
			address = re.sub(address0, address1, address)
			location_info = re.sub(address0, address1, location_info)
		for middle_initial in middle_initials:
			middle_initial0 = middle_initial[0]
			middle_initial1 = middle_initial[1]
			sellers = re.sub(middle_initial0, middle_initial1, sellers)
			buyers = re.sub(middle_initial0, middle_initial1, buyers)

		for neighborhood_name in neighborhood_names:
			name0 = neighborhood_name[0]
			name1 = neighborhood_name[1]
			neighborhood = re.sub(name0, name1, neighborhood)

		# Must do regex for "St" and others. Imagine "123 Star St". Scanning for " St" in the above loop 
		# would catch the start of the street name here. "St " wouldn't work either.
		address = re.sub(r"St$",r"St.",address) #Check for "St" followed by end-of-line character
		address = re.sub(r"Ave$",r"Ave.",address)
		address = re.sub(r"Dr$",r"Dr.",address)
		address = re.sub(r" N ",r" N. ",address)
		address = re.sub(r" S ",r" S. ",address)
		address = re.sub(r" E ",r" E. ",address)
		address = re.sub(r" W ",r" W. ",address)
		sellers = re.sub(r"Inc$",r"Inc.", sellers)
		buyers = re.sub(r"Inc$",r"Inc.", buyers)
		amt = str(amt)
		amt = re.sub(r'\$',r'', amt) # remove the $
		amt = re.sub(r',',r'',amt) # remove the comma
		amt = float(amt) # change string to a float
		amt = round(amt) # round to nearest dollar
		amt = int(amt)

		all_addresses_text = ''

		address_list1 = address.split(';')

		for row in address_list1:
			# unit: x, condo: 4, etc.

			address_list2 = row.split(',')

			individiual_address_text = ''

			for l in address_list2:
				#condo: x

				try:
					if l.strip()[-1] != ':':
						if individiual_address_text == '':#If first addition
							individiual_address_text = l.strip()
						else:#If second addition or later
							individiual_address_text = individiual_address_text + ', ' + l.strip()
				except:
					continue

			if all_addresses_text == '':
				if individiual_address_text != '':
					all_addresses_text = individiual_address_text.strip()
			else:
				if individiual_address_text != '':
					all_addresses_text = all_addresses_text + '; ' + individiual_address_text.strip()

		#location_info = location_info.replace(';', ',')#So can split on commas for both semi-colons and commas

		#To remove district ordinal
		location_info = location_info.replace('1st', '1')
		location_info = location_info.replace('2nd', '2')
		location_info = location_info.replace('3rd', '3')
		location_info = location_info.replace('4th', '4')
		location_info = location_info.replace('5th', '5')
		location_info = location_info.replace('6th', '6')
		location_info = location_info.replace('7th', '7')

		all_locations_text = ''

		list1 = location_info.split(';')

		for row in list1:
			# unit: x, condo: 4, etc.

			list2 = row.split(',')

			individiual_location_text = ''

			for l in list2:
				#condo: x

				try:
					if l.strip()[-1] != ':':
						if individiual_location_text == '':#If first addition
							individiual_location_text = l.strip()
						else:#If second addition or later
							individiual_location_text = individiual_location_text + ', ' + l.strip()
				except:
					continue

				#print 'individiual_location_text:', individiual_location_text

			if all_locations_text == '':
				if individiual_location_text != '':
					all_locations_text = individiual_location_text.strip()
			else:
				if individiual_location_text != '':
					all_locations_text = all_locations_text + '; ' + individiual_location_text.strip()

		#unit = re.match(r"^.*UNIT\: (.*)\, CONDO", location_info).group(1)

		# Write over current row's values with newer, cleaner, smarter, better values
		rows[i]['sellers'] = sellers.strip(' ,').replace('  ', ' ').replace(' ,', ',')
		rows[i]['buyers'] = buyers.strip(' ,').replace('  ', ' ').replace(' ,', ',')
		rows[i]['address'] = all_addresses_text.strip(" ,").replace('  ', ' ').replace(' ,', ',')
		rows[i]['location_info'] = all_locations_text.strip(" ,").replace('  ', ' ').replace(' ,', ',')
		rows[i]['amount'] = amt
		rows[i]['neighborhood'] = neighborhood.replace('  ', ' ').replace(' ,', ',')
	return rows
