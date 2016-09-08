# -*- coding: utf-8 -*-

"""
Create the results language on the /search page.

Ex. "10 sales found for keyword 'LLC' in the French Quarter neighborhood where
the price was between $10,000 and $200,000 between Feb. 18, 2014, and
Feb. 20, 2014.'
"""

from www.utils import (
    get_number_with_commas,
    get_num_with_curr_sign,
    ymd_to_full_date)


class ResultsLanguage(object):
    """Convert data to readable format for front-end."""

    def __init__(self, data):
        """Define class variables."""
        self.data = data

    def plural_or_not(self):
        """Check if more than one result."""
        if self.data['number_of_records'] == 1:
            plural_or_not = "sale"
        else:
            plural_or_not = "sales"

        return plural_or_not

    def add_initial_language(self, plural_or_not):
        """Create initial sentence language."""
        number_of_sales = get_number_with_commas(
            self.data['number_of_records'])

        final_sentence = "{0} {1} found".format(
            str(number_of_sales),
            plural_or_not)

        return final_sentence

    def add_keyword_language(self, final_sentence):
        """Add keyword or key phrase language."""
        if self.data['name_address'] != '':
            if len(self.data['name_address'].split(' ')) > 1:  # Multiple words
                term = "key phrase"
            else:  # One word
                term = "keyword"

            final_sentence += ' for {0} "{1}"'.format(
                term,
                self.data['name_address'])

        return final_sentence

    def add_nbhd_zip_language(self, final_sentence):
        """Add neighborhood or ZIP code language."""
        if self.data['neighborhood'] != '':
            if self.data['zip_code'] != '':
                final_sentence += " in the {0} neighborhood and {1}".format(
                    self.data['neighborhood'],
                    self.data['zip_code'])
            else:
                final_sentence += " in the {} neighborhood".format(
                    self.data['neighborhood'])
        elif self.data['zip_code'] != '':
            final_sentence += " in ZIP code {}".format(self.data['zip_code'])

        return final_sentence

    def add_amount_language(self, final_sentence):
        """Add amount language."""
        if self.data['amount_low'] != '':
            if self.data['amount_high'] != '':
                final_sentence += (
                    " where the price was between {0} and {1}").format(
                        get_num_with_curr_sign(self.data['amount_low']),
                        get_num_with_curr_sign(self.data['amount_high']))
            else:
                final_sentence += (
                    " where the price was greater than {}").format(
                        get_num_with_curr_sign(self.data['amount_low']))
        elif self.data['amount_high'] != '':
            final_sentence += " where the price was less than {}".format(
                get_num_with_curr_sign(self.data['amount_high']))

        return final_sentence

    def add_date_language(self, final_sentence):
        """
        Add date language.

        Ex. ...between Feb. 10, 2014, and Feb. 12, 2014.
        """
        if self.data['begin_date'] != '':
            if self.data['end_date'] != '':
                final_sentence += " between {0}, and {1},".format(
                    ymd_to_full_date(self.data['begin_date'], no_day=True),
                    ymd_to_full_date(self.data['end_date'], no_day=True))
            else:
                final_sentence += " after {},".format(
                    ymd_to_full_date(self.data['begin_date'], no_day=True))
        elif self.data['end_date'] != '':
            final_sentence += " before {},".format(
                ymd_to_full_date(self.data['end_date'], no_day=True))

        return final_sentence

    def add_map_filtering_language(self, final_sentence):
        """Add language depending on whether map filtering is turned on."""
        if self.data['map_button_state']:
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
        final_sentence = self.add_final_sentence_language(final_sentence)
        return final_sentence
