from fabric.api import local
from landrecords import config


def configuration():
    local('scp %s/config.py tom@%s:%s' % (
        config.PROJECT_DIR, config.SERVER_NAME, config.SERVER_PROJECT_PATH))


def git_ignore():
    local('scp %s/.gitignore ' % (config.PROJECT_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_LIB_DIR))


def templates():
    local('scp %s/404.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/banner.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/dashboard.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/footer.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/head.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/index.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/js.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/sale.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/search.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/searchArea.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))
    local('scp %s/table.html tom@%s:%s' % (
        config.LOCAL_TEMPLATE_DIR, config.SERVER_NAME,
        config.SERVER_TEMPLATE_DIR))


def lib():
    local('scp %s/build.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/check_assessor_urls.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/check_temp_status.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/clean.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/dashboard_sync.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/email_template.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/geocode.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/libraries.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/log.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/mail.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/parsers.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/publish.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/scrape.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/stat_analysis.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/utils.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))
    local('scp %s/webhook.py tom@%s:%s' % (
        config.LOCAL_LIB_DIR, config.SERVER_NAME, config.SERVER_LIB_DIR))


def css():
    '''
    S3
    '''

    local('aws s3 cp %s/font-awesome.css ' % (config.LOCAL_CSS_DIR) +
          '%s/css/font-awesome.css --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/foundation.min.css ' % (config.LOCAL_CSS_DIR) +
          '%s/' % (config.S3_PATH) +
          'css/foundation.min.css --acl public-read')
    local('aws s3 cp %s/jquery-ui.css ' % (config.LOCAL_CSS_DIR) +
          '%s/css/jquery-ui.css --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_CSS_DIR) +
          'jquery.tablesorter.pager.css ' +
          '%s/' % (config.S3_PATH) +
          'css/jquery.tablesorter.pager.css --acl public-read')
    local('aws s3 cp %s/lens.css ' % (config.LOCAL_CSS_DIR) +
          '%s/css/lens.css --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/lenstablesorter.css ' % (config.LOCAL_CSS_DIR) +
          '%s/' % (config.S3_PATH) +
          'css/lenstablesorter.css --acl public-read')
    local('aws s3 cp %s/mapbox.css ' % (config.LOCAL_CSS_DIR) +
          '%s/css/mapbox.css --acl public-read' % (config.S3_PATH))

    '''
    Server
    '''

    local('scp %s/font-awesome.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/foundation.min.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/jquery-ui.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/jquery.tablesorter.pager.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/lens.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/lenstablesorter.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))
    local('scp %s/mapbox.css tom@%s:%s' % (
        config.LOCAL_CSS_DIR, config.SERVER_NAME, config.SERVER_CSS_DIR))


def images():
    '''
    S3
    '''

    local('aws s3 cp %s/ajax-loader.gif ' % (config.LOCAL_IMAGES_DIR) +
          '%s/ajax-loader.gif --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/black-asc.gif ' % (config.LOCAL_IMAGES_DIR) +
          '%s/black-asc.gif --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/black-desc.gif ' % (config.LOCAL_IMAGES_DIR) +
          '%s/black-desc.gif --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_IMAGES_DIR) +
          'black-unsorted.gif ' +
          '%s/black-unsorted.gif --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/favicon.ico ' % (config.LOCAL_IMAGES_DIR) +
          '%s/favicon.ico --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/first.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/first.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/icons-000000.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/icons-000000.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_IMAGES_DIR) +
          'icons-000000@2x.png ' +
          '%s/icons-000000@2x.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/info-i.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/info-i.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/last.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/last.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_IMAGES_DIR) +
          'lens-logo-retina.png ' +
          '%s/lens-logo-retina.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          '%s/lens-logo-magnifying-glass-only.png ' % (config.S3_PATH) +
          '--acl public-read')
    local('aws s3 cp %s/next.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/next.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/prev.png ' % (config.LOCAL_IMAGES_DIR) +
          '%s/prev.png --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          '%s/' % (config.S3_PATH) +
          'ui-bg_flat_75_ffffff_40x100.png --acl public-read')

    '''
    Server
    '''

    local('scp %s/ajax-loader.gif ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/black-asc.gif ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/black-desc.gif ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/black-unsorted.gif ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/favicon.ico ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/first.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/icons-000000.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/icons-000000@2x.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/info-i.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/last.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/lens-logo-retina.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/' % (config.LOCAL_IMAGES_DIR) +
          'lens-logo-magnifying-glass-only.png ' +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/next.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/prev.png ' % (config.LOCAL_IMAGES_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))
    local('scp %s/' % (config.LOCAL_IMAGES_DIR) +
          'ui-bg_flat_75_ffffff_40x100.png ' +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_IMAGES_DIR))


def fonts():
    '''
    S3
    '''
    local('aws s3 cp %s/' % (config.LOCAL_FONTS_DIR) +
          'fontawesome-webfont.eot ' +
          '%s/' % (config.S3_PATH) +
          'fontawesome-webfont.eot --acl public-read')
    local('aws s3 cp %s/' % (config.LOCAL_FONTS_DIR) +
          'fontawesome-webfont.svg ' +
          '%s/' % (config.S3_PATH) +
          'fontawesome-webfont.svg --acl public-read')
    local('aws s3 cp %s/' % (config.LOCAL_FONTS_DIR) +
          'fontawesome-webfont.ttf ' +
          '%s/' % (config.S3_PATH) +
          'fontawesome-webfont.ttf --acl public-read')
    local('aws s3 cp %s/' % (config.LOCAL_FONTS_DIR) +
          'fontawesome-webfont.woff ' +
          '%s/' % (config.S3_PATH) +
          'fontawesome-webfont.woff --acl public-read')
    local('aws s3 cp %s/FontAwesome.otf ' % (config.LOCAL_FONTS_DIR) +
          '%s/FontAwesome.otf --acl public-read' % (config.S3_PATH))

    '''
    Server
    '''
    local('scp %s/fontawesome-webfont.eot ' % (config.LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.svg ' % (config.LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.ttf ' % (config.LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_FONTS_DIR))
    local('scp %s/fontawesome-webfont.woff ' % (config.LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_FONTS_DIR))
    local('scp %s/FontAwesome.otf ' % (config.LOCAL_FONTS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_FONTS_DIR))


def js():
    '''
    S3
    '''

    local('aws s3 cp %s/dashboard.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/dashboard.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/foundation.min.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/foundation.min.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/foundation.tooltip.js ' % (config.LOCAL_JS_DIR) +
          '%s/' % (config.S3_PATH) +
          'js/foundation.tooltip.js --acl public-read')
    local('aws s3 cp %s/index.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/index.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/jquery-1.11.0.min.js ' % (config.LOCAL_JS_DIR) +
          '%s/' % (config.S3_PATH) +
          'js/jquery-1.11.0.min.js --acl public-read')
    local('aws s3 cp %s/jquery-ui.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/jquery-ui.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_JS_DIR) +
          'jquery.tablesorter.min.js ' +
          '%s/' % (config.S3_PATH) +
          'js/jquery.tablesorter.min.js --acl public-read')
    local('aws s3 cp %s/' % (config.LOCAL_JS_DIR) +
          'jquery.tablesorter.pager.min.js ' +
          '%s/' % (config.S3_PATH) +
          'js/jquery.tablesorter.pager.min.js --acl public-read')
    local('aws s3 cp %s/leaflet.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/leaflet.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/lens.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/lens.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/map.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/map.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/' % (config.LOCAL_JS_DIR) +
          'mapbox.uncompressed.js ' +
          '%s/' % (config.S3_PATH) +
          'js/mapbox.uncompressed.js --acl public-read')
    local('aws s3 cp %s/modernizr.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/modernizr.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/neighborhoods-topo.js ' % (config.LOCAL_JS_DIR) +
          '%s/' % (config.S3_PATH) +
          'js/neighborhoods-topo.js --acl public-read')
    local('aws s3 cp %s/' % (config.LOCAL_JS_DIR) +
          'neighborhoods-topo.min.js ' +
          '%s/' % (config.S3_PATH) +
          'js/neighborhoods-topo.min.js --acl public-read')
    local('aws s3 cp %s/sale.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/sale.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/search.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/search.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/searchArea.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/searchArea.js --acl public-read' % (config.S3_PATH))
    local('aws s3 cp %s/squares-topo.js ' % (config.LOCAL_JS_DIR) +
          '%s/js/squares-topo.js --acl public-read' % (config.S3_PATH))

    '''
    Server
    '''

    local('scp %s/dashboard.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/foundation.min.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/foundation.tooltip.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/index.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/jquery-1.11.0.min.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/jquery-ui.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.min.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/jquery.tablesorter.pager.min.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/leaflet.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/lens.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/mapbox.uncompressed.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/modernizr.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/neighborhoods-topo.min.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/sale.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/search.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))
    local('scp %s/squares-topo.js ' % (config.LOCAL_JS_DIR) +
          'tom@%s:%s' % (config.SERVER_NAME, config.SERVER_JS_DIR))


def doitall():
    lib()
    templates()
    js()
    css()
    images()
    fonts()
    git_ignore()
    # configuration()


def s3():
    '''Copy static assets to S3'''
