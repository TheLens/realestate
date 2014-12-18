http://vault.thelensnola.org/realestate

# Basics

Uses Postgres 9.3, Python 2.7, Flask, SQL Alchemy and Beautiful Soup 4.

`scrape.py`

The daily scraper that pulls HTML for records from the previous day.

`initialize.py`

Creates the database `landrecords`, parses the HTML downloaded from `scrape.py` and inserts the records into `landrecords`.

`app.py`

Launches the web page at `index.html`. Uses `Cleanup.py` to make data more presentable in the HTML table and ready for plotting onto the map.