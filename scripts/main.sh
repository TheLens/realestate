#!/bin/bash

# Ran chmod +x on this file

workon realestate
python /home/ubuntu/realestate/realestate/lib/scrape.py
python /home/ubuntu/realestate/scripts/initialize.py
deactivate
