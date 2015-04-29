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
    LOCAL_TESTS_DIR,
    SERVER_NAME,
    SERVER_APP_DIR,
    SERVER_CSS_DIR,
    SERVER_DATA_DIR,
    SERVER_FONTS_DIR,
    SERVER_IMAGES_DIR,
    SERVER_JS_DIR,
    SERVER_LIB_DIR,
    SERVER_PROJECT_DIR,
    SERVER_SCRIPTS_DIR,
    SERVER_TEMPLATE_DIR,
    SERVER_TESTS_DIR,
    S3_PATH
)


def config():
    '''config.py'''

    local('scp %s/config.py tom@%s:%s' % (
        LOCAL_APP_DIR,
        SERVER_NAME,
        SERVER_APP_DIR))


def delete_dates():
    '''realestate/lib/delete_dates.py'''

    local('scp %s/delete_dates.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def git_ignore():
    '''.gitignore'''

    local('scp %s/.gitignore ' % (LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_PROJECT_DIR))


def geocode():
    local('scp %s/geocode.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def init():
    '''initialize.py'''

    local('scp %s/initialize.py tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))


def mail():
    '''mail.py'''

    local('scp %s/mail.py tom@%s:%s' % (LOCAL_LIB_DIR,
                                        SERVER_NAME,
                                        SERVER_LIB_DIR))


def scrape():
    '''scrape.py'''

    local('scp %s/scrape.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def build():
    '''build.py'''

    local('scp %s/build.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def clean():
    '''clean.py'''

    local('scp %s/clean.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def data():
    '''Data files'''

    local('scp %s/assessor-error-html/assessor_error.html tom@%s:%s' % (
        LOCAL_DATA_DIR, SERVER_NAME,
        SERVER_DATA_DIR))
    local('scp %s/sale-error-html/sale_error.html tom@%s:%s' % (
        LOCAL_DATA_DIR, SERVER_NAME,
        SERVER_DATA_DIR))


def repo():
    '''/'''

    local('scp %s/.gitignore ' % (LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_PROJECT_DIR))
    local('scp %s/README.md ' % (LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_PROJECT_DIR))
    local('scp %s/requirements.txt ' % (LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_PROJECT_DIR))
    local('scp %s/trifecta.sh ' % (LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_PROJECT_DIR))


def app():
    '''/realestate/'''

    local('scp %s/__init__.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))
    local('scp %s/app.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))
    local('scp %s/config.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))
    local('scp %s/db.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))
    local('scp %s/models.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))
    local('scp %s/views.py tom@%s:%s' % (
        LOCAL_APP_DIR, SERVER_NAME,
        SERVER_APP_DIR))


def scripts():
    '''/scripts/'''

    local('scp %s/backup.sh tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/delete_db.py tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/initialize.py tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/main.sh tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/make_db.py tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/screen.js tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))
    local('scp %s/tserver.py tom@%s:%s' % (
        LOCAL_SCRIPTS_DIR, SERVER_NAME,
        SERVER_SCRIPTS_DIR))


def tests():
    '''/tests/'''

    local('scp %s/__init__.py tom@%s:%s' % (
        LOCAL_TESTS_DIR, SERVER_NAME,
        SERVER_TESTS_DIR))
    local('scp %s/test_pep8.py tom@%s:%s' % (
        LOCAL_TESTS_DIR, SERVER_NAME,
        SERVER_TESTS_DIR))
    local('scp %s/test_pylint.py tom@%s:%s' % (
        LOCAL_TESTS_DIR, SERVER_NAME,
        SERVER_TESTS_DIR))


def templates():
    '''/realestate/templates'''

    local('scp %s/404.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/banner.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/dashboard.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/footer.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/head.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/index.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/js.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/sale.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/search.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/search-area.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))
    local('scp %s/table.html tom@%s:%s' % (
        LOCAL_TEMPLATE_DIR, SERVER_NAME,
        SERVER_TEMPLATE_DIR))


def lib():
    '''/realestate/lib'''

    local('scp %s/__init__.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME,
        SERVER_LIB_DIR))
    local('scp %s/build.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/build_assessor_urls.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/check_assessor_urls.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/check_temp_status.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/clean.py tom@%s:%s' % (
        LOCAL_LIB_DIR,
        SERVER_NAME,
        SERVER_LIB_DIR))
    local('scp %s/dashboard_sync.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/delete_dates.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/email_template.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/form_tweet.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/geocode.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/get_dates.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/libraries.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/mail.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/parse.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/publish.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/results_language.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/scrape.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/stat_analysis.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/twitter.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/utils.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))
    local('scp %s/webhook.py tom@%s:%s' % (
        LOCAL_LIB_DIR, SERVER_NAME, SERVER_LIB_DIR))


def css():
    '''/realestate/static/css'''

    # S3
    local('aws s3 cp %s/banner.css ' % (LOCAL_CSS_DIR) +
          '%s/css/banner.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/font-awesome.css ' % (LOCAL_CSS_DIR) +
          '%s/css/font-awesome.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/foundation.min.css ' % (LOCAL_CSS_DIR) +
          '%s/' % (S3_PATH) +
          'css/foundation.min.css --acl public-read')
    local('aws s3 cp %s/jquery-ui.css ' % (LOCAL_CSS_DIR) +
          '%s/css/jquery-ui.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/' % (LOCAL_CSS_DIR) +
          'jquery.tablesorter.pager.css ' +
          '%s/' % (S3_PATH) +
          'css/jquery.tablesorter.pager.css --acl public-read')
    local('aws s3 cp %s/realestate.css ' % (LOCAL_CSS_DIR) +
          '%s/css/realestate.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/lens.css ' % (LOCAL_CSS_DIR) +
          '%s/css/lens.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/lenstablesorter.css ' % (LOCAL_CSS_DIR) +
          '%s/' % (S3_PATH) +
          'css/lenstablesorter.css --acl public-read')
    local('aws s3 cp %s/mapbox.css ' % (LOCAL_CSS_DIR) +
          '%s/css/mapbox.css --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/table.css ' % (LOCAL_CSS_DIR) +
          '%s/css/table.css --acl public-read' % (S3_PATH))

    # Server
    local('scp %s/banner.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/font-awesome.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/foundation.min.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/jquery-ui.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/jquery.tablesorter.pager.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/realestate.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/lens.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/lenstablesorter.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/mapbox.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))
    local('scp %s/table.css tom@%s:%s' % (
        LOCAL_CSS_DIR, SERVER_NAME, SERVER_CSS_DIR))


def images():
    '''/realestate/static/css/images'''

    # S3
    local('aws s3 cp %s/corporate-realty.jpg ' % (LOCAL_IMAGES_DIR) +
          '%s/css/images/' % (S3_PATH) +
          'corporate-realty.jpg --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'corporate-realty-large.jpg ' +
          '%s/css/images/' % (S3_PATH) +
          'corporate-realty-large.jpg --acl public-read')
    local('aws s3 cp %s/corporate-realty.png ' % (LOCAL_IMAGES_DIR) +
          '%s/css/images/' % (S3_PATH) +
          'corporate-realty.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'corporate-realty-large.png ' +
          '%s/css/images/' % (S3_PATH) +
          'corporate-realty-large.png --acl public-read')
    local('aws s3 cp %s/favicon.ico ' % (LOCAL_IMAGES_DIR) +
          '%s/css/images/favicon.ico --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/icons-000000.png ' % (LOCAL_IMAGES_DIR) +
          '%s/css/images/' % (S3_PATH) +
          'icons-000000.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'icons-000000@2x.png ' +
          '%s/css/images/' % (S3_PATH) +
          'icons-000000@2x.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'lens-logo-retina.png ' +
          '%s/css/images/' % (S3_PATH) +
          'lens-logo-retina.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          '%s/css/images/' % (S3_PATH) +
          'lens-logo-magnifying-glass-only.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_flat_75_ffffff_40x100.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_55_fbf9ee_1x400.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_glass_55_fbf9ee_1x400.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_75_dadada_1x400.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_glass_75_dadada_1x400.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_75_e6e6e6_1x400.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_glass_75_e6e6e6_1x400.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_highlight-soft_75_cccccc_1x100.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_highlight-soft_75_cccccc_1x100.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_65_ffffff_1x400.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-bg_glass_65_ffffff_1x400.png --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-icons_454545_256x240.png ' +
          '%s/css/images/' % (S3_PATH) +
          'ui-icons_454545_256x240.png --acl public-read')

    # Server
    local('scp %s/corporate-realty.jpg ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/corporate-realty-large.jpg ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/corporate-realty.png ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/corporate-realty-large.png ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/favicon.ico ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/icons-000000.png ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/icons-000000@2x.png ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/lens-logo-retina.png ' % (LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_55_fbf9ee_1x400.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_75_dadada_1x400.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_75_e6e6e6_1x400.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_highlight-soft_75_cccccc_1x100.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-bg_glass_65_ffffff_1x400.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))
    local('scp %s/' % (LOCAL_IMAGES_DIR) +
          'ui-icons_454545_256x240.png ' +
          'tom@%s:%s' % (SERVER_NAME, SERVER_IMAGES_DIR))


def fonts():
    '''/realestate/static/fonts'''

    # S3
    local('aws s3 cp %s/' % (LOCAL_FONTS_DIR) +
          'fontawesome-webfont.eot ' +
          '%s/fonts/' % (S3_PATH) +
          'fontawesome-webfont.eot --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_FONTS_DIR) +
          'fontawesome-webfont.svg ' +
          '%s/fonts/' % (S3_PATH) +
          'fontawesome-webfont.svg --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_FONTS_DIR) +
          'fontawesome-webfont.ttf ' +
          '%s/fonts/' % (S3_PATH) +
          'fontawesome-webfont.ttf --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_FONTS_DIR) +
          'fontawesome-webfont.woff ' +
          '%s/fonts/' % (S3_PATH) +
          'fontawesome-webfont.woff --acl public-read')
    local('aws s3 cp %s/FontAwesome.otf ' % (LOCAL_FONTS_DIR) +
          '%s/fonts/FontAwesome.otf --acl public-read' % (S3_PATH))

    # Server
    local('scp %s/fontawesome-webfont.eot ' % (LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.svg ' % (LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.ttf ' % (LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.woff ' % (LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_FONTS_DIR))
    local('scp %s/FontAwesome.otf ' % (LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_FONTS_DIR))


def js():
    '''/realestate/static/js'''

    # S3
    local('aws s3 cp %s/dashboard.js ' % (LOCAL_JS_DIR) +
          '%s/js/dashboard.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/foundation.min.js ' % (LOCAL_JS_DIR) +
          '%s/js/foundation.min.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/foundation.tooltip.js ' % (LOCAL_JS_DIR) +
          '%s/' % (S3_PATH) +
          'js/foundation.tooltip.js --acl public-read')
    local('aws s3 cp %s/index.js ' % (LOCAL_JS_DIR) +
          '%s/js/index.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/jquery-1.11.0.min.js ' % (LOCAL_JS_DIR) +
          '%s/' % (S3_PATH) +
          'js/jquery-1.11.0.min.js --acl public-read')
    local('aws s3 cp %s/jquery-ui.js ' % (LOCAL_JS_DIR) +
          '%s/js/jquery-ui.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/' % (LOCAL_JS_DIR) +
          'jquery.tablesorter.min.js ' +
          '%s/' % (S3_PATH) +
          'js/jquery.tablesorter.min.js --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_JS_DIR) +
          'jquery.tablesorter.pager.min.js ' +
          '%s/' % (S3_PATH) +
          'js/jquery.tablesorter.pager.min.js --acl public-read')
    local('aws s3 cp %s/leaflet.js ' % (LOCAL_JS_DIR) +
          '%s/js/leaflet.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/lens.js ' % (LOCAL_JS_DIR) +
          '%s/js/lens.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/map.js ' % (LOCAL_JS_DIR) +
          '%s/js/map.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/' % (LOCAL_JS_DIR) +
          'mapbox.uncompressed.js ' +
          '%s/' % (S3_PATH) +
          'js/mapbox.uncompressed.js --acl public-read')
    local('aws s3 cp %s/modernizr.js ' % (LOCAL_JS_DIR) +
          '%s/js/modernizr.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/neighborhoods-topo.js ' % (LOCAL_JS_DIR) +
          '%s/' % (S3_PATH) +
          'js/neighborhoods-topo.js --acl public-read')
    local('aws s3 cp %s/' % (LOCAL_JS_DIR) +
          'neighborhoods-topo.min.js ' +
          '%s/' % (S3_PATH) +
          'js/neighborhoods-topo.min.js --acl public-read')
    local('aws s3 cp %s/sale.js ' % (LOCAL_JS_DIR) +
          '%s/js/sale.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/search.js ' % (LOCAL_JS_DIR) +
          '%s/js/search.js --acl public-read' % (S3_PATH))
    local('aws s3 cp %s/search-area.js ' % (LOCAL_JS_DIR) +
          '%s/js/search-area.js --acl public-read' % (S3_PATH))

    # Server
    local('scp %s/dashboard.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/foundation.min.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/foundation.tooltip.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/index.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/jquery-1.11.0.min.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/jquery-ui.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.min.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.pager.min.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/leaflet.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/lens.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/map.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/mapbox.uncompressed.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/modernizr.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.min.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/sale.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/search.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))
    local('scp %s/search-area.js ' % (LOCAL_JS_DIR) +
          'tom@%s:%s' % (SERVER_NAME, SERVER_JS_DIR))


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
    git_ignore()
    config()


def python():
    '''Deploy all *.py files.'''

    app()
    scripts()
    lib()


def s3():
    '''Copy static assets to S3.'''
    pass

if __name__ == '__main__':
    pass
