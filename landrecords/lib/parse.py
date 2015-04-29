# -*- coding: utf-8 -*-

"""
This contains all of the logic for parsing the different pages for each sale
and makes use of the [Beautiful Soup]
(http://www.crummy.com/software/BeautifulSoup/bs4/doc/) library. Returns
either a dict of list of dicts.
"""

import re
from bs4 import BeautifulSoup
from landrecords.lib.utils import Utils


class AllPurposeParser(object):

    '''Parsing that is not specific to any table.'''

    def __init__(self, html_path):
        '''
        Receives path to HTML file.

        :param html_path: A path to a sale file. Ex. '/path/OPR123456789.html'

        '''

        self.document_id = self.get_document_id(html_path)

    @staticmethod
    def get_document_id(html_path):
        """
        Return a sale's document ID based on the file name.

        :param html_path: A path to a sale file. Ex. '/path/OPR123456789.html'
        :type html_path: string
        :returns: A string containing the document ID. Ex. 'OPR123456789'
        """

        doc_id = re.search(r"(\w+)\.html", html_path).group(1)

        return doc_id


class DetailParser(object):

    '''Parses the details section of the HTML.'''

    def __init__(self, html_path):
        '''Create self variables for each detail field.'''

        self.rows = self.get_rows(html_path)

        self.document_id = AllPurposeParser(html_path).document_id

        self.document_type = self.get_field(0)
        self.instrument_no = self.get_field(1)
        self.multi_seq = self.get_field(2)
        self.min_ = self.get_field(3)
        self.cin = self.get_field(4)
        self.book_type = self.get_field(5)
        self.book = self.get_field(6)
        self.page = self.get_field(7)
        self.document_date = self.get_field(8)
        self.document_recorded = self.get_field(9)
        self.amount = Utils().convert_amount(self.get_field(10))
        self.status = self.get_field(11)
        self.prior_mortgage_doc_type = self.get_field(12)
        self.prior_conveyance_doc_type = self.get_field(13)
        self.cancel_status = self.get_field(14)
        self.remarks = self.get_field(15)
        self.no_pages_in_image = self.get_field(16)
        self.image = self.get_field(17)

    def get_rows(self, html_path):
        """
        Return rows for details table HTML.

        :param html_path: A path to a sale file. Ex. '/path/OPR123456789.html'
        :type html_path: string
        :returns: A something containing something.
        """

        html_file = open(html_path, 'r')
        soup = BeautifulSoup(html_file.read())

        rows = self.parse_rows(soup)

        soup.decompose()
        html_file.close()

        return rows

    @staticmethod
    def parse_rows(soup):
        """
        Find rows in details table HTML.

        :param soup: A BeautifulSoup object.
        :type soup: something
        :returns: something.
        """

        rows = soup.find(
            'table',
            id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList"
        ).find_all('tr')

        # log.debug('# or rows: %d', len(rows))

        return rows

    def get_field(self, row_id):
        """
        Extract the value in a given row's key-value pair.

        :param row_id: The row ID in the HTML, specifying the field. Ex. '0'
        :type row_id: string
        :returns: A string containing the field in the row. Ex. 'SALE'
        """

        # log.debug(row_id)

        cells = self.rows[row_id].find_all('td')
        field = str(cells[1].string)  # 0 is key, 1 is value

        # log.debug(field)

        # prekey = cells[0]
        # log.debug(prekey)

        key = str(cells[0].string)

        # log.debug('key: %s', key)

        cond = (key.strip() == 'Document Date:' or
                key.strip() == 'Date Recorded:')

        if field == "None" or field == '' or field == "NONE":
            # log.debug('LOOK')
            # log.debug('Key: %s', key)
            field = ""
            if cond:
                # log.debug('LOOK 2.0!')  # todo: remove
                # log.debug('Key 2.0: %s', key)
                field = None

        # log.debug(field)

        return field

    def form_dict(self):
        """
        Return dict of this sale's detail table.

        :param self: The self variable, which contains the necessary fields.
        :type row_id: instance
        :returns: A dict containg all of the details values.
        """

        dict_output = self.__dict__

        del dict_output['rows']

        return dict_output


