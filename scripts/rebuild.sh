#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate

bash $PYTHONPATH/scripts/delete_db.sh
python $PYTHONPATH/scripts/make_db.py
python $PYTHONPATH/scripts/initialize.py

deactivate
