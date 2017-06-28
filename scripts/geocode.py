# -*- coding: utf-8 -*-

"""Use the Google Geocoding API on addresses and update database records."""

import os
import googlemaps

from sqlalchemy import func, cast, Float, update

from www.db import Detail, Location, Neighborhood

import www


class Geocode(object):
    """Geocoding class."""

    def __init__(self, initial_date=None, until_date=None):
        """Prepare Geocode class.

        Creates a connection to the Google Geocoding API.

        Args:
            initial_date (str): The initial date. (default: {None})
            until_date (str): The final date. (default: {None})
        """
        self.initial_date = initial_date
        self.until_date = until_date

        self._gmaps = googlemaps.Client(
            key=os.getenv('GOOGLE_GEOCODING_API_KEY'))

    def update_locations_with_neighborhoods(self):
        """Find neighborhoods and handle if none found."""
        self.neighborhood_found()
        self.no_neighborhood_found()

    def neighborhood_found(self):
        """Use PostGIS to find lat/lng coordinate's neighborhood.

        This relies on a neighborhood shapefile available from data.nola.gov.
        """
        www.SESSION.query(
            Location
        ).filter(
            func.ST_Contains(
                Neighborhood.geom,
                func.ST_SetSRID(
                    func.ST_Point(
                        cast(Location.longitude, Float),
                        cast(Location.latitude, Float)
                    ),
                    4326
                )
            )
        ).update(
            {Location.neighborhood: Neighborhood.gnocdc_lab},
            synchronize_session='fetch'
        )

        www.SESSION.commit()

    def no_neighborhood_found(self):
        """Note that no neighborhood was found."""
        www.SESSION.query(
            Location
        ).filter(
            Location.neighborhood.is_(None)
        ).update(
            {Location.neighborhood: "None"},
            synchronize_session='fetch'
        )

        www.SESSION.commit()

    def get_rows_with_null_rating(self):
        """Query the `locations` table for locations where the rating is null.

        Returns:
            list: The query results.
        """
        query = www.SESSION.query(
            Location.rating,
            Location.document_id,
            Location.street_number,
            Location.address
        ).join(
            Detail
        ).filter(
            Location.rating.is_(None)
        ).filter(
            Detail.document_recorded >= '{}'.format(self.initial_date)
        ).filter(
            Detail.document_recorded <= '{}'.format(self.until_date)
        ).all()

        www.log.debug('Rows with rating is NULL: {}'.format(len(query)))

        www.SESSION.close()

        return query

    def process_google_results(self, results):
        """Extract values from the Google Geocoding API response.

        https://developers.google.com/maps/documentation/geocoding/
            intro#GeocodingResponses

        Args:
            results (list): Google Geocoding API response ("results" only).

        Returns:
            dict: This location's rating, latitude, longitude and ZIP code
        """
        # TODO: Handle more than one returned location in result.
        #   Could compare accuracies and use that to decide which to store.
        loc = results[0]

        values = {
            'latitude': loc['geometry']['location']['lat'],
            'longitude': loc['geometry']['location']['lng'],
            'rating': loc['geometry']['location_type']}

        try:
            values['zip_code'] = loc['address_components'][7]['short_name']
        except Exception:  # TODO: More specific error.
            www.log.info("No zip code.")
            values['zip_code'] = "None"

        return values

    def update_location_row(self, document_id, values):
        """Update the details of this location's records.

        Args:
            document_id (str): This sale's ID.
            values (dict): The values with which to update this record.
        """
        try:
            with www.SESSION.begin_nested():
                u = update(Location)
                u = u.values(values)
                u = u.where(Location.document_id == document_id)
                www.SESSION.execute(u)
                www.SESSION.flush()
        except Exception as error:  # TODO: Handle specific errors.
            www.log.exception(error, exc_info=True)
            www.SESSION.rollback()

        www.SESSION.commit()

    def geocode(self):
        """Update latitude, longitude, rating and ZIP in Locations table."""
        print('\nGeocoding...')

        rows_to_geocode = self.get_rows_with_null_rating()

        for row in rows_to_geocode:
            full_address = "{0} {1}, New Orleans, LA".format(
                row.street_number, row.address)

            result = self._gmaps.geocode(full_address)

            if len(result) == 0:
                www.log.info('No results for: {}'.format(full_address))

                # TODO: Need to also note failure so future geocoding scripts
                #   don't keep trying and failing on the same addresses.
                #   Possibly update Location's `rating` and/or Cleaned's
                #   `location_publish` fields.
                continue

            values = self.process_google_results(result)
            self.update_location_row(row.document_id, values)
