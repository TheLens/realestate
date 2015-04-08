# -*- coding: utf-8 -*-

from __future__ import absolute_import

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
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    subdivision = Column(String)
    condo = Column(String)
    district = Column(String)
    square = Column(String)
    lot = Column(String)
    cancel_status = Column(String)
    street_number = Column(String)
    address = Column(String)
    unit = Column(String)
    weeks = Column(String)
    cancel_stat = Column(String)
    freeform_legal = Column(String)
    document_id = Column(String,
                         ForeignKey("details.document_id"),
                         nullable=False)
    full_address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    zip_code = Column(String)
    neighborhood = Column(String)
    location_publish = Column(String)

    def __init__(self,
                 id,
                 subdivision,
                 condo,
                 district,
                 square,
                 lot,
                 cancel_status,
                 street_number,
                 address,
                 unit,
                 weeks,
                 cancel_stat,
                 freeform_legal,
                 document_id,
                 full_address,
                 latitude,
                 longitude,
                 rating,
                 zip_code,
                 neighborhood,
                 location_publish):
        self.id = id,
        self.subdivision = subdivision,
        self.condo = condo,
        self.district = district,
        self.square = square,
        self.lot = lot,
        self.cancel_status = cancel_status,
        self.street_number = street_number,
        self.address = address,
        self.unit = unit,
        self.weeks = weeks,
        self.cancel_stat = cancel_stat,
        self.freeform_legal = freeform_legal,
        self.document_id = document_id,
        self.full_address = full_address,
        self.latitude = latitude,
        self.longitude = longitude,
        self.rating = rating,
        self.zip_code = zip_code,
        self.neighborhood = neighborhood,
        self.location_publish = location_publish
        pass

    def __repr__(self):
        return "<Location(id='%s', street_number='%s')>" % (
            self.id, self.street_number)


class Cleaned(Base):
    __tablename__ = 'cleaned'

    # id = Column(Integer, primary_key=True)
    instrument_no = Column(String, primary_key=True, index=True)
    geom = Column(Geometry(geometry_type='POINT',
                           srid=4326,
                           spatial_index=True))
    amount = Column(BigInteger)
    document_date = Column(Date, nullable=True)
    document_recorded = Column(Date, nullable=True)
    address = Column(String,
                     index=True)
    location_info = Column(String, index=True)
    sellers = Column(String, index=True)
    buyers = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    zip_code = Column(String, index=True)
    detail_publish = Column(String)
    location_publish = Column(String)
    assessor_publish = Column(String)
    permanent_flag = Column(Boolean, nullable=True)
    neighborhood = Column(String, index=True)

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
        # self.id = id,
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
        pass

    def __repr__(self):
        return """
            <Cleaned(amount='%s', document_date='%s', address='%s',
            sellers='%s', buyers='%s', instrument_no='%s')>""" % (
            self.amount,
            self.document_date,
            self.address,
            self.sellers,
            self.buyers,
            self.instrument_no)


