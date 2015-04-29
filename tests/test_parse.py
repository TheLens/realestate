# -*- coding: utf-8 -*-

# import mock
from unittest import TestCase

from realestate.lib.parse import (
    AllPurposeParser,
    DetailParser,
    VendorParser,
    VendeeParser,
    LocationParser
)
from realestate import DATA_DIR


class TestAllPurposeParser(TestCase):
    "TestAllPurposeParser"

    html_path = (
        '%s/' % DATA_DIR +
        'raw/2014-02-18/form-html/OPR288694480.html')

    def test_all_purpose_get_document_id_var(self):
        '''Test that AllPurposeParser has document ID as self variable.'''

        document_id = AllPurposeParser(self.html_path).document_id

        self.assertEqual(document_id, "OPR288694480")

    def test_all_purpose_get_document_id_method(self):
        '''Test AllPurposeParser method for finding document ID.'''

        document_id = AllPurposeParser(
            self.html_path).get_document_id(self.html_path)

        self.assertEqual(document_id, "OPR288694480")


class TestDetailParser(TestCase):

    '''Test parser for details table.'''

    html_path = (
        '%s/' % DATA_DIR +
        'raw/2014-02-18/form-html/OPR288694480.html')

    # todo: rows, parse_rows

    def test_get_field_document_type_var(self):
        "test_get_field_document_type_var"

        document_type = DetailParser(self.html_path).document_type

        self.assertEqual(document_type, "SALE")

    def test_get_field_instrument_no_var(self):
        "test_get_field_instrument_no_var"

        instrument_no = DetailParser(self.html_path).instrument_no

        self.assertEqual(instrument_no, "2014-06269")

    def test_get_field_multi_seq_var(self):
        "test_get_field_multi_seq_var"

        multi_seq = DetailParser(self.html_path).multi_seq

        self.assertEqual(multi_seq, "0")

    def test_get_field_min__var(self):
        "test_get_field_min__var"

        min_ = DetailParser(self.html_path).min_

        self.assertEqual(min_, "")

    def test_get_field_cin_var(self):
        "test_get_field_cin_var"

        cin = DetailParser(self.html_path).cin

        self.assertEqual(cin, "549928")

    def test_get_field_book_type_var(self):
        "test_get_field_book_type_var"

        book_type = DetailParser(self.html_path).book_type

        self.assertEqual(book_type, "")

    def test_get_field_book_var(self):
        "test_get_field_book_var"

        book = DetailParser(self.html_path).book

        self.assertEqual(book, "")

    def test_get_field_page_var(self):
        "test_get_field_page_var"

        page = DetailParser(self.html_path).page

        self.assertEqual(page, "")

    def test_get_field_document_date_var_none(self):
        '''
        Test that if no document date is entered,
        then a value of None/NULL is returned.
        '''

        html_no_document_date = (
            '%s/' % DATA_DIR +
            'raw/2014-05-01/form-html/OPR291526640.html')

        document_date = DetailParser(html_no_document_date).document_date

        self.assertEqual(document_date, None)

    def test_get_field_document_date_var(self):
        "test_get_field_document_date_var"

        document_date = DetailParser(self.html_path).document_date

        self.assertEqual(document_date, "02/10/2014")

    def test_get_field_document_recorded_var(self):
        "test_get_field_document_recorded_var"

        document_recorded = DetailParser(self.html_path).document_recorded

        self.assertEqual(document_recorded, "02/18/2014 10:35:37 AM")

    def test_get_field_amount_var(self):
        "test_get_field_amount_var"

        amount = DetailParser(self.html_path).amount

        self.assertEqual(amount, 41000)

    def test_get_field_status_var(self):
        "test_get_field_status_var"

        status = DetailParser(self.html_path).status

        self.assertEqual(status, "Verified")

    def test_get_field_prior_mortgage_doc_type_var(self):
        "test_get_field_prior_mortgage_doc_type_var"

        prior_mortgage_doc_type = DetailParser(
            self.html_path
        ).prior_mortgage_doc_type

        self.assertEqual(prior_mortgage_doc_type, "")

    def test_get_field_prior_conveyance_doc_type_var(self):
        "test_get_field_prior_conveyance_doc_type_var"

        output = DetailParser(self.html_path).prior_conveyance_doc_type

        self.assertEqual(output, "")

    def test_get_field_cancel_status_var(self):
        "test_get_field_cancel_status_var"

        cancel_status = DetailParser(self.html_path).cancel_status

        self.assertEqual(cancel_status, "")

    def test_get_field_remarks_var(self):
        "test_get_field_remarks_var"

        remarks = DetailParser(self.html_path).remarks

        self.assertEqual(remarks, "")

    def test_get_field_no_pages_in_image_var(self):
        "test_get_field_no_pages_in_image_var"

        no_pages_in_image = DetailParser(self.html_path).no_pages_in_image

        self.assertEqual(no_pages_in_image, "8")

    def test_get_field_image_var(self):
        "test_get_field_image_var"

        image = DetailParser(self.html_path).image

        self.assertEqual(image, "")

    # def test_form_dict(self):
    #     "test_form_dict"

    #     output = DetailParser(self.html_path).form_dict()

    #     self.assertEqual(type(output), dict)

    def test_form_dict(self):
        '''docstring'''

        details_dict = {
            'status': 'Verified',
            'document_recorded': '02/18/2014 10:35:37 AM',
            'prior_conveyance_doc_type': '',
            'no_pages_in_image': '8',
            'prior_mortgage_doc_type': '',
            'cin': '549928',
            'instrument_no': '2014-06269',
            'page': '',
            'amount': 41000,
            'book_type': '',
            'document_id': 'OPR288694480',
            'cancel_status': '',
            'min_': '',
            'remarks': '',
            'document_type': 'SALE',
            'image': '',
            'book': '',
            'multi_seq': '0',
            'document_date': '02/10/2014'
        }

        test_details_dict = DetailParser(self.html_path).form_dict()

        self.assertEqual(test_details_dict, details_dict)


