#!/bin/bash

# Declare environment variables needed for virtualenvwrapper.
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME

source `which virtualenvwrapper.sh`

workon realestate
# rm /backups/realestate/realestate-db*.sql
pg_dump realestate > /backups/realestate/realestate-db-$(date +%Y-%m-%d).sql

aws s3 cp /backups/realestate/realestate-db-$(date +%Y-%m-%d).sql s3://lensnola/realestate/backups/realestate-db-$(date +%Y-%m-%d).sql
deactivate
