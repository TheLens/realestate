
"""Unit tests for www/results_language.py."""

import copy
import os
import sys
import unittest

from mock import patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../www')))

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

    def setUp(self):
        """Set up each unit test."""
        self.rl = ResultsLanguage(standard_data)

    def test_plural_or_not(self):
        """Test convert_amount()."""
        output = self.rl.plural_or_not()
        self.assertEqual(output, "sales")

    def test_plural_or_not_single(self):
        """Test convert_amount() for a single sale."""
        new_data = copy.deepcopy(standard_data)
        new_data["number_of_records"] = 1

        self.rl = ResultsLanguage(new_data)
        output = self.rl.plural_or_not()

        self.assertEqual(output, "sale")

    @patch('www.results_language.utils.get_number_with_commas')
    def test_add_initial_language(self, mock_utils):
        """Test add_initial_language()."""
        mock_utils.return_value = "4,344"

        output = self.rl.add_initial_language("sales")

        self.assertEqual(output, "4,344 sales found")

    def test_add_keyword_language_keyword(self):
        """Test add_keyword_language() for single word."""
        output = self.rl.add_keyword_language("Sentence")
        self.assertEqual(output, 'Sentence for keyword "Keyword"')

    def test_add_keyword_language_key_phrase(self):
        """Test add_keyword_language() for multiple words."""
        new_data = copy.deepcopy(standard_data)
        new_data["name_address"] = "Key phrase"

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_keyword_language("Sentence")

        self.assertEqual(output, 'Sentence for key phrase "Key phrase"')

    def test_add_keyword_language_key_empty(self):
        """Test add_keyword_language() for empty search."""
        new_data = copy.deepcopy(standard_data)
        new_data["name_address"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_keyword_language("Current sentence")

        self.assertEqual(output, "Current sentence")

    def test_add_nbhd_zip_language_nothing_new(self):
        """Test add_nbhd_zip_language() nothing new."""
        new_data = copy.deepcopy(standard_data)
        new_data["neighborhood"] = ""
        new_data["zip_code"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_nbhd_zip_language("Current sentence")

        self.assertEqual(output, "Current sentence")

    def test_add_nbhd_zip_language_zip_only(self):
        """Test add_nbhd_zip_language() with zip only."""
        new_data = copy.deepcopy(standard_data)
        new_data["neighborhood"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_nbhd_zip_language("Current sentence")

        self.assertEqual(output, "Current sentence in ZIP code 70125")

    def test_add_nbhd_zip_language_nbhd_only(self):
        """Test add_nbhd_zip_language() with neighborhood only."""
        new_data = copy.deepcopy(standard_data)
        new_data["zip_code"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_nbhd_zip_language("Current sentence")

        self.assertEqual(
            output, "Current sentence in the Gert Town neighborhood")

    def test_add_nbhd_zip_language_nbhd_and_zip(self):
        """Test add_nbhd_zip_language() with zip and neighborhood."""
        output = self.rl.add_nbhd_zip_language("Current sentence")
        self.assertEqual(
            output, "Current sentence in the Gert Town neighborhood and 70125")

    def test_add_amount_language_none(self):
        """Test add_amount_language() without anything new."""
        new_data = copy.deepcopy(standard_data)
        new_data["amount_low"] = ""
        new_data["amount_high"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_amount_language("Current sentence")

        self.assertEqual(output, "Current sentence")

    def test_add_amount_language_both(self):
        """Test add_amount_language() with both."""
        output = self.rl.add_amount_language("Current sentence")
        self.assertEqual(
            output,
            "Current sentence where the price was between $10 and $1,000")

    def test_add_amount_language_low_only(self):
        """Test add_amount_language() with low amount only."""
        new_data = copy.deepcopy(standard_data)
        new_data["amount_high"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_amount_language("Current sentence")

        self.assertEqual(
            output, "Current sentence where the price was greater than $10")

    def test_add_amount_language_high_only(self):
        """Test add_amount_language() with high amount only."""
        new_data = copy.deepcopy(standard_data)
        new_data["amount_low"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_amount_language("Current sentence")

        self.assertEqual(
            output, "Current sentence where the price was less than $1,000")

    def test_add_date_language_none(self):
        """Test add_date_language() without any new data."""
        new_data = copy.deepcopy(standard_data)
        new_data["begin_date"] = ""
        new_data["end_date"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_date_language("Current sentence")

        self.assertEqual(output, "Current sentence")

    def test_add_date_language_both(self):
        """Test add_date_language() with both dates."""
        output = self.rl.add_date_language("Current sentence")
        self.assertEqual(
            output, "Current sentence between May 1, 2016, and Dec. 31, 2016,")

    def test_add_date_language_begin_only(self):
        """Test add_date_language() with beginning date only."""
        new_data = copy.deepcopy(standard_data)
        new_data["end_date"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_date_language("Current sentence")

        self.assertEqual(output, "Current sentence after May 1, 2016,")

    def test_add_date_language_end_only(self):
        """Test add_date_language() with end date only."""
        new_data = copy.deepcopy(standard_data)
        new_data["begin_date"] = ""

        self.rl = ResultsLanguage(new_data)
        output = self.rl.add_date_language("Current sentence")

        self.assertEqual(output, "Current sentence before Dec. 31, 2016,")

    def test_add_map_filtering_language(self):
        """Test add_map_filtering_language()."""
        output = self.rl.add_map_filtering_language("Current sentence")
        self.assertEqual(output, "Current sentence in the current map view")

    def test_add_final_sentence_language_no_quotes(self):
        """Test add_final_sentence_language() without quotes."""
        output = self.rl.add_final_sentence_language("Current sentence")
        self.assertEqual(output, "Current sentence.")

    def test_add_final_sentence_language_end_on_date(self):
        """Test add_final_sentence_language() ending on a date."""
        output = self.rl.add_final_sentence_language(
            "Current sentence Dec. 31, 2016,")
        self.assertEqual(output, "Current sentence Dec. 31, 2016.")

    def test_add_final_sentence_language_single_quotes(self):
        """Test add_final_sentence_language() with single quotes at end."""
        output = self.rl.add_final_sentence_language("Current 'sentence'")
        self.assertEqual(output, "Current 'sentence.'")

    def test_add_final_sentence_language_double_quotes(self):
        """Test add_final_sentence_language() with double quotes at end."""
        output = self.rl.add_final_sentence_language('Current "sentence"')
        self.assertEqual(output, 'Current "sentence."')

    def test_main_all(self):
        """Test main() with all components."""
        output = self.rl.main()
        expected = (
            '4,344 sales found for keyword "Keyword" in the Gert Town ' +
            "neighborhood and 70125 where the price was between $10 and " +
            "$1,000 between May 1, 2016, and Dec. 31, 2016, in the " +
            "current map view.")

        self.assertEqual(output, expected)

if __name__ == '__main__':
    unittest.main()
