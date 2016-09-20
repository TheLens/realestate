#!/bin/bash

# Declare environment variables needed for virtualenvwrapper.
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME

source `which virtualenvwrapper.sh`

workon realestate

python /home/ubuntu/realestate/scripts/scrape.py
python /home/ubuntu/realestate/scripts/initialize.py

deactivate
