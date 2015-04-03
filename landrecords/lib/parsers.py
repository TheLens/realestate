# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup


class AllPurposeParser(object):

    def __init__(self, html):
        self.document_id = self.get_document_id(html)

    def get_document_id(self, html):
        "Input: html (string) is the full path to an HTML file."
        "Output: The sale's document ID"
        doc_id = re.search(r"(\w+)\.html", html).group(1)
        return doc_id


class DetailParser(object):

    def __init__(self, html):
        soup = BeautifulSoup(open(html))
        rows = self.parse_rows(soup)

        self.document_id = AllPurposeParser(html).document_id

        self.document_type = self.get_field(rows, 0)
        self.instrument_no = self.get_field(rows, 1)
        self.multi_seq = self.get_field(rows, 2)
        self.min_ = self.get_field(rows, 3)
        self.cin = self.get_field(rows, 4)
        self.book_type = self.get_field(rows, 5)
        self.book = self.get_field(rows, 6)
        self.page = self.get_field(rows, 7)
        self.document_date = self.get_field(rows, 8)
        self.document_recorded = self.get_field(rows, 9)
        self.amount = self.convert_amount(self.get_field(rows, 10))
        self.status = self.get_field(rows, 11)
        self.prior_mortgage_doc_type = self.get_field(rows, 12)
        self.prior_conveyance_doc_type = self.get_field(rows, 13)
        self.cancel_status = self.get_field(rows, 14)
        self.remarks = self.get_field(rows, 15)
        self.no_pages_in_image = self.get_field(rows, 16)
        self.image = self.get_field(rows, 17)

    def parse_rows(self, soup):
        rows = soup.find('table',
                         id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList"
                         ).find_all('tr')

        return rows

    def get_field(self, rows, row_id):
        cells = rows[row_id].find_all('td')
        field = str(cells[1].string)  # 0 is key, 1 is value

        if field == "None" or field == '' or field == "NONE":
            field = ""

        return field

    def convert_amount(self, amount):
        amount = re.sub(r"\$", r"", amount)
        amount = re.sub(r"\,", r"", amount)
        return int(float(amount))

    def form_dict(self):
        return self.__dict__


class VendorParser(object):

    def __init__(self, html):
        soup = BeautifulSoup(open(html))
        rows = self.parse_rows(soup)

        self.document_id = AllPurposeParser(html).document_id
        self.list_output = self.form_list(rows)

    def parse_rows(self, soup):
        rows = soup.find('table',
                         id="ctl00_cphNoMargin_f_oprTab_tmpl0_DataList11"
                         ).find_all('tr')
        return rows

    def form_list(self, rows):
        list_output = []

        for i, row in enumerate(rows):
            # print 'form_list row:', row
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

    def get_field(self, row, cell_id):
        cells = row.find_all('span')
        cell = cells[cell_id]

        if isinstance(cell, str) == 0:
            cell = str(cell.string)
        if cell == "None" or cell == '' or cell == "NONE":
            cell = ""
        return cell


class VendeeParser(object):

    def __init__(self, html):
        soup = BeautifulSoup(open(html))
        rows = self.parse_rows(soup)

        self.document_id = AllPurposeParser(html).document_id
        self.list_output = self.form_list(rows)

    def parse_rows(self, soup):
        rows = soup.find('table',
                         id="ctl00_cphNoMargin_f_oprTab_tmpl0_Datalist1"
                         ).find_all('tr')
        return rows

    def form_list(self, rows):
        list_output = []

        for i, row in enumerate(rows):
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

    def get_field(self, row, cell_id):
        cells = row.find_all('span')
        cell = cells[cell_id]

        if isinstance(cell, str) == 0:
            cell = str(cell.string)
        if cell == "None" or cell == '' or cell == "NONE":
            cell = ""
        return cell


