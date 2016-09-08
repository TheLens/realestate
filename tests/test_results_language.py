
"""Unit tests for www/utils.py."""

import copy
import mock
import unittest

from www.results_language import ResultsLanguage

standard_data = {
    "name_address": "Keyword",
    "number_of_records": 4344,
    "neighborhood": "Gert Town",
    "zip_code": "70125",
    "amount_low": 10,
    "amount_high": 1000,
    "begin_date": "2016-05-01",
    "end_date": "2016-12-31",
    "map_button_state": True}


class TestResultsLanguage(unittest.TestCase):
    """Test cases for www/results_language.py."""

    def test_plural_or_not(self):
        """Test convert_amount()."""
        expected = "sales"

        rl = ResultsLanguage(standard_data)
        actual = rl.plural_or_not()

        self.assertEqual(actual, expected)

    def test_plural_or_not_single(self):
        """Test convert_amount() for a single sale."""
        expected = "sale"

        new_data = copy.deepcopy(standard_data)
        new_data["number_of_records"] = 1
        rl = ResultsLanguage(new_data)

        actual = rl.plural_or_not()

        self.assertEqual(actual, expected)

    @mock.patch('www.results_language.get_number_with_commas')
    def test_add_initial_language(self, mock_commas):
        """Test add_initial_language()."""
        mock_commas.return_value = "One"

        input = "sale"
        expected = "One sale found"

        rl = ResultsLanguage(standard_data)
        actual = rl.add_initial_language(input)

        self.assertEqual(actual, expected)

    def test_add_keyword_language_keyword(self):
        """Test add_keyword_language() for single word."""
        input = "Current language"
        expected = 'Current language for keyword "Keyword"'

        rl = ResultsLanguage(standard_data)
        actual = rl.add_keyword_language(input)

        self.assertEqual(actual, expected)

    def test_add_keyword_language_key_phrase(self):
        """Test add_keyword_language() for multiple words."""
        input = "Current language"
        expected = 'Current language for key phrase "Key phrase"'

        new_data = copy.deepcopy(standard_data)
        new_data["name_address"] = "Key phrase"
        rl = ResultsLanguage(new_data)

        actual = rl.add_keyword_language(input)

        self.assertEqual(actual, expected)

    def test_add_keyword_language_key_empty(self):
        """Test add_keyword_language() for empty search."""
        input = "Current language"
        expected = 'Current language'

        new_data = copy.deepcopy(standard_data)
        new_data["name_address"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_keyword_language(input)

        self.assertEqual(actual, expected)

    def test_add_nbhd_zip_language_nothing_new(self):
        """Test add_nbhd_zip_language() nothing new."""
        input = "Current sentence"
        expected = "Current sentence"

        new_data = copy.deepcopy(standard_data)
        new_data["neighborhood"] = ""
        new_data["zip_code"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_nbhd_zip_language(input)

        self.assertEqual(actual, expected)

    def test_add_nbhd_zip_language_zip_only(self):
        """Test add_nbhd_zip_language() with zip only."""
        input = "Current sentence"
        expected = "Current sentence in ZIP code 70125"

        new_data = copy.deepcopy(standard_data)
        new_data["neighborhood"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_nbhd_zip_language(input)

        self.assertEqual(actual, expected)

    def test_add_nbhd_zip_language_nbhd_only(self):
        """Test add_nbhd_zip_language() with neighborhood only."""
        input = "Current sentence"
        expected = "Current sentence in the Gert Town neighborhood"

        new_data = copy.deepcopy(standard_data)
        new_data["zip_code"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_nbhd_zip_language(input)

        self.assertEqual(actual, expected)

    def test_add_nbhd_zip_language_nbhd_and_zip(self):
        """Test add_nbhd_zip_language() with zip and neighborhood."""
        input = "Current sentence"
        expected = "Current sentence in the Gert Town neighborhood and 70125"

        rl = ResultsLanguage(standard_data)
        actual = rl.add_nbhd_zip_language(input)

        self.assertEqual(actual, expected)

    def test_add_amount_language_none(self):
        """Test add_amount_language() without anything new."""
        input = "Current sentence"
        expected = "Current sentence"

        new_data = copy.deepcopy(standard_data)
        new_data["amount_low"] = ""
        new_data["amount_high"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_amount_language(input)

        self.assertEqual(actual, expected)

    def test_add_amount_language_both(self):
        """Test add_amount_language() with both."""
        input = "Current sentence"
        expected = "Current sentence where the price was between " + \
            "$10 and $1,000"

        rl = ResultsLanguage(standard_data)
        actual = rl.add_amount_language(input)

        self.assertEqual(actual, expected)

    def test_add_amount_language_low_only(self):
        """Test add_amount_language() with low amount only."""
        input = "Current sentence"
        expected = "Current sentence where the price was greater than $10"

        new_data = copy.deepcopy(standard_data)
        new_data["amount_high"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_amount_language(input)

        self.assertEqual(actual, expected)

    def test_add_amount_language_high_only(self):
        """Test add_amount_language() with high amount only."""
        input = "Current sentence"
        expected = "Current sentence where the price was less than $1,000"

        new_data = copy.deepcopy(standard_data)
        new_data["amount_low"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_amount_language(input)

        self.assertEqual(actual, expected)

    def test_add_date_language_none(self):
        """Test add_date_language() without any new data."""
        input = "Current sentence"
        expected = "Current sentence"

        new_data = copy.deepcopy(standard_data)
        new_data["begin_date"] = ""
        new_data["end_date"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_date_language(input)

        self.assertEqual(actual, expected)

    def test_add_date_language_both(self):
        """Test add_date_language() with both dates."""
        input = "Current sentence"
        expected = "Current sentence between May 1, 2016, and Dec. 31, 2016,"

        rl = ResultsLanguage(standard_data)
        actual = rl.add_date_language(input)

        self.assertEqual(actual, expected)

    def test_add_date_language_begin_only(self):
        """Test add_date_language() with beginning date only."""
        input = "Current sentence"
        expected = "Current sentence after May 1, 2016,"

        new_data = copy.deepcopy(standard_data)
        new_data["end_date"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_date_language(input)

        self.assertEqual(actual, expected)

    def test_add_date_language_end_only(self):
        """Test add_date_language() with end date only."""
        input = "Current sentence"
        expected = "Current sentence before Dec. 31, 2016,"

        new_data = copy.deepcopy(standard_data)
        new_data["begin_date"] = ""
        rl = ResultsLanguage(new_data)

        actual = rl.add_date_language(input)

        self.assertEqual(actual, expected)

    def test_add_map_filtering_language(self):
        """Test add_map_filtering_language()."""
        input = "Current sentence"
        expected = "Current sentence in the current map view"

        rl = ResultsLanguage(standard_data)  # True
        actual = rl.add_map_filtering_language(input)

        self.assertEqual(actual, expected)

    def test_add_final_sentence_language_no_quotes(self):
        """Test add_final_sentence_language() without quotes."""
        input = "Current sentence"
        expected = "Current sentence."

        rl = ResultsLanguage(standard_data)
        actual = rl.add_final_sentence_language(input)

        self.assertEqual(actual, expected)

    def test_add_final_sentence_language_end_on_date(self):
        """Test add_final_sentence_language() ending on a date."""
        input = "Current sentence Dec. 31, 2016,"
        expected = "Current sentence Dec. 31, 2016."

        rl = ResultsLanguage(standard_data)
        actual = rl.add_final_sentence_language(input)

        self.assertEqual(actual, expected)

    def test_add_final_sentence_language_single_quotes(self):
        """Test add_final_sentence_language() with single quotes at end."""
        input = "Current 'sentence'"
        expected = "Current 'sentence.'"

        rl = ResultsLanguage(standard_data)
        actual = rl.add_final_sentence_language(input)

        self.assertEqual(actual, expected)

    def test_add_final_sentence_language_double_quotes(self):
        """Test add_final_sentence_language() with double quotes at end."""
        input = 'Current "sentence"'
        expected = 'Current "sentence."'

        rl = ResultsLanguage(standard_data)
        actual = rl.add_final_sentence_language(input)

        self.assertEqual(actual, expected)

    def test_main_all(self):
        """Test main() with all components."""
        expected = (
            '4,344 sales found for keyword "Keyword" in the Gert Town ' +
            "neighborhood and 70125 where the price was between $10 and " +
            "$1,000 between May 1, 2016, and Dec. 31, 2016, in the " +
            "current map view.")

        rl = ResultsLanguage(standard_data)
        actual = rl.main()

        self.assertEqual(actual, expected)
