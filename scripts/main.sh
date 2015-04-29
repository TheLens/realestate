#!/bin/bash

# Ran chmod +x on this file

cd /apps/realestate
. bin/activate
cd /apps/realestate/repo/realestate/lib
python scrape.py
cd /apps/realestate/repo/scripts
python initialize.py
