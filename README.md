# New Orleans land records

[http://vault.thelensnola.org/realestate](http://vault.thelensnola.org/realestate)

This app scrapes the latest property sales in New Orleans, stores the records in a database and publishes the results with a map.

[![Build Status](https://travis-ci.org/TheLens/land-records.svg?branch=master)](https://travis-ci.org/TheLens/land-records) [![Documentation Status](https://readthedocs.org/projects/land-records/badge/?version=latest)](https://readthedocs.org/projects/land-records/?badge=latest) [![Coverage Status](https://coveralls.io/repos/TheLens/land-records/badge.svg?branch=master)](https://coveralls.io/r/TheLens/land-records?branch=master)

Documentation: https://readthedocs.org/projects/land-records/

Issues: https://github.com/TheLens/land-records/issues

Tests: https://travis-ci.org/TheLens/land-records

Testing coverage: https://coveralls.io/r/TheLens/land-records

#### Dependencies

* Python 2.7
* PostgreSQL 9.3+
* PostGIS 2.1
* Flask
* SQLAlchemy

#### Setup

Not yet sure if this setup will work or not.

`git clone https://github.com/TheLens/land-records.git`

`cd` into the `land-records` directory.

`pip install -r requirements.txt`

Make changes to `landrecords/config.py` and keep private.

`python scripts/delete_db.py`  # If already have database. Can ignore if not.

`psql landrecords < backups/landrecords.sql`  # For now, only available to The
Lens employees. Access on the server.

#### Daily scripts

This will scrape, build, geocode, clean and publish the previous day's sales. 

`python landrecords/lib/scrape.py`

`python scripts/initialize.py`

#### Environment variables

Create two environment variables, and do so both locally and on the server:

```bash
export SERVER_ENGINE='postgresql://myuser:mypass@localhost/landrecords'

export SERVER_CONNECTION='dbname=landrecords user=myuser password=mypass'

export LRD_USERNAME='myuser'

export LRD_PASSWORD='mypass'

export GOOGLE_API_KEY='mykey'

# Twitter

export APP_KEY='myappkey' # Customer Key

export APP_SECRET='myappsecret' # Customer secret

export OAUTH_TOKEN='myoauthtoken'

export OAUTH_TOKEN_SECRET='myoauthtokensecret'

# Dashboard

export DASHBOARD_USERNAME='myuser'

export DASHBOARD_PASSWORD='mypass'

# Gmail

export GMAIL_USERNAME='myemail'

export GMAIL_PASSWORD='mypass'
```
