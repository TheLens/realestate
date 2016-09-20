#!/bin/bash

# Declare environment variables needed for virtualenvwrapper.
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME

source `which virtualenvwrapper.sh`

workon realestate

# Copy server backup files to local directory
rsync -avzh ubuntu@vault.thelensnola.org:/backups/realestate/ $PROJECT_DIRECTORY/backups/
rsync -avzh ubuntu@vault.thelensnola.org:/home/ubuntu/realestate/data/ $PROJECT_DIRECTORY/data/

deactivate
