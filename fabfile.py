# -*- coding: utf-8 -*-

'''Methods for deploying app to server.'''

from fabric.api import local
from realestate import (
    LOCAL_APP_DIR,
    LOCAL_CSS_DIR,
    LOCAL_DATA_DIR,
    LOCAL_FONTS_DIR,
    LOCAL_IMAGES_DIR,
    LOCAL_JS_DIR,
    LOCAL_LIB_DIR,
    LOCAL_PROJECT_DIR,
    LOCAL_SCRIPTS_DIR,
    LOCAL_TEMPLATE_DIR,
    LOCAL_TESTS_DIR
)


def push():
    local('git push origin master')


def data():
    '''/data'''

    local(
        'git add %s/assessor-error-html/assessor_error.html' % LOCAL_DATA_DIR)
    local(
        'git add %s/sale-error-html/sale_error.html' % LOCAL_DATA_DIR)


def repo():
    '''/'''

    local('git add %s/.coveragerc' % LOCAL_PROJECT_DIR)
    local('git add %s/.gitignore' % LOCAL_PROJECT_DIR)
    local('git add %s/.travis.yml' % LOCAL_PROJECT_DIR)
    local('git add %s/MANIFEST.in' % LOCAL_PROJECT_DIR)
    local('git add %s/README.md' % LOCAL_PROJECT_DIR)
    local('git add %s/app.ini' % LOCAL_PROJECT_DIR)
    local('git add %s/fabfile.py' % LOCAL_PROJECT_DIR)
    local('git add %s/realestate.conf' % LOCAL_PROJECT_DIR)
    local('git add %s/requirements.txt' % LOCAL_PROJECT_DIR)
    local('git add %s/setup.py' % LOCAL_PROJECT_DIR)


def app():
    '''/realestate/'''

    local('git add %s/__init__.py' % LOCAL_APP_DIR)
    local('git add %s/app.py' % LOCAL_APP_DIR)
    local('git add %s/config.py' % LOCAL_APP_DIR)
    local('git add %s/db.py' % LOCAL_APP_DIR)
    local('git add %s/models.py' % LOCAL_APP_DIR)
    local('git add %s/views.py' % LOCAL_APP_DIR)


def scripts():
    '''/scripts/'''

    local('git add %s/backup.sh' % LOCAL_SCRIPTS_DIR)
    local('git add %s/delete_db.py' % LOCAL_SCRIPTS_DIR)
    local('git add %s/initialize.py' % LOCAL_SCRIPTS_DIR)
    local('git add %s/main.sh' % LOCAL_SCRIPTS_DIR)
    local('git add %s/make_db.py' % LOCAL_SCRIPTS_DIR)
    local('git add %s/screen.js' % LOCAL_SCRIPTS_DIR)
    local('git add %s/tserver.py' % LOCAL_SCRIPTS_DIR)


def tests():
    '''/tests/'''

    local('git add %s/__init__.py' % LOCAL_TESTS_DIR)
    local('git add %s/test_pep8.py' % LOCAL_TESTS_DIR)
    local('git add %s/test_pylint.py' % LOCAL_TESTS_DIR)


def templates():
    '''/realestate/templates'''

    local('git add %s/404.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/banner.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/dashboard.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/footer.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/head.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/index.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/js.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/sale.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/search.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/search-area.html' % LOCAL_TEMPLATE_DIR)
    local('git add %s/table.html' % LOCAL_TEMPLATE_DIR)


def lib():
    '''/realestate/lib'''

    local('git add %s/__init__.py' % LOCAL_LIB_DIR)
    local('git add %s/build.py' % LOCAL_LIB_DIR)
    local('git add %s/build_assessor_urls.py' % LOCAL_LIB_DIR)
    local('git add %s/check_assessor_urls.py' % LOCAL_LIB_DIR)
    local('git add %s/check_temp_status.py' % LOCAL_LIB_DIR)
    local('git add %s/clean.py' % LOCAL_LIB_DIR)
    local('git add %s/dashboard_sync.py' % LOCAL_LIB_DIR)
    local('git add %s/delete_dates.py' % LOCAL_LIB_DIR)
    local('git add %s/email_template.py' % LOCAL_LIB_DIR)
    local('git add %s/form_tweet.py' % LOCAL_LIB_DIR)
    local('git add %s/geocode.py' % LOCAL_LIB_DIR)
    local('git add %s/get_dates.py' % LOCAL_LIB_DIR)
    local('git add %s/libraries.py' % LOCAL_LIB_DIR)
    local('git add %s/mail.py' % LOCAL_LIB_DIR)
    local('git add %s/parse.py' % LOCAL_LIB_DIR)
    local('git add %s/publish.py' % LOCAL_LIB_DIR)
    local('git add %s/results_language.py' % LOCAL_LIB_DIR)
    local('git add %s/scrape.py' % LOCAL_LIB_DIR)
    local('git add %s/stat_analysis.py' % LOCAL_LIB_DIR)
    local('git add %s/twitter.py' % LOCAL_LIB_DIR)
    local('git add %s/utils.py' % LOCAL_LIB_DIR)
    local('git add %s/webhook.py' % LOCAL_LIB_DIR)


