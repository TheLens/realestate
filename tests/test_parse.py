# -*- coding: utf-8 -*-

from __future__ import absolute_import

# import mock
from unittest import TestCase

from landrecords import config
from landrecords.lib.parse import (
    AllPurposeParser,
    DetailParser
    # VendorParser,
    # VendeeParser,
    # LocationParser
)


class TestAllPurposeParser(TestCase):
    "TestAllPurposeParser"

    # def test_all_purpose_parser(self):
    #     "TK"

    #     html = (
    #         '%s/' % config.DATA_DIR +
    #         'raw/2014-02-18/form-html/OPR288694480.html')

    #     output = AllPurposeParser(html)

    #     self.assertEqual(output, mock_object)

    def test_all_purpose_parser_document_id(self):
        "test_all_purpose_parser_document_id"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        output = AllPurposeParser(html).document_id

        self.assertEqual(output, "OPR288694480")

    def test_all_purpose_get_document_id(self):
        "test_all_purpose_get_document_id"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        document_id = AllPurposeParser(html).get_document_id(html)

        self.assertEqual(document_id, "OPR288694480")


class TestDetailParser(TestCase):
    "TestDetailParser"

    # def test_parse_rows(self):
    #     "Extract detail rows."

    #     html = (
    #         '%s/' % config.DATA_DIR +
    #         'raw/2014-02-18/form-html/OPR288694480.html')

    #     output = DetailParser(html).parse_rows()

    #     self.assertEqual(output, mock_soup_object)

    def test_get_field_document_type(self):
        "test_get_field_document_type"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        document_type = DetailParser(html).document_type

        self.assertEqual(document_type, "SALE")

    def test_get_field_instrument_no(self):
        "test_get_field_instrument_no"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        instrument_no = DetailParser(html).instrument_no

        self.assertEqual(instrument_no, "2014-06269")

    def test_get_field_multi_seq(self):
        "test_get_field_multi_seq"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        multi_seq = DetailParser(html).multi_seq

        self.assertEqual(multi_seq, "0")

    def test_get_field_min_(self):
        "test_get_field_min_"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        min_ = DetailParser(html).min_

        self.assertEqual(min_, "")

    def test_get_field_cin(self):
        "test_get_field_cin"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        cin = DetailParser(html).cin

        self.assertEqual(cin, "549928")

    def test_get_field_book_type(self):
        "test_get_field_book_type"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        book_type = DetailParser(html).book_type

        self.assertEqual(book_type, "")

    def test_get_field_book(self):
        "test_get_field_book"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        book = DetailParser(html).book

        self.assertEqual(book, "")

    def test_get_field_page(self):
        "test_get_field_page"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        page = DetailParser(html).page

        self.assertEqual(page, "")

    def test_get_field_document_date(self):
        "test_get_field_document_date"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        document_date = DetailParser(html).document_date

        self.assertEqual(document_date, "02/10/2014")

    def test_get_field_document_recorded(self):
        "test_get_field_document_recorded"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        document_recorded = DetailParser(html).document_recorded

        self.assertEqual(document_recorded, "02/18/2014 11:35:37 AM")

    def test_get_field_amount(self):
        "test_get_field_amount"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        amount = DetailParser(html).amount

        self.assertEqual(amount, 41000)

    def test_get_field_status(self):
        "test_get_field_status"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        status = DetailParser(html).status

        self.assertEqual(status, "Verified")

    def test_get_field_prior_mortgage_doc_type(self):
        "test_get_field_prior_mortgage_doc_type"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        prior_mortgage_doc_type = DetailParser(html).prior_mortgage_doc_type

        self.assertEqual(prior_mortgage_doc_type, "")

    def test_get_field_prior_conveyance_doc_type(self):
        "test_get_field_prior_conveyance_doc_type"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        output = DetailParser(html).prior_conveyance_doc_type

        self.assertEqual(output, "")

    def test_get_field_cancel_status(self):
        "test_get_field_cancel_status"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        cancel_status = DetailParser(html).cancel_status

        self.assertEqual(cancel_status, "")

    def test_get_field_remarks(self):
        "test_get_field_remarks"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        remarks = DetailParser(html).remarks

        self.assertEqual(remarks, "")

    def test_get_field_no_pages_in_image(self):
        "test_get_field_no_pages_in_image"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        no_pages_in_image = DetailParser(html).no_pages_in_image

        self.assertEqual(no_pages_in_image, "8")

    def test_get_field_image(self):
        "test_get_field_image"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        image = DetailParser(html).image

        self.assertEqual(image, "")

    def test_convert_amount(self):
        "test_convert_amount"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        output1 = DetailParser(html).convert_amount('0')
        output2 = DetailParser(html).convert_amount('10')
        output3 = DetailParser(html).convert_amount('100')
        output4 = DetailParser(html).convert_amount('1000')
        output5 = DetailParser(html).convert_amount('10000')

        output6 = DetailParser(html).convert_amount('$0')
        output7 = DetailParser(html).convert_amount('$10')
        output8 = DetailParser(html).convert_amount('$100')
        output9 = DetailParser(html).convert_amount('$1000')
        output10 = DetailParser(html).convert_amount('$10000')

        output11 = DetailParser(html).convert_amount('$1,000')

        self.assertEqual(output1, 0)
        self.assertEqual(output2, 10)
        self.assertEqual(output3, 100)
        self.assertEqual(output4, 1000)
        self.assertEqual(output5, 10000)
        self.assertEqual(output6, 0)
        self.assertEqual(output7, 10)
        self.assertEqual(output8, 100)
        self.assertEqual(output9, 1000)
        self.assertEqual(output10, 10000)
        self.assertEqual(output11, 1000)

    def test_form_dict(self):
        "test_form_dict"

        html = (
            '%s/' % config.DATA_DIR +
            'raw/2014-02-18/form-html/OPR288694480.html')

        output = DetailParser(html).form_dict()

        self.assertEqual(type(output), dict)
        # self.assertEqual(output, {...})

    # def test_check_for_urls_one(self):
    #     "Twitter status contains one URL."
    #     status = "http://vault.thelensnola.org/realestate/sale/123456"
    #     length = len(status)
    #     output = Twitter(status).check_for_urls()
    #     self.assertEqual(output, length - (1 * 22))

    # def test_check_for_urls_two(self):
    #     "Twitter status contains two URLs."
    #     status = ("http://vault.thelensnola.org/realestate/sale/123456 "
    #               "http://vault.thelensnola.org/realestate/sale/123456")
    #     length = len(status) - 1
    #     output = Twitter(status).check_for_urls()
    #     self.assertEqual(output, length - (2 * 22))

    # '''
    # Status length
    # '''

    # def test_check_length_fits(self):
    #     "Twitter status fits and has no attachments."
    #     output = Twitter('four').check_length()
    #     self.assertTrue(output)

    # def test_check_length_fits_attachment(self):
    #     "Twitter status fits and has an attachment."
    #     output = Twitter('four').check_length(
    #         '/Users/Tom/projects/lens-utilities/repo/README.txt'
    #         )
    #     self.assertTrue(output)

    # def test_check_length_long(self):
    #     "Twitter status is too long and has no attachments."
    #     output = Twitter(
    #         'One two three four five six seven eight nine ten '
    #         'eleven twelve thirteen fourteen fiften sixteen seventeen '
    #         'eighteen nineteen twenty twenty-one twenty-two twenty-three '
    #         'twenty-four twenty-five.'
    #         ).check_length()
    #     self.assertFalse(output)

    # def test_check_length_long_attachment(self):
    #     "Twitter status is too long and has an attachment."
    #     output = Twitter(
    #         'One two three four five six seven eight nine ten '
    #         'eleven twelve thirteen fourteen fiften sixteen seventeen '
    #         'eighteen nineteen twenty twenty-one twenty-two twenty-three '
    #         'twenty-four twenty-five.'
    #         ).check_length(
    #         '/Users/Tom/projects/lens-utilities/repo/README.txt'
    #         )
    #     self.assertFalse(output)

    # '''
    # Test send_as_text
    # '''

    # # todo: switch to autospec = True.
    # @mock.patch.object(Twython, 'update_status', autospec=False)
    # def test_send_as_text_permitted(self, mock):
    #     "Send tweet without attachment that passes checks"

    #     status = 'This is also a test.'

    #     t = Twitter(status).send_as_text()

    #     mock.assert_called_with(status=status)

    # # todo: switch to autospec = True.
    # @mock.patch.object(Twython, 'update_status', autospec=False)
    # def test_send_as_text_blocked(self, mock):
    #     "Send tweet without attachment that fails checks"

    #     status = ('One two three four five six seven eight nine ten eleven '
    #               'twelve thirteen fourteen fiften sixteen seventeen '
    #               'eighteen nineteen twenty twenty-one twenty-two '
    #               'twenty-three twenty-four twenty-five.')
    #     try:
    #         t = Twitter(status).send_as_text()
    #     except AssertionError:
    #         pass

    #     self.assertFalse(mock.called)

    # '''
    # Test send_with_attachment
    # '''

    # # todo: switch to autospec = True.
    # @mock.patch.object(Twython, 'update_status_with_media', autospec=False)
    # def test_send_with_attachment_permitted(self, mock):
    #     "Send tweet with attachment that passes checks."

    #     status = 'This is a test.'
    #     media = '/Users/Tom/projects/lens-utilities/repo/README.txt'

    #     t = Twitter(status).send_with_media(media)

    #     # attachment = open(media, 'rb')

    #     # todo: fix to check for specific parameters
    #     mock.assertTrue(mock.called)
