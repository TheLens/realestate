from fabric.api import local
from landrecords.config import Config


def config():
    local('scp %s/config.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR,
        Config().SERVER_NAME,
        Config().SERVER_APP_DIR))


def git_ignore():
    local('scp %s/.gitignore ' % (Config().LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_PROJECT_DIR))


def init():
    local('scp %s/initialize.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))


def log():
    local('scp %s/log.py tom@%s:%s' % (Config().LOCAL_LIB_DIR,
                                       Config().SERVER_NAME,
                                       Config().SERVER_LIB_DIR))


def mail():
    local('scp %s/mail.py tom@%s:%s' % (Config().LOCAL_LIB_DIR,
                                        Config().SERVER_NAME,
                                        Config().SERVER_LIB_DIR))


def scrape():
    local('scp %s/scrape.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))


def build():
    local('scp %s/build.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))


def clean():
    local('scp %s/clean.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))


def data():
    local('scp %s/assessor-error-html/error.html tom@%s:%s' % (
        Config().LOCAL_DATA_DIR, Config().SERVER_NAME,
        Config().SERVER_DATA_DIR))


def repo():
    local('scp %s/.gitignore ' % (Config().LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_PROJECT_DIR))
    local('scp %s/README.md ' % (Config().LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_PROJECT_DIR))
    local('scp %s/requirements.txt ' % (Config().LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_PROJECT_DIR))
    local('scp %s/trifecta.sh ' % (Config().LOCAL_PROJECT_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_PROJECT_DIR))


def app():
    local('scp %s/__init__.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))
    local('scp %s/app.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))
    local('scp %s/config.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))
    local('scp %s/db.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))
    local('scp %s/models.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))
    local('scp %s/views.py tom@%s:%s' % (
        Config().LOCAL_APP_DIR, Config().SERVER_NAME,
        Config().SERVER_APP_DIR))


def scripts():
    local('scp %s/backup.sh tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/create_neighborhood_geojson.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/delete_db.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/initialize.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/make_db.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/scrape.sh tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/screen.js tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/screen.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))
    local('scp %s/tserver.py tom@%s:%s' % (
        Config().LOCAL_SCRIPTS_DIR, Config().SERVER_NAME,
        Config().SERVER_SCRIPTS_DIR))


def tests():
    local('scp %s/__init__.py tom@%s:%s' % (
        Config().LOCAL_TESTS_DIR, Config().SERVER_NAME,
        Config().SERVER_TESTS_DIR))
    local('scp %s/test_pep8.py tom@%s:%s' % (
        Config().LOCAL_TESTS_DIR, Config().SERVER_NAME,
        Config().SERVER_TESTS_DIR))
    local('scp %s/test_pylint.py tom@%s:%s' % (
        Config().LOCAL_TESTS_DIR, Config().SERVER_NAME,
        Config().SERVER_TESTS_DIR))


def templates():
    local('scp %s/404.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/banner.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/dashboard.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/footer.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/head.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/index.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/js.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/sale.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/search.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/search-area.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))
    local('scp %s/table.html tom@%s:%s' % (
        Config().LOCAL_TEMPLATE_DIR, Config().SERVER_NAME,
        Config().SERVER_TEMPLATE_DIR))


def lib():
    local('scp %s/__init__.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME,
        Config().SERVER_LIB_DIR))
    local('scp %s/build.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/check_assessor_urls.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/check_temp_status.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/clean.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR,
        Config().SERVER_NAME,
        Config().SERVER_LIB_DIR)
    )
    local('scp %s/dashboard_sync.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/email_template.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/geocode.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/libraries.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/log.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/mail.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/parse.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/publish.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/scrape.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/stat_analysis.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/utils.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))
    local('scp %s/webhook.py tom@%s:%s' % (
        Config().LOCAL_LIB_DIR, Config().SERVER_NAME, Config().SERVER_LIB_DIR))


def css():
    '''
    S3
    '''

    local('aws s3 cp %s/font-awesome.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/css/font-awesome.css --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/foundation.min.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/' % (Config().S3_PATH) +
          'css/foundation.min.css --acl public-read')
    local('aws s3 cp %s/jquery-ui.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/css/jquery-ui.css --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_CSS_DIR) +
          'jquery.tablesorter.pager.css ' +
          '%s/' % (Config().S3_PATH) +
          'css/jquery.tablesorter.pager.css --acl public-read')
    local('aws s3 cp %s/lens.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/css/lens.css --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/lenstablesorter.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/' % (Config().S3_PATH) +
          'css/lenstablesorter.css --acl public-read')
    local('aws s3 cp %s/mapbox.css ' % (Config().LOCAL_CSS_DIR) +
          '%s/css/mapbox.css --acl public-read' % (Config().S3_PATH))

    '''
    Server
    '''

    local('scp %s/font-awesome.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/foundation.min.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/jquery-ui.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/jquery.tablesorter.pager.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/lens.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/lenstablesorter.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))
    local('scp %s/mapbox.css tom@%s:%s' % (
        Config().LOCAL_CSS_DIR, Config().SERVER_NAME, Config().SERVER_CSS_DIR))


def images():
    '''
    S3
    '''

    local('aws s3 cp %s/favicon.ico ' % (Config().LOCAL_IMAGES_DIR) +
          '%s/favicon.ico --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/icons-000000.png ' % (Config().LOCAL_IMAGES_DIR) +
          '%s/icons-000000.png --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'icons-000000@2x.png ' +
          '%s/icons-000000@2x.png --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'lens-logo-retina.png ' +
          '%s/lens-logo-retina.png --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          '%s/lens-logo-magnifying-glass-only.png ' % (Config().S3_PATH) +
          '--acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          '%s/' % (Config().S3_PATH) +
          'ui-bg_flat_75_ffffff_40x100.png --acl public-read')

    '''
    Server
    '''

    local('scp %s/favicon.ico ' % (Config().LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))
    local('scp %s/icons-000000.png ' % (Config().LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))
    local('scp %s/icons-000000@2x.png ' % (Config().LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))
    local('scp %s/lens-logo-retina.png ' % (Config().LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))
    local('scp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))
    local('scp %s/' % (Config().LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_IMAGES_DIR))


def fonts():
    '''
    S3
    '''
    local('aws s3 cp %s/' % (Config().LOCAL_FONTS_DIR) +
          'fontawesome-webfont.eot ' +
          '%s/' % (Config().S3_PATH) +
          'fontawesome-webfont.eot --acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_FONTS_DIR) +
          'fontawesome-webfont.svg ' +
          '%s/' % (Config().S3_PATH) +
          'fontawesome-webfont.svg --acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_FONTS_DIR) +
          'fontawesome-webfont.ttf ' +
          '%s/' % (Config().S3_PATH) +
          'fontawesome-webfont.ttf --acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_FONTS_DIR) +
          'fontawesome-webfont.woff ' +
          '%s/' % (Config().S3_PATH) +
          'fontawesome-webfont.woff --acl public-read')
    local('aws s3 cp %s/FontAwesome.otf ' % (Config().LOCAL_FONTS_DIR) +
          '%s/FontAwesome.otf --acl public-read' % (Config().S3_PATH))

    '''
    Server
    '''
    local('scp %s/fontawesome-webfont.eot ' % (Config().LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.svg ' % (Config().LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.ttf ' % (Config().LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.woff ' % (Config().LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_FONTS_DIR))
    local('scp %s/FontAwesome.otf ' % (Config().LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_FONTS_DIR))


def js():
    '''
    S3
    '''

    local('aws s3 cp %s/dashboard.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/dashboard.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/foundation.min.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/foundation.min.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/foundation.tooltip.js ' % (Config().LOCAL_JS_DIR) +
          '%s/' % (Config().S3_PATH) +
          'js/foundation.tooltip.js --acl public-read')
    local('aws s3 cp %s/index.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/index.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/jquery-1.11.0.min.js ' % (Config().LOCAL_JS_DIR) +
          '%s/' % (Config().S3_PATH) +
          'js/jquery-1.11.0.min.js --acl public-read')
    local('aws s3 cp %s/jquery-ui.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/jquery-ui.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_JS_DIR) +
          'jquery.tablesorter.min.js ' +
          '%s/' % (Config().S3_PATH) +
          'js/jquery.tablesorter.min.js --acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_JS_DIR) +
          'jquery.tablesorter.pager.min.js ' +
          '%s/' % (Config().S3_PATH) +
          'js/jquery.tablesorter.pager.min.js --acl public-read')
    local('aws s3 cp %s/leaflet.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/leaflet.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/lens.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/lens.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/map.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/map.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/' % (Config().LOCAL_JS_DIR) +
          'mapbox.uncompressed.js ' +
          '%s/' % (Config().S3_PATH) +
          'js/mapbox.uncompressed.js --acl public-read')
    local('aws s3 cp %s/modernizr.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/modernizr.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/neighborhoods-topo.js ' % (Config().LOCAL_JS_DIR) +
          '%s/' % (Config().S3_PATH) +
          'js/neighborhoods-topo.js --acl public-read')
    local('aws s3 cp %s/' % (Config().LOCAL_JS_DIR) +
          'neighborhoods-topo.min.js ' +
          '%s/' % (Config().S3_PATH) +
          'js/neighborhoods-topo.min.js --acl public-read')
    local('aws s3 cp %s/sale.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/sale.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/search.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/search.js --acl public-read' % (Config().S3_PATH))
    local('aws s3 cp %s/search-area.js ' % (Config().LOCAL_JS_DIR) +
          '%s/js/search-area.js --acl public-read' % (Config().S3_PATH))

    '''
    Server
    '''

    local('scp %s/dashboard.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/foundation.min.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/foundation.tooltip.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/index.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/jquery-1.11.0.min.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/jquery-ui.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.min.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.pager.min.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/leaflet.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/lens.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/map.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/mapbox.uncompressed.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/modernizr.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.min.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/sale.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/search.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))
    local('scp %s/search-area.js ' % (Config().LOCAL_JS_DIR) +
          'tom@%s:%s' % (Config().SERVER_NAME, Config().SERVER_JS_DIR))


def doitall():
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


def s3():
    '''Copy static assets to S3'''
