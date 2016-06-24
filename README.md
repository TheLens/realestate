# New Orleans real estate

[https://vault.thelensnola.org/realestate](https://vault.thelensnola.org/realestate)

This app scrapes the latest property sales in New Orleans, stores the records in a database and publishes the results with a map.

[![Build Status](https://travis-ci.org/TheLens/realestate.svg?branch=master)](https://travis-ci.org/TheLens/realestate) [![Coverage Status](https://coveralls.io/repos/TheLens/realestate/badge.svg?branch=master)](https://coveralls.io/r/TheLens/realestate?branch=master)

- Issues: https://github.com/TheLens/realestate/issues
- Tests: https://travis-ci.org/TheLens/realestate
- Testing coverage: https://coveralls.io/r/TheLens/realestate

#### Dependencies

* Python 2.7
* PostgreSQL 9.3+
* PostGIS 2.1
* Flask
* SQLAlchemy
* Virtualenvwrapper/virtualenv

#### Daily scripts

Every day, these two commands are run to scrape and then build, geocode, clean and publish the previous day's sales. These are summarized in `scripts/main.sh`, which is run on a cron job every night.

```bash
python realestate/lib/scrape.py
python scripts/initialize.py
```

Occasionally, due to bugs or password expiration, you will need to scrape and build beyond the previous day. You can specify the date range for both commands by using command-line arguments.

```bash
# <starting_date> <ending_date>
python realestate/lib/scrape.py 2016-05-01 2016-05-05
python scripts/initialize.py 2016-05-01 2016-05-05
```

There is also a cron task to run `scripts/backups.sh`, which creates a date-stamped database backup on the server and then copies the file to S3. This runs every night.

#### Environment variables

Create environment variables in `~/.virtualenvs/realestate/bin/postactivate` locally. Do the same at `/home/ubuntu/.virtualenvs/realestate/bin/postactivate` on the server. You will need to include two lines in the server's postactivate file so that Upstart can find and use the variables.

```bash
REAL_ESTATE_LRD_USERNAME='MyLandRecordsDivisionUsername'
REAL_ESTATE_LRD_PASSWORD='MyLandRecordsDivisionPassword'
REAL_ESTATE_DATABASE_USERNAME='MyDatabaseUsername'
REAL_ESTATE_DATABASE_PASSWORD='MyDatabasePassword'

export REAL_ESTATE_LRD_USERNAME='MyLandRecordsDivisionUsername'
export REAL_ESTATE_LRD_PASSWORD='MyLandRecordsDivisionPassword'
export REAL_ESTATE_DATABASE_USERNAME='MyDatabaseUsername'
export REAL_ESTATE_DATABASE_PASSWORD='MyDatabasePassword'
```
