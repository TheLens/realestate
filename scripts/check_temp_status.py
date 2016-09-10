# -*- coding: utf-8 -*-

"""
Needs more work.

The Land Records Division's remote subscription service has a permanent date
range and temporary date range for its records. Sales are indexed, marked as
temporary and then reviewed a second time to become permanent. This means
that there is usually a lag of a day or two between its initial, temporary
record and the permanent version. Lately, the records have not been fully
entered on the first pass, so the records really can't be trusted until they
are labeled as permanent.

When sales first come in, they are assumed to be temporary (`permanent_flag`
is False) in `cleaned` table. `check_temp_status.py` checks when the sales
were scraped compared to the Land Records permanent date range at the time of
the scrape. If the date of a scrape falls within the permanent date range,
those records are updated to `permanent_flag` is True in `cleaned`. Otherwise,
it stays temporary.

This is checked each day. Once a date eventually falls within the permanent
date range, the day's records are re-scraped, built, geocoded, cleaned and
published, with `permanent_flag` set as True.
"""

import os
import re
import glob

from datetime import datetime, timedelta
from sqlalchemy import func

from www import log, PROJECT_DIR, SESSION
from www.db import Cleaned, Detail
from scripts.delete_dates import DeleteDates
from scripts.scrape import Scrape


class CheckTemp(object):
    """Check on the temporary/permanent status of sales."""

    def __init__(self):
        """Establish connections to the database."""
        pass

    def earliest_date_no_flag(self):
        """Find the earliest date_recorded without permanent_flag set."""
        query = SESSION.query(
            func.min(Detail.document_recorded).label('early_date')
        ).filter(
            Detail.permanent_flag.is_(None)  # To satisfy PEP8
        ).all()

        for row in query:
            earliest_none_date = row.early_date

        earliest_none_datetime = datetime.combine(
            earliest_none_date, datetime.min.time())

        SESSION.close()

        return earliest_none_datetime

    def latest_date_no_flag(self):
        """Finds the latest date_recorded without permanent_flag set."""
        query = SESSION.query(
            func.max(Detail.document_recorded).label('late_date')
        ).filter(
            Detail.permanent_flag.is_(None)
        ).all()

        for row in query:
            latest_none_date = row.late_date

        latest_none_datetime = datetime.combine(
            latest_none_date, datetime.min.time())

        SESSION.close()

        return latest_none_datetime

    @staticmethod
    def find_early_perm_date_when_scraped(current_iteration_date):
        """Finds the earliest date_recorded with permanent_flag."""
        pattern = (
            r'%s/data/raw/' % PROJECT_DIR +
            r'%s/' % current_iteration_date +
            r'permanent-date-range-when-scraped_(\d+)-(\d+).html')

        file_path = glob.glob(
            '%s/data/raw/%s/permanent-date-range-when-scraped_*.html' % (
                PROJECT_DIR, current_iteration_date))[0]

        early_permanent_date = re.match(pattern, file_path).group(1)

        early_permanent_datetime = datetime.strptime(
            early_permanent_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return early_permanent_datetime

    @staticmethod
    def find_late_perm_date_when_scraped(current_iteration_date):
        """TODO."""
        pattern = (
            r'%s/data/raw/' % PROJECT_DIR +
            r'%s/' % current_iteration_date +
            r'permanent-date-range-when-scraped_(\d+)-(\d+).html')

        file_path = glob.glob(
            '%s/data/raw/%s/permanent-date-range-when-scraped_*.html' % (
                PROJECT_DIR, current_iteration_date))[0]

        late_permanent_date = re.match(pattern, file_path).group(2)

        late_permanent_datetime = datetime.strptime(
            late_permanent_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return late_permanent_datetime

    def update_this_dates_permanent_flag(self,
                                         current_datetime,
                                         early_permanent_datetime,
                                         late_permanent_datetime):
        """TODO."""
        cond = (early_permanent_datetime <= current_datetime and
                current_datetime <= late_permanent_datetime)

        if cond:
            SESSION.query(
                Detail
            ).filter(
                Detail.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": True})

            SESSION.query(
                Cleaned
            ).filter(
                Cleaned.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": True})
            SESSION.commit()
        else:
            SESSION.query(
                Detail
            ).filter(
                Detail.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": False})

            SESSION.query(
                Cleaned
            ).filter(
                Cleaned.document_recorded == '%s' % current_datetime
            ).update({"permanent_flag": False})
            SESSION.commit()

    def check_permanent_status_of_new_sales(self):
        """
        Examine first-time sales and assign True or False for permanent_flag.
        """
        log.debug('Check permanent status of new sales')

        # TODO: Is this function called for sales that have already been given
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
        """Find earliest date with permanent_flag = False."""
        query = SESSION.query(
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

            SESSION.close()

            return earliest_temp_datetime
        else:
            SESSION.close()
            return None

    @staticmethod
    def latest_permanent_datetime():
        """TODO."""
        pattern = r'%s/data/' % (PROJECT_DIR) + \
                  r'most-recent-permanent-date-range_(\d+)-(\d+).html'

        file_path = glob.glob(
            '%s/data/most-recent-permanent-date-range_*.html' % (
                PROJECT_DIR))[0]

        global_permanent_range_last_date = re.match(
            pattern, file_path).group(2)

        global_permanent_range_last_datetime = datetime.strptime(
            global_permanent_range_last_date,
            '%m%d%Y')  # ).strftime('%Y-%m-%d')

        return global_permanent_range_last_datetime

    @staticmethod
    def find_newly_permanent_date_range(start_temp_datetime,
                                        end_permanent_datetime):
        """TODO."""
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
        """
        Compare latest permanent date range to the range of sales in our
        database that are labeled "temporary." If any of those temporary sales
        now fall within the permanent range, re-scrape and re-initialize.
        """
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
        """docstring"""

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
        except Exception as error:
            log.error(error, exc_info=True)

    def delete_existing_records(self, early_date, late_date):
        """Delete existing records for this date. Order matters"""

        DeleteDates(
            initial_date=early_date,
            until_date=late_date
        ).main()

    @staticmethod
    def rebuild_days(early_date, late_date):
        """Scrapes and initializes dates."""

        print(early_date, late_date)

        # Build those newly scraped records.
        # This will set perm_flag = True in
        # checkPermanentStatusOfNewSales().
        log.info('doitall')
        # initialize.do_it_all(early_date, late_date)  # todo: uncomment

if __name__ == '__main__':
    pass
