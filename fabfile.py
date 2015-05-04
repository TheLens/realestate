# -*- coding: utf-8 -*-

'''
Methods for commiting app to Github.
It should never deploy to the server or
S3. That should be left to Travis CI and the server calling git pull.
'''

from fabric.api import local
from realestate import PROJECT_DIR

APP_DIR = '%s/realestate' % PROJECT_DIR
CSS_DIR = '%s/realestate/static/css' % PROJECT_DIR
DATA_DIR = '%s/data' % PROJECT_DIR
DOCS_DIR = '%s/docs' % PROJECT_DIR
FONTS_DIR = '%s/realestate/static/fonts' % PROJECT_DIR
IMAGES_DIR = '%s/realestate/static/css/images' % PROJECT_DIR
JS_DIR = '%s/realestate/static/js' % PROJECT_DIR
LIB_DIR = '%s/realestate/lib' % PROJECT_DIR
PICTURES_DIR = '%s' % PROJECT_DIR + '/realestate/static/pictures'
SCRIPTS_DIR = '%s/scripts' % PROJECT_DIR
TEMPLATE_DIR = '%s/realestate/templates' % PROJECT_DIR
TESTS_DIR = '%s/tests' % PROJECT_DIR


def repo():
    '''/'''

    local('git add %s/.coveragerc' % PROJECT_DIR)
    local('git add %s/.gitignore' % PROJECT_DIR)
    local('git add %s/.travis.yml' % PROJECT_DIR)
    local('git add %s/MANIFEST.in' % PROJECT_DIR)
    local('git add %s/README.md' % PROJECT_DIR)
    local('git add %s/app.ini' % PROJECT_DIR)
    local('git add %s/fabfile.py' % PROJECT_DIR)
    local('git add %s/realestate.conf' % PROJECT_DIR)
    local('git add %s/requirements.txt' % PROJECT_DIR)
    local('git add %s/setup.py' % PROJECT_DIR)


def data():
    '''/data'''

    local(
        'git add %s/assessor-error-html/assessor_error.html' % DATA_DIR)
    local('git add %s/sale-error-html/sale_error.html' % DATA_DIR)


def docs():
    '''/docs/'''

    local('git add %s/' % DOCS_DIR)

    # local('git add %s/build.rst' % DOCS_DIR)
    # local('git add %s/conf.py' % DOCS_DIR)
    # local('git add %s/database.rst' % DOCS_DIR)
    # local('git add %s/index.rst' % DOCS_DIR)
    # local('git add %s/Makefile' % DOCS_DIR)
    # local('git add %s/misc.rst' % DOCS_DIR)
    # local('git add %s/scrape.rst' % DOCS_DIR)
    # local('git add %s/tests.rst' % DOCS_DIR)


def realestate():
    '''/realestate/'''

    local('git add %s/__init__.py' % APP_DIR)
    local('git add %s/app.py' % APP_DIR)
    local('git add %s/db.py' % APP_DIR)
    local('git add %s/models.py' % APP_DIR)
    local('git add %s/views.py' % APP_DIR)


def lib():
    '''/realestate/lib'''

    local('git add %s/__init__.py' % LIB_DIR)
    local('git add %s/build.py' % LIB_DIR)
    local('git add %s/clean.py' % LIB_DIR)
    local('git add %s/delete_dates.py' % LIB_DIR)
    local('git add %s/email_template.py' % LIB_DIR)
    local('git add %s/form_tweet.py' % LIB_DIR)
    local('git add %s/geocode.py' % LIB_DIR)
    local('git add %s/get_dates.py' % LIB_DIR)
    local('git add %s/libraries.py' % LIB_DIR)
    local('git add %s/mail.py' % LIB_DIR)
    local('git add %s/parse.py' % LIB_DIR)
    local('git add %s/publish.py' % LIB_DIR)
    local('git add %s/results_language.py' % LIB_DIR)
    local('git add %s/scrape.py' % LIB_DIR)
    local('git add %s/stat_analysis.py' % LIB_DIR)
    local('git add %s/twitter.py' % LIB_DIR)
    local('git add %s/utils.py' % LIB_DIR)


def css():
    '''/realestate/static/css'''

    local('git add %s/banner.css' % CSS_DIR)
    local('git add %s/font-awesome.css' % CSS_DIR)
    local('git add %s/foundation.min.css' % CSS_DIR)
    local('git add %s/jquery-ui.css' % CSS_DIR)
    local('git add %s/jquery.tablesorter.pager.css' % CSS_DIR)
    local('git add %s/lens.css' % CSS_DIR)
    local('git add %s/lenstablesorter.css' % CSS_DIR)
    local('git add %s/mapbox.css' % CSS_DIR)
    local('git add %s/realestate.css' % CSS_DIR)
    local('git add %s/table.css' % CSS_DIR)


