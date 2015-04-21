# -*- coding: utf-8 -*-

'''Builds languages for returned results.'''

from landrecords.lib.utils import Utils


class ResultsLanguage(object):

    '''Methods for each page in the app.'''

    def __init__(self, data):
        '''Starting things off.'''

        self.data = data

    def plural_or_not(self):
        '''Checks if more than one result.'''

        if self.data['number_of_records'] == 1:
            plural_or_not = "sale"
        else:
            plural_or_not = "sales"

        return plural_or_not

    def add_initial_language(self, plural_or_not):
        '''Creates initial sentence language.'''

        final_sentence = str(Utils().get_number_with_commas(
            self.data['number_of_records'])) + ' ' + plural_or_not + ' found'

        return final_sentence

    def add_keyword_language(self, final_sentence):
        '''Adds keyword or key phrase language.'''

        if self.data['name_address'] != '':
            if len(self.data['name_address'].split()) > 1:
                final_sentence += ' for key phrase "' + \
                    self.data['name_address'] + '"'
                # for 'keyword'
            else:
                final_sentence += ' for keyword "' + \
                    self.data['name_address'] + '"'
                # for 'keyword'

        return final_sentence

    def add_nbhd_zip_language(self, final_sentence):
        '''Adds neighborhood or ZIP code language.'''

        if self.data['neighborhood'] != '':
            if self.data['zip_code'] != '':
                final_sentence += " in the " + self.data['neighborhood'] + \
                    " neighborhood and " + self.data['zip_code']
                # in the Mid-City neighborhood and 70119
            else:
                final_sentence += " in the " + self.data['neighborhood'] + \
                    " neighborhood"
                # in the Mid-City neighborhood
        elif self.data['zip_code'] != '':
            final_sentence += " in ZIP code " + self.data['zip_code']
            # in ZIP code 70119

        return final_sentence

    def add_amount_language(self, final_sentence):
        '''Adds amount language.'''

        if self.data['amount_low'] != '':
            if self.data['amount_high'] != '':
                final_sentence += " where the price was between " + \
                    Utils().get_num_with_curr_sign(self.data['amount_low']) + \
                    + " and " + \
                    Utils().get_num_with_curr_sign(self.data['amount_high'])
                # where the amount is between $10 and $20
            else:
                final_sentence += " where the price was greater than " + \
                    Utils().get_num_with_curr_sign(self.data['amount_low'])
                # where the amount is greater than $10
        elif self.data['amount_high'] != '':
            final_sentence += " where the price was less than " + \
                Utils().get_num_with_curr_sign(self.data['amount_high'])
            # where the amount is less than $20

        return final_sentence

    def add_date_language(self, final_sentence):
        '''Adds date language.'''

        if self.data['begin_date'] != '':
            if self.data['end_date'] != '':
                final_sentence += " between " + \
                    Utils().ymd_to_full_date(
                        self.data['begin_date'],
                        no_day=True) + \
                    ", and " + \
                    Utils().ymd_to_full_date(
                        self.data['end_date'],
                        no_day=True)
                # between Feb. 10, 2014, and Feb. 12, 2014
            else:
                final_sentence += " after " + \
                    Utils().ymd_to_full_date(
                        self.data['begin_date'],
                        no_day=True)
                # after Feb. 10, 2014.
        elif self.data['end_date'] != '':
            final_sentence += " before " + \
                Utils().ymd_to_full_date(
                    self.data['end_date'],
                    no_day=True)
            # before Feb. 20, 2014.

        return final_sentence

    def add_map_filtering_language(self, final_sentence):
        '''Adds language depending on whether map filtering is turned on.'''

        if self.data['map_button_state'] is True:
            final_sentence += ' in the current map view'

        return final_sentence

    @staticmethod
    def add_final_sentence_language(final_sentence):
        '''Endings for the sentences.'''

        # Punctuation comes before quotation marks
        if final_sentence[-1] == "'" or final_sentence[-1] == '"':
            last_character = final_sentence[-1]
            final_sentence_list = list(final_sentence)
            final_sentence_list[-1] = '.'
            final_sentence_list.append(last_character)
            final_sentence = ''.join(final_sentence_list)
        else:
            final_sentence += '.'

        return final_sentence

    def main(self):
        '''Runs through all sentence-building methods.'''

        plural_or_not = self.plural_or_not()
        final_sentence = self.add_initial_language(plural_or_not)
        final_sentence = self.add_keyword_language(final_sentence)
        final_sentence = self.add_nbhd_zip_language(final_sentence)
        final_sentence = self.add_amount_language(final_sentence)
        final_sentence = self.add_date_language(final_sentence)
        final_sentence = self.add_map_filtering_language(final_sentence)
        final_sentence = self.add_final_sentence_language(final_sentence)

        return final_sentence

if __name__ == '__main__':
    pass