class Dashboard(Base):
    __tablename__ = 'dashboard'

    id = Column(Integer, primary_key=True)
    amount = Column(BigInteger)
    document_date = Column(Date, nullable=True)
    document_recorded = Column(Date, nullable=True)
    address = Column(String)
    location_info = Column(String)
    sellers = Column(String)
    buyers = Column(String)
    instrument_no = Column(String,
                           ForeignKey("cleaned.instrument_no"),
                           nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    zip_code = Column(String)
    detail_publish = Column(String)
    location_publish = Column(String)
    neighborhood = Column(String)
    copied_to_cleaned = Column(Boolean)

    def __init__(self,
                 id,
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
        self.id = id,
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
        pass

    def __repr__(self):
        return """
            <Dashboard(id='%s', fixed='%s', amount='%s',
            document_date='%s', address='%s', sellers='%s', buyers='%s',
            instrument_no='%s')>""" % (
               self.id, self.fixed, self.amount, self.document_date,
               self.address, self.sellers, self.buyers, self.instrument_no)


class Detail(Base):
    __tablename__ = 'details'

    # id = Column(Integer, primary_key=True)
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
    detail_publish = Column(String)
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
        pass

    def __repr__(self):
        return "<Detail(id='%s', amount='%s')>" % (
            self.document_id, self.amount)


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    vendor_blank = Column(String)
    vendor_p_c = Column(String)
    vendor_lastname = Column(String)
    vendor_firstname = Column(String)
    vendor_relator = Column(String)
    vendor_cancel_status = Column(String)
    document_id = Column(String,
                         ForeignKey("details.document_id"),
                         nullable=False)

    def __init__(self,
                 id,
                 document_id,
                 vendor_blank,
                 vendor_p_c,
                 vendor_lastname,
                 vendor_firstname,
                 vendor_relator,
                 vendor_cancel_status):
        self.id = id,
        self.document_id = document_id,
        self.vendor_blank = vendor_blank,
        self.vendor_p_c = vendor_p_c,
        self.vendor_lastname = vendor_lastname,
        self.vendor_firstname = vendor_firstname,
        self.vendor_relator = vendor_relator,
        self.vendor_cancel_status = vendor_cancel_status
        pass

    def __repr__(self):
        return """
            <Vendor(id='%s', vendor_lastname='%s',
            vendor_firstname='%s')>""" % (
               self.id, self.vendor_lastname, self.vendor_firstname)


class Vendee(Base):
    __tablename__ = 'vendees'

    id = Column(Integer, primary_key=True)
    vendee_blank = Column(String)
    vendee_p_c = Column(String)
    vendee_lastname = Column(String)
    vendee_firstname = Column(String)
    vendee_relator = Column(String)
    vendee_cancel_status = Column(String)
    document_id = Column(String,
                         ForeignKey("details.document_id"),
                         nullable=False)

    def __init__(self,
                 id,
                 document_id,
                 vendee_blank,
                 vendee_p_c,
                 vendee_lastname,
                 vendee_firstname,
                 vendee_relator,
                 vendee_cancel_status):
        self.id = id,
        self.document_id = document_id,
        self.vendee_blank = vendee_blank,
        self.vendee_p_c = vendee_p_c,
        self.vendee_lastname = vendee_lastname,
        self.vendee_firstname = vendee_firstname,
        self.vendee_relator = vendee_relator,
        self.vendee_cancel_status = vendee_cancel_status
        pass

    def __repr__(self):
        return """
            <Vendee(id='%s', vendee_lastname='%s',
            vendee_firstname='%s')>""" % (
            self.id, self.vendee_lastname, self.vendee_firstname)


class Neighborhood(Base):

    __tablename__ = 'neighborhoods'

    gid = Column(Integer, primary_key=True)
    objectid = Column(Integer)
    gnocdc_lab = Column(String)
    lup_lab = Column(String)
    neigh_id = Column(String)
    shape_leng = Column(Numeric)
    shape_area = Column(Numeric)
    geom = Column(Geometry('POLYGON'))

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
        pass

    def __repr__(self):
        return "<Neighborhood(gnocdc_lab='%s')>" % (self.gnocdc_lab)


class Square(Base):

    __tablename__ = 'squares'

    gid = Column(Integer, primary_key=True)
    objectid = Column(Numeric)
    square = Column(String)
    count_ = Column(Numeric)
    nogis_cnog = Column(Numeric)
    perimeter = Column(Numeric)
    acres = Column(Numeric)
    hectares = Column(Numeric)
    status = Column(Numeric)
    sq_name = Column(String)
    mun_dst = Column(String)
    square_id = Column(String)
    nbhd = Column(String)
    shape_area = Column(Numeric)
    shape_len = Column(Numeric)
    geom = Column(Geometry('POLYGON'))

    def __init__(self,
                 gid,
                 objectid,
                 square,
                 count_,
                 nogis_cnog,
                 perimeter,
                 acres,
                 hectares,
                 status,
                 sq_name,
                 mun_dst,
                 square_id,
                 nbhd,
                 shape_area,
                 shape_len,
                 geom):
        self.gid = gid,
        self.objectid = objectid,
        self.square = square,
        self.count_ = count_,
        self.nogis_cnog = nogis_cnog,
        self.perimeter = perimeter,
        self.acres = acres,
        self.hectares = hectares,
        self.status = status,
        self.sq_name = sq_name,
        self.mun_dst = mun_dst,
        self.square_id = square_id,
        self.nbhd = nbhd,
        self.shape_area = shape_area,
        self.shape_len = shape_len,
        self.geom = geom
        pass

    def __repr__(self):
        return "<Square(nbhd='%s', mun_dst='%s', square='%s')>" % (
            self.nbhd, self.mun_dst, self.square)
