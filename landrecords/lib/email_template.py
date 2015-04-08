# -*- coding: utf-8 -*-

from landrecords.lib import stat_analysis
from landrecords.lib.log import Log
from landrecords.lib.utils import Utils


class EmailTemplate(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('email_template').logger

        self.initial_date = initial_date
        self.until_date = until_date

    def generate_subject(self):
        subject = "Land records summary for"

        if self.initial_date == self.until_date:
            subject += " %s" % Utils().ymd_to_full_date(self.initial_date)
        else:
            subject += " %s to %s" % (
                Utils().ymd_to_full_date(self.initial_date, no_day=True),
                Utils().ymd_to_full_date(self.until_date, no_day=True))

        return subject

    def generate_body(self):
        stat = stat_analysis.StatAnalysis(
            'cleaned', self.initial_date, self.until_date)

        # todo: handle if either or both dates not specified?
        email_string = (
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
            Utils().ymd_to_full_date(self.initial_date),
            Utils().ymd_to_full_date(self.until_date),
            format(stat.count(), ','),
            Utils().ymd_to_full_date(self.initial_date),
            Utils().ymd_to_full_date(self.until_date),
            format(stat.detail_not_published(), ','),
            format(stat.location_not_published(), ','),
            format(stat.highest_amount(), ','),
            format(stat.lowest_amount(), ',')
        )

        rows = stat.all_records()

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

            email_string += message.encode('utf8')
            email_string += '\n'
            message = ''

        return email_string