class TestVendorParser(TestCase):

    '''TestVendorParser'''

    html_path = (
        '%s/' % DATA_DIR +
        'raw/2014-02-18/form-html/OPR288694480.html')

    def test_get_vendor_blank(self):
        "test_get_vendor_blank"

        l = VendorParser(self.html_path).form_list()

        vendor_blank1 = l[0]['vendor_blank']
        vendor_blank2 = l[1]['vendor_blank']

        self.assertEqual(vendor_blank1, "1")
        self.assertEqual(vendor_blank2, "2")

    def test_get_vendor_p_c(self):
        "test_get_vendor_p_c"

        l = VendorParser(self.html_path).form_list()

        vendor_p_c1 = l[0]['vendor_p_c']
        vendor_p_c2 = l[1]['vendor_p_c']

        self.assertEqual(vendor_p_c1, "C")
        self.assertEqual(vendor_p_c2, "C")

    def test_get_vendor_lastname(self):
        "test_get_vendor_lastname"

        l = VendorParser(self.html_path).form_list()

        vendor_lastname1 = l[0]['vendor_lastname']
        vendor_lastname2 = l[1]['vendor_lastname']

        self.assertEqual(
            vendor_lastname1,
            "NEW ORLEANS REDEVELOPMENT AUTHORITY"
        )
        self.assertEqual(
            vendor_lastname2,
            "COMMUNITY IMPROVEMENT AGENCY"
        )

    def test_get_vendor_firstname(self):
        "test_get_vendor_firstname"

        l = VendorParser(self.html_path).form_list()

        vendor_firstname1 = l[0]['vendor_firstname']
        vendor_firstname2 = l[1]['vendor_firstname']

        self.assertEqual(vendor_firstname1, "")
        self.assertEqual(vendor_firstname2, "")

    def test_get_vendor_relator(self):
        "test_get_vendor_relator"

        l = VendorParser(self.html_path).form_list()

        vendor_relator1 = l[0]['vendor_relator']
        vendor_relator2 = l[1]['vendor_relator']

        self.assertEqual(vendor_relator1, "FKA")
        self.assertEqual(vendor_relator2, "")

    def test_get_vendor_cancel_status(self):
        "test_get_vendor_cancel_status"

        l = VendorParser(self.html_path).form_list()

        vendor_cancel_status1 = l[0]['vendor_cancel_status']
        vendor_cancel_status2 = l[1]['vendor_cancel_status']

        self.assertEqual(vendor_cancel_status1, "")
        self.assertEqual(vendor_cancel_status2, "")

    def test_form_list(self):
        '''docstring'''

        vendors_list = [{
            'vendor_blank': '1',
            'vendor_p_c': 'C',
            'vendor_relator': 'FKA',
            'vendor_cancel_status': '',
            'vendor_firstname': '',
            'document_id': 'OPR288694480',
            'vendor_lastname': 'NEW ORLEANS REDEVELOPMENT AUTHORITY'
        }, {
            'vendor_blank': '2',
            'vendor_p_c': 'C',
            'vendor_relator': '',
            'vendor_cancel_status': '',
            'vendor_firstname': '',
            'document_id': 'OPR288694480',
            'vendor_lastname': 'COMMUNITY IMPROVEMENT AGENCY'
        }]

        test_vendors_list = VendorParser(self.html_path).form_list()

        self.assertEqual(vendors_list, test_vendors_list)


