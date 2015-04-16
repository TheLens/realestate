# -*- coding: utf-8 -*-

from __future__ import absolute_import

from subprocess import call
from sqlalchemy.engine import reflection
from sqlalchemy import create_engine
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint
)

from landrecords.lib.log import Log
from landrecords.config import Config


class Delete(object):

    def __init__(self):

        engine = create_engine('%s' % (Config().SERVER_ENGINE))
        self.conn = engine.connect()
        self.trans = self.conn.begin()
        self.inspector = reflection.Inspector.from_engine(engine)

        # https://bitbucket.org/zzzeek/sqlalchemy/
        # wiki/UsageRecipes/DropEverything

    def main(self):
        self.dump_dashboard_table()
        self.vacuum_database()
        self.drop_tables()

    def dump_dashboard_table(self):
        # Backup dashboard table, if it exists
        try:
            call(['pg_dump',
                  '-Fc',
                  'landrecords',
                  '-t',
                  'dashboard',
                  '-f',
                  '{0}'.format(Config().BACKUP_DIR) +
                  '/dashboard_table_{0}.sql'.format(Config().TODAY_DATE)])
        except Exception, e:
            print e

    def vacuum_database(self):
        # Make sure to get rid of deleted rows
        try:
            call(['psql',
                  'landrecords',
                  '-c',
                  'VACUUM;'])
        except Exception, e:
            print e

    def drop_tables(self):
        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.

        metadata = MetaData()
        tbs = []
        all_fks = []

        for table_name in self.inspector.get_table_names():
            fks = []
            for fk in self.inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(
                    ForeignKeyConstraint((), (), name=fk['name'])
                )
            t = Table(table_name, metadata, *fks)
            tbs.append(t)
            all_fks.extend(fks)

        for fkc in all_fks:
            self.conn.execute(DropConstraint(fkc))

        for table in tbs:
            # This table is part of PostGIS extension.
            if table.name == 'spatial_ref_sys':
                continue
            self.conn.execute(DropTable(table))

        self.trans.commit()

if __name__ == '__main__':
    log = Log(__name__).initialize_log()
    Delete().main()
