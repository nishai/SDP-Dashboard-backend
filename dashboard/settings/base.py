"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import datetime
import logging.config
import os

import corsheaders.defaults

from .log.loggers import create_default_logger

# ========================================================================= #
# Entry Points                                                              #
# ========================================================================= #

WSGI_APPLICATION = 'dashboard.wsgi.application'

ROOT_URLCONF = 'dashboard.urls'

# ========================================================================= #
# Directories                                                               #
# ========================================================================= #

# Helper Variables
DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # folder in same directory as manage.py
ROOT_DIR = os.path.dirname(DASHBOARD_DIR)                                      # folder containing manage.py
DATA_DIR = os.path.join(ROOT_DIR, "data")                                      # recommended data storage location

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"Made data directory: {DATA_DIR}")

# ========================================================================= #
# Apps                                                                      #
# ========================================================================= #

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    # dashboard apps
    'dashboard.apps.dashapi',       # user related
    'dashboard.apps.excel_import',  # wits related - legacy
    'dashboard.apps.jsonquery',     # wits related
    # external apps
    'rest_framework',               # http://www.django-rest-framework.org
    'rest_framework_jwt',           # http://getblimp.github.io/django-rest-framework-jwt
    'django_auth_ldap',             # https://django-auth-ldap.readthedocs.io
    # alternative documentation views
    'rest_framework_swagger',
    # views & routing
    # 'dynamic_rest',  # https://github.com/AltSchool/dynamic-rest # 'rest_framework_filters' may be better alternative: https://github.com/philipn/django-rest-framework-filters # combined with https://github.com/alanjds/drf-nested-routers

]

# ========================================================================= #
# Requests                                                                  #
# ========================================================================= #

# Whitelist of trusted domains you can serve your app on
ALLOWED_HOSTS = []

# intercept and handle requests before our app.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================================================================== #
# CORS Policy (Cross-Origin Resource Sharing)                                #
#                                                                            #
# SETTINGS: https://github.com/ottoyiu/django-cors-headers                   #
#                                                                            #
# INFO: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS               #
#                                                                            #
# Cross-Origin Resource Sharing (CORS) is a mechanism that uses additional   #
# HTTP headers to tell a browser to let a web application running at one     #
# origin (domain) have permission to access selected resources from a server #
# at a different origin. A web application makes a cross-origin HTTP request #
# when it requests a resource that has a different origin                    #
# (domain, protocol, and port) than its own origin.                          #
#                                                                            #
# An example of a cross-origin request: The frontend JavaScript code for a   #
# web application served from http://domain-a.com uses XMLHttpRequest to     #
# make a request for http://api.domain-b.com/data.json.                      #
# ========================================================================== #

# A list of origin hostnames that are authorized to make cross-site HTTP requests (default: [])
CORS_ORIGIN_WHITELIST = [
    'dashboard-dev.ms.wits.ac.za:4080',
]

# GET, POST, etc (default: corsheaders.defaults.default_methods)
CORS_ALLOW_METHODS = corsheaders.defaults.default_methods

# accept, accept-encoding, authorization, content-type, etc (default: corsheaders.defaults.default_headers)
CORS_ALLOW_HEADERS = corsheaders.defaults.default_headers

# cookies will be allowed to be included in cross-site HTTP requests (default: False)
CORS_ALLOW_CREDENTIALS = False

# ========================================================================= #
# Authentication                                                            #
# ========================================================================= #

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# specifying ldap & local auth,
# allows us to assign permissions to individual ldap users,
# or even create a local superuser not present on the ldap
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'dashboard.settings.ldap.backends.LDAPBackendWitsStudents',  # extends 'django_auth_ldap.backend.LDAPBackend'
    'dashboard.settings.ldap.backends.LDAPBackendWitsStaff',     # extends 'django_auth_ldap.backend.LDAPBackend'
]

# All the settings: https://getblimp.github.io/django-rest-framework-jwt/#additional-settings
# Clarification on expiration settings: https://github.com/GetBlimp/django-rest-framework-jwt/issues/92#issuecomment-227763338
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),             # Default: seconds=300 - individual token expiration time (cannot be used to refresh if this passes)
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=30),    # Default: days=7 - how much time after the first original token was issued that future tokens can be refreshed from.
    # 'JWT_AUTH_HEADER_PREFIX': 'JWT',                              # Default: 'JWT' - http header "Authentication: JWT <token>"
    # 'JWT_AUTH_COOKIE': None,                                      # Default: None - If the specified cookie name should also be checked in addition to the auth header (header overrides cookie if present)
}

# ========================================================================= #
# Rest Framework                                                            #
# ========================================================================= #

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAuthenticated', # TODO: UNCOMMENT TO FORCE JWT AUTHENTICATION
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
}

# ========================================================================= #
# Templates                                                                 #
# ========================================================================= #

# needed for rest_framework debugging
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ========================================================================= #
# Database                                                                  #
# ========================================================================= #

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 10,  # https://docs.python.org/3.7/library/sqlite3.html#sqlite3.connect
        }
    }
}

# ========================================================================== #
# Languages                                                                  #
# ========================================================================== #

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ========================================================================== #
# Static Files                                                               #
# ========================================================================== #

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
# https://stackoverflow.com/questions/24022558
# needed for debug

STATIC_URL = '/static/'

# where files uploaded using FileField will go
MEDIA_ROOT = os.path.join(DATA_DIR, 'uploads')

# folders where Django will search for additional static files aside from the static folder of each app installed.
STATICFILES_DIRS = []

# directory where $ `manage.py collectstatic` will collect static files for deployment.
# this copies all files from STATICFILES_DIRS as well as all enabled apps
STATIC_ROOT = os.path.join(ROOT_DIR, 'dist')

# ========================================================================== #
# Logging - Config                                                           #
# ========================================================================== #

# template from django docs:
# https://docs.djangoproject.com/en/2.1/topics/logging/
# and django loggers and handlers
# https://stackoverflow.com/questions/45972977/django-logging-requests

LOGGING = create_default_logger(
    log_path=os.path.join(ROOT_DIR, "logs"),
    name=datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S"),
    console_only=os.getenv("DJANGO_LOG_TO_FILES") is None,
)

logging.config.dictConfig(LOGGING)

# ========================================================================== #
# Secret Key                                                                 #
# ========================================================================== #

def get_or_gen_key(file_url: str, length: int):
    try:
        return open(file_url).read().strip()
    except IOError:
        try:
            from django.utils.crypto import get_random_string
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
            key = get_random_string(length, chars)
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            with open(file_url, 'w+') as f:
                f.write(key)
                print(f'Generated new secret key at: {file_url}')
            if len(key) != length:
                raise Exception('Secret key length mismatch!')
            return key
        except IOError:
            raise Exception(f'Could not open {file_url} for writing!')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_FILE = os.path.join(DATA_DIR, "secret.token")
SECRET_KEY = get_or_gen_key(SECRET_FILE, 50)

# ========================================================================== #
# EOF                                                                        #
# ========================================================================== #

