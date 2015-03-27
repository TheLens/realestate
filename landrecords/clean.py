# -*- coding: utf-8 -*-

import re
import pprint
import logging

pp = pprint.PrettyPrinter()


def initialize_log():
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs debug messages or higher
    fh = logging.FileHandler('logs/initialize.log')
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('''
        %(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(lineno)d
        - %(message)s''')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)


class Clean(object):

    def __init__(self):
        self.rows = "rows"  # self.get_rows()  # todo: define this function

    def get_number_with_commas(self, value):
        return "{:,}".format(value)

    def get_number_with_currency_sign(self, value):
        value = int(value)
        return "${:,}".format(value)

    def ymd_to_mdy(self, value):
        # Receive yyyy-mm-dd. Return mm-dd-yyyy
        if value is not None:
            return value.strftime("%m-%d-%Y")
        else:
            return "None"

    def ymd_to_full_date(self, value, no_day=None):
        # Receive yyyy-mm-dd. Return Day, Month Date, Year
        if value is not None:
            if (type(value) == unicode):
                # value = urllib.unquote(value).decode('utf8')
                readable_date = str(value)
                readable_date = datetime.strptime(readable_date, '%m/%d/%Y')
                readable_date = readable_date.strftime('%b. %-d, %Y')

            else:
                # value = str(value)
                if no_day is None:
                    readable_date = value.strftime('%A, %b. %-d, %Y')
                else:
                    readable_date = value.strftime('%b. %-d, %Y')

            readable_date = readable_date.replace('Mar.', 'March')
            readable_date = readable_date.replace('Apr.', 'April')
            readable_date = readable_date.replace('May.', 'May')
            readable_date = readable_date.replace('Jun.', 'June')
            readable_date = readable_date.replace('Jul.', 'July')

            return readable_date  # value.strftime('%A, %b. %-d, %Y')

        else:
            return "None"

    def convert_month_to_ap_style(self, month):
        if re.match(r"[jJ][aA]", month) is not None:
            month = "Jan."

        if re.match(r"[fF]", month) is not None:
            month = "Feb."

        if re.match(r"[mM][aA][rR]", month) is not None:
            month = "March"

        if re.match(r"[aA][pP]", month) is not None:
            month = "April"

        if re.match(r"[mM][aA][yY]", month) is not None:
            month = "May"

        if re.match(r"[jJ][uU][nN]", month) is not None:
            month = "June"

        if re.match(r"[jJ][uU][lL]", month) is not None:
            month = "July"

        if re.match(r"[aA][uU]", month) is not None:
            month = "Aug."

        if re.match(r"[sS][eE]", month) is not None:
            month = "Sept."

        if re.match(r"[oO][cC]", month) is not None:
            month = "Oct."

        if re.match(r"[nN][oO]", month) is not None:
            month = "Nov."

        if re.match(r"[dD][eE]", month) is not None:
            month = "Dec."

        return month

    def binary_to_english(self, bit):
        bit = int(bit)
        conversion_dict = {
            0: "No",
            1: "Yes"
        }
        english = conversion_dict[bit]
        return english

    def english_to_binary(self, english):
        # Accepts Yes, Y, yeah, yes sir, etc.
        english = english[0].title()
        conversion_dict = {
            "N": 0,
            "Y": 1
        }
        bit = conversion_dict[english]
        return bit

    def CleanNew(self, rows):
        '''
        This function takes in ALL CAPS and returns clean text.
        '''

        logger.info('CleanNew')

        # This loop returns text that is not all-caps, but is still flawed:
        for i, row in enumerate(rows): # to standardize upper and lowercases
            # Read this row's values
            sellers = row['sellers']
            buyers = row['buyers']
            address = row['address']
            location_info = row['location_info']
            neighborhood = row['neighborhood']

            # Capitalizes the first letter in each word.
            # Results in words like Llc, Xiv, etc
            sellers = sellers.title()
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
                    except Exception, e:
                        logger.error(e, exc_info=True)
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
                    except Exception, e:
                        logger.error(e, exc_info=True)
                        continue

                    #print 'individiual_location_text:', individiual_location_text

                if all_locations_text == '':
                    if individiual_location_text != '':
                        all_locations_text = individiual_location_text.strip()
                else:
                    if individiual_location_text != '':
                        all_locations_text = all_locations_text + '; ' + individiual_location_text.strip()

            #unit = re.match(r"^.*UNIT\: (.*)\, CONDO", location_info).group(1)

            logger.info('Final values:')

            # Write over current row's values with newer, cleaner, smarter, better values
            rows[i]['sellers'] = sellers.strip(' ,').replace('  ', ' ').replace(' ,', ',')
            logger.debug(rows[i]['sellers'])

            rows[i]['buyers'] = buyers.strip(' ,').replace('  ', ' ').replace(' ,', ',')
            logger.debug(rows[i]['buyers'])

            rows[i]['address'] = all_addresses_text.strip(" ,").replace('  ', ' ').replace(' ,', ',')
            logger.debug(rows[i]['address'])

            rows[i]['location_info'] = all_locations_text.strip(" ,").replace('  ', ' ').replace(' ,', ',')
            logger.debug(rows[i]['location_info'])

            rows[i]['amount'] = amt
            logger.debug(rows[i]['amount'])

            rows[i]['neighborhood'] = neighborhood.replace('  ', ' ').replace(' ,', ',')
            logger.debug(rows[i]['neighborhood'])

        return rows
