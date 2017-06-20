.. _setup:

Dependencies
^^^^^^^^^^^^

* Python 3.4+
* PostgreSQL 9.3+
* PostGIS 2.1+
* Flask
* SQLAlchemy

Setup
^^^^^

When creating a virtual environment for this project, make sure to use Python 3.4 or later.

.. code-block:: bash

    mkvirtualenv --python=`which python3` realestate

Install the Python dependencies.

.. code-block:: bash

    pip install -r requirements.txt

Install the npm dependencies.

.. code-block:: bash

    npm install

Set these environment variables, either in ``~/.env``, ``~/.virtualenvs/realestate/bin/postactivate`` or another file that gets sourced.

.. code-block:: bash

    export REAL_ESTATE_LRD_USERNAME=LandRecordsDivisionUsername
    export REAL_ESTATE_LRD_PASSWORD=LandRecordsDivisionPassword
    export REAL_ESTATE_DATABASE_USERNAME=DatabaseUsername
    export REAL_ESTATE_DATABASE_PASSWORD=DatabasePassword
    export REAL_ESTATE_GMAIL_USERNAME=GmailUsername
    export REAL_ESTATE_GMAIL_PASSWORD=GmailPassword

Tests
^^^^^

Run all back-end (Python) tests.

.. code-block:: bash

    npm run tests

Determine the code coverage.

.. code-block:: bash

    npm run coverage

Use ``tox`` to run tests with Python 3.4, which our server uses since it is Ubuntu 14.

.. code-block:: bash

    tox
