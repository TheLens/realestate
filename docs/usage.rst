.. _usage:

Daily usage
^^^^^^^^^^^

Every day, these two files are run to scrape, clean, geocode and store the previous day's property sales. These two lines are summarized in ``scripts/main.sh``, which is run on a cron job every night.

.. code-block:: bash

    python scripts/scrape.py
    python scripts/initialize.py

Periodic usage
^^^^^^^^^^^^^^

Occasionally, due to bugs, password expiration or changes in the Land Records Division website, you will need to scrape and prepare data older than the previous day. You can specify the date range for either command by using command-line arguments.

.. code-block:: bash

    python scripts/scrape.py 2016-05-01 2016-05-05      # <start_date> <end_date> (YYYY-MM-DD)
    python scripts/initialize.py 2016-05-01 2016-05-05  # <start_date> <end_date> (YYYY-MM-DD)
