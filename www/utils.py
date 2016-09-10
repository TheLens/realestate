# -*- coding: utf-8 -*-

"""Utility functions."""

import re

from datetime import datetime


zip_codes = [
    70112, 70113, 70114, 70115, 70116, 70117, 70118, 70119, 70121, 70122,
    70123, 70124, 70125, 70126, 70127, 70128, 70129, 70130, 70131, 70139,
    70140, 70141, 70142, 70143, 70145, 70146, 70148, 70149, 70150, 70151,
    70152, 70153, 70154, 70156, 70157, 70158, 70159, 70160, 70161, 70162,
    70163, 70164, 70165, 70166, 70167, 70170, 70172, 70174, 70175, 70176,
    70177, 70178, 70179, 70181, 70182, 70183, 70184, 70185, 70186, 70187,
    70189, 70190, 70195]


def convert_amount(amount):
    """Convert formatted string amount to integer."""
    amount = re.sub(r"\$", r"", amount)
    amount = re.sub(r"\,", r"", amount)
    return int(float(amount))


def get_number_with_commas(value):
    """Convert integer to formatted string."""
    return "{:,}".format(value)


def get_num_with_curr_sign(value):
    """Convert integer to formatted currency string."""
    return "${:,}".format(int(value))


def ymd_to_mdy(value):
    """
    Convert yyyy-mm-dd to mm-dd-yyyy.

    :param value: A date string.
    :type value: str
    :returns: str
    """
    if value is None:
        return "None"
    else:
        value = datetime.strptime(value, '%Y-%m-%d').date()
        return value.strftime("%m-%d-%Y")


def ymd_to_mdy_slashes(value):
    """Convert yyyy-mm-dd to mm/dd/yyyy."""
    if value is None:
        return "None"
    else:
        value = datetime.strptime(value, '%Y-%m-%d').date()
        value = value.strftime("%m/%d/%Y")
        return value


def ymd_to_full_date(value, no_day=False):
    """Convert yyyy-mm-dd to Day, Month Date, Year."""
    if value is None:
        return "None"

    # 12/31/2016. Why?
    # if isinstance(value, unicode):  # TODO: Why? Remove.
    if value[2] == "/":  # TODO: Hack. Improve.
        readable_date = str(value)
        readable_date = datetime.strptime(
            readable_date, '%m/%d/%Y').date()
        readable_date = readable_date.strftime('%b. %-d, %Y')
    else:  # 2016-12-31. Why?
        if no_day is False:
            readable_datetime = datetime.strptime(
                value, '%Y-%m-%d').date()
            readable_date = readable_datetime.strftime(
                '%A, %b. %-d, %Y')
        else:
            readable_datetime = datetime.strptime(
                value, '%Y-%m-%d').date()
            readable_date = readable_datetime.strftime('%b. %-d, %Y')

    readable_date = readable_date.replace('Mar.', 'March')
    readable_date = readable_date.replace('Apr.', 'April')
    readable_date = readable_date.replace('May.', 'May')
    readable_date = readable_date.replace('Jun.', 'June')
    readable_date = readable_date.replace('Jul.', 'July')
    return readable_date


def convert_month_to_ap_style(month):
    """
    Convert month to abbreviated AP style.

    Ex. January => Jan. May ==> May.
    """
    if re.match(r"[jJ][aA]", month):
        month = "Jan."

    if re.match(r"[fF]", month):
        month = "Feb."

    if re.match(r"[mM][aA][rR]", month):
        month = "March"

    if re.match(r"[aA][pP]", month):
        month = "April"

    if re.match(r"[mM][aA][yY]", month):
        month = "May"

    if re.match(r"[jJ][uU][nN]", month):
        month = "June"

    if re.match(r"[jJ][uU][lL]", month):
        month = "July"

    if re.match(r"[aA][uU]", month):
        month = "Aug."

    if re.match(r"[sS][eE]", month):
        month = "Sept."

    if re.match(r"[oO][cC]", month):
        month = "Oct."

    if re.match(r"[nN][oO]", month):
        month = "Nov."

    if re.match(r"[dD][eE]", month):
        month = "Dec."

    return month


def binary_to_english(bit):
    """Convert 0/1 to No/Yes."""
    bit = int(bit)
    conversion_dict = {
        0: "No",
        1: "Yes"}
    english = conversion_dict[bit]
    return english


def english_to_binary(english):
    """Convert No/Yes to 0/1."""
    # Accepts Yes, Y, yeah, yes sir, etc.
    english = english[0].upper()
    conversion_dict = {
        "N": 0,
        "Y": 1}
    bit = conversion_dict[english]
    return bit
