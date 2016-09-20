#!/bin/bash

# Declare environment variables needed for virtualenvwrapper.
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME

source `which virtualenvwrapper.sh`

workon realestate

bash $PROJECT_DIRECTORY/scripts/delete_db.sh
python $PROJECT_DIRECTORY/scripts/make_db.py
python $PROJECT_DIRECTORY/scripts/initialize.py

deactivate
