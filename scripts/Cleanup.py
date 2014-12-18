import re
import pprint

pp = pprint.PrettyPrinter()

def CombineORM(c):
	rows = [] # 'rows' returns the table, as a dict, but with only one row per sale
	last = len(c) - 1
	for index, row in enumerate(c):
		if index == 0: # need to establish variables for first iteration
			# Note: 'temp' variables are the values from the previous iteration
			tempid = 'placeholder'
			temprow = row ### Single row
			temprows = 'placeholder' ### Collection of rows
		if tempid == row['document_id']: # if previous iteration's document_id equals current iteration's document_id...
			#...Then it is okay to store the previous iteration's information to temprows bc they are same sale
			temprows.append(temprow)
			if index == last: # Append and send temprows to CombineRows
				temprows.append(row) # add current (final) row value
				temprows = CombineRows(temprows) ### temprows is now _______
				for thistemprow in temprows:
					rows.append(thistemprow)

		if tempid != row['document_id']: # if previous iteration of document_id is different from current document_id...
			#...Then it is okay to run the previous iterations' info (stored in 'temprows') through CombineRows and write out to permanent 'rows'
			if temprows == []: # Checks ______
				rows.append(temprow) # Add the single, unique entry "temprow" from previous iteration
				if index == last:
					rows.append(row)
			elif temprows == 'placeholder': #If first entry
				temprows = []
			else:
				#write code to cycle through temprows array to feed them one-by-one into rows
				temprows.append(temprow) #to get the most recent iteration in for this series of duplicates
				if index == last:
					temprows.append(row)
				temprows = CombineRows(temprows) # What if temprows is just a single row? Should still work
				for thistemprow in temprows: #empy "temprows" into "rows"
					rows.append(thistemprow)

			temprows = [] # resets temprows because past id != current id, meaning the start of new ID(s)
		tempid = row['document_id'] # always carries document_id over to next iteration
		temprow = row
	return rows

def CombineRows(temprows):
	'''
	"temprows" is a list of records with the same document_id, of format: [{stuff: stuff},{stuff: stuff}]
	General idea of this function is to compare the present iteration's records against the previous iterations' records.
	By doing so, we can combine rows of the same document_id and eliminate duplicates at the same time.

	''' 
	lastposition = len(temprows) - 1
	temparray = []
	tempnamearray = []
	templocationarray = []
	for index, x in enumerate(temprows):
		# The present iteration's records
		'''
		Need code to:
		Check if no street address, then use
		lot and unit information instead.
		Also need to check on condos plus weeks.
		'''
		vendorlastname = x['vendor_lastname']
		vendorfirstname = x['vendor_firstname']
		vendeelastname = x['vendee_lastname']
		vendeefirstname = x['vendee_firstname']
		street_number = x['street_number']
		address = x['address']
		district = x['district']
		district = re.sub(r"st",r"", district)
		district = re.sub(r"nd",r"", district)
		district = re.sub(r"rd",r"", district)
		district = re.sub(r"th",r"", district)
		lot = x['lot']
		square = x['square']
		unit = x['unit']
		subdivision = x['subdivision']
		condo = x['condo']
		weeks = x['weeks']
		vendor = vendorfirstname + ' ' + vendorlastname
		vendee = vendeefirstname + ' ' + vendeelastname

		location = street_number + ' ' + address
		if len(unit) > 0:
			location = location + ", Unit: " + unit
		if len(condo) > 0:
			location = location + ", Condo: " + condo
		if len(weeks) > 0:
			location = location + ", Weeks: " + weeks
		if len(subdivision) > 0:
			location = location + ", Subdivision: " + subdivision

		if len(district) > 0:
			location = location + ", District: " + district
		if len(square) > 0:
			location = location + ", Square: " + square
		if len(lot) > 0:
			location = location + ", Lot: " + lot

		location = location.strip(" ,")

		# Initiate variables for past iteration's values
		# On first iteration, there is no previous value to compare to,
		# so need to create fake values that will fail tests
		if index == 0:
		 	tempvendor = 'placeholder' #temp variables hold previous iteration's values. Ex. "Doug"
		 	tempvendee = 'placeholder'
		 	templocation = 'placeholder'
		 	tempvendorstring = 'placeholder' #tempstring variables hold all previous iterations' values. Ex. "Doug, Dave, Don"
		 	tempvendeestring = 'placeholder'
		 	templocationstring = 'placeholder'

		# For all ensuing records:
		if index != 0:
			if index == 1:
				# On second iteration, we know that the previous iteration should be added
				# because we have not written the first iteration's value yet.
				# Set tempstring = temp to write out the first iteration's value (a few lines down)
				tempvendorstring = tempvendor
				tempvendeestring = tempvendee
				templocationstring = templocation # If a location string is longer than 4, which all normal street addresses such as 1 Way are, then you know it is safe to add. Anything shorter than 4 is essentially nothing because no street address would have such a short name. In that case, add the Unit, District, etc. location string.
				
				
			# Compare to an array of previous names and not just the previous iteration's value because duplicates
			# are not necessary consecutive.
			# Don't need to check for unit and lot because these could conceivably repeat for addresses that are 
			# actually different.
			if any(vendor == i for i in tempnamearray) == False: # Meaning that a duplicate was not found, so...
				tempvendorstring = tempvendorstring + ', ' + vendor #...add what is now known to be a unique value.
			if any(vendee == i for i in tempnamearray) == False:
				tempvendeestring = tempvendeestring + ', ' + vendee
			if any(location == i for i in templocationarray) == False:
				templocationstring = templocationstring + '; ' + location

		# Now that the past iteration's values have been tested, and included in tempstring if necessary, we
		# can write what will be the next iteration's temp variable equal to the present iteration's values
		tempvendor = vendor
		tempvendee = vendee
		templocation = location

		# Add present iteration's value into collection for comparison in the next iteration
		tempnamearray.append(vendor)
		tempnamearray.append(vendee)
		templocationarray.append(location)
		# There is no iteration to check the last iteration, so must check for it directly.
		if index == lastposition:
			# Now that all rows have been checked and all unique values added into the temp string, can write out back into 'temprows'
			# tempvendorstring = CatchSimilarNames(tempvendorstring)
			# tempvendeestring = CatchSimilarNames(tempvendeestring)
			#templocationstring = CatchSimilarNames(templocationstring)
			x['vendor_lastname'] = tempvendorstring
			x['vendor_firstname'] = ''
			x['vendee_lastname'] = tempvendeestring
			x['vendee_firstname'] = ''
			x['address'] = templocationstring
			x['street_number'] = ''
	temparray.append(x)
	return temparray