class VendorParser(object):

    '''Parses the vendors section of the HTML.'''

    def __init__(self, html_path):
        '''Establish self variables.'''

        self.rows = self.get_rows(html_path)

        self.document_id = AllPurposeParser(html_path).document_id

    def get_rows(self, html_path):
        '''Return rows for vendors.'''

        html_file = open(html_path, 'r')
        soup = BeautifulSoup(html_file.read())

        rows = self.parse_rows(soup)

        soup.decompose()
        html_file.close()

        return rows

    @staticmethod
    def parse_rows(soup):
        '''Find rows for vendors HTML.'''

        rows = soup.find(
            'table',
            id="ctl00_cphNoMargin_f_oprTab_tmpl0_DataList11"
        ).find_all('tr')

        return rows

    def form_list(self):
        '''Form list of dicts for vendors HTML.'''

        list_output = []

        for i, row in enumerate(self.rows):
            if i % 2 == 1:
                dict_output = {
                    'vendor_blank': self.get_field(row, 0),
                    'vendor_p_c': self.get_field(row, 1),
                    'vendor_lastname': self.get_field(row, 2),
                    'vendor_firstname': self.get_field(row, 3),
                    'vendor_relator': self.get_field(row, 4),
                    'vendor_cancel_status': self.get_field(row, 5),
                    'document_id': self.document_id
                }
                list_output.append(dict_output)

        return list_output

    @staticmethod
    def get_field(row, cell_id):
        '''Make corrections to dict values.'''

        cells = row.find_all('span')
        cell = cells[cell_id]

        if isinstance(cell, str) == 0:
            cell = str(cell.string)
        if cell == "None" or cell == '' or cell == "NONE":
            cell = ""
        return cell


class VendeeParser(object):

    '''Parses the vendees section of the HTML.'''

    def __init__(self, html_path):
        '''Establish self variables.'''

        self.rows = self.get_rows(html_path)

        self.document_id = AllPurposeParser(html_path).document_id

    def get_rows(self, html_path):
        '''Return rows for vendees.'''

        html_file = open(html_path, 'r')
        soup = BeautifulSoup(html_file.read())

        rows = self.parse_rows(soup)

        soup.decompose()
        html_file.close()

        return rows

    @staticmethod
    def parse_rows(soup):
        '''Find rows for vendees.'''

        rows = soup.find(
            'table',
            id="ctl00_cphNoMargin_f_oprTab_tmpl0_Datalist1"
        ).find_all('tr')
        return rows

    def form_list(self):
        '''Form list of dicts for vendees HTML.'''

        list_output = []

        for i, row in enumerate(self.rows):
            if i % 2 == 1:
                dict_output = {
                    'vendee_blank': self.get_field(row, 0),
                    'vendee_p_c': self.get_field(row, 1),
                    'vendee_lastname': self.get_field(row, 2),
                    'vendee_firstname': self.get_field(row, 3),
                    'vendee_relator': self.get_field(row, 4),
                    'vendee_cancel_status': self.get_field(row, 5),
                    'document_id': self.document_id
                }
                list_output.append(dict_output)

        return list_output

    @staticmethod
    def get_field(row, cell_id):
        '''Make corrections to dict values.'''

        cells = row.find_all('span')
        cell = cells[cell_id]

        if isinstance(cell, str) == 0:
            cell = str(cell.string)
        if cell == "None" or cell == '' or cell == "NONE":
            cell = ""
        return cell


