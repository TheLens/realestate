# -*- coding: utf-8 -*-

import re
import pprint
from bs4 import BeautifulSoup
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import db

pp = pprint.PrettyPrinter()


class AllPurposeParser(object):

    def __init__(self, html):
        self.document_id = self.get_document_id(html)

    def get_document_id(self, html):
        # Input: html (string) is the full path to an HTML file.
        # Output: The sale's document ID
        doc_id = re.search(r"(\w+)\.html", html).group(1)
        return doc_id


class DetailParser(object):

    # def convert_to_location():
    #     return Location(self.subdivision, self.condo)

    def __init__(self, html):
        soup = BeautifulSoup(open(html))
        rows = self.parse_rows(soup)

        self.document_id = self.get_document_id(html)

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
                         id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentIn"
                            "foList"
                         ).find_all('tr')

        # print 'rows:', rows

        return rows

    def get_document_id(self, html):
        # html (string) is the full path to an HTML file.
        # Regex to take "..../OPR1245.html" and convert to OPR1245
        doc_id = re.search(r"(\w+)\.html", html).group(1)
        print doc_id
        return doc_id

    def get_field(self, rows, row_id):
        for i, row in enumerate(rows):
            if i != row_id:
                continue
            else:
                # print 'ROW:', row
                cells = row.find_all('td')

                # print "Length:", len(cells)
                # print "Cells:", cells

                field = str(cells[1].string)  # 0 is key, 1 is value

                if field == "None" or field == 'NONE' or field == "":
                    field = None

                return field

    def convert_amount(self, amount):
        amount = re.sub(r"\$", r"", amount)
        amount = re.sub(r"\,", r"", amount)
        return int(float(amount))

    def form_dict(self):
        return self.__dict__


class VendorParser(object):

    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(open(self.html))
        self.rows = self.parse_rows(self.soup)

        self.document_id = self.get_document_id()

        self.vendor_blank = self.get_field(self.rows, 0)
        self.vendor_p_c = self.get_field(self.rows, 1)
        self.vendor_lastname = self.get_field(self.rows, 2)
        self.vendor_firstname = self.get_field(self.rows, 3)
        self.vendor_relator = self.get_field(self.rows, 4)
        self.vendor_cancel_status = self.get_field(self.rows, 5)

    # logger.debug(form_id)

    def parse_rows(self, soup):
        rows = self.soup.find('table',
                              id="ctl00_cphNoMargin_f_oprTab_tmpl0_"
                                 "DataList11"
                              ).find_all('tr')
        return rows

    def get_document_id(self):
        # Regex to take "..../OPR1245.html" and convert to OPR1245
        doc_id = re.search("(\w+).html", self.html).group(1)
        return doc_id

    def get_field(self, rows, row_id):
        for row in rows:
            cells = row.find_all('span')

            for i, cell in enumerate(cells):
                # means this is the last in a new row,
                if i >= 5 and i % 5 == 0:
                    # i = 5, 10, 15, etc.
                    if isinstance(cell, str) == 0:
                        cell = str(cell.string)
                    if cell == "None" or cell == '':
                        cell = None
                else:
                    if isinstance(cell, str) == 0:
                        cell = str(cell.string)
                    if cell == "None" or cell == '':
                        cell = None

            # field = str(cells[row_id][1].string)  # 0 is key, 1 is value

            # if field == "None" or field == "":
            #     field = None

            # return field

        return cell

    def add_to_session(self):
        # todo: this
        i = insert(db.Vendor)
        i = i.values(dict_output)
        session.execute(i)


