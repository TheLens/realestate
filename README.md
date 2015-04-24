# New Orleans land records

[http://vault.thelensnola.org/realestate](http://vault.thelensnola.org/realestate)

This app scrapes the latest property sales in New Orleans, stores the records in a database and publishes the results with a map.

Dependencies:

* Python 2.7
* PostgreSQL 9.3+
* PostGIS 2.1
* Flask
* SQLAlchemy

### Database setup

###### `delete_db.py`

Makes backup of dashboard's manual adjustments before dropping all tables (minus PostGIS' `spatial_ref_sys` table) and running `VACUUM`.

###### `make_db.py`

Creates the database if not yet created, creates tables, imports geographic data and creates spatial indexes. It makes use of `db.py`.

###### `db.py`

Contains the SQLAlchemy table classes.

### Scraping

####### `scrape.py`

The daily scraper that checks for the previous day's sales and saves the HTML for those records. It uses [Selenium](https://github.com/SeleniumHQ/selenium/tree/master/py) and [PhantomJS](http://phantomjs.org/). This also makes a note of when each date was scraped and what the Land Records Division's permanent date range was at the time of that scrape (see `check_temp_status.py` for details).

### Adding records to database

###### `initialize.py`

It calls on `get_dates.py` to determine which dates have not yet been added to the database, then performs an ordered list of commands using the following files:

###### `parse.py` 

This contains all of the logic for parsing the different pages for each sale and makes use of the [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) library. Returns either a dict of list of dicts.

###### `build.py`

Receives the parsed data and commits it to the database.

###### `geocode.py`

Uses the Google Geocoding API (we used to use the PostGIS Geocoder) to geocode addresses, resulting in ZIP codes, latitude, longitude and an accuracy rating. A rating of "ROOFTOP" or "RANGE_INTERPOLATED" is good enough for publication.