class LocationParser(object):

    '''Parses the locations section of the HTML.'''

    def __init__(self, html_path):
        '''Establish self variables.'''

        self.rows = self.get_rows(html_path)

        self.document_id = AllPurposeParser(html_path).document_id

    def get_rows(self, html_path):
        '''Return rows for locations.'''

        html_file = open(html_path, 'r')
        soup = BeautifulSoup(html_file.read())

        rows = self.parse_rows(soup)

        soup.decompose()
        html_file.close()

        return rows

    @staticmethod
    def parse_rows(soup):
        '''Find rows for locations.'''

        rows = soup.find(
            'table',
            id="ctl00_cphNoMargin_f_oprTab_tmpl1_ComboLegals"
        ).find_all('tr')

        # log.debug('rows:')
        # log.debug(rows)

        return rows

    def form_list(self):
        '''Form list of dicts for locations HTML.'''

        list_output = []

        # Find number of mini tables:
        # 9 rows per table. A total of 9 rows if one table, but a total of
        # 19 rows if two, 29 if three, etc.
        # (Because of border row that only appears once multiple tables
        number_of_tables = ((len(self.rows) - 9) / 10) + 1

        for table_no in range(0, number_of_tables):
            dict_output = {
                'subdivision': self.get_subdivision(table_no),
                'condo': self.get_condo(table_no),
                'district': self.get_district(table_no),
                'square': self.get_square(table_no),
                'lot': self.get_lot(table_no),
                'cancel_status_lot': self.get_cancel_status_lot(table_no),
                'street_number': self.get_street_number(table_no),
                'address': self.get_address(table_no),
                'unit': self.get_unit(table_no),
                'weeks': self.get_weeks(table_no),
                'cancel_status_unit': self.get_cancel_status_unit(table_no),
                'freeform_legal': self.get_freeform_legal(table_no),
                'document_id': self.document_id
            }
            # log.debug('dict_output:')
            # log.debug(dict_output)
            list_output.append(dict_output)

        return list_output

    @staticmethod
    def convert_to_string(lot):
        '''Make corrections to dict values.'''

        if isinstance(lot, str) == 0:
            lot = str(lot.string)
        if lot == "None" or lot == '' or lot == "NONE":
            lot = ""
        return lot

    def get_field(self, row_index, cell_index, table_no):
        '''Get the field value for a given table's row and cell indeces.'''

        overall_index = table_no * 10 + row_index

        # log.debug('overall_index:')
        # log.debug(overall_index)

        field = self.rows[overall_index].find_all('span')[cell_index]

        # log.debug('field:')
        # log.debug(field)

        return self.convert_to_string(field)

    def get_subdivision(self, table_no):
        '''Returns the subdivision field value.'''

        row_index = 0
        cell_index = 1

        subdivision = self.get_field(row_index, cell_index, table_no)

        return subdivision

    def get_condo(self, table_no):
        '''Returns the condo field value.'''

        row_index = 1
        cell_index = 1

        condo = self.get_field(row_index, cell_index, table_no)

        return condo

    def get_district(self, table_no):
        '''Returns the district field value.'''

        row_index = 3
        cell_index = 1

        district = self.get_field(row_index, cell_index, table_no)

        return district

    def get_square(self, table_no):
        '''Returns the square field value.'''

        row_index = 3
        cell_index = 3

        square = self.get_field(row_index, cell_index, table_no)

        return square

    def get_street_number(self, table_no):
        '''Returns the street number field value.'''

        row_index = 5
        cell_index = 1

        street_number = self.get_field(row_index, cell_index, table_no)

        return street_number

    def get_address(self, table_no):
        '''Returns the address field value.'''

        # log.debug('get_address:')

        row_index = 5
        cell_index = 3

        address = self.get_field(row_index, cell_index, table_no)

        # log.debug(address)

        return address

    def get_unit(self, table_no):
        '''Returns the unit field value.'''

        row_index = 6
        cell_index = 1

        unit = self.get_field(row_index, cell_index, table_no)

        return unit

    def get_weeks(self, table_no):
        '''Returns the weeks field value.'''

        row_index = 6
        cell_index = 3

        weeks = self.get_field(row_index, cell_index, table_no)

        return weeks

    def get_cancel_status_unit(self, table_no):
        '''Returns the cancel stat field value.'''

        row_index = 6
        cell_index = 5

        cancel_status_unit = self.get_field(row_index, cell_index, table_no)

        return cancel_status_unit

    def get_freeform_legal(self, table_no):
        '''Returns the freeform legal field value.'''

        row_index = 8
        cell_index = 1

        freeform_legal = self.get_field(row_index, cell_index, table_no)

        return freeform_legal

    def get_cancel_status_lot(self, table_no):
        '''Returns the cancel status field value.'''

        row_index = 3
        overall_index = table_no * 10 + row_index

        cancel_status_lot = ""

        cells = self.rows[overall_index].find_all('span')

        if len(cells) == 10:  # There are Lot from and Lot to fields
            cancel_status_lot = self.convert_to_string(cells[9])
        else:
            cancel_status_lot = self.convert_to_string(cells[7])

        return cancel_status_lot

    def get_lot(self, table_no):
        '''Returns the lot field value.'''

        row_index = 3
        overall_index = table_no * 10 + row_index

        lot = ""

        cells = self.rows[overall_index].find_all('span')

        if len(cells) == 10:  # There are Lot from and Lot to fields
            frm = self.convert_to_string(cells[5])
            to = self.convert_to_string(cells[7])

            if len(frm) == 0 and len(to) != 0:
                lot = to
            elif len(frm) != 0 and len(to) == 0:
                lot = frm
            elif len(frm) != 0 and len(to) != 0:
                lot = frm + " to " + to
            else:
                lot = ""

        return lot

if __name__ == '__main__':
    # from landrecords.config import Config
    # html_path = (
    #     '%s/' % Config().DATA_DIR +
    #     'raw/2014-02-18/form-html/OPR288694480.html')
    # print LocationParser(html_path).form_list()
    pass
