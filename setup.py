# -*- coding: utf-8 -*-

"""TODO."""

import os
from setuptools import setup


def read(fname):
    """TODO."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='realestate',
    version='0.0.1',
    packages=(
        'scripts',
        'tests',
        'www',
    ),
    data_files=[
        (".", ["README.md", "requirements.txt"]),
        ("logs", ["logs/realestate.log"]),
        ("scripts", [
            "scripts/backup.sh",
            "scripts/delete_db.py",
            "scripts/initialize.py",
            "scripts/main.sh",
            "scripts/make_db.py"])
    ],
    include_package_data=True,
    license='MIT',
    description=(
        "A package for scraping and publishing New Orleans land " +
        "records."),
    long_description=read('README.md'),
    keywords="The Lens realestate",
    url='https://vault.thelensnola.org/realestate/',
    author='Thomas Thoren',
    author_email='tthoren@thelensnola.org',
    install_requires=(
        'alabaster',
        'astroid',
        'Babel',
        'bcdoc',
        'beautifulsoup4',
        'botocore',
        'colorama',
        'docopt',
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
        'pylint',
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
        'Werkzeug',
    ),
)
