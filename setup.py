# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='land-records',
    version='0.0.1',
    packages=(
        'landrecords',
        'tests',
    ),
    include_package_data=True,
    license='MIT',
    description=(
        "A package for scraping and publishing New Orleans land " +
        "records."),
    long_description="",
    keywords="The Lens land records",
    url='http://vault.thelensnola.org/realestate/',
    author='Thomas Thoren',
    author_email='tthoren@thelensnola.org',
    install_requires=(
        'Flask>=0.10.1',
        'SQLAlchemy'
    ),
)
