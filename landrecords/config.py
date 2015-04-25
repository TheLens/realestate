# -*- coding: utf-8 -*-

'''KEEP THIS PRIVATE'''

from datetime import date, timedelta
import getpass


class Config(object):

    '''
    Stores passwords, common variables and anything that needs to be kept as a
    variable in order to make the local app compatible with the server version.
    '''

    def __init__(self):
        '''Create self variables.'''

        self.USER = getpass.getuser()

        if self.USER == 'thomasthoren':  # Check if local
            self.SERVER_ENGINE = 'postgresql://myuser:' + \
                'mypass@localhost/landrecords'
            self.SERVER_CONNECTION = 'dbname=landrecords user=myuser'
            self.DATABASE_NAME = 'landrecords'

            self.PROJECT_DIR = '/Users/thomasthoren/projects/' + \
                'land-records/repo'
            self.BACKUP_DIR = '/Users/thomasthoren/projects/land-records/' + \
                'repo/backups'
            self.DATA_DIR = '/Users/thomasthoren/projects/land-records/' + \
                'repo/data'
            self.LOG_DIR = '/Users/thomasthoren/projects/land-records/' + \
                'repo/logs'
            self.LIB_DIR = '/Users/thomasthoren/projects/' + \
                'land-records/repo/landrecords/lib'
            self.GEO_DIR = '/Users/thomasthoren/projects/geographic-data/repo'
            self.PICTURES_DIR = '/Users/thomasthoren/projects/' + \
                'land-records/repo/landrecords/static/pictures'
            self.SCRIPTS_DIR = '/Users/thomasthoren/projects/' + \
                'land-records/repo/scripts'

            self.PROJECT_URL = 'http://localhost:5000/realestate'

            self.APP_ROUTING = '/realestate'
            self.JS_APP_ROUTING = '/realestate'

            # Static assets
            self.JS = '/static/js/lens.js'
            self.SEARCH_AREA_JS = '/static/js/search-area.js'
            self.INDEX_JS = "/static/js/index.js"
            self.SEARCH_JS = "/static/js/search.js"
            self.MAP_JS = "/static/js/map.js"
            self.SALE_JS = "/static/js/sale.js"
            self.DASHBOARD_JS = "/static/js/dashboard.js"
            self.NEIGHBORHOODS_TOPO = "/static/js/neighborhoods-topo.min.js"
            self.SQUARES_TOPO = "/static/js/squares-topo.js"

            self.LENS_CSS = "/static/css/lens.css"
            self.LANDRECORDS_CSS = "/static/css/landrecords.css"
            self.BANNER_CSS = "/static/css/banner.css"
            self.TABLE_CSS = "/static/css/table.css"

            self.RELOADER = True
            self.DEBUG = True

        else:  # Server
            self.SERVER_ENGINE = 'postgresql://myuser:mypass@' + \
                'localhost:5432/landrecords'
            self.SERVER_CONNECTION = 'dbname=landrecords user=myuser ' + \
                'password=mypass'
            self.DATABASE_NAME = 'landrecords'

            self.PROJECT_DIR = '/apps/land-records/repo'
            self.BACKUP_DIR = '/backups/land-records'
            self.DATA_DIR = '/apps/land-records/repo/data'
            self.LOG_DIR = '/apps/land-records/repo/logs'
            self.LIB_DIR = '/apps/land-records/repo' + \
                '/landrecords/lib'
            self.GEO_DIR = '/apps/geographic-data/repo'
            self.PICTURES_DIR = '/apps/land-records/repo' + \
                '/landrecords/static/pictures'
            self.SCRIPTS_DIR = '/apps/land-records/repo/scripts'

            self.PROJECT_URL = 'http://vault.thelensnola.org/realestate'

            self.APP_ROUTING = ''
            self.JS_APP_ROUTING = '/realestate'

            # Static assets
            self.JS = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/js/lens.js"
            self.SEARCH_AREA_JS = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/js/search-area.js"
            self.INDEX_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/js/index.js"
            self.SEARCH_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/js/search.js"
            self.MAP_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/js/map.js"
            self.SALE_JS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/js/sale.js"
            self.DASHBOARD_JS = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/js/dashboard.js"
            self.NEIGHBORHOODS_TOPO = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/js/neighborhoods-topo.min.js"
            self.SQUARES_TOPO = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/js/squares-topo.js"

            self.LENS_CSS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/css/lens.css"
            self.LANDRECORDS_CSS = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/css/landrecords.css"
            self.BANNER_CSS = "https://s3-us-west-2.amazonaws.com/" + \
                "lensnola/land-records/css/banner.css"
            self.TABLE_CSS = "https://s3-us-west-2.amazonaws.com/lensnola/" + \
                "land-records/css/table.css"

            self.RELOADER = True
            self.DEBUG = True

        # Stuff that is permanent, such as for fabfile deployment
        self.SERVER_NAME = 'vault.thelensnola.org'

        self.LOCAL_PROJECT_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo'
        self.LOCAL_APP_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords'
        self.LOCAL_DATA_DIR = '/Users/thomasthoren/projects/land-records/' + \
            'repo/data'
        self.LOCAL_SCRIPTS_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/scripts'
        self.LOCAL_TESTS_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/tests'
        self.LOCAL_TEMPLATE_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/templates'
        self.LOCAL_LIB_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/lib'
        self.LOCAL_CSS_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/static/css'
        self.LOCAL_JS_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/static/js'
        self.LOCAL_FONTS_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/static/fonts'
        self.LOCAL_IMAGES_DIR = '/Users/thomasthoren/projects/' + \
            'land-records/repo/landrecords/static/css/images'

        self.SERVER_PROJECT_DIR = '/apps/land-records/repo'
        self.SERVER_APP_DIR = '/apps/land-records/repo/landrecords'
        self.SERVER_DATA_DIR = '/apps/land-records/repo/data'
        self.SERVER_SCRIPTS_DIR = '/apps/land-records/repo/scripts'
        self.SERVER_TESTS_DIR = '/apps/land-records/repo/tests'
        self.SERVER_TEMPLATE_DIR = '/apps/land-records/repo' + \
            '/landrecords/templates'
        self.SERVER_LIB_DIR = '/apps/land-records/repo' + \
            '/landrecords/lib'
        self.SERVER_CSS_DIR = '/apps/land-records/repo' + \
            '/landrecords/static/css'
        self.SERVER_JS_DIR = '/apps/land-records/repo' + \
            '/landrecords/static/js'
        self.SERVER_FONTS_DIR = '/apps/land-records/repo' + \
            '/landrecords/static/fonts'
        self.SERVER_IMAGES_DIR = '/apps/land-records' + \
            '/repo/landrecords/static/css/images'

        '''
        Variables, passwords, etc.
        '''

        self.OPENING_DAY = date(2014, 2, 18).strftime('%Y-%m-%d')

        self.OPENING_DATE = date(2014, 2, 18)

        self.YESTERDAY_DAY = (
            date.today() - timedelta(days=1)
        ).strftime('%Y-%m-%d')

        self.YESTERDAY_DATE = date.today() - timedelta(days=1)

        self.TODAY_DAY = (date.today()).strftime('%Y-%m-%d')
        self.TODAY_DATE = date.today()

        self.S3_PATH = 's3://lensnola/land-records'

        # Land Records Division remote subscription service:
        self.LRD_USERNAME = "myuser"
        self.LRD_PASSWORD = "mypass"

        self.GOOGLE_API_KEY = "mykey"

        # Twitter account:
        # Customer Key
        self.APP_KEY = 'myappkey'

        # Customer secret
        self.APP_SECRET = 'myappsecret'

        # Access Token
        self.OAUTH_TOKEN = 'myoauthtoken'

        # Access Token Secret
        self.OAUTH_TOKEN_SECRET = 'myoauthtokensecret'

        # Dashboard credentials
        self.DASHBOARD_USERNAME = 'myuser'
        self.DASHBOARD_PASSWORD = 'mypass'

        # Gmail credentials
        self.GMAIL_USERNAME = "myemail"
        self.GMAIL_PASSWORD = "mypass"
