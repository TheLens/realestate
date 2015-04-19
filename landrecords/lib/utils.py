# -*- coding: utf-8 -*-

'''Common utility functions, like converting between dates and types.'''

import re
from datetime import datetime

# from landrecords import log


class Utils(object):

    '''Common utility functions.'''

    zip_codes = [
        70112, 70113, 70114, 70115, 70116, 70117, 70118,
        70119, 70121, 70122, 70123, 70124, 70125, 70126,
        70127, 70128, 70129, 70130, 70131, 70139, 70140,
        70141, 70142, 70143, 70145, 70146, 70148, 70149,
        70150, 70151, 70152, 70153, 70154, 70156, 70157,
        70158, 70159, 70160, 70161, 70162, 70163, 70164,
        70165, 70166, 70167, 70170, 70172, 70174, 70175,
        70176, 70177, 70178, 70179, 70181, 70182, 70183,
        70184, 70185, 70186, 70187, 70189, 70190, 70195
    ]

    @staticmethod
    def get_number_with_commas(value):
        '''Convert interger to string with commas.'''

        return "{:,}".format(value)

    @staticmethod
    def get_num_with_curr_sign(value):
        '''Convert integer to string with commas and dollar sign.'''

        value = int(value)
        return "${:,}".format(value)

    @staticmethod
    def ymd_to_mdy(value):
        '''Convert yyyy-mm-dd to mm-dd-yyyy.'''

        if value is not None:
            return value.strftime("%m-%d-%Y")
        else:
            return "None"

    @staticmethod
    def ymd_to_full_date(value, no_day=False):
        '''Convert yyyy-mm-dd to Day, Month Date, Year.'''

        if value is not None:
            if isinstance(value, unicode):
                # value = urllib.unquote(value).decode('utf8')
                readable_date = str(value)
                readable_date = datetime.strptime(readable_date, '%m/%d/%Y')
                readable_date = readable_date.strftime('%b. %-d, %Y')

            else:
                # value = str(value)
                if no_day is False:
                    readable_datetime = datetime.strptime(value, '%Y-%m-%d')
                    readable_date = readable_datetime.strftime(
                        '%A, %b. %-d, %Y')
                else:
                    readable_datetime = datetime.strptime(value, '%Y-%m-%d')
                    readable_date = readable_datetime.strftime('%b. %-d, %Y')

            readable_date = readable_date.replace('Mar.', 'March')
            readable_date = readable_date.replace('Apr.', 'April')
            readable_date = readable_date.replace('May.', 'May')
            readable_date = readable_date.replace('Jun.', 'June')
            readable_date = readable_date.replace('Jul.', 'July')

            return readable_date  # value.strftime('%A, %b. %-d, %Y')

        else:
            return "None"

    @staticmethod
    def convert_month_to_ap_style(month):
        '''Convert month to AP Style. Ex. January => Jan.'''

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

    @staticmethod
    def binary_to_english(bit):
        '''Convert 0/1 to No/Yes.'''

        bit = int(bit)
        conversion_dict = {
            0: "No",
            1: "Yes"
        }
        english = conversion_dict[bit]
        return english

    @staticmethod
    def english_to_binary(english):
        '''Convert No/Yes to 0/1.'''

        # Accepts Yes, Y, yeah, yes sir, etc.
        english = english[0].title()
        conversion_dict = {
            "N": 0,
            "Y": 1
        }
        bit = conversion_dict[english]
        return bit

if __name__ == '__main__':
    pass
