# -*- coding: utf-8 -*-

'''
Calls on other classes to build, geocode, clean and publish records to the
cleaned table. Can receive a date range or determine the dates on its own.
'''

from realestate.lib.build import Build
from realestate.lib.clean import Clean
from realestate.lib.geocode import Geocode
from realestate.lib.get_dates import GetDates
from realestate.lib.mail import Mail
from realestate.lib.publish import Publish
# from realestate.lib.check_temp_status import CheckTemp
from realestate.lib.email_template import EmailTemplate
from realestate import log, LOG_DIR


class Initialize(object):

    '''
    Calls on other classes to build, geocode, clean and publish
    records to the cleaned table.
    '''

    def __init__(self, initial_date=None, until_date=None):
        '''Runs through all classes.'''

        if initial_date is not None and until_date is not None:
            self.initial_date = initial_date
            self.until_date = until_date
        else:
            date_range = GetDates().get_date_range()
            self.initial_date = date_range['initial_date']
            self.until_date = date_range['until_date']

        log.debug('self.initial_date: %s', self.initial_date)
        log.debug('self.until_date: %s', self.until_date)

        # try:
        #     Build(
        #         initial_date=self.initial_date,
        #         until_date=self.until_date
        #     ).build_all()

        # except Exception, error:
        #     log.exception(error, exc_info=True)

        Geocode(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).geocode()  # Geocoding takes over an hour
        # Geocode().update_locations_with_neighborhoods()

        # try:
        #     Publish(
        #         initial_date=self.initial_date,
        #         until_date=self.until_date
        #     ).main()
        # except Exception, error:
        #     log.exception(error, exc_info=True)

        # try:
        #     Clean(
        #         initial_date=self.initial_date,
        #         until_date=self.until_date
        #     ).main()
        # except Exception, error:
        #     log.exception(error, exc_info=True)

        # # dashboard_sync.DashboardSync()  # todo

        # Clean(
        #     initial_date=self.initial_date,
        #     until_date=self.until_date
        # ).update_cleaned_geom()

        # CheckTemp(
        #     initial_date=self.initial_date,
        #     until_date=self.until_date
        # ).check_permanent_status_of_new_sales()

        # CheckTemp(
        #     initial_date=self.initial_date,
        #     until_date=self.until_date
        # ).check_permanent_status_of_temp_sales()

        Mail(
            subject=EmailTemplate(
                initial_date=self.initial_date,
                until_date=self.until_date
            ).generate_subject(),
            body=EmailTemplate(
                initial_date=self.initial_date,
                until_date=self.until_date
            ).generate_body(),
            frm='tthoren@thelensnola.org',
            to=['tthoren@thelensnola.org']
        ).send_as_html()

        # check_assessor_urls().check(
        #     initial_date=initial_date, until_date=until_date)


if __name__ == '__main__':
    try:
        # Default is to build and clean anything that needs it.
        # Specify custom date range in 'YYYY-mm-dd' string format
        # or use variables such as OPENING_DAY, YESTERDAY_DAY.
        Initialize(
            # select count(*) from locations join details on
            # locations.document_id = details.document_id where
            # details.document_recorded >= '2014-09-30' and
            # details.document_recorded <= '2014-12-09';  # 2475 records
            initial_date='2014-09-30',
            until_date='2014-12-09'
        )
    except Exception, error:
        log.exception(error, exc_info=True)
        Mail(
            subject="Error running realestate's initialize.py script",
            body='Check log for more details.',
            frm='tthoren@thelensnola.org',
            to=['tthoren@thelensnola.org']
        ).send_with_attachment(
            files=['%s/realestate.log' % LOG_DIR]
        )
