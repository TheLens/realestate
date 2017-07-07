# -*- coding: utf-8 -*-

"""
Create the results language on the /search page.

Ex. "10 sales found for keyword 'LLC' in the French Quarter neighborhood where
the price was between $10,000 and $200,000 between Feb. 18, 2014, and
Feb. 20, 2014."
"""

import utils


class ResultsLanguage(object):
    """Convert data to readable format for front-end."""

    def __init__(self, data):
        """Define class variables."""
        self.number_of_records = data['number_of_records']
        self.name_address = data['name_address']
        self.neighborhood = data['neighborhood']
        self.zip_code = data['zip_code']
        self.amount_low = data['amount_low']
        self.amount_high = data['amount_high']
        self.begin_date = data['begin_date']
        self.end_date = data['end_date']
        self.map_button_state = data['map_button_state']

    def plural_or_not(self):
        """Check if more than one result."""
        if self.number_of_records == 1:
            return "sale"

        return "sales"

    def add_initial_language(self, plural_or_not):
        """Create initial sentence language."""
        number_of_sales = utils.get_number_with_commas(self.number_of_records)
        return "{0} {1} found".format(str(number_of_sales), plural_or_not)

    def add_keyword_language(self, final_sentence):
        """Add keyword or key phrase language."""
        if self.name_address != '':
            if len(self.name_address.split(' ')) > 1:  # Multiple words
                term = "key phrase"
            else:  # One word
                term = "keyword"

            final_sentence += ' for {0} "{1}"'.format(term, self.name_address)

        return final_sentence

    def add_nbhd_zip_language(self, final_sentence):
        """Add neighborhood or ZIP code language."""
        if self.neighborhood != '':
            if self.zip_code != '':
                final_sentence += " in the {0} neighborhood and {1}".format(
                    self.neighborhood, self.zip_code)
            else:
                final_sentence += " in the {} neighborhood".format(
                    self.neighborhood)
        elif self.zip_code != '':
            final_sentence += " in ZIP code {}".format(self.zip_code)

        return final_sentence

    def add_amount_language(self, final_sentence):
        """Add amount language."""
        if self.amount_low != '':
            if self.amount_high != '':
                final_sentence += (
                    " where the price was between {0} and {1}").format(
                        utils.get_num_with_curr_sign(self.amount_low),
                        utils.get_num_with_curr_sign(self.amount_high))
            else:
                final_sentence += (
                    " where the price was greater than {}").format(
                        utils.get_num_with_curr_sign(self.amount_low))
        elif self.amount_high != '':
            final_sentence += " where the price was less than {}".format(
                utils.get_num_with_curr_sign(self.amount_high))

        return final_sentence

    def add_date_language(self, final_sentence):
        """
        Add date language.

        Ex. ...between Feb. 10, 2014, and Feb. 12, 2014.
        """
        if self.begin_date != '':
            if self.end_date != '':
                final_sentence += " between {0}, and {1},".format(
                    utils.ymd_to_full_date(self.begin_date, no_day=True),
                    utils.ymd_to_full_date(self.end_date, no_day=True))
            else:
                final_sentence += " after {},".format(
                    utils.ymd_to_full_date(self.begin_date, no_day=True))
        elif self.end_date != '':
            final_sentence += " before {},".format(
                utils.ymd_to_full_date(self.end_date, no_day=True))

        return final_sentence

    def add_map_filtering_language(self, final_sentence):
        """Add language depending on whether map filtering is turned on."""
        if self.map_button_state:
            final_sentence += ' in the current map view'

        return final_sentence

    @staticmethod
    def add_final_sentence_language(final_sentence):
        """End sentences."""
        # Punctuation comes before quotation marks
        if final_sentence[-1] == "'" or final_sentence[-1] == '"':
            last_character = final_sentence[-1]
            final_sentence_list = list(final_sentence)
            final_sentence_list[-1] = '.'
            final_sentence_list.append(last_character)
            final_sentence = ''.join(final_sentence_list)
        elif final_sentence[-1] == ",":  # Ending on date
            final_sentence = final_sentence[:-1]
            final_sentence += '.'
        else:
            final_sentence += '.'

        return final_sentence

    def main(self):
        """Run through all sentence-building methods."""
        plural_or_not = self.plural_or_not()
        final_sentence = self.add_initial_language(plural_or_not)
        final_sentence = self.add_keyword_language(final_sentence)
        final_sentence = self.add_nbhd_zip_language(final_sentence)
        final_sentence = self.add_amount_language(final_sentence)
        final_sentence = self.add_date_language(final_sentence)
        final_sentence = self.add_map_filtering_language(final_sentence)
        return self.add_final_sentence_language(final_sentence)
