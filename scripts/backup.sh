#!/bin/bash

cd /backups/land-records
rm landrecords-db*.sql
pg_dump landrecords > /backups/land-records/landrecords-db-$(date +%Y-%m-%d).sql
