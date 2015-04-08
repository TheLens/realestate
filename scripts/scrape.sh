#!/bin/bash

#Property sales
# ran chmod +x on this file
cd /apps/land-records
. bin/activate
cd /apps/land-records/repo/scripts
python scrape.py
cd /apps/land-records/repo/scripts
python initialize.py
