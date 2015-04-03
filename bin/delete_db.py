# -*- coding: utf-8 -*-

from __future__ import absolute_import

from fabric.api import local
from sqlalchemy.engine import reflection
from sqlalchemy import create_engine
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint
)
from landrecords import config

# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything

engine = create_engine('%s' % (config.SERVER_ENGINE))

conn = engine.connect()

# the transaction only applies if the DB supports
# transactional DDL, i.e. Postgresql, MS SQL Server
trans = conn.begin()

inspector = reflection.Inspector.from_engine(engine)

# gather all data first before dropping anything.
# some DBs lock after things have been dropped in
# a transaction.

metadata = MetaData()

tbs = []
all_fks = []

# Backup dashboard table, if it exists
# Might need to full VACUUM to get rid of deleted rows
try:
    local('pg_dump -Fc landrecords -t dashboard > ' + config.BACKUP_DIR +
          '/dashboard_table_$(date +%Y-%m-%d).sql')
except:
    print 'Could not dump dashboard table.'


try:
    local('psql landrecords -c "VACUUM;"')
except:
    print 'Could not vacuum.'


for table_name in inspector.get_table_names():
    fks = []
    for fk in inspector.get_foreign_keys(table_name):
        if not fk['name']:
            continue
        fks.append(
            ForeignKeyConstraint((), (), name=fk['name'])
        )
    t = Table(table_name, metadata, *fks)
    tbs.append(t)
    all_fks.extend(fks)

for fkc in all_fks:
    conn.execute(DropConstraint(fkc))
print tbs
for table in tbs:
    # This table is part of PostGIS extension.
    if table.name == 'spatial_ref_sys':
        continue
    conn.execute(DropTable(table))

trans.commit()
