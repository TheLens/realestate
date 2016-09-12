
"""Unit tests for www/utils.py."""

import mock
import unittest

from scripts.initialize import (
    BadDateRangeError, initialize, cli, cli_has_errors)

# Good
single_date_arguments = {
    "<single_date>": "2016-12-11",
    "<early_date>": None,
    "<late_date>": None}

date_range_arguments = {
    "<single_date>": None,
    "<early_date>": "2016-12-21",
    "<late_date>": "2016-12-31"}

no_arguments = {
    "<single_date>": None,
    "<early_date>": None,
    "<late_date>": None}

# Bad
all_arguments = {
    "<single_date>": "2016-12-11",
    "<early_date>": "2016-12-21",
    "<late_date>": "2016-12-31"}

single_and_early_arguments = {
    "<single_date>": "2016-12-11",
    "<early_date>": "2016-12-21",
    "<late_date>": None}

single_and_late_arguments = {
    "<single_date>": "2016-12-11",
    "<early_date>": None,
    "<late_date>": "2016-12-31"}

early_only_arguments = {
    "<single_date>": None,
    "<early_date>": "2016-12-21",
    "<late_date>": None}

late_only_arguments = {
    "<single_date>": None,
    "<early_date>": None,
    "<late_date>": "2016-12-31"}

backward_date_range_arguments = {
    "<single_date>": None,
    "<early_date>": "2016-12-31",
    "<late_date>": "2016-12-21"}


class TestInitialize(unittest.TestCase):
    """Test cases for scripts/initialize.py."""

    def test_cli_errors_all(self):
        """Test cli_has_errors() when all arguments supplied."""
        output = cli_has_errors(all_arguments)
        self.assertEqual(output, True)

    def test_cli_errors_single_and_early(self):
        """Test cli_has_errors() with single and early bound date arguments."""
        output = cli_has_errors(single_and_early_arguments)
        self.assertEqual(output, True)

    def test_cli_errors_single_and_late(self):
        """Test cli_has_errors() with single and late bound date arguments."""
        output = cli_has_errors(single_and_late_arguments)
        self.assertEqual(output, True)

    def test_cli_errors_early_only(self):
        """Test cli_has_errors() with early bound date only."""
        output = cli_has_errors(early_only_arguments)
        self.assertEqual(output, True)

    def test_cli_errors_late_only(self):
        """Test cli_has_errors() with late bound date only."""
        output = cli_has_errors(late_only_arguments)
        self.assertEqual(output, True)

    def test_cli_errors_single_date(self):
        """Test cli_has_errors() with single date only."""
        output = cli_has_errors(single_date_arguments)
        self.assertEqual(output, False)

    def test_cli_errors_date_range(self):
        """Test cli_has_errors() with date range only."""
        output = cli_has_errors(date_range_arguments)
        self.assertEqual(output, False)

    def test_cli_errors_no_date(self):
        """Test cli_has_errors() with no supplied dates."""
        output = cli_has_errors(no_arguments)
        self.assertEqual(output, False)

    @mock.patch('scripts.initialize.cli_has_errors')
    def test_cli_with_parsing_errors(self, mock_cli_has_errors):
        """Test cli() when there are CLI parsing errors."""
        mock_cli_has_errors.return_value = True
        output = cli(no_arguments)
        self.assertEqual(output, None)

    @mock.patch('scripts.initialize.initialize')
    @mock.patch('scripts.initialize.cli_has_errors')
    def test_cli_no_date(self, mock_cli_has_errors, mock_initialize):
        """Test cli() without specified date."""
        mock_cli_has_errors.return_value = False
        cli(no_arguments)
        mock_initialize.assert_called_with()

    @mock.patch('scripts.initialize.initialize')
    @mock.patch('scripts.initialize.cli_has_errors')
    def test_cli_single_date(self, mock_cli_has_errors, mock_initialize):
        """Test cli() with single date only."""
        mock_cli_has_errors.return_value = False
        cli(single_date_arguments)
        mock_initialize.assert_called_with(
            initial_date=single_date_arguments['<single_date>'],
            until_date=single_date_arguments['<single_date>'])

    @mock.patch('scripts.initialize.initialize')
    @mock.patch('scripts.initialize.cli_has_errors')
    def test_cli_date_range(self, mock_cli_has_errors, mock_initialize):
        """Test cli() with date range."""
        mock_cli_has_errors.return_value = False
        cli(date_range_arguments)
        mock_initialize.assert_called_with(
            initial_date=date_range_arguments['<early_date>'],
            until_date=date_range_arguments['<late_date>'])

    @mock.patch('scripts.initialize.initialize')
    @mock.patch('scripts.initialize.cli_has_errors')
    def test_cli_backward_date_range(self, mock_cli_has_errors, mock_init):
        """Test cli() with backward date range."""
        mock_cli_has_errors.return_value = False

        with self.assertRaises(BadDateRangeError):
            cli(backward_date_range_arguments)

    # initialize()
    @mock.patch('scripts.initialize.Publish')
    @mock.patch('scripts.initialize.GetDates')
    @mock.patch('scripts.initialize.Geocode')
    @mock.patch('scripts.initialize.Clean')
    @mock.patch('scripts.initialize.Build')
    def test_initialize_no_dates(self, mock_build, mock_clean, mock_geocode,
                                 mock_getdates, mock_publish):
        """Test initialize() with no dates supplied."""
        mock_getdates.return_value.get_date_range.return_value = {
            "initial_date": "2016-12-11",
            "until_date": "2016-12-21"}

        initialize()

        # Get dates
        mock_getdates.assert_called_with()
        mock_getdates.return_value.get_date_range.assert_called_with()

        # Build
        mock_build.assert_called_with(
            initial_date="2016-12-11", until_date="2016-12-21")
        mock_build.return_value.build_all.assert_called_with()

        # Geocode
        expected_call_list = [
            mock.call(
                initial_date="2016-12-11",
                until_date="2016-12-21"),
            mock.call()]

        self.assertEqual(len(mock_geocode.call_args_list), 2)
        self.assertEqual(mock_geocode.call_args_list, expected_call_list)

        mock_geocode.return_value.geocode.assert_called_with()
        mock_geocode.return_value.\
            update_locations_with_neighborhoods.assert_called_with()

        # Publish
        mock_publish.assert_called_with(
            initial_date="2016-12-11", until_date="2016-12-21")
        mock_publish.return_value.main.assert_called_with()

        # Clean
        expected_call_list = [
            mock.call(initial_date="2016-12-11", until_date="2016-12-21"),
            mock.call(initial_date="2016-12-11", until_date="2016-12-21")]

        self.assertEqual(len(mock_clean.call_args_list), 2)
        self.assertEqual(mock_clean.call_args_list, expected_call_list)

        mock_clean.return_value.main.assert_called_with()
        mock_clean.return_value.update_cleaned_geom.assert_called_with()