def images():
    '''/realestate/static/css/images'''

    local('git add %s/corporate-realty.jpg' % IMAGES_DIR)
    local('git add %s/corporate-realty-large.jpg' % IMAGES_DIR)
    local('git add %s/corporate-realty.png' % IMAGES_DIR)
    local('git add %s/corporate-realty-large.png' % IMAGES_DIR)
    local('git add %s/favicon.ico' % IMAGES_DIR)
    local('git add %s/icons-000000.png' % IMAGES_DIR)
    local('git add %s/icons-000000@2x.png' % IMAGES_DIR)
    local('git add %s/lens-logo-retina.png' % IMAGES_DIR)
    local('git add %s/lens-logo-magnifying-glass-only.png' % IMAGES_DIR)
    local('git add %s/ui-bg_flat_75_ffffff_40x100.png' % IMAGES_DIR)
    local('git add %s/ui-bg_glass_55_fbf9ee_1x400.png' % IMAGES_DIR)
    local('git add %s/ui-bg_glass_75_dadada_1x400.png' % IMAGES_DIR)
    local('git add %s/ui-bg_glass_75_e6e6e6_1x400.png' % IMAGES_DIR)
    local(
        'git add %s/' % IMAGES_DIR +
        'ui-bg_highlight-soft_75_cccccc_1x100.png')
    local('git add %s/ui-bg_glass_65_ffffff_1x400.png' % IMAGES_DIR)
    local('git add %s/ui-icons_454545_256x240.png' % IMAGES_DIR)


def fonts():
    '''/realestate/static/fonts'''

    local('git add %s/fontawesome-webfont.eot' % FONTS_DIR)
    local('git add %s/fontawesome-webfont.svg' % FONTS_DIR)
    local('git add %s/fontawesome-webfont.ttf' % FONTS_DIR)
    local('git add %s/fontawesome-webfont.woff' % FONTS_DIR)
    local('git add %s/FontAwesome.otf' % FONTS_DIR)


def js():
    '''/realestate/static/js'''

    local('git add %s/dashboard.js' % JS_DIR)
    local('git add %s/foundation.min.js' % JS_DIR)
    local('git add %s/foundation.tooltip.js' % JS_DIR)
    local('git add %s/index.js' % JS_DIR)
    local('git add %s/jquery-1.11.0.min.js' % JS_DIR)
    local('git add %s/jquery-ui.js' % JS_DIR)
    local('git add %s/jquery.tablesorter.min.js' % JS_DIR)
    local('git add %s/jquery.tablesorter.pager.min.js' % JS_DIR)
    local('git add %s/leaflet.js' % JS_DIR)
    local('git add %s/lens.js' % JS_DIR)
    local('git add %s/map.js' % JS_DIR)
    local('git add %s/mapbox.uncompressed.js' % JS_DIR)
    local('git add %s/modernizr.js' % JS_DIR)
    local('git add %s/neighborhoods-topo.js' % JS_DIR)
    local('git add %s/neighborhoods-topo.min.js' % JS_DIR)
    local('git add %s/sale.js' % JS_DIR)
    local('git add %s/search.js' % JS_DIR)
    local('git add %s/search-area.js' % JS_DIR)


def templates():
    '''/realestate/templates'''

    local('git add %s/404.html' % TEMPLATE_DIR)
    local('git add %s/banner.html' % TEMPLATE_DIR)
    local('git add %s/dashboard.html' % TEMPLATE_DIR)
    local('git add %s/footer.html' % TEMPLATE_DIR)
    local('git add %s/head.html' % TEMPLATE_DIR)
    local('git add %s/index.html' % TEMPLATE_DIR)
    local('git add %s/js.html' % TEMPLATE_DIR)
    local('git add %s/sale.html' % TEMPLATE_DIR)
    local('git add %s/search.html' % TEMPLATE_DIR)
    local('git add %s/search-area.html' % TEMPLATE_DIR)
    local('git add %s/table.html' % TEMPLATE_DIR)


def scripts():
    '''/scripts/'''

    local('git add %s/backup.sh' % SCRIPTS_DIR)
    local('git add %s/delete_db.py' % SCRIPTS_DIR)
    local('git add %s/initialize.py' % SCRIPTS_DIR)
    local('git add %s/main.sh' % SCRIPTS_DIR)
    local('git add %s/make_db.py' % SCRIPTS_DIR)
    local('git add %s/screen.js' % SCRIPTS_DIR)
    local('git add %s/screen.py' % SCRIPTS_DIR)


def tests():
    '''/tests/'''

    local('git add %s/__init__.py' % TESTS_DIR)
    local('git add %s/test_parse.py' % TESTS_DIR)
    local('git add %s/test_pep8.py' % TESTS_DIR)
    local('git add %s/test_pylint.py' % TESTS_DIR)


# Others
def addthemall():
    '''Run through entire deployment.'''

    repo()
    data()
    docs()
    realestate()
    lib()
    css()
    images()
    fonts()
    js()
    templates()
    scripts()
    tests()


def commit(message):
    local('git commit -m "%s"' % message)


def push():
    local('git push origin master')


def pull():
    local('git pull origin master')


def github(message):
    '''Add, commit and push to Github.'''

    addthemall()
    commit(message)
    push()


if __name__ == '__main__':
    pass
