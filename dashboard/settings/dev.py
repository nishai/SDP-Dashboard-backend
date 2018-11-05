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

# dangerous on production
CORS_ORIGIN_ALLOW_ALL = True

# makes life easier sometimes
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
]

# print annoying deprecated messages:
MIDDLEWARE += [
    'dashboard.shared.middleware.DeprecatedViewsMiddleware'
]




