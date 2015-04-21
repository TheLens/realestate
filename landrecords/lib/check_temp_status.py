# -*- coding: utf-8 -*-

'''
Check on the temporary/permanent status of sales. Sales are first recorded on
the Land Records Division site as temporary. This checks for changes in the
permanent date range and whether a "temporary" sale is now "permanent."
'''

import re
import glob
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords.config import Config
from landrecords.db import (
    Cleaned,
    Detail
)
from landrecords.lib.scrape import Scrape
from landrecords import log


class CheckTemp(object):

    '''Check on the temporary/permanent status of sales.'''

    def __init__(self):
        '''Establishes connections to the database.'''

        base = declarative_base()
        self.engine = create_engine(Config().SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        self.sn = sessionmaker(bind=self.engine)

    def earliest_date_no_flag(self):
        '''Finds the earliest date_recorded without permanent_flag set.'''

        session = self.sn()

        query = session.query(
            func.min(Detail.document_recorded).label('early_date')
        ).filter(
            Detail.permanent_flag.is_(None)  # To satisfy PEP8
        ).all()

        for row in query:
            earliest_none_date = row.early_date

        earliest_none_datetime = datetime.combine(
            earliest_none_date, datetime.min.time())

        session.close()

        return earliest_none_datetime

    def latest_date_no_flag(self):
        '''Finds the latest date_recorded without permanent_flag set.'''

        session = self.sn()

        query = session.query(
            func.max(Detail.document_recorded).label('late_date')
        ).filter(
            Detail.permanent_flag.is_(None)
        ).all()

        for row in query:
            latest_none_date = row.late_date

        latest_none_datetime = datetime.combine(
            latest_none_date, datetime.min.time())

        session.close()

        return latest_none_datetime

    @staticmethod
    def find_early_perm_date_when_scraped(current_iteration_date):
        '''Finds the earliest date_recorded with permanent_flag.'''

        pattern = (
            r'%s/raw/' % Config().DATA_DIR +
            r'%s/' % current_iteration_date +
            r'permanent-date-range-when-scraped_(\d+)-(\d+).html')

        file_path = glob.glob(
            '%s/raw/%s/permanent-date-range-when-scraped_*.html' % (
                Config().DATA_DIR, current_iteration_date))[0]

        early_permanent_date = re.match(pattern, file_path).group(1)

        early_permanent_datetime = datetime.strptime(
            early_permanent_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return early_permanent_datetime

    @staticmethod
    def find_late_perm_date_when_scraped(current_iteration_date):
        '''docstring'''

        pattern = (
            r'%s/raw/' % Config().DATA_DIR +
            r'%s/' % current_iteration_date +
            r'permanent-date-range-when-scraped_(\d+)-(\d+).html')

        file_path = glob.glob(
            '%s/raw/%s/permanent-date-range-when-scraped_*.html' % (
                Config().DATA_DIR, current_iteration_date))[0]

        late_permanent_date = re.match(pattern, file_path).group(2)

        late_permanent_datetime = datetime.strptime(
            late_permanent_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return late_permanent_datetime

    def update_this_dates_permanent_flag(self,
                                         current_datetime,
                                         early_permanent_datetime,
                                         late_permanent_datetime):
        '''docstring'''

        cond = (early_permanent_datetime <= current_datetime and
                current_datetime <= late_permanent_datetime)

        session = self.sn()

        if cond:
            session.query(
                Detail
            ).filter(
                Detail.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": True})

            session.query(
                Cleaned
            ).filter(
                Cleaned.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": True})
            session.commit()
        else:
            session.query(
                Detail
            ).filter(
                Detail.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": False})

            session.query(
                Cleaned
            ).filter(
                Cleaned.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": False})
            session.commit()

        session.close()

    def check_permanent_status_of_new_sales(self):
        '''
        Examine first-time sales and assign True or False for permanent_flag.
        '''

        log.debug('Check permanent status of new sales')

        # todo: Is this function called for sales that have already been given
        # a False flag? Need to change that if so, because this only looks
        # for sales with no flag. Could change to check for None or False.

        # Get dates to inspect
        earliest_datetime = self.earliest_date_no_flag()
        latest_datetime = self.latest_date_no_flag()

        # For all folders (dates)
        while earliest_datetime != (latest_datetime + timedelta(days=1)):
            current_iteration_date = earliest_datetime.strftime('%Y-%m-%d')

            early_permanent_datetime = self.find_early_perm_date_when_scraped(
                current_iteration_date)

            late_permanent_datetime = self.find_late_perm_date_when_scraped(
                current_iteration_date)

            # For this date that is currently considered temporary (whether by
            # default or because it was previously confirmed to be temporary),
            # check on the permanent date range at the time of the scrape.

            self.update_this_dates_permanent_flag(earliest_datetime,
                                                  early_permanent_datetime,
                                                  late_permanent_datetime)

            earliest_datetime += timedelta(days=1)

    # Check to see if temporary sales can now be scraped as permanent
    def earliest_date_temp_flag(self):
        '''Find earliest date with permanent_flag = False.'''

        session = self.sn()

        query = session.query(
            func.min(Detail.document_recorded).label('early_date')
        ).filter(
            Detail.permanent_flag.is_(False)  # To satisfy PEP8
        ).all()

        for row in query:
            earliest_temp_date = row.early_date

        if earliest_temp_date is not None:
            earliest_temp_datetime = datetime.combine(
                earliest_temp_date, datetime.min.time())

            log.debug(earliest_temp_datetime)

            session.close()

            return earliest_temp_datetime
        else:
            session.close()
            return None

    @staticmethod
    def latest_permanent_datetime():
        '''docstring'''

        pattern = r'%s/' % (Config().DATA_DIR) + \
                  r'most-recent-permanent-date-range/(\d+)-(\d+).html'

        file_path = glob.glob(
            '%s/most-recent-permanent-date-range/*.html' % (
                Config().DATA_DIR))[0]

        global_permanent_range_last_date = re.match(
            pattern, file_path).group(2)

        global_permanent_range_last_datetime = datetime.strptime(
            global_permanent_range_last_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return global_permanent_range_last_datetime

    @staticmethod
    def find_newly_permanent_date_range(start_temp_datetime,
                                        end_permanent_datetime):
        '''docstring'''

        # Find difference between permanent end date and temp start date.
        # If positive or zero, then those two dates form the scrape range.

        date_diff = end_permanent_datetime - start_temp_datetime

        if date_diff.days >= 0:
            # There is at least one day currently labeled as "temporary" that
            # now falls within "permanent" date range.
            dates_to_redo = [
                start_temp_datetime, end_permanent_datetime]
            return dates_to_redo
        else:
            # The "temporary" sales are all still in the temporary date range
            return None

    def check_permanent_status_of_temp_sales(self):
        '''
        Compare latest permanent date range to the range of sales in our
        database that are labeled "temporary." If any of those temporary sales
        now fall within the permanent range, re-scrape and re-initialize.
        '''

        log.debug('Check permanent status of temporary sales')

        # Don't need to know temporary end date or permanent start date.
        # Only need to know temporary start date and permanent end date
        # to determine the dates that were temporary but are now permanent.
        # See find_date_range_to_rescrape_and_initialize() for logic.

        earliest_temp_datetime = self.earliest_date_temp_flag()

        if earliest_temp_datetime is None:  # No temporary sales
            return

        global_permanent_range_last_datetime = self.latest_permanent_datetime()

        dates_to_redo = self.find_newly_permanent_date_range(
            earliest_temp_datetime,
            global_permanent_range_last_datetime)

        if dates_to_redo is not None:
            self.scrape_days(dates_to_redo[0], dates_to_redo[1])

    @staticmethod
    def scrape_days(early_date, late_date):
        '''docstring'''

        early_datetime = datetime.strptime(early_date, '%Y-%m-%d')
        log.debug(early_datetime)
        late_datetime = datetime.strptime(late_date, '%Y-%m-%d')
        log.debug(early_datetime)

        # Scrape those days over again
        log.info('scrape')
        try:
            Scrape(
                initial_date=early_datetime,
                until_date=late_datetime
            ).main()
        except Exception, error:
            log.error(error, exc_info=True)

    @staticmethod
    def delete_using_sql_query(early_date, late_date, table):
        '''docstring'''

        sql = """DELETE FROM {0} USING details
                 WHERE details.document_id = {0}.document_id
                 AND details.document_recorded >= {1}
                 AND details.document_recorded <= {2}
              """.format(table, early_date, late_date)

        return sql

    @staticmethod
    def delete_sql_query(early_date, late_date, table):
        '''docstring'''

        sql = """DELETE FROM {0}
                 WHERE document_recorded >= {1}
                 AND document_recorded <= {2}
              """.format(table, early_date, late_date)

        return sql

    def delete_existing_records(self, early_date, late_date):
        '''Delete existing records for this date. Order matters'''

        print self, early_date, late_date  # todo: uncomment

        return  # todo: uncomment

        # location_sql = self.delete_using_sql_query(
        #     early_date, late_date, 'locations')
        # self.engine.execute(location_sql)

        # vendor_sql = self.delete_using_sql_query(
        #     early_date, late_date, 'vendors')
        # self.engine.execute(vendor_sql)

        # vendee_sql = self.delete_using_sql_query(
        #     early_date, late_date, 'vendees')
        # self.engine.execute(vendee_sql)

        # detail_sql = self.delete_sql_query(
        #     early_date, late_date, 'details')
        # self.engine.execute(detail_sql)

        # cleaned_sql = self.delete_sql_query(
        #     early_date, late_date, 'cleaned')
        # self.engine.execute(cleaned_sql)

    @staticmethod
    def rebuild_days(early_date, late_date):
        '''Scrapes and initializes dates.'''

        print early_date, late_date

        # Build those newly scraped records.
        # This will set perm_flag = True in
        # checkPermanentStatusOfNewSales().
        log.info('doitall')
        # initialize.do_it_all(early_date, late_date)  # todo: uncomment

if __name__ == '__main__':
    pass
