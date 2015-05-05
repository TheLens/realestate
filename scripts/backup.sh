#!/bin/bash

workon realestate
# rm /backups/realestate/realestate-db*.sql
pg_dump realestate > /backups/realestate/realestate-db-$(date +%Y-%m-%d).sql

aws s3 cp /backups/realestate/realestate-db-$(date +%Y-%m-%d).sql s3://lensnola/realestate/backups/realestate-db-$(date +%Y-%m-%d).sql
deactivate
