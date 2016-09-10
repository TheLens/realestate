#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate

python /home/ubuntu/realestate/scripts/scrape.py
python /home/ubuntu/realestate/scripts/initialize.py

deactivate
