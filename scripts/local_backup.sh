#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate

# Copy server backup files to local directory
rsync -avzh ubuntu@vault.thelensnola.org:/backups/realestate/ $PYTHONPATH/backups/
rsync -avzh ubuntu@vault.thelensnola.org:/home/ubuntu/realestate/data/ $PYTHONPATH/data/

deactivate
