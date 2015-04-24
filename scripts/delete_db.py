# -*- coding: utf-8 -*-

'''Deletes the database.'''

# from __future__ import absolute_import

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

from landrecords import log
from landrecords.config import Config


class Delete(object):

    '''Prepares for deletion and DROPs all tables.'''

    def __init__(self):
        '''Establish connection to the database.'''

        engine = create_engine('%s' % (Config().SERVER_ENGINE))
        self.conn = engine.connect()
        self.trans = self.conn.begin()
        self.inspector = reflection.Inspector.from_engine(engine)

        # https://bitbucket.org/zzzeek/sqlalchemy/
        # wiki/UsageRecipes/DropEverything

    def main(self):
        '''Runs through each method.'''

        # self.dump_dashboard_table()
        # self.drop_db()
        self.vacuum_database()
        self.drop_tables()

    @staticmethod
    def dump_dashboard_table():
        '''
        Make a backup of the dashboard table so that any changes
        made in the past will be carried over to the future.
        '''

        log.debug('dump_dashboard_table')

        # Backup dashboard table, if it exists
        try:
            call([
                'pg_dump',
                '-Fc',
                '%s' % Config().DATABASE_NAME,
                '-t',
                'dashboard',
                '-f',
                '{0}'.format(Config().BACKUP_DIR) +
                '/dashboard_table_{0}.sql'.format(Config().TODAY_DATE)
            ])
        except Exception, error:
            log.debug(error, exc_info=True)

    @staticmethod
    def drop_db():
        '''
        Deletes the database.
        '''

        log.debug('drop DB')

        # Backup dashboard table, if it exists
        try:
            call([
                'dropdb',
                '%s' % Config().DATABASE_NAME
            ])
        except Exception, error:
            log.debug(error, exc_info=True)

    @staticmethod
    def vacuum_database():
        '''VACUUM the database.'''

        log.debug('vacuum_database')

        # Make sure to get rid of deleted rows
        try:
            call([
                'psql',
                '%s' % Config().DATABASE_NAME,
                '-c',
                'VACUUM;'
            ])
        except Exception, error:
            log.debug(error, exc_info=True)

    def drop_tables(self):
        '''DROP all tables except those for PostGIS.'''

        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.

        log.debug('drop_tables')

        metadata = MetaData()
        tables = []
        all_foreign_keys = []

        for table_name in self.inspector.get_table_names():
            foreign_keys = []
            for foreign_key in self.inspector.get_foreign_keys(table_name):
                if not foreign_key['name']:
                    continue
                foreign_keys.append(
                    ForeignKeyConstraint((), (), name=foreign_key['name'])
                )
            table = Table(table_name, metadata, *foreign_keys)
            tables.append(table)
            all_foreign_keys.extend(foreign_keys)

        for foreign_key in all_foreign_keys:
            self.conn.execute(DropConstraint(foreign_key))

        for table in tables:
            # This table is part of PostGIS extension.
            if table.name == 'spatial_ref_sys':
                continue
            self.conn.execute(DropTable(table))

        self.trans.commit()

if __name__ == '__main__':
    Delete().main()
