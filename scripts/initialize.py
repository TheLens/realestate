# -*- coding: utf-8 -*-

"""
Build, geocode, clean and publish records to the cleaned table.

Use command-line arguments to specify a date range or use yesterday as default.

Usage:
    initialize.py
    initialize.py <single_date>
    initialize.py <early_date> <late_date>

Options:
    -h, --help  Show help screen.
    --version   Show version number.

Dates are in the format YYYY-MM-DD. Ex. 2016-12-31
"""

from datetime import datetime
from docopt import docopt

from scripts.build import Build
from scripts.clean import Clean
from scripts.geocode import Geocode
from scripts.get_dates import GetDates
# from scripts.mail import Mail
from scripts.publish import Publish
# from scripts.check_temp_status import CheckTemp
# from scripts.email_template import EmailTemplate
from www import log  # LOG_DIR, OPENING_DAY


class BadDateRangeError(Exception):
    """Error for when date range is backward."""

    pass


def initialize(initial_date=None, until_date=None):
    """Build, geocode, clean and publish records to the cleaned table."""
    if initial_date is None or until_date is None:
        date_range = GetDates().get_date_range()
        initial_date = date_range['initial_date']
        until_date = date_range['until_date']

    log.debug('self.initial_date: {}'.format(initial_date))
    log.debug('self.until_date: {}'.format(until_date))

    # try:  # TODO
    Build(initial_date=initial_date, until_date=until_date).build_all()

    # except Exception as error:
    #     log.exception(error, exc_info=True)

    # Geocoding takes over an hour
    Geocode(initial_date=initial_date, until_date=until_date).geocode()
    Geocode().update_locations_with_neighborhoods()

    # try:  # TODO
    Publish(initial_date=initial_date, until_date=until_date).main()
    # except Exception as error:
    #     log.exception(error, exc_info=True)

    # try:  # TODO
    Clean(initial_date=initial_date, until_date=until_date).main()
    # except Exception as error:
    #     log.exception(error, exc_info=True)

    Clean(
        initial_date=initial_date,
        until_date=until_date
    ).update_cleaned_geom()

    # TODO: Send email summary

    # CheckTemp(
    #     initial_date=self.initial_date,
    #     until_date=self.until_date
    # ).check_permanent_status_of_new_sales()

    # CheckTemp(
    #     initial_date=self.initial_date,
    #     until_date=self.until_date
    # ).check_permanent_status_of_temp_sales()


def cli_has_errors(arguments):
    """Check for any CLI parsing errors."""
    all_arguments = (
        arguments['<single_date>'] is not None and
        arguments['<early_date>'] is not None and
        arguments['<late_date>'] is not None)

    if all_arguments:
        # print("Must use single date or date range, but not both.")
        return True

    single_and_other_arguments = (
        (
            arguments['<single_date>'] is not None and
            arguments['<early_date>'] is not None
        ) or
        (
            arguments['<single_date>'] is not None and
            arguments['<late_date>'] is not None
        ))

    if single_and_other_arguments:
        # print("Cannot use a single date and a date range bound.")
        return True

    one_date_bound_only = (
        (
            arguments['<early_date>'] is not None and
            arguments['<late_date>'] is None
        ) or
        (
            arguments['<early_date>'] is None and
            arguments['<late_date>'] is not None
        ))

    if one_date_bound_only:
        # print("Must pick both ends of a date range bound.")
        return True

    # All good
    return False


def cli(arguments):
    """Parse command-line arguments."""
    # Catch any missed errors
    if cli_has_errors(arguments):
        return

    if arguments['<single_date>']:  # Single date
        early_date = arguments['<single_date>']
        late_date = arguments['<single_date>']

        log.info('Initializing single date: {}.'.format(early_date))
    elif arguments['<early_date>'] and arguments['<late_date>']:  # Date range
        early_date = arguments['<early_date>']
        late_date = arguments['<late_date>']

        log.info('Initializing date range: {0} to {1}.'.format(
            early_date, late_date))
    else:  # No dates provided
        log.info('Initializing all dates that need it.')

        initialize()  # Default: initialize all in need.
        return

    # Check for errors
    early_datetime = datetime.strptime(early_date, "%Y-%m-%d")
    late_datetime = datetime.strptime(late_date, "%Y-%m-%d")

    if early_datetime > late_datetime:
        raise BadDateRangeError("The date range does not make sense.")

    initialize(initial_date=early_date, until_date=late_date)


if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.0.1")
    cli(arguments)
