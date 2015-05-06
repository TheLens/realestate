#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate
python /home/ubuntu/realestate/realestate/lib/scrape.py
python /home/ubuntu/realestate/scripts/initialize.py
deactivate
