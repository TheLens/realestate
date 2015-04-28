# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='land-records',
    version='0.0.1',
    packages=(
        'landrecords',
        'landrecords.lib',
        'tests',
    ),
    data_files={
        "": [
            ("", ["README.md", "requirements.txt"]),
            ("logs", ["landrecords.log"]),
            ("scripts", [
                "backup.sh",
                "delete_db.py",
                "initialize.py",
                "main.sh",
                "make_db.py",
                "screen.js",
                "screen.py",
                "tserver.py"])
        ]
    },
    include_package_data=True,
    license='MIT',
    description=(
        "A package for scraping and publishing New Orleans land " +
        "records."),
    long_description=read('README.md'),
    keywords="The Lens land records",
    url='http://vault.thelensnola.org/realestate/',
    author='Thomas Thoren',
    author_email='tthoren@thelensnola.org',
    install_requires=(
        'alabaster',
        'astroid',
        'awscli',
        'Babel',
        'bcdoc',
        'beautifulsoup',
        'botocore',
        'colorama',
        'docutils',
        'Flask',
        'GeoAlchemy2',
        'googlemaps',
        'itsdangerous',
        'Jinja2',
        'jmespath',
        'logilab-common',
        'MarkupSafe',
        'mock',
        'nose',
        'oauthlib',
        'pep8',
        'pip',
        'psycopg2',
        'pyasn1',
        'Pygments',
        'pylint',
        'python-dateutil',
        'pytz',
        'requests',
        'requests-oauthlib',
        'rsa',
        'selenium',
        'setuptools',
        'six',
        'snowballstemmer',
        'Sphinx',
        'sphinx-rtd-theme',
        'SQLAlchemy',
        'twython',
        'Werkzeug',
    ),
)
