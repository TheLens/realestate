#!/bin/bash

source `which virtualenvwrapper.sh`

workon realestate

# Copy server backup files to local directory
rsync -avzh ubuntu@vault.thelensnola.org:/backups/realestate/ $PROJECT_DIRECTORY/backups/
rsync -avzh ubuntu@vault.thelensnola.org:/home/ubuntu/realestate/data/ $PROJECT_DIRECTORY/data/

deactivate
