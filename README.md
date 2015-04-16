# New Orleans land records

[http://vault.thelensnola.org/realestate](http://vault.thelensnola.org/realestate)

This app scrapes the latest property sales in New Orleans, stores the records in a database and publishes the results.

Dependencies:

* Python 2.7
* PostgreSQL 9.3
* PostGIS 2.1
* Flask
* SQLAlchemy

### Setup

#### `delete_db.py`

In case you already have this database, delete it. This has a built-in function to make a backup of the dashboard adjustments before deleting the table.

#### `make_db.py`

Creates the tables, imports geographic data and creates spatial indexes. It makes use of `db.py`.

#### `db.py`

Contains the SQLAlchemy table classes.

### Scraping

##### `scrape.py`

The daily scraper that checks for the previous day's sales and saves the HTML for those records. It uses [Selenium](https://github.com/SeleniumHQ/selenium/tree/master/py) and [PhantomJS](http://phantomjs.org/). This also makes a note of when each date was scraped and what the Land Records Division's permanent date range was at the time of that scrape (see `check_temp_status.py` for details).

### Adding records to database

`initialize.py` is just an ordered list of commands, using the following files.

#### `parse.py` 

This contains all of the logic for parsing the different pages for each sale and makes use of the [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) library. Returns either a dict of list of dicts.

#### `build.py`

Receives the parsed data and commits it to the database.

#### `geocode.py`

Uses PostGIS' Geocoder feature to geocode addresses, resulting in ZIP codes, latitude, longitude and an accuracy rating. Any rating <= 3 is good enough for publication.

This also includes a method that uses PostGIS to find the neighborhood in which each sale occurred.

#### `clean.py`

Has two classes: `Join()` and `Clean()`.

`Join()` joins each of the four sale tables (details, vendors, vendees and locations) on their document ID and commits each sale to the `cleaned` table.

`Clean()` has methods to check for errors, mistakes and style issues. It utilizes `libraries.py`, a collection of items to check for.  

### `publish.py`

Runs checks against the `cleaned` table to make sure information is suitable for publication. Checks for things such as lat/long coordinates outside of New Orleans, sale amounts that are questionably high or low and whether the sale has a date or not.

Sales can fail for detail data (`detail_publish` field) or location data (`location_publish`). If a sale fails meet all criteria, it will not appear on the map and/or in the table.

#### `check_temp_status.py`

The Land Records Division's remote subscription service has a permanent date range and temporary date range for its records. Sales are indexed, marked as temporary and then reviewed a second time to become permanent. This means that there is usually a lag of a day or two between its initial, temporary record and the permanent version. There doesn't seem to be a difference, but the records could theoretically change in their first few days on the site.

When sales first come in, they are assumed to be temporary (`permanent_flag` is False) in `cleaned` table. `check_temp_status.py` checks when the sales were scraped compared to the Land Records permanent date range at the time of the scrape. If the date of a scrape falls within the permanent date range, those records are updated to `permanent_flag` is True in `cleaned`. Otherwise, it stays temporary.

This is checked each day. Once a date eventually falls within the permanent date range, the day's records are re-scraped, built, geocoded, cleaned and published, with `permanent_flag` is True.

#### `check_assessor_urls.py`

Checks if URL generated for [Orleans Parish Assessor's Office](http://nolaassessor.com/) database successfully finds sale.

#### `dashboard_sync.py`

Keeps `cleaned` and `dashboard` in sync.

### Presentation

#### `app.py`

Routes requests and returns responses.

#### `models.py`

Gets the data.

#### `views.py`

Renders the data.

### Misc.

#### `log.py`

The universal logging class that can be imported into any script like so: `log = Log('initialize').initialize_log()`. Then it can be accessed throughout the script like so:

`log.debug('Description')`
`log.info('Description')`
`log.error('Description')`

You can change the logging level to your choosing. The default is DEBUG.

#### `mail.py`

A universal mail-sender, with methods for plain text, HTML and attachments.