def css():
    '''/realestate/static/css'''

    # Server
    local('git add %s/banner.css' % LOCAL_CSS_DIR)
    local('git add %s/font-awesome.css' % LOCAL_CSS_DIR)
    local('git add %s/foundation.min.css' % LOCAL_CSS_DIR)
    local('git add %s/jquery-ui.css' % LOCAL_CSS_DIR)
    local('git add %s/jquery.tablesorter.pager.css' % LOCAL_CSS_DIR)
    local('git add %s/realestate.css' % LOCAL_CSS_DIR)
    local('git add %s/lens.css' % LOCAL_CSS_DIR)
    local('git add %s/lenstablesorter.css' % LOCAL_CSS_DIR)
    local('git add %s/mapbox.css' % LOCAL_CSS_DIR)
    local('git add %s/table.css' % LOCAL_CSS_DIR)


def images():
    '''/realestate/static/css/images'''

    # Server
    local('git add %s/corporate-realty.jpg' % LOCAL_IMAGES_DIR)
    local('git add %s/corporate-realty-large.jpg' % LOCAL_IMAGES_DIR)
    local('git add %s/corporate-realty.png' % LOCAL_IMAGES_DIR)
    local('git add %s/corporate-realty-large.png' % LOCAL_IMAGES_DIR)
    local('git add %s/favicon.ico' % LOCAL_IMAGES_DIR)
    local('git add %s/icons-000000.png' % LOCAL_IMAGES_DIR)
    local('git add %s/icons-000000@2x.png' % LOCAL_IMAGES_DIR)
    local('git add %s/lens-logo-retina.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/lens-logo-magnifying-glass-only.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/ui-bg_flat_75_ffffff_40x100.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/ui-bg_glass_55_fbf9ee_1x400.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/ui-bg_glass_75_dadada_1x400.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/ui-bg_glass_75_e6e6e6_1x400.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/' % LOCAL_IMAGES_DIR +
        'ui-bg_highlight-soft_75_cccccc_1x100.png')
    local(
        'git add %s/ui-bg_glass_65_ffffff_1x400.png' % LOCAL_IMAGES_DIR)
    local(
        'git add %s/ui-icons_454545_256x240.png' % LOCAL_IMAGES_DIR)


def fonts():
    '''/realestate/static/fonts'''

    # Server
    local('git add %s/fontawesome-webfont.eot' % LOCAL_FONTS_DIR)
    local('git add %s/fontawesome-webfont.svg' % LOCAL_FONTS_DIR)
    local('git add %s/fontawesome-webfont.ttf' % LOCAL_FONTS_DIR)
    local('git add %s/fontawesome-webfont.woff' % LOCAL_FONTS_DIR)
    local('git add %s/FontAwesome.otf' % LOCAL_FONTS_DIR)


def js():
    '''/realestate/static/js'''

    # Server
    local('git add %s/dashboard.js' % LOCAL_JS_DIR)
    local('git add %s/foundation.min.js' % LOCAL_JS_DIR)
    local('git add %s/foundation.tooltip.js' % LOCAL_JS_DIR)
    local('git add %s/index.js' % LOCAL_JS_DIR)
    local('git add %s/jquery-1.11.0.min.js' % LOCAL_JS_DIR)
    local('git add %s/jquery-ui.js' % LOCAL_JS_DIR)
    local('git add %s/jquery.tablesorter.min.js' % LOCAL_JS_DIR)
    local('git add %s/jquery.tablesorter.pager.min.js' % LOCAL_JS_DIR)
    local('git add %s/leaflet.js' % LOCAL_JS_DIR)
    local('git add %s/lens.js' % LOCAL_JS_DIR)
    local('git add %s/map.js' % LOCAL_JS_DIR)
    local('git add %s/mapbox.uncompressed.js' % LOCAL_JS_DIR)
    local('git add %s/modernizr.js' % LOCAL_JS_DIR)
    local('git add %s/neighborhoods-topo.js' % LOCAL_JS_DIR)
    local('git add %s/neighborhoods-topo.min.js' % LOCAL_JS_DIR)
    local('git add %s/sale.js' % LOCAL_JS_DIR)
    local('git add %s/search.js' % LOCAL_JS_DIR)
    local('git add %s/search-area.js' % LOCAL_JS_DIR)


def doitall():
    '''Run through entire deployment.'''

    data()
    repo()
    app()
    scripts()
    tests()
    lib()
    templates()
    js()
    css()
    images()
    fonts()


def python():
    '''Deploy all *.py files.'''

    app()
    scripts()
    lib()


if __name__ == '__main__':
    pass