class LocationParser(object):

    def __init__(self, html):
        soup = BeautifulSoup(open(html))
        rows = self.parse_rows(soup)

        self.document_id = AllPurposeParser(html).document_id
        self.list_output = self.form_list(rows)

    def parse_rows(self, soup):
        rows = soup.find('table',
                         id="ctl00_cphNoMargin_f_oprTab_tmpl1_ComboLegals"
                         ).find_all('tr')
        return rows

    def form_list(self, rows):
        list_output = []

        # Find number of mini tables:
        # 9 rows per table. A total of 9 rows if one table, but a total of
        # 19 rows if two, 29 if three, etc.
        # (Because of border row that only appears once multiple tables
        number_of_tables = ((len(rows) - 9) / 10) + 1

        # print '\nnumber_of_tables:', number_of_tables

        for table_no in range(0, number_of_tables):
            dict_output = {
                'subdivision': self.get_subdivision(rows, table_no),
                'condo': self.get_condo(rows, table_no),
                'district': self.get_district(rows, table_no),
                'square': self.get_square(rows, table_no),
                'lot': self.get_lot(rows, table_no),
                'cancel_status': self.get_cancel_status(rows, table_no),
                'street_number': self.get_street_number(rows, table_no),
                'address': self.get_address(rows, table_no),
                'unit': self.get_unit(rows, table_no),
                'weeks': self.get_weeks(rows, table_no),
                'cancel_stat': self.get_cancel_stat(rows, table_no),
                'freeform_legal': self.get_freeform_legal(rows, table_no),
                'document_id': self.document_id
            }
            # print '\ndict_output:', dict_output
            list_output.append(dict_output)

            # Check if new mini table:
            # if (i - 9) % 10:  # This is the first row in a new table!

        # print '\nlist_output:', list_output
        return list_output

    def convert_to_string(self, lot):
        if isinstance(lot, str) == 0:
            lot = str(lot.string)
        if lot == "None" or lot == '' or lot == "NONE":
            lot = ""
        return lot

    def get_field(self, row_index, cell_index, rows, table_no):
        overall_index = table_no * 10 + row_index

        field = rows[overall_index].find_all('span')[cell_index]

        return self.convert_to_string(field)

    def get_subdivision(self, rows, table_no):
        row_index = 0
        cell_index = 1

        subdivision = self.get_field(row_index, cell_index, rows, table_no)

        return subdivision

    def get_condo(self, rows, table_no):
        row_index = 1
        cell_index = 1

        condo = self.get_field(row_index, cell_index, rows, table_no)

        return condo

    def get_district(self, rows, table_no):
        row_index = 3
        cell_index = 1

        district = self.get_field(row_index, cell_index, rows, table_no)

        return district

    def get_square(self, rows, table_no):
        row_index = 3
        cell_index = 3

        square = self.get_field(row_index, cell_index, rows, table_no)

        return square

    def get_street_number(self, rows, table_no):
        row_index = 5
        cell_index = 1

        street_number = self.get_field(row_index, cell_index, rows, table_no)

        return street_number

    def get_address(self, rows, table_no):
        row_index = 5
        cell_index = 3

        weeks = self.get_field(row_index, cell_index, rows, table_no)

        return weeks

    def get_unit(self, rows, table_no):
        row_index = 6
        cell_index = 1

        unit = self.get_field(row_index, cell_index, rows, table_no)

        return unit

    def get_weeks(self, rows, table_no):
        row_index = 6
        cell_index = 3

        weeks = self.get_field(row_index, cell_index, rows, table_no)

        return weeks

    def get_cancel_stat(self, rows, table_no):
        row_index = 6
        cell_index = 5

        cancel_stat = self.get_field(row_index, cell_index, rows, table_no)

        return cancel_stat

    def get_freeform_legal(self, rows, table_no):
        row_index = 8
        cell_index = 1

        freeform_legal = self.get_field(row_index, cell_index, rows, table_no)

        return freeform_legal

    def get_cancel_status(self, rows, table_no):
        row_index = 3
        overall_index = table_no * 10 + row_index

        field = ""

        cells = rows[overall_index].find_all('span')

        if len(cells) == 10:  # There are Lot from and Lot to fields
            field = self.convert_to_string(cells[9])
        else:
            field = self.convert_to_string(cells[7])

        return field

    def get_lot(self, rows, table_no):
        row_index = 3
        overall_index = table_no * 10 + row_index

        lot = ""

        cells = rows[overall_index].find_all('span')

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