class TestVendeeParser(TestCase):

    '''TestVendeeParser'''

    html_path = (
        '%s/' % DATA_DIR +
        'raw/2014-02-18/form-html/OPR288694480.html')

    def test_get_vendee_blank(self):
        "test_get_vendee_blank"

        l = VendeeParser(self.html_path).form_list()

        vendee_blank = l[0]['vendee_blank']

        self.assertEqual(vendee_blank, "1")

    def test_get_vendee_p_c(self):
        "test_get_vendee_p_c"

        l = VendeeParser(self.html_path).form_list()

        vendee_p_c = l[0]['vendee_p_c']

        self.assertEqual(vendee_p_c, "C")

    def test_get_vendee_lastname(self):
        "test_get_vendee_lastname"

        l = VendeeParser(self.html_path).form_list()

        vendee_lastname = l[0]['vendee_lastname']

        self.assertEqual(vendee_lastname, "UV SOLO TRUST")

    def test_get_vendee_firstname(self):
        "test_get_vendee_firstname"

        l = VendeeParser(self.html_path).form_list()

        vendee_firstname = l[0]['vendee_firstname']

        self.assertEqual(vendee_firstname, "")

    def test_get_vendee_relator(self):
        "test_get_vendee_relator"

        l = VendeeParser(self.html_path).form_list()

        vendee_relator = l[0]['vendee_relator']

        self.assertEqual(vendee_relator, "")

    def test_get_vendee_cancel_status(self):
        "test_get_vendee_cancel_status"

        l = VendeeParser(self.html_path).form_list()

        vendee_cancel_status = l[0]['vendee_cancel_status']

        self.assertEqual(vendee_cancel_status, "")

    def test_form_list(self):
        '''docstring'''

        vendees_list = [{
            'vendee_lastname': 'UV SOLO TRUST',
            'vendee_cancel_status': '',
            'vendee_p_c': 'C',
            'vendee_firstname': '',
            'vendee_relator': '',
            'vendee_blank': '1',
            'document_id': 'OPR288694480'
        }]

        test_vendees_list = VendeeParser(self.html_path).form_list()

        self.assertEqual(vendees_list, test_vendees_list)


class TestLocationParser(TestCase):

    "TestLocationParser"

    html_path = (
        '%s/' % DATA_DIR +
        'raw/2014-02-18/form-html/OPR288694480.html')

    def test_get_field_subdivision(self):
        "test_get_field_subdivision"

        subdivision = LocationParser(self.html_path).get_subdivision(0)

        self.assertEqual(subdivision, "ARDYN PARK")

    def test_get_field_condo(self):
        "test_get_field_condo"

        condo = LocationParser(self.html_path).get_condo(0)

        self.assertEqual(condo, "")

    def test_get_field_district(self):
        "test_get_field_district"

        district = LocationParser(self.html_path).get_district(0)

        self.assertEqual(district, "3RD")

    def test_get_field_square(self):
        "test_get_field_square"

        square = LocationParser(self.html_path).get_square(0)

        self.assertEqual(square, "4-A")

    def test_get_field_street_number(self):
        "test_get_field_street_number"

        street_number = LocationParser(
            self.html_path).get_street_number(0)

        self.assertEqual(street_number, "7532")

    def test_get_field_address(self):
        "test_get_field_address"

        address = LocationParser(self.html_path).get_address(0)

        self.assertEqual(address, "PRIMROSE DR")

    def test_get_field_unit(self):
        "test_get_field_unit"

        unit = LocationParser(self.html_path).get_unit(0)

        self.assertEqual(unit, "")

    def test_get_field_weeks(self):
        "test_get_field_weeks"

        weeks = LocationParser(self.html_path).get_weeks(0)

        self.assertEqual(weeks, "")

    def test_get_field_cancel_status_unit(self):
        "test_get_field_cancel_status_unit"

        cancel_status_unit = LocationParser(
            self.html_path).get_cancel_status_unit(0)

        self.assertEqual(cancel_status_unit, " ")

    def test_get_field_freeform_legal(self):
        "test_get_field_freeform_legal"

        freeform_legal = LocationParser(
            self.html_path).get_freeform_legal(0)

        self.assertEqual(freeform_legal, "")

    # todo: closer look with various versions
    def test_get_field_cancel_status_lot(self):
        "test_get_field_cancel_status_lot"

        cancel_status_lot = LocationParser(
            self.html_path).get_cancel_status_lot(0)

        self.assertEqual(cancel_status_lot, " ")

    # todo: closer look with various HTML, for "xx to xx"
    def test_get_field_lot(self):
        "test_get_field_lot"

        lot = LocationParser(self.html_path).get_lot(0)

        self.assertEqual(lot, "17-A")

    def test_form_list(self):
        '''docstring'''

        locations_list = [{
            'square': '4-A',
            'address': 'PRIMROSE DR',
            'condo': '',
            'cancel_status_unit': ' ',
            'unit': '',
            'freeform_legal': '',
            'subdivision': 'ARDYN PARK',
            'street_number': '7532',
            'district': '3RD',
            'cancel_status_lot': ' ',
            'document_id': 'OPR288694480',
            'lot': '17-A',
            'weeks': ''
        }]

        test_locations_list = LocationParser(self.html_path).form_list()

        self.assertEqual(locations_list, test_locations_list)