def Clean(rows):
	'''
	This function takes in ALL CAPS and returns clean text.
	'''
	# This loop returns text that is not all-caps, but is still flawed:
	for i, row in enumerate(rows): # to standardize upper and lowercases
		# Read this row's values
		vendor_lastname = row['vendor_lastname']
		vendor_firstname = row['vendor_firstname']
		vendee_lastname = row['vendee_lastname']
		vendee_firstname = row['vendee_firstname']
		address = row['address']
		vendor_lastname = vendor_lastname.title() # Capitalizes the first letter in each word. Great, except for words like "LLC" (Llc)
		vendor_firstname = vendor_firstname.title()
		vendee_lastname = vendee_lastname.title()
		vendee_firstname = vendee_firstname.title()
		address = address.title()
		# Write over this rows values with newer, cleaner values
		rows[i]['vendor_lastname'] = vendor_lastname
		rows[i]['vendor_firstname'] = vendor_firstname
		rows[i]['vendee_lastname'] = vendee_lastname
		rows[i]['vendee_firstname'] = vendee_firstname
		rows[i]['address'] = address
	# Accumulate all problematic words and give substitutions
	acronyms = [['Llc', 'LLC'], ['Iii', 'III'], ['L L C', 'LLC'], ['Xiv', 'XIV'], ['Ii', 'II'], ['Fbo', 'FBO'], ['Pcw85 ', 'PCW85'], ['Nola', 'NOLA'], ['Fka', 'FKA'], ['Bwe', 'BWE']]
	abbreviations = [['Jr', 'Jr.'], ['Sr', 'Sr.'], ['St ', 'St. '],['Dr ', 'Dr. ']]
	mcnames = [['Mca', 'McA'], ['Mcb', 'McB'], ['Mcc', 'McC'], ['Mcd', 'McD'], ['Mce', 'McE'], ['Mcf', 'McF'], ['Mcg', 'McG'], ['Mch', 'McH'], ['Mci', 'McI'], ['Mcj', 'McJ'], ['Mck', 'McK'], ['Mcl', 'McL'], ['Mcm', 'McM'], ['Mcn', 'McN'], ['Mco', 'McO'], ['Mcp', 'McP'], ['Mcq', 'McQ'], ['Mcr', 'McR'], ['Mcs', 'McS'], ['Mct', 'McT'], ['Mcu', 'McU'], ['Mcv', 'McV'], ['Mcw', 'McW'], ['Mcx', 'McX'], ['Mcy', 'McY'], ['Mcz', 'McZ'], ]
	address_abbreviations = [['Blvd', 'Blvd.'], ['Hwy', 'Highway'], [' Rd', ' Road'], ['Ct', 'Court'], ['Ave,', 'Ave.,'], ['Blvd,', 'Blvd.,'], [' To ', ' to '], ['1St,', '1st,'], ['2Nd', '2nd'], ['3Rd,', '3rd,'], ['4Th,', '4th,'], ['5Th', '5th'], ['6Th,', '6th,'], ['7Th,', '7th,'], ['8Th,', '8th,'], ['9Th,', '9th,'], ['0Th,', '0th,']] # Not sure what to do for "St.". This --> [' St', ' St.'] would also pick up something such as 123 Straight Road. The same could conceivably happen with "Ave". "Dr" needs to become "Drive", but have the same problem
	middle_initials = [[' A ', ' A. '], [' B ', ' B. '], [' C ', ' C. '], [' D ', ' D. '], [' E ', ' E. '], [' F ', ' F. '], [' G ', ' G. '], [' H ', ' H. '], [' I ', ' I. '], [' J ', ' J. '], [' K ', ' K. '], [' L ', ' L. '], [' M ', ' M. '], [' N ', ' N. '], [' O ', ' O. '], [' P ', ' P. '], [' Q ', ' Q. '], [' R ', ' R. '], [' S ', ' S. '], [' T ', ' T. '], [' U ', ' U. '], [' V ', ' V. '], [' W ', ' W. '], [' X ', ' X. '], [' Y ', ' Y. '], [' Z ', ' Z. ']]
	# This loop scans for the above problem words and replaces them with their substitutes:
	for i, row in enumerate(rows):
		# Read the current rows values
		vendor_lastname = row['vendor_lastname']
		vendor_firstname = row['vendor_firstname']
		vendee_lastname = row['vendee_lastname']
		vendee_firstname = row['vendee_firstname']
		address = row['address']
		amt = row['amount']
		# Check for occurences of problematic acronyms
		for acronym in acronyms:
			acronym0 = acronym[0] # Problem acronym
			acronym1 = acronym[1] # Solution acronym
			# If find problem acronym (acronym0) in a string, replace with solution acronym (acronym1) 
			vendor_lastname = re.sub(acronym0,acronym1, vendor_lastname)
			vendor_firstname = re.sub(acronym0,acronym1, vendor_firstname)
			vendee_lastname = re.sub(acronym0,acronym1, vendee_lastname)
			vendee_firstname = re.sub(acronym0,acronym1, vendee_firstname)
			address = re.sub(acronym0,acronym1, address)
		# Check for occurences of problematic "Mc" names. Corrections assume that the letter after should be capitalized:
		for mcname in mcnames:
			mcname0 = mcname[0]
			mcname1 = mcname[1]
			vendor_lastname = re.sub(mcname0,mcname1, vendor_lastname)
			vendor_firstname = re.sub(mcname0,mcname1, vendor_firstname)
			vendee_lastname = re.sub(mcname0,mcname1, vendee_lastname)
			vendee_firstname = re.sub(mcname0,mcname1, vendee_firstname)
			address = re.sub(mcname0,mcname1, address)
		# Check for problematic abbreviations:
		for abbreviation in abbreviations:
			abbreviation0 = abbreviation[0]
			abbreviation1 = abbreviation[1]
			vendor_lastname = re.sub(abbreviation0, abbreviation1, vendor_lastname)
			vendor_firstname = re.sub(abbreviation0, abbreviation1, vendor_firstname)
			vendee_lastname = re.sub(abbreviation0, abbreviation1, vendee_lastname)
			vendee_firstname = re.sub(abbreviation0, abbreviation1, vendee_firstname)
			address = re.sub(abbreviation0, abbreviation1, address)
		# Fix address abbreviations (for AP style purposes)
		for address_abbreviation in address_abbreviations:
			address0 = address_abbreviation[0]
			address1 = address_abbreviation[1]
			address = re.sub(address0, address1, address)
		for middle_initial in middle_initials:
			middle_initial0 = middle_initial[0]
			middle_initial1 = middle_initial[1]
			vendor_lastname = re.sub(middle_initial0, middle_initial1, vendor_lastname)
			vendor_firstname = re.sub(middle_initial0, middle_initial1, vendor_firstname)
			vendee_lastname = re.sub(middle_initial0, middle_initial1, vendee_lastname)
			vendee_firstname = re.sub(middle_initial0, middle_initial1, vendee_firstname)
		# Must do regex for "St" and others. Imagine "123 Star St". Scanning for " St" in the above loop 
		# would catch the start of the street name here. "St " wouldn't work either.
		address = re.sub(r"St$",r"St.",address) #Check for "St" followed by end-of-line character
		address = re.sub(r"Ave$",r"Ave.",address)
		address = re.sub(r"Dr$",r"Dr.",address)
		address = re.sub(r" N ",r" N. ",address)
		address = re.sub(r" S ",r" S. ",address)
		address = re.sub(r" E ",r" E. ",address)
		address = re.sub(r" W ",r" W. ",address)
		vendor_lastname = re.sub(r"Inc$",r"Inc.", vendor_lastname)
		vendor_firstname = re.sub(r"Inc$",r"Inc.", vendor_firstname)
		vendee_lastname = re.sub(r"Inc$",r"Inc.", vendee_lastname)
		vendee_firstname = re.sub(r"Inc$",r"Inc.", vendee_firstname)
		amt = str(amt)
		amt = re.sub(r'\$',r'', amt) # remove the $
		amt = re.sub(r',',r'',amt) # remove the comma
		amt = float(amt) # change string to a float
		amt = round(amt) # round to nearest dollar
		amt = int(amt) 

		# Write over current row's values with newer, cleaner, smarter, better values
		rows[i]['vendor_lastname'] = vendor_lastname
		rows[i]['vendor_firstname'] = vendor_firstname
		rows[i]['vendee_lastname'] = vendee_lastname
		rows[i]['vendee_firstname'] = vendee_firstname
		rows[i]['address'] = address.strip(" ,")
		rows[i]['amount'] = amt
	return rows