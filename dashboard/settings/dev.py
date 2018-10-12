from .base import *


DEBUG = True
ALLOWED_HOSTS += ['*']

INSTALLED_APPS += [
    # erd diagram generator
    #'django_extensions',
]

# graph generation
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

CORS_ORIGIN_WHITELIST += [
    'dashboard-dev.ms.wits.ac.za:3080',
    'localhost:4080',
    'localhost:3080',
]
