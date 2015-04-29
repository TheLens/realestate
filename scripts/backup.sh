#!/bin/bash

cd /backups/realestate
rm realestate-db*.sql
pg_dump realestate > /backups/realestate/realestate-db-$(date +%Y-%m-%d).sql
