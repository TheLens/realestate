# -*- coding: utf-8 -*-

from landrecords import config
from landrecords.lib.log import Log
from landrecords.lib import (
    build,
    # check_assessor_urls,
    check_temp_status,
    clean,
    # dashboard_sync,
    email_template,
    geocode,
    mail,
    publish
)


class Initialize(object):

    def __init__(self,
                 initial_date='2014-02-18',
                 until_date=config.YESTERDAY_DATE):
        self.log = Log('initialize').logger

        self.initial_date = initial_date
        self.until_date = until_date

        self.log.debug('Build')
        build.Build(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).build_all()

        self.log.debug('Geocode')
        geocode.Geocoder()  # Geocoding entire archive can take over an hour.

        self.log.debug('Publish')
        publish.PublishChecker(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).check_them_all()

        self.log.debug('Clean')
        clean.Clean(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).main()

        # todo:
        # dashboard_sync.DashboardSync()

        self.log.debug('Update Cleaned geom')
        clean.Clean(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).update_cleaned_geom()

        self.log.debug('Check status of new sales')
        check_temp_status.CheckTemp(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).check_permanent_status_of_new_sales()

        self.log.debug('Check status of temp sales')
        check_temp_status.CheckTemp(
            initial_date=self.initial_date,
            until_date=self.until_date
        ).check_permanent_status_of_temp_sales()

        self.log.debug('Mail')
        mail.Mail(
            subject=email_template.EmailTemplate(
                initial_date=self.initial_date,
                until_date=self.until_date
            ).generate_subject(),
            body=email_template.EmailTemplate(
                initial_date=self.initial_date,
                until_date=self.until_date
            ).generate_body(),
            frm='tthoren@thelensnola.org',
            to=['tthoren@thelensnola.org']
        ).send_as_html()

        # check_assessor_urls().check(
        #     initial_date=initial_date, until_date=until_date)


if __name__ == '__main__':
    log = Log('initialize').logger

    try:
        # Default is to build entire archive since 2014/02/18
        Initialize(
            initial_date='2014-02-18',
            until_date='2014-02-20'
        )
        # Initialize()
    except Exception, e:
        log.exception(e, exc_info=True)
        mail.Mail(
            subject="Error running Land Record's initialize.py script",
            body='Check {0}.log for more details.'.format(
                'relevant_log'),  # todo
            frm='tthoren@thelensnola.org',
            to=['tthoren@thelensnola.org']
        ).send_as_text()