This also includes a method that uses PostGIS to find the neighborhood in which each sale occurred, working with a neighborhood shapefile available from [data.nola.gov](http://data.nola.gov).

###### `clean.py`

Has two classes: `Join` and `Clean`.

`Join` joins each of the four sale tables (details, vendors, vendees and locations) on their document ID and commits each sale to the `cleaned` table.

`Clean` has methods to check for errors, mistakes and style issues. It utilizes `libraries.py`, a collection of items to check for.  

###### `publish.py`

Runs checks against the `cleaned` table to make sure information is suitable for publication. Checks for things such as lat/long coordinates outside of New Orleans, sale amounts that are questionably high or low and whether the sale has a date or not.

Sales can fail for detail data (`detail_publish` field) or location data (`location_publish`). If a sale fails meet all criteria for each field, it will be set as False. Sales will only appear in the table if `detail_publish` is True but `location_publish` is False. If both are False, then sale won't appear at all.

###### `check_temp_status.py`

Needs more work.

The Land Records Division's remote subscription service has a permanent date range and temporary date range for its records. Sales are indexed, marked as temporary and then reviewed a second time to become permanent. This means that there is usually a lag of a day or two between its initial, temporary record and the permanent version. Lately, the records have not been fully entered on the first pass, so the records really can't be trusted until they are labeled as permanent.

When sales first come in, they are assumed to be temporary (`permanent_flag` is False) in `cleaned` table. `check_temp_status.py` checks when the sales were scraped compared to the Land Records permanent date range at the time of the scrape. If the date of a scrape falls within the permanent date range, those records are updated to `permanent_flag` is True in `cleaned`. Otherwise, it stays temporary.

This is checked each day. Once a date eventually falls within the permanent date range, the day's records are re-scraped, built, geocoded, cleaned and published, with `permanent_flag` set as True.

###### `build_assessor_urls.py`

Needs more work.

Forms the assessor URLs by performing a series of checks and conversions.

###### `check_assessor_urls.py`

Needs more work.

Checks if URL generated for [Orleans Parish Assessor's Office](http://nolaassessor.com/) database successfully finds sale.

###### `dashboard_sync.py`

Needs more work.

Keeps `cleaned` and `dashboard` in sync.

### Presentation

###### `app.py`

Routes requests and returns responses, including error pages.

###### `models.py`

Gets the data.

###### `views.py`

Renders the data.

###### `results_language.py`

Creates the results language on the /search page, such as, "10 sales found for keyword 'LLC' in the French Quarter neighborhood where the price was between $10,000 and $200,000 between Feb. 18, 2014, and Feb. 20, 2014.'

### Logging

The universal logger is defined in `__init__.py` in the root of the `landrecords` module. Then it can be accessed by any module like so:

`log.debug('Description')`

`log.info('Description')`

`log.error('Description')`

`log.exception(error, exc_info=True)`

You can change the logging level to your choosing. The default is DEBUG.

### Email alerts

###### `mail.py`

A universal mail-sender, with methods for plain text, HTML and attachments.

###### `email_template.py`

The template for the summary email. Draws on `stat_analysis.py` for common, interesting queries.

###### `stat_analysis.py`

Common queries like highest sale amount in a given date range, total number of sales, etc.

### Twitter

###### `twitter.py`

Takes message and attachment, forms tweet and sends tweet using Twython. Performs checks on number of characters before sending to prevent an #embarrassing moment.

###### `form_tweet.py`

Does analysis and uses results to craft language of the tweet. Also takes screenshot of that particular sale's map using `screen.js` (PhantomJS).

### Misc.

###### `libraries.py`

A collection of useful data, such as abbreviations, acronyms, neighborhood names and noteworthy names (needs more work).

###### `utils.py`

A collection of usefull utility functions, such as converting date formats and converting integer dollar amounts to string currency formats.

###### `delete_dates.py`

Accpts command line parameters for quick deletion of all records for a given date or date range. Meant for quicker testing.

```bash
python delete_dates.py '2014-02-18' # Deletes one day
python delete_dates.py '2014-02-18' '2014-02-19' # Deletes range
```

###### `webhook.py`

Needs more work.

Keeps S3 in sync with Github repo. Might eventually scrap this in favor of [Travis CI](https://travis-ci.org/).

### Database tables

#### `cleaned`

The "cleaned" data that is ready for the public.

* geom
* amount
* document_date
* document_recorded
* address
* location_info
* sellers
* buyers
* instrument_no
* latitude
* longitude
* zip_code
* detail_publish
* location_publish
* assessor_publish
* permanent_flag
* neighborhood

#### `details`

* document_id
* document_type
* instrument_no
* multi_seq
* min_
* cin
* book_type
* book
* page
* document_date
* document_recorded
* amount
* status
* prior_mortgage_doc_type
* prior_conveyance_doc_type
* cancel_status
* remarks
* no_pages_in_image
* image
* detail_publish
* permanent_flag

#### `locations`

* id
  * Serial, primary key 
* document_id
  * String, foreign key is details.document_id (ON DELETE CASCADE)
* subdivision
* condo
* district
* square
* lot
* cancel_status
* street_number
* address
* unit
* weeks
* cancel_stat
* freeform_legal
* latitude
  * Float
* longitude
  * Float
* rating
* zip_code
* neighborhood
* location_publish
  * Boolean

#### `vendors`

* id
* document_id
  * String, foreign key is details.document_id (ON DELETE CASCADE)
* vendor_blank
* vendor_p_c
* vendor_lastname
* vendor_firstname
* vendor_relator
* vendor_cancel_status

#### `vendees`

* id
* document_id
  * String, foreign key is details.document_id (ON DELETE CASCADE)
* vendee_blank
* vendee_p_c
* vendee_lastname
* vendee_firstname
* vendee_relator
* vendee_cancel_status

#### `neighborhoods`

* gid
* objectid
* gnocdc_lab
* lup_lab
* neigh_id
* shape_leng
* shape_area
* geom