# Python imports
from os.path import abspath, basename, dirname, join, normpath
import sys


# ##### PATH CONFIGURATION ################################


DJANGO_ROOT = dirname(dirname(abspath(__file__)))               # fetch Django's project directory
PROJECT_ROOT = dirname(DJANGO_ROOT)                             # fetch the project_root
SITE_NAME = basename(DJANGO_ROOT)                               # the name of the whole site
STATIC_ROOT = join(PROJECT_ROOT, 'deploy', 'data', 'static')    # collect static files here
MEDIA_ROOT = join(PROJECT_ROOT, 'deploy', 'data', 'media')      # collect media files here
STATICFILES_DIRS = [                                            # look for static assets here
    join(PROJECT_ROOT, 'static'),
]


# Modify Python Path
sys.path.append(normpath(join(PROJECT_ROOT, 'apps')))           # add apps/ to the Python path

# Apps
DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ##### SECURITY CONFIGURATION ############################

# We store the secret key here
# The required SECRET_KEY is fetched at the end of this file
SECRET_FILE = normpath(join(PROJECT_ROOT, 'deploy', 'run', 'SECRET.key'))

# these persons receive error notification
ADMINS = (
    ('your name', 'your_name@example.com'),
)
MANAGERS = ADMINS


# ========================================================================== #
# Running Config                                                             #
# ========================================================================== #

# ##### DJANGO RUNNING CONFIGURATION ######################

# the default WSGI application
WSGI_APPLICATION = f'{SITE_NAME}.wsgi.application'
ROOT_URLCONF = f'{SITE_NAME}.urls'

# ========================================================================== #
# URLS                                                                       #
# ========================================================================== #

API_URL_PREFIX = '/api'

# ========================================================================== #
# Debug                                                                      #
# ========================================================================== #

DEBUG = False

# ========================================================================== #
# Secret Key                                                                 #
# ========================================================================== #

try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        from django.utils.crypto import get_random_string
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
        SECRET_KEY = get_random_string(50, chars)
        with open(SECRET_FILE, 'w') as f:
            f.write(SECRET_KEY)
    except IOError:
        raise Exception(f'Could not open {SECRET_FILE} for writing!')
