#!/bin/bash

# Ran chmod +x on this file

cd /home/ubuntu/realestate
workon realestate
cd /home/ubuntu/realestate/realestate/lib
python scrape.py
cd /home/ubuntu/realestate/scripts
python initialize.py
