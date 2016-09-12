#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate

bash $PROJECT_DIRECTORY/scripts/delete_db.sh
python $PROJECT_DIRECTORY/scripts/make_db.py
python $PROJECT_DIRECTORY/scripts/initialize.py

deactivate
