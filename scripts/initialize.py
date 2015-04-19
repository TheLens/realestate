# -*- coding: utf-8 -*-

'''
Calls on other classes to build, geocode, clean and
publish records to the cleaned table.
'''

from landrecords.config import Config
# from landrecords.lib.log import Log

from landrecords.lib.build import Build
from landrecords.lib.clean import Clean
from landrecords.lib.geocode import Geocode
from landrecords.lib.mail import Mail
from landrecords.lib.publish import Publish
# from landrecords.lib.check_temp_status import CheckTemp
from landrecords.lib.email_template import EmailTemplate
from landrecords import log


class Initialize(object):

    '''
    Calls on other classes to build, geocode, clean and publish
    records to the cleaned table.
    '''

    def __init__(self,
                 initial_date=Config().OPENING_DAY,
                 until_date=Config().YESTERDAY_DATE):
        '''Runs through all classes.'''

        self.initial_date = initial_date
        self.until_date = until_date

        log.debug(self.initial_date)
        log.debug(self.until_date)

        Build(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).build_all()

        Clean().prep_locations_for_geocoding()
        Geocode().geocode()  # Geocoding entire archive can take over an hour
        Geocode().update_locations_with_neighborhoods()

        Clean(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).main()

        Publish(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).check_them_all()

        # dashboard_sync.DashboardSync()  # todo

        Clean(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).update_cleaned_geom()

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
        # Default is to build entire archive since 2014/02/18
        Initialize(
            # initial_date='2014-02-18',
            # until_date='2014-02-20'
        )
        # Initialize()
    except Exception, error:
        log.exception(error, exc_info=True)
        Mail(
            subject="Error running Land Record's initialize.py script",
            body='Check log for more details.',
            frm='tthoren@thelensnola.org',
            to=['tthoren@thelensnola.org']
        ).send_as_text()