class VendeeParser(object):

    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(open(self.html))
        self.rows = self.parse_rows(self.soup)

        self.document_id = self.get_document_id()

        self.vendee_blank = self.get_field(self.rows, 0)
        self.vendee_p_c = self.get_field(self.rows, 1)
        self.vendee_lastname = self.get_field(self.rows, 2)
        self.vendee_firstname = self.get_field(self.rows, 3)
        self.vendee_relator = self.get_field(self.rows, 4)
        self.vendee_cancel_status = self.get_field(self.rows, 5)

    # logger.debug(form_id)

    def parse_rows(self, soup):
        rows = self.soup.find('table',
                              id="ctl00_cphNoMargin_f_oprTab_tmpl0_Datalist1"
                              ).find_all('tr')
        return rows

    def get_document_id(self):
        # Regex to take "..../OPR1245.html" and convert to OPR1245
        doc_id = re.search("(\w+).html", self.html).group(1)
        return doc_id

    def get_field(self, rows, row_id):
        # todo: coulud return many values, right?
        for row in rows:
            cells = row.find_all('span')
            for i, cell in enumerate(cells):
                # means this is the last in a new row,
                if i >= 5 and i % 5 == 0:
                    # i = 5, 10, 15, etc.
                    if isinstance(cell, str) == 0:
                        cell = str(cell.string)
                    if cell == "None" or cell == '':
                        cell = None
                else:
                    if isinstance(cell, str) == 0:
                            cell = str(cell.string)
                    if cell == "None" or cell == '':
                        cell = None

        return cell

    def add_to_session(self):
        # todo: this
        i = insert(db.Vendee)
        i = i.values(dict_output)
        session.execute(i)


class LocationParser(object):

    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(open(self.html))
        self.rows = self.parse_rows(self.soup)

        self.document_id = self.get_document_id()

        self.subdivision = self.get_field(self.rows, 0)
        self.condo = self.get_field(self.rows, 1)
        self.district = self.get_field(self.rows, 2)
        self.square = self.get_field(self.rows, 3)
        self.lot = self.get_field(self.rows, 4)
        self.cancel_status = self.get_field(self.rows, 5)
        self.street_number = self.get_field(self.rows, 6)
        self.address = self.get_field(self.rows, 7)
        self.unit = self.get_field(self.rows, 8)
        self.weeks = self.get_field(self.rows, 9)
        self.cancel_stat = self.get_field(self.rows, 10)
        self.freeform_legal = self.get_field(self.rows, 11)

    def parse_rows(self, soup):
        rows = self.soup.find('table',
                              id="ctl00_cphNoMargin_f_oprTab_tmpl1_"
                                 "ComboLegals"
                              ).find_all('tr')
        return rows

    def get_document_id(self):
        # Regex to take "..../OPR1245.html" and convert to OPR1245
        doc_id = re.search("(\w+).html", self.html).group(1)
        return doc_id

    def get_field(self, rows, row_id):
        for j, row in enumerate(rows):
            cells = row.find_all('span')
            lot_from_string = ""
            for i, cell in enumerate(cells):
                # check if there are entries for lot_from and lot_to
                # (this adds an extra column, which messes up the database
                # since most records don't have a "Lot to" and a "Lot From"
                # column, but just a "Lot" column:
                # check if j == 3, 13, 23, etc.

                # len(cells) == 8 if just
                if (j - 3) % 10 == 0 and len(cells) == 10:
                    # a "lot" field, which is most common
                    # If find Lot to and Lot from, concatenate with "to",
                    # store as single value, then ....
                    if i % 2 == 1:  # Not sure
                        if isinstance(cell, str) == 0:
                                cell = str(cell.string)
                        if cell == "None":
                            cell = ""
                        if i == 5:
                            lot_from_string = cell
                            continue
                        if i == 7:
                            if lot_from_string == "":
                                cell = cell
                            if cell == "":
                                cell = lot_from_string
                            else:
                                cell = lot_from_string + " to " + cell
                        cell = re.sub(r"'", r"''", cell)
                        return cell
                else:
                    if i % 2 == 1:  # Not sure
                        if isinstance(cell, str) == 0:
                                cell = str(cell.string)
                        if cell == "None":
                            cell = ""
                        cell = re.sub(r"'", r"''", cell)
                        return cell
            # if j == 8, 18, 28, etc. Means the end of a table,
            # so need to commit
            # and start over with next table (or stop if the last)
            if (j - 8) % 10 == 0:

                return cell

    def add_to_session(self):
        # todo: this
        i = insert(db.Location)
        i = i.values(dict_output)
        session.execute(i)
