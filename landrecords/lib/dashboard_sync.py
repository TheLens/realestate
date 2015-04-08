# -*- coding: utf-8 -*-

from subprocess import call
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from landrecords import config, db
from landrecords.lib.log import Log


class DashboardSync(object):

    def __init__(self):
        self.log = Log('dashboard_sync').logger

        base = declarative_base()
        self.engine = create_engine(config.SERVER_ENGINE)
        base.metadata.create_all(self.engine)
        sn = sessionmaker(bind=self.engine)

        self.session = sn()

    # main()
    def copy_dashboard_to_cleaned(self):
        '''
        Correct Cleaned entries based on overrides made in dashboard.

        Only for building database from scratch.
        Normal flow is add yesterday to Cleaned and publish.
        Dashboard interaction then comes after and directly updates Cleaned
        while simultaneously adding to/updating same entry in Dashboard table.
        '''

        self.restore_dashboard_table_from_backup()
        self.correct_dashboard_table_id_field()

        rows = self.query_get_dashboard_rows()
        self.copy_dashboard_rows_to_cleaned_table(rows)
        self.change_dashboard_entry_fixed_field_to_true(rows)

    def restore_dashboard_table_from_backup(self):
        # If run multiple times, will produce key value warning..

        try:
            call(["pg_restore",
                  "--data-only",
                  "-d",
                  "landrecords",
                  "-t",
                  "dashboard",
                  "{0}".format(config.BACKUP_DIR) +
                  "/dashboard_table_$(date +%Y-%m-%d).sql"])
        except Exception, e:
            self.log.info('Could not restore dashboard table')
            self.log.error(e, exc_info=True)

    def correct_dashboard_table_id_field(self):
        fix_id_sql = """SELECT setval('dashboard_id_seq', MAX(id))
                        FROM dashboard;"""
        self.engine.execute(fix_id_sql)

    def query_get_unfixed_dashboard_rows(self):
        q = self.session.query(
            db.Dashboard
        ).order_by(  # update Cleaned in order Dashboard changes were made
            db.Dashboard.id.asc()
        ).all()

        rows = []
        for row in q:
            # row_dict = {}
            # row_dict['instrument_no'] = row.instrument_no
            # row_dict['detail_publish'] = row.detail_publish
            # row_dict['location_publish'] = row.location_publish
            # row_dict['document_date'] = row.document_date
            # row_dict['amount'] = row.amount
            # row_dict['address'] = row.address
            # row_dict['location_info'] = row.location_info
            # row_dict['sellers'] = row.sellers
            # row_dict['buyers'] = row.buyers
            # row_dict['document_recorded'] = row.document_recorded
            # row_dict['latitude'] = row.latitude
            # row_dict['longitude'] = row.longitude
            # row_dict['zip_code'] = row.zip_code
            # row_dict['neighborhood'] = row.neighborhood

            row_dict = row.__dict__

            rows.append(row_dict)

        return rows

    def copy_dashboard_rows_to_cleaned_table(self, rows):
        for row in rows:
            self.log.info(row['instrument_no'])

            u = update(db.Cleaned)
            u = u.values(row)
            u = u.where(
                db.Cleaned.instrument_no == '%s' % row['instrument_no'])
            self.session.execute(u)
            self.session.commit()

    def change_dashboard_entry_fixed_field_to_true(self, rows):
        for row in rows:
            self.log.info(row['instrument_no'])
            u = update(db.Dashboard)
            u = u.values({"fixed": True})
            u = u.where(
                db.Dashboard.instrument_no == '%s' % row['instrument_no'])
            self.session.execute(u)
            self.session.commit()
