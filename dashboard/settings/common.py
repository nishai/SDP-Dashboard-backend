"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Helper Variables
DJANGO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # folder in same directory as manage.py
PROJECT_DIR = os.path.dirname(DJANGO_DIR)                                   # folder containing manage.py
DATA_DIR = os.path.join(PROJECT_DIR, "data")                                # recommended data storage location

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
# $ python manage.py check --deploy

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dashboard.urls'

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

WSGI_APPLICATION = 'dashboard.wsgi.application'


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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
# also needed for debug

STATIC_URL = '/static/'

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

# Logging stuff
from .loggers import LOGGING
import logging.config
logging.config.dictConfig(LOGGING)
