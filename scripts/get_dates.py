# -*- coding: utf-8 -*-

"""Get date range for initialize script."""

from datetime import timedelta

from www.db import Detail
from www import log, YESTERDAY_DATE, OPENING_DATE, SESSION


class GetDates(object):
    """Get date range for initialize script."""

    def __init__(self):
        """Initialize self variables and establish connection to database."""
        pass

    def get_date_range(self):
        """Check which dates have not been entered into the database yet."""
        existing_until_date = self.get_existing_until_date()

        # log.debug(type(existing_until_date))
        # log.debug(existing_until_date)

        # Check if all dates already added
        yesterday_date = (YESTERDAY_DATE)

        if existing_until_date == yesterday_date:
            raise ValueError("All dates already added to database.")

        initial_date = existing_until_date + timedelta(days=1)
        until_date = YESTERDAY_DATE

        initial_date = initial_date.strftime('%Y-%m-%d')
        until_date = until_date.strftime('%Y-%m-%d')

        return_dict = {}
        return_dict['initial_date'] = initial_date
        return_dict['until_date'] = until_date

        return return_dict

    def get_existing_until_date(self):
        """TODO: Docstring."""
        query_until_date = SESSION.query(
            Detail.document_recorded
        ).order_by(
            Detail.document_recorded.desc()
        ).limit(1).all()

        # Check if any records at all
        if len(query_until_date) == 0:
            # Make it so initialized date range will start from beginning.
            until_date = OPENING_DATE - timedelta(days=1)
            # log.debug(until_date)
            # log.debug(type(until_date))
        else:
            log.debug(len(query_until_date))
            for row in query_until_date:
                # TODO: will this fail w/o .one()?
                until_date = row.document_recorded

            # log.debug(until_date)
            # log.debug(type(until_date))

        # log.debug(until_date)

        SESSION.close()

        return until_date

if __name__ == '__main__':
    pass
