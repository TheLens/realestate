
"""Unit tests for www/utils.py."""

import unittest

from www.utils import (
    convert_amount,
    get_number_with_commas,
    get_num_with_curr_sign,
    ymd_to_mdy,
    ymd_to_mdy_slashes,
    ymd_to_full_date,
    convert_month_to_ap_style,
    binary_to_english,
    english_to_binary)


class TestUtils(unittest.TestCase):
    """Test cases for www/utils.py."""

    def test_convert_amount(self):
        """Test convert_amount()."""
        input = "$4,000"
        expected = 4000
        actual = convert_amount(input)

        self.assertEqual(actual, expected)

    def test_get_number_with_commas(self):
        """Test get_number_with_commas()."""
        input = 5000
        expected = '5,000'
        actual = get_number_with_commas(input)

        self.assertEqual(actual, expected)

    def test_get_num_with_curr_sign(self):
        """Test get_num_with_curr_sign()."""
        input = 5000
        expected = '$5,000'
        actual = get_num_with_curr_sign(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_mdy(self):
        """Test ymd_to_mdy()."""
        input = "2016-12-31"
        expected = "12-31-2016"
        actual = ymd_to_mdy(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_mdy_none(self):
        """Test ymd_to_mdy() when input is None."""
        input = None
        expected = "None"
        actual = ymd_to_mdy(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_mdy_slashes(self):
        """Test ymd_to_mdy_slashes()."""
        input = "2016-12-31"
        expected = "12/31/2016"
        actual = ymd_to_mdy_slashes(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_mdy_slashes_none(self):
        """Test ymd_to_mdy_slashes() when input is None."""
        input = None
        expected = "None"
        actual = ymd_to_mdy_slashes(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date(self):
        """Test ymd_to_full_date()."""
        input = "2016-12-31"
        expected = "Saturday, Dec. 31, 2016"
        actual = ymd_to_full_date(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date_no_leading_zero(self):
        """Test ymd_to_full_date() with one-digit date."""
        input = "2016-12-01"
        expected = "Thursday, Dec. 1, 2016"
        actual = ymd_to_full_date(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date_no_ap_month_abbr(self):
        """Test ymd_to_full_date() with unabbreviated month."""
        input = "2016-07-21"
        expected = "Thursday, July 21, 2016"
        actual = ymd_to_full_date(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date_no_day(self):
        """Test ymd_to_full_date() without day."""
        input = "2016-12-31"
        expected = "Dec. 31, 2016"
        actual = ymd_to_full_date(input, no_day=True)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date_slashes(self):
        """Test ymd_to_full_date() when input has slashes."""
        input = "12/31/2016"
        expected = "Dec. 31, 2016"
        actual = ymd_to_full_date(input)

        self.assertEqual(actual, expected)

    def test_ymd_to_full_date_none(self):
        """Test ymd_to_full_date() when input is None."""
        input = None
        expected = "None"
        actual = ymd_to_full_date(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_january(self):
        """Test convert_month_to_ap_style() for January."""
        input = "January"
        expected = "Jan."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_february(self):
        """Test convert_month_to_ap_style() for February."""
        input = "February"
        expected = "Feb."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_march(self):
        """Test convert_month_to_ap_style() for March."""
        input = "March"
        expected = "March"
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_april(self):
        """Test convert_month_to_ap_style() for April."""
        input = "April"
        expected = "April"
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_no_abbr(self):
        """Test convert_month_to_ap_style() for May."""
        input = "May"
        expected = "May"
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_june(self):
        """Test convert_month_to_ap_style() for June."""
        input = "June"
        expected = "June"
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_july(self):
        """Test convert_month_to_ap_style() for July."""
        input = "July"
        expected = "July"
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_august(self):
        """Test convert_month_to_ap_style() for August."""
        input = "August"
        expected = "Aug."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_september(self):
        """Test convert_month_to_ap_style() for September."""
        input = "September"
        expected = "Sept."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_october(self):
        """Test convert_month_to_ap_style() for October."""
        input = "October"
        expected = "Oct."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_november(self):
        """Test convert_month_to_ap_style() for November."""
        input = "November"
        expected = "Nov."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_convert_month_to_ap_style_december(self):
        """Test convert_month_to_ap_style() for December."""
        input = "December"
        expected = "Dec."
        actual = convert_month_to_ap_style(input)

        self.assertEqual(actual, expected)

    def test_binary_to_english_1(self):
        """Test binary_to_english() when input is 1."""
        input = 1
        expected = "Yes"
        actual = binary_to_english(input)

        self.assertEqual(actual, expected)

    def test_binary_to_english_0(self):
        """Test binary_to_english() when input is 0."""
        input = 0
        expected = "No"
        actual = binary_to_english(input)

        self.assertEqual(actual, expected)

    def test_english_to_binary_yes(self):
        """Test english_to_binary()."""
        input = "Yes"
        expected = 1
        actual = english_to_binary(input)

        self.assertEqual(actual, expected)

    def test_english_to_binary_ya(self):
        """Test english_to_binary()."""
        input = "ya"
        expected = 1
        actual = english_to_binary(input)

        self.assertEqual(actual, expected)

    def test_english_to_binary_no(self):
        """Test english_to_binary()."""
        input = "No"
        expected = 0
        actual = english_to_binary(input)

        self.assertEqual(actual, expected)

    def test_english_to_binary_nah(self):
        """Test english_to_binary()."""
        input = "nah"
        expected = 0
        actual = english_to_binary(input)

        self.assertEqual(actual, expected)
