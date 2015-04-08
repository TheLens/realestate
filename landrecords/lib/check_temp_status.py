# -*- coding: utf-8 -*-

import re
import glob
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib import scrape
from landrecords.lib.log import Log


class CheckTemp(object):

    def __init__(self, initial_date=None, until_date=None):
        self.log = Log('check_temp').logger

        self.initial_date = initial_date
        self.until_date = until_date

        base = declarative_base()
        self.engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

        rows = self.get_rows_with_neighborhood()
        clean_rows = self.clean_rows(rows)
        self.commit_rows(clean_rows)

        rows = self.get_rows_without_neighborhood()
        clean_rows = self.clean_rows(rows)
        self.commit_rows(clean_rows)

    def check_permanent_status_of_new_sales(self):
        '''
        Examine first-time sales and assign True or False for permanent_flag.
        '''

        self.log.info('checkPermanentStatusOfNewSales')

        # Find the date range of sales to look at. This is only to reduce the
        # number of iterations needed by the for-loop below.

        earliest_none_date = ''
        latest_none_date = ''

        q = self.session.query(
            func.min(db.Detail.document_recorded).label('early_date')
        ).filter(
            db.Detail.permanent_flag is None
        )

        for u in q:
            earliest_none_date = u.early_date

        print 'earliest_none_date:', earliest_none_date
        self.log.debug(earliest_none_date)

        q = self.session.query(
            func.max(db.Detail.document_recorded).label('late_date')
        ).filter(
            db.Detail.permanent_flag is None
        )

        for u in q:
            latest_none_date = u.late_date

        print 'latest_none_date:', latest_none_date
        self.log.debug(latest_none_date)

        # For all folders (dates)
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            # self.log.debug(folder)

            cur_it_date = folder.split('/')[-1]
            # self.log.debug(cur_it_date)

            try:
                cur_it_datetime = datetime.strptime(cur_it_date, '%m-%d-%Y')
                # self.log.debug(cur_it_datetime)
            except Exception, e:
                self.log.error(e, exc_info=True)
                continue

            try:
                earliest_none_datetime = datetime.combine(
                    earliest_none_date, datetime.min.time())
                # self.log.debug(earliest_none_datetime)
            except Exception, e:
                self.log.error(e, exc_info=True)
                continue

            if cur_it_datetime < earliest_none_datetime:
                continue

            # For this date that is currently considered temporary (whether by
            # default or because it was previously confirmed to be temporary),
            # check on the permanent date range at the time of the scrape.
            this_path = '%s/permanent-date-range-when-scraped_*.html' % (
                folder)
            for pathname in sorted(glob.glob(this_path)):
                # For all records (within each day)
                # print 'pathname:', pathname
                self.log.debug(pathname)

                perm_range_when_scr_d1 = re.match(
                    r"../data/" +
                    cur_it_date +
                    r"/permanent-date-range-when-scraped_(\d+)-(\d+).html",
                    pathname).group(1)

                print 'perm_range_when_scr_d1:'
                print perm_range_when_scr_d1

                self.log.debug(perm_range_when_scr_d1)

                perm_range_when_scr_d1 = datetime.strptime(
                    perm_range_when_scr_d1,
                    '%m%d%Y')  # ).strftime('%Y-%m-%d')
                self.log.debug(perm_range_when_scr_d1)

                perm_range_when_scr_d2 = re.match(
                    r"../data/" +
                    cur_it_date +
                    r"/permanent-date-range-when-scraped_(\d+)-(\d+).html",
                    pathname).group(2)

                print 'perm_range_when_scr_d2:'
                print perm_range_when_scr_d2

                self.log.debug(perm_range_when_scr_d2)

                perm_range_when_scr_d2 = datetime.strptime(
                    perm_range_when_scr_d2,
                    '%m%d%Y')  # ).strftime('%Y-%m-%d')
                self.log.debug(perm_range_when_scr_d2)

                cond = (perm_range_when_scr_d1 <= cur_it_datetime and
                        cur_it_datetime <= perm_range_when_scr_d2)

                if cond:
                    self.log.info('query')
                    self.session.query(
                        db.Detail
                    ).filter(
                        db.Detail.document_recorded == '%s' % cur_it_date
                    ).update({"permanent_flag": True})
                    self.log.info('query')
                    self.session.query(
                        db.Cleaned
                    ).filter(
                        db.Cleaned.document_recorded == '%s' % cur_it_date
                    ).update({"permanent_flag": True})
                    self.log.info('commit')
                    self.session.commit()
                else:
                    self.log.info('query')
                    self.session.query(
                        db.Detail
                    ).filter(
                        db.Detail.document_recorded == '%s' % cur_it_date
                    ).update({"permanent_flag": False})
                    self.log.info('query')
                    self.session.query(
                        db.Cleaned
                    ).filter(
                        db.Cleaned.document_recorded == '%s' % cur_it_date
                    ).update({"permanent_flag": False})
                    self.log.info('commit')
                    self.session.commit()
            print '\n'

            # If reached final date, then end.
            if cur_it_date == latest_none_date:
                break

    def check_permanent_status_of_temp_sales(self):
        '''
        Compare most recently downloaded permanent date range against sales
        that were previously determined to have permanent_flag = False to see
        if any sales should be re-scraped.
        '''

        # Find the date range of temporary sales to look at. This is only to
        # reduce the number of iterations needed by the for-loop below.

        earliest_temp_date = ''
        latest_temp_date = ''

        q = self.session.query(
            db.Detail
        ).filter(
            db.Detail.permanent_flag is False
        ).order_by(
            # update Cleaned in order Dashboard changes were made
            db.Detail.document_recorded
        ).limit(1).all()

        self.log.debug(q)

        for u in q:
            self.log.debug(u)
            earliest_temp_date = u.document_recorded
            self.log.debug(earliest_temp_date)

        q = self.session.query(
            db.Detail
        ).filter(
            db.Detail.permanent_flag is False
        ).order_by(
            # update Cleaned in order Dashboard changes were made
            db.Detail.document_recorded.desc()
        ).limit(1).all()

        for u in q:
            latest_temp_date = u.document_recorded
            self.log.debug(latest_temp_date)

        dates_to_redo = []

        permanent_range_first_date = ''
        permanent_range_last_date = ''

        this_path = '%s/most-recent-permanent-date-range_*.html' % (
            config.DATA_DIR)
        # Find most recently updated permanent date range.
        for pathname in glob.glob(this_path):
            self.log.debug(pathname)

            permanent_range_first_date = re.match(
                r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html",
                pathname).group(1)
            permanent_range_first_date = datetime.strptime(
                permanent_range_first_date,
                '%m%d%Y')  # ).strftime('%Y-%m-%d')
            self.log.debug(permanent_range_first_date)

            permanent_range_last_date = re.match(
                r"../data/most-recent-permanent-date-range_(\d+)-(\d+).html",
                pathname).group(2)
            permanent_range_last_date = datetime.strptime(
                permanent_range_last_date,
                '%m%d%Y')  # ).strftime('%Y-%m-%d')
            self.log.debug(permanent_range_last_date)

        # For all folders (dates)
        for folder in sorted(glob.glob('%s/raw/*' % (config.DATA_DIR))):
            cur_it_date = folder.split('/')[-1]

            try:
                cur_it_datetime = datetime.strptime(
                    cur_it_date, '%m-%d-%Y')
            except Exception, e:
                self.log.error(e, exc_info=True)
                continue

            try:
                earliest_temp_datetime = datetime.combine(
                    earliest_temp_date, datetime.min.time())
            except Exception, e:
                self.log.error(e, exc_info=True)
                continue

            if cur_it_datetime < earliest_temp_datetime:
                continue

            self.log.debug(cur_it_date)
            self.log.debug(cur_it_datetime)
            self.log.debug(earliest_temp_datetime)

            cond = (permanent_range_first_date <= cur_it_datetime and
                    cur_it_datetime <= permanent_range_last_date)
            if cond:
                self.log.info('date_to_redo.append')
                dates_to_redo.append(cur_it_datetime)

            # else:
                # Do nothing. Keep records and don't change permanent_flag

            # If reached final date, then end.
            if cur_it_date == latest_temp_date:
                self.log.info('break')
                break

        # print 'date_to_redo:'
        # print dates_to_redo

        try:
            early_date = min(dates_to_redo)
            self.log.debug(early_date)

            late_date = max(dates_to_redo)
            self.log.debug(late_date)
        except Exception, e:
            # Nothing left to do because no records are "temporary"
            self.log.error(e, exc_info=True)
            return

        self.scrape_days(early_date, late_date)

        def scrape_days(self, early_date, late_date):
            early_datetime = datetime.strptime(early_date, '%Y-%m-%d')
            self.log.debug(early_datetime)
            late_datetime = datetime.strptime(late_date, '%Y-%m-%d')
            self.log.debug(early_datetime)

            # Scrape those days over again
            self.log.info('scrape')
            try:
                scrape.Scraper().main(
                    from_date=early_datetime,
                    until_date=late_datetime)
            except Exception, e:
                self.log.error(e, exc_info=True)

        self.delete_existing_records(early_date, late_date)

        def delete_existing_records(self, early_date, late_date):
            # Delete existing records for this date
            location_sql = """
                DELETE FROM locations USING details
                WHERE details.document_id = locations.document_id
                AND details.document_recorded >= '%s'
                AND details.document_recorded <= '%s'
            """ % (early_date, late_date)
            self.engine.execute(location_sql)

            vendor_sql = """
                DELETE FROM vendors USING details
                WHERE details.document_id = vendors.document_id
                AND details.document_recorded >= '%s'
                AND details.document_recorded <= '%s'
            """ % (early_date, late_date)
            self.engine.execute(vendor_sql)

            vendee_sql = """
                DELETE FROM vendees USING details
                WHERE details.document_id = vendees.document_id
                AND details.document_recorded >= '%s'
                AND details.document_recorded <= '%s'
            """ % (early_date, late_date)
            self.engine.execute(vendee_sql)

            detail_sql = """
                DELETE FROM details
                WHERE document_recorded >= '%s'
                AND document_recorded <= '%s'
            """ % (early_date, late_date)
            self.engine.execute(detail_sql)

            cleaned_sql = """
                DELETE FROM cleaned
                WHERE document_recorded >= '%s'
                AND document_recorded <= '%s'
            """ % (early_date, late_date)
            self.engine.execute(cleaned_sql)

        def rebuild_days(self, early_date, late_date):
            # Build those newly scraped records.
            # This will set perm_flag = True in
            # checkPermanentStatusOfNewSales().
            self.log.info('doitall')
            # todo: initialize.do_it_all(early_date, late_date)
