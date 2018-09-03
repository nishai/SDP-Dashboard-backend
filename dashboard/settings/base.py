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
    # dashboard apps
    'dashboard.apps.dashboard_api',
    'dashboard.apps.excel_import',
    # external apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
]

# ========================================================================= #
# Requests                                                                  #
# ========================================================================= #

ALLOWED_HOSTS = []

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
    }
}

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
    os.path.join(ROOT_DIR, "logs"),
    datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
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

