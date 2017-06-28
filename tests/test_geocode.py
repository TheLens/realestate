
"""Unit tests for scripts/initialize.py."""

from mock import patch, call
import unittest

from scripts.geocode import Geocode


class TestGeocode(unittest.TestCase):
    """Test cases for scripts/geocode.py."""

    def setUp(self):
        """Set up unit tests."""
        self.gmaps_patcher = patch('scripts.geocode.googlemaps')
        self.mock_gmaps = self.gmaps_patcher.start()
        self.addCleanup(self.gmaps_patcher.stop)

    def test_init(self):
        """Test __init__()."""
        g = Geocode()

        self.assertIsNone(g.initial_date)
        self.assertIsNone(g.until_date)

        assert g._gmaps

    def test_init_with_args(self):
        """Test __init__() when supplied with arguments."""
        g = Geocode(initial_date='2017-01-01', until_date='2017-01-31')

        self.assertEqual(g.initial_date, '2017-01-01')
        self.assertEqual(g.until_date, '2017-01-31')

        assert g._gmaps

    @patch('scripts.geocode.Geocode.neighborhood_found')
    @patch('scripts.geocode.Geocode.no_neighborhood_found')
    def test_update_locations(self, mock_no_nbhd, mock_nbhd_found):
        """Test update_locations_with_neighborhoods()."""
        Geocode().update_locations_with_neighborhoods()

        mock_nbhd_found.assert_called_with()
        mock_no_nbhd.assert_called_with()

    def test_neighborhood_found(self):
        """Test neighborhood_found()."""
        # TODO: Mock database and test query method.
        pass

    def test_no_neighborhood_found(self):
        """Test no_neighborhood_found()."""
        # TODO: Mock database and test query method.
        pass

    def test_get_rows_with_null_rating(self):
        """Test get_rows_with_null_rating()."""
        # TODO: Mock database and test query method.
        pass

    def test_update_location_row(self):
        """Test update_location_row()."""
        # TODO: Mock database and test query method.
        pass

    def test_process_google_results_with_zip(self):
        """Test process_google_results() with a zip code."""
        results = [{
            'geometry': {
                'location': {'lat': 1, 'lng': 2}, 'location_type': 'LT'},
            'address_components': [0, 1, 2, 3, 4, 5, 6, {'short_name': 'S'}]
        }]

        actual = Geocode().process_google_results(results)
        expected = {'latitude': 1, 'longitude': 2, 'rating': 'LT',
                    'zip_code': 'S'}

        self.assertEqual(actual, expected)

    def test_process_google_results_without_zip(self):
        """Test process_google_results() without a zip code."""
        results = [{
            'geometry': {
                'location': {'lat': 1, 'lng': 2}, 'location_type': 'LT'},
            'address_components': [0, 1, 2, 3, 4, 5, 6]
        }]

        actual = Geocode().process_google_results(results)
        expected = {'latitude': 1, 'longitude': 2, 'rating': 'LT',
                    'zip_code': 'None'}

        self.assertEqual(actual, expected)

    def test_process_google_results_multiple_results(self):
        """Test process_google_results() with multiple results."""
        results = [
            {
                'geometry': {
                    'location': {'lat': 1, 'lng': 2}, 'location_type': 'LT'},
                'address_components': [0, 1, 2, 3, 4, 5, 6]
            },
            {
                'geometry': {
                    'location': {'lat': 10, 'lng': 20}, 'location_type': 'lt'},
                'address_components': [0, 1, 2, 3, 4, 5, 6]
            }
        ]

        actual = Geocode().process_google_results(results)
        expected = {'latitude': 1, 'longitude': 2, 'rating': 'LT',
                    'zip_code': 'None'}

        self.assertEqual(actual, expected)

    @patch('scripts.geocode.Geocode.update_location_row')
    @patch('scripts.geocode.Geocode.process_google_results')
    @patch('scripts.geocode.Geocode.get_rows_with_null_rating')
    def test_geocode(self, mock_get_null_rows, mock_process, mock_update):
        """Test geocode()."""
        from collections import namedtuple
        N = namedtuple('Null_rows', 'street_number address document_id')
        mock_get_null_rows.return_value = [
            N("123", "Main Street", "1"),
            N("345", "Sixth Street", "2")]

        self.mock_gmaps.Client.return_value.geocode.return_value = [1]

        Geocode().geocode()

        mock_process_calls = [call([1]), call([1])]  # Called twice

        self.assertEqual(mock_process.call_args_list, mock_process_calls)

    @patch('scripts.geocode.Geocode.update_location_row')
    @patch('scripts.geocode.Geocode.process_google_results')
    @patch('scripts.geocode.Geocode.get_rows_with_null_rating')
    def test_geocode_empty_results(self, mock_get_null_rows, mock_process,
                                   mock_update):
        """Test geocode() when response is an empty list."""
        from collections import namedtuple
        N = namedtuple('Null_rows', 'street_number address document_id')
        mock_get_null_rows.return_value = [
            N("123", "Main Street", "1"),
            N("345", "Sixth Street", "2")]

        self.mock_gmaps.Client.return_value.geocode.return_value = []

        Geocode().geocode()

        mock_process_calls = []  # Never called

        self.assertEqual(mock_process.call_args_list, mock_process_calls)

if __name__ == '__main__':
    unittest.main()
