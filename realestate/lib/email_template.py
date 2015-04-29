# -*- coding: utf-8 -*-

'''
The template for the summary email. Draws on `stat_analysis.py` for common,
interesting queries.
'''

from landrecords.lib.stat_analysis import StatAnalysis
from landrecords.lib.utils import Utils


class EmailTemplate(object):
    '''Email template class, including subject and body generators.'''

    def __init__(self, initial_date=None, until_date=None):
        '''Initialize self variables with date range.'''

        self.initial_date = initial_date
        self.until_date = until_date

    def generate_subject(self):
        '''Generates subject for email.'''

        subject = "Land records summary for"

        if self.initial_date == self.until_date:
            subject += " %s" % Utils().ymd_to_full_date(self.initial_date)
        else:
            subject += " %s to %s" % (
                Utils().ymd_to_full_date(self.initial_date, no_day=True),
                Utils().ymd_to_full_date(self.until_date, no_day=True))

        return subject

    def generate_body(self):
        '''Combine the email body parts.'''

        email_summary = self.generate_body_summary()
        email_list = self.generate_body_list()

        email_string = email_summary + email_list

        return email_string

    def generate_body_summary(self):
        '''Generates body for email, including statistics.'''

        stat = StatAnalysis(
            initial_date=self.initial_date,
            until_date=self.until_date
        )

        email_summary = (
            '<p>http://vault.thelensnola.org/realestate/search?d1={0}&d2={1}' +
            '</p>' +
            '\n' +
            '\n' +
            '<p>{2} sales recorded on {3} to {4}.' +
            '</p>' +
            '\n' +
            '\n' +
            '<p>{5} records not published because of questionable data.' +
            '</p>' +
            '\n' +
            '\n' +
            '<p>{6} records not published because location ' +
            'could not be found.' +
            '</p>' +
            '\n' +
            '\n' +
            '<p>http://vault.thelensnola.org/realestate/dashboard' +
            '</p>' +
            '\n' +
            '\n' +
            '<p>High: ${7}</p>' +
            '\n' +
            '\n' +
            '<p>Low: ${8}</p>' +
            '\n' +
            '\n'
        ).format(
            Utils().ymd_to_mdy_slashes(self.initial_date),
            Utils().ymd_to_mdy_slashes(self.until_date),
            format(stat.count(), ','),
            Utils().ymd_to_full_date(self.initial_date),
            Utils().ymd_to_full_date(self.until_date),
            format(stat.detail_not_published(), ','),
            format(stat.location_not_published(), ','),
            stat.highest_amount(),
            stat.lowest_amount()
        )

        return email_summary

    def generate_body_list(self):
        '''Generate list of all sales in given date range.'''

        stat = StatAnalysis(self.initial_date, self.until_date)

        rows = stat.all_records()

        email_list = ''
        message = ''

        for row in rows:
            if row['document_date'] is None:
                message += '<p><strong>Sale date</strong><br>None<br>\n'
            else:
                message += (
                    '<p><strong>Sale date</strong><br>' +
                    row['document_date'].strftime('%A, %b. %-d, %Y') +
                    '<br>\n')
            message += (
                '<strong>Amount</strong><br>${0}<br>\n' +
                '<strong>Buyers</strong><br>{1}<br>\n' +
                '<strong>Sellers</strong><br>{2}<br>\n' +
                '<strong>Address</strong><br>{3}<br>\n' +
                '<strong>Location info</strong><br>{4}<br>\n' +
                '<strong>Zip</strong><br>{5}<br>\n' +
                '<strong>Neighborhood</strong><br>{6}</p>\n'
            ).format(
                format(row['amount'], ','),
                row['buyers'],
                row['sellers'],
                row['address'],
                row['location_info'],
                row['zip_code'],
                row['neighborhood']
            )

            email_list += message.encode('utf8')
            email_list += '\n'
            message = ''

        return email_list

if __name__ == '__main__':
    pass
