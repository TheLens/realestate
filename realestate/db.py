# -*- coding: utf-8 -*-

"""
Defines tables in `landrecords` database using SQLAlchemy.

The `landrecords` database consists of eight tables, four of which come from \
the raw HTML data (`details`, `vendors`, `vendees` and `locations`). \
`neighborhoods` comes from the city's shapefile on data.nola.gov. `dashboard` \
is a private admin dashboard. `spatial_ref_sys` is part of the PostGIS \
extension. The cleaned and crunched data in the original four tables feed \
into the `cleaned` table, which is the only public-facing table.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Numeric,
    Date,
    Float,
    ForeignKey,
    Boolean
)
from geoalchemy2 import Geometry

Base = declarative_base()


class Location(Base):
    """
    Fields for the `locations` table.

    :param gid: Integer. Primary key ID
    :param document_id: String. The unique ID on the Land Records \
    Division's website.
    :param street_number: String. Street number. Ex. '123', for *123* MAIN ST.
    :param address: String. The street name and type. Ex. 'MAIN ST', for 123 \
    *MAIN ST*.
    :param district: String. The municipal district.
    :param square: String. The property's square (block) in the assessor's \
    database.
    :param lot: String. The property's lot number in the assessor's database.
    :param unit: String. The individual unit(s) within a particular lot.
    :param subdivision: String. The subdivision of the property.
    :param condo: String. The condominium the property is a part of.
    :param weeks: String. The number of weeks per year the property was sold \
    for.
    :param cancel_status_lot: String. The cancel status of the lot (first in \
    locations table).
    :param cancel_status_unit: String. The cancel status of the unit (second \
    in locations table).
    :param freeform_legal: String. Last field in locations table.
    :param latitude: Float. Not part of raw data. Determined via geocoding.
    :param longitude: Float. Not part of raw data. Determined via geocoding.
    :param rating: String. Not part of raw data. Determined via geocoding.
    :param zip_code: String. Not part of raw data. Determined via geocoding.
    :param neighborhood: String. Not part of raw data. Determined via PostGIS \
    query between lat/lng and the city's neighborhood shapefile.
    :param location_publish: Boolean. True allows to plot on map, False does \
    not plot on map. True/False determined by checks in publish.py.
    """

    __tablename__ = 'locations'

    gid = Column(Integer, primary_key=True)
    document_id = Column(
        String,
        ForeignKey("details.document_id", ondelete="CASCADE"),
        nullable=False
    )
    street_number = Column(String)
    address = Column(String)
    district = Column(String)
    square = Column(String)
    lot = Column(String)
    unit = Column(String)
    subdivision = Column(String)
    condo = Column(String)
    weeks = Column(String)
    cancel_status_lot = Column(String)
    cancel_status_unit = Column(String)
    freeform_legal = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(String)
    zip_code = Column(String)
    neighborhood = Column(String)
    location_publish = Column(Boolean, nullable=True)

    def __init__(self,
                 gid,
                 subdivision,
                 condo,
                 district,
                 square,
                 lot,
                 cancel_status_lot,
                 street_number,
                 address,
                 unit,
                 weeks,
                 cancel_status_unit,
                 freeform_legal,
                 document_id,
                 latitude,
                 longitude,
                 rating,
                 zip_code,
                 neighborhood,
                 location_publish):
        self.gid = gid,
        self.subdivision = subdivision,
        self.condo = condo,
        self.district = district,
        self.square = square,
        self.lot = lot,
        self.cancel_status_lot = cancel_status_lot,
        self.street_number = street_number,
        self.address = address,
        self.unit = unit,
        self.weeks = weeks,
        self.cancel_status_unit = cancel_status_unit,
        self.freeform_legal = freeform_legal,
        self.document_id = document_id,
        self.latitude = latitude,
        self.longitude = longitude,
        self.rating = rating,
        self.zip_code = zip_code,
        self.neighborhood = neighborhood,
        self.location_publish = location_publish

    def __repr__(self):
        representation = (
            "<Location(" +
            "gid='{0}', " +
            "subdivision='{1}', " +
            "condo='{2}', " +
            "district='{3}', " +
            "square='{4}', " +
            "lot='{5}', " +
            "cancel_status_lot='{6}', " +
            "street_number='{7}', " +
            "address='{8}', " +
            "unit='{9}', " +
            "weeks='{10}', " +
            "cancel_status_unit='{11}', " +
            "freeform_legal='{12}', " +
            "document_id='{13}', " +
            "latitude='{15}', " +
            "longitude='{16}', " +
            "rating='{17}', " +
            "zip_code='{18}', " +
            "neighborhood='{19}', " +
            "location_publish='{20}', " +
            ")>"
        ).format(
            self.gid,
            self.subdivision,
            self.condo,
            self.district,
            self.square,
            self.lot,
            self.cancel_status_lot,
            self.street_number,
            self.address,
            self.unit,
            self.weeks,
            self.cancel_status_unit,
            self.freeform_legal,
            self.document_id,
            self.latitude,
            self.longitude,
            self.rating,
            self.zip_code,
            self.neighborhood,
            self.location_publish
        )

        return representation

    def __str__(self):
        string = "Location table"

        return string


class Cleaned(Base):
    """
    Fields for the `cleaned` table.

    :param instrument_no: String. Primary key ID.
    :param amount: BigInteger. The sale amount.
    :param document_date: Date. The date the property was sold.
    :param document_recorded: Date. The date the property sale was recorded.
    :param address: String. The full address of the property, \
    including the street number and the address. Ex. 123 Main St.
    :param location_info: String. All of the extra location information, such \
    as the lot, unit, condo, etc.
    :param sellers: String. The person, people or companies that sold the \
    property, AKA the "vendors."
    :param buyers: String. The person, people or companies that bought the \
    property, AKA the "vendees."
    :param latitude: Float. Determined from geocoding.
    :param longitude: Float. Determined from geocoding.
    :param rating: String. Determined from geocoding.
    :param zip_code: String. Determined from geocoding.
    :param neighborhood: String. Determined via PostGIS query between lat/lng \
    and the city's neighborhood shapefile.
    :param detail_publish: Boolean. True allows to publish at all, False does \
    not publish in table or on map. True/False determined by checks in \
    publish.py.
    :param location_publish: Boolean. True allows to plot on map, False does \
    not plot on map. True/False determined by checks in publish.py.
    :param assessor_publish: Boolean. True allows link to assessor's website, \
    False does not. True/False determined by checks in check_assessor.py.
    :param permanent_flag: Boolean. True denotes permanent status, False \
    denotes temporary status. True/False (permanent/temporary) is determined \
    by the permanent range found during scraping.
    :param geom: Geometry (Point). A spatial index for spatial queries.
    """

    __tablename__ = 'cleaned'

    instrument_no = Column(String, primary_key=True, index=True)
    amount = Column(BigInteger)
    document_date = Column(Date, nullable=True)
    document_recorded = Column(Date, nullable=True)
    address = Column(String, index=True)
    location_info = Column(String, index=True)
    sellers = Column(String, index=True)
    buyers = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    zip_code = Column(String, index=True)
    detail_publish = Column(Boolean, nullable=True)
    location_publish = Column(Boolean, nullable=True)
    assessor_publish = Column(Boolean, nullable=True)
    permanent_flag = Column(Boolean, nullable=True)
    neighborhood = Column(String, index=True)
    geom = Column(Geometry(
        geometry_type='POINT',
        srid=4326,
        spatial_index=True
    ))

    def __init__(self,
                 geom,
                 amount,
                 document_date,
                 document_recorded,
                 address,
                 location_info,
                 sellers,
                 buyers,
                 instrument_no,
                 latitude,
                 longitude,
                 zip_code,
                 detail_publish,
                 location_publish,
                 assessor_publish,
                 permanent_flag,
                 neighborhood):
        self.geom = geom,
        self.amount = amount,
        self.document_date = document_date,
        self.document_recorded = document_recorded,
        self.location = address,
        self.location_info = location_info,
        self.sellers = sellers,
        self.buyers = buyers,
        self.instrument_no = instrument_no,
        self.latitude = latitude,
        self.longitude = longitude,
        self.zip_code = zip_code,
        self.detail_publish = detail_publish,
        self.location_publish = location_publish,
        self.assessor_publish = assessor_publish,
        self.permanent_flag = permanent_flag
        self.neighborhood = neighborhood

    def __repr__(self):
        return """
            <Cleaned(amount='%s', document_date='%s', address='%s',
            sellers='%s', buyers='%s', instrument_no='%s')>
            """ % (self.amount, self.document_date, self.address,
                   self.sellers, self.buyers, self.instrument_no)


class Dashboard(Base):
    """Dashboard table, only for private admin use."""

    __tablename__ = 'dashboard'

    gid = Column(Integer, primary_key=True)
    amount = Column(BigInteger)
    document_date = Column(Date, nullable=True)
    document_recorded = Column(Date, nullable=True)
    address = Column(String)
    location_info = Column(String)
    sellers = Column(String)
    buyers = Column(String)
    instrument_no = Column(
        String,
        # ForeignKey("cleaned.instrument_no"),
        nullable=False
    )
    latitude = Column(Float)
    longitude = Column(Float)
    zip_code = Column(String)
    detail_publish = Column(Boolean, nullable=True)
    location_publish = Column(Boolean, nullable=True)
    neighborhood = Column(String)
    copied_to_cleaned = Column(Boolean)

    def __init__(self,
                 gid,
                 amount,
                 document_date,
                 document_recorded,
                 address,
                 location_info,
                 sellers,
                 buyers,
                 instrument_no,
                 latitude,
                 longitude,
                 zip_code,
                 detail_publish,
                 location_publish,
                 neighborhood,
                 fixed):
        self.gid = gid,
        self.amount = amount,
        self.document_date = document_date,
        self.document_recorded = document_recorded,
        self.address = address,
        self.location_info = location_info,
        self.sellers = sellers,
        self.buyers = buyers,
        self.instrument_no = instrument_no,
        self.latitude = latitude,
        self.longitude = longitude,
        self.zip_code = zip_code,
        self.detail_publish = detail_publish,
        self.location_publish = location_publish,
        self.neighborhood = neighborhood,
        self.fixed = fixed

    def __repr__(self):
        return """
            <Dashboard(gid='%s', fixed='%s', amount='%s',
            document_date='%s', address='%s', sellers='%s', buyers='%s',
            instrument_no='%s')>
            """ % (self.gid, self.fixed, self.amount,
                   self.document_date, self.address,
                   self.sellers, self.buyers, self.instrument_no)


class Detail(Base):
    """
    Fields for the `details` table.

    :param document_id: String. Primary key ID.
    :param document_type: String. The type of document on the Land Records \
    Division's website. Ex. Sale, marriage certificate, lien, etc.
    :param instrument_no: String. The unique identifier in the Land Records \
    Division's records.
    :param multi_seq: String. Not used.
    :param min_: String. Not used. Uses "min_" instead of "min" because "min" \
    is a reserved word in Python.
    :param cin: String. Not used.
    :param book_type: String. Not used.
    :param page: String. Not used.
    :param document_date: Date. The date when the sale was made.
    :param document_recorded: Date. The date when the sale was recorded.
    :param amount: BigInteger. The sale amount.
    :param status: String. The status of the indexing process. Ex. Verified, \
    Entered. Refers to the status of the permanent-temporary process.
    :param prior_mortgage_doc_type: String. Not used.
    :param prior_conveyance_doc_type: String. Not used.
    :param cancel_status: String. Not used.
    :param remarks: String. Not used.
    :param no_pages_in_image: String. The number of images. Not used.
    :param image: String. A link to the image. Not used.
    :param detail_publish: Boolean. True means this sale is okay to publish, \
    False means it is not okay to publish. True/False is determined by checks \
    in publish.py.
    :param permanent_flag: Boolean. True means this sale's information is \
    permanent, False means it is still temporary. True/False is determined by \
    checks during scraping process.
    """

    __tablename__ = 'details'

    document_id = Column(String, primary_key=True)
    document_type = Column(String)
    instrument_no = Column(String)
    multi_seq = Column(String, nullable=True)
    min_ = Column(String, nullable=True)  # min is python reserved word
    cin = Column(String, nullable=True)
    book_type = Column(String, nullable=True)
    book = Column(String, nullable=True)
    page = Column(String, nullable=True)
    document_date = Column(Date, nullable=True)
    document_recorded = Column(Date, nullable=True)
    amount = Column(BigInteger)
    status = Column(String, nullable=True)
    prior_mortgage_doc_type = Column(String, nullable=True)
    prior_conveyance_doc_type = Column(String, nullable=True)
    cancel_status = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    no_pages_in_image = Column(String, nullable=True)
    image = Column(String, nullable=True)
    detail_publish = Column(Boolean, nullable=True)
    permanent_flag = Column(Boolean, nullable=True)

    def __init__(self,
                 document_id,
                 document_type,
                 instrument_no,
                 multi_seq,
                 min_,
                 cin,
                 book_type,
                 book,
                 page,
                 document_date,
                 document_recorded,
                 amount,
                 status,
                 prior_mortgage_doc_type,
                 prior_conveyance_doc_type,
                 cancel_status,
                 remarks,
                 no_pages_in_image,
                 image,
                 detail_publish,
                 permanent_flag):
        self.document_id = document_id,
        self.document_type = document_type,
        self.instrument_no = instrument_no,
        self.multi_seq = multi_seq,
        self.min_ = min_,
        self.cin = cin,
        self.book_type = book_type,
        self.book = book,
        self.page = page,
        self.document_date = document_date,
        self.document_recorded = document_recorded,
        self.amount = amount,
        self.status = status,
        self.prior_mortgage_doc_type = prior_mortgage_doc_type,
        self.prior_conveyance_doc_type = prior_conveyance_doc_type,
        self.cancel_status = cancel_status,
        self.remarks = remarks,
        self.no_pages_in_image = no_pages_in_image,
        self.image = image,
        self.detail_publish = detail_publish,
        self.permanent_flag = permanent_flag

    def __repr__(self):
        return "<Detail(id='%s', amount='%s')>" % (
            self.document_id, self.amount)


class Vendor(Base):
    """
    Fields for the `vendors` table.

    :param gid: Integer. Primary key ID.
    :param document_id: String. The unique identifier on the Land Records \
    Division's website.
    :param vendor_blank: String. Not used.
    :param vendor_p_c: String. Not used.
    :param vendor_lastname: String. The last name of the vendor.
    :param vendor_firstname: String. The first name of the vendor.
    :param vendor_relator: String. Can't remember right now.
    :param vendor_cancel_status: String. Not used.
    """

    __tablename__ = 'vendors'

    gid = Column(Integer, primary_key=True)
    vendor_blank = Column(String)
    vendor_p_c = Column(String)
    vendor_lastname = Column(String)
    vendor_firstname = Column(String)
    vendor_relator = Column(String)
    vendor_cancel_status = Column(String)
    document_id = Column(
        String,
        ForeignKey("details.document_id", ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self,
                 gid,
                 document_id,
                 vendor_blank,
                 vendor_p_c,
                 vendor_lastname,
                 vendor_firstname,
                 vendor_relator,
                 vendor_cancel_status):
        self.gid = gid,
        self.document_id = document_id,
        self.vendor_blank = vendor_blank,
        self.vendor_p_c = vendor_p_c,
        self.vendor_lastname = vendor_lastname,
        self.vendor_firstname = vendor_firstname,
        self.vendor_relator = vendor_relator,
        self.vendor_cancel_status = vendor_cancel_status

    def __repr__(self):
        return """
            <Vendor(gid='%s', vendor_lastname='%s',
            vendor_firstname='%s')>
            """ % (self.gid, self.vendor_lastname, self.vendor_firstname)


class Vendee(Base):
    """
    Fields for the `vendees` table.

    :param gid: Integer. Primary key ID.
    :param document_id: String. The unique identifier on the Land Records \
    Division's website.
    :param vendee_blank: String. Not used.
    :param vendee_p_c: String. Not used.
    :param vendee_lastname: String. The last name of the vendee.
    :param vendee_firstname: String. The first name of the vendee.
    :param vendee_relator: String. Can't remember right now.
    :param vendee_cancel_status: String. Not used.
    """

    __tablename__ = 'vendees'

    gid = Column(Integer, primary_key=True)
    vendee_blank = Column(String)
    vendee_p_c = Column(String)
    vendee_lastname = Column(String)
    vendee_firstname = Column(String)
    vendee_relator = Column(String)
    vendee_cancel_status = Column(String)
    document_id = Column(
        String,
        ForeignKey("details.document_id", ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self,
                 gid,
                 document_id,
                 vendee_blank,
                 vendee_p_c,
                 vendee_lastname,
                 vendee_firstname,
                 vendee_relator,
                 vendee_cancel_status):
        self.gid = gid,
        self.document_id = document_id,
        self.vendee_blank = vendee_blank,
        self.vendee_p_c = vendee_p_c,
        self.vendee_lastname = vendee_lastname,
        self.vendee_firstname = vendee_firstname,
        self.vendee_relator = vendee_relator,
        self.vendee_cancel_status = vendee_cancel_status

    def __repr__(self):
        return """
            <Vendee(gid='%s', vendee_lastname='%s',
            vendee_firstname='%s')>
            """ % (self.gid, self.vendee_lastname, self.vendee_firstname)


class Neighborhood(Base):
    """
    Fields for the `neighborhoods` table.

    :param gid: Integer. Primary key ID.
    :param objectid: Integer. Not sure
    :param gnocdc_lab: String. Not sure.
    :param lup_lab: String. Not sure.
    :param neigh_id: String. Not sure.
    :param shape_leng: Numeric. The (perimeter?) of the neighborhood (units?).
    :param shape_area: Numeric. The area of the neighborhood (units?).
    :param geom: Geometry(Multipolygon). The PostGIS geometry of the \
    neighborhood.
    """

    __tablename__ = 'neighborhoods'

    gid = Column(Integer, primary_key=True)
    objectid = Column(Integer)
    gnocdc_lab = Column(String)
    lup_lab = Column(String)
    neigh_id = Column(String)
    shape_leng = Column(Numeric)
    shape_area = Column(Numeric)
    geom = Column(Geometry('MULTIPOLYGON'))

    def __init__(self,
                 gid,
                 objectid,
                 gnocdc_lab,
                 lup_lab,
                 neigh_id,
                 shape_leng,
                 shape_area,
                 geom):
        self.gid = gid,
        self.objectid = objectid,
        self.gnocdc_lab = gnocdc_lab,
        self.lup_lab = lup_lab,
        self.neigh_id = neigh_id,
        self.shape_leng = shape_leng,
        self.shape_area = shape_area,
        self.geom = geom

    def __repr__(self):
        return "<Neighborhood(gnocdc_lab='%s')>" % (self.gnocdc_lab)